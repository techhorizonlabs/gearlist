"""Group guides (guides.json) stay plain sentences with checked entry links and named sources."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import guides  # noqa: E402

ENTRIES = [{"id": "apple-mac-mini", "category": "Hardware"}, {"id": "gemma-4", "category": "Models"}]


def guide(paragraph="A Mac mini such as [[apple-mac-mini]] can host agents.", heading="Host only",
          sources=("https://www.apple.com/mac-mini/",), title="Which set-up do you need?", group="Hardware"):
    return {"groups": {group: {"title": title, "sections": [
        {"heading": heading, "paragraphs": [paragraph], "sources": list(sources)}]}}}


class GuidesTest(unittest.TestCase):
    def test_the_real_guides_pass(self):
        data = json.loads((ROOT / "resources.json").read_text())
        path = ROOT / "guides.json"
        if path.exists():
            self.assertEqual(guides.check(json.loads(path.read_text()), data["resources"]), [])

    def test_a_good_guide_passes(self):
        self.assertEqual(guides.check(guide(), ENTRIES), [])

    def test_links_split_into_parts(self):
        self.assertEqual(guides.parts("Use [[gemma-4]] locally."),
                         [("text", "Use "), ("link", "gemma-4"), ("text", " locally.")])

    def test_bad_guides_are_refused(self):
        cases = [
            guide(paragraph="Links to [[no-such-entry]]."),
            guide(paragraph="Has <b>HTML</b>."),
            guide(paragraph="Has a [markdown](https://x.example) link."),
            guide(paragraph="Has `code` and *stars*."),
            guide(paragraph="Has a pipe | here."),
            guide(paragraph="Two lines\n\n# Heading"),
            guide(paragraph="An en dash \u2013 here."),
            guide(paragraph=""),
            guide(paragraph="x" * 701),
            guide(heading="Heading # with hash"),
            guide(sources=()),
            guide(sources=("http://insecure.example",)),
            guide(sources=("https://a.example/ path",)),
            guide(group="No such group"),
            guide(paragraph="  1. indented ordered item"),
            guide(paragraph="    indented code"),
            guide(paragraph="Trailing space "),
            guide(heading=" Padded heading"),
            guide(paragraph="Email test@example.invalid"),
        ]
        for case in cases:
            self.assertTrue(guides.check(case, ENTRIES), case)

    def test_messages_have_no_en_or_em_dashes(self):
        for p in guides.check(guide(paragraph="An en dash \u2013 here."), ENTRIES):
            self.assertNotRegex(p, "[\u2013\u2014]")


class SourceTest(unittest.TestCase):
    def test_only_plain_https_urls_with_a_hostname_pass(self):
        good = ["https://www.apple.com/mac-mini/specs/", "https://docs.x.ai/build/overview"]
        bad = ["http://apple.com/", "javascript:alert(1)", "https://", "https:///path", "https://user:pw@apple.com/",
               "https://apple.com:8443/", "https://localhost/", "https://apple.com/ x", "https://apple.com/\"x",
               "https://apple.com/\nx", "data:text/html,hi", "//apple.com/", 7]
        for u in good:
            self.assertTrue(guides.source_ok(u), u)
        for u in bad:
            self.assertFalse(guides.source_ok(u), u)
            self.assertTrue(guides.check(guide(sources=(u,)), ENTRIES), u)


class MarkdownTextTest(unittest.TestCase):
    def test_text_that_would_start_a_markdown_block_is_escaped(self):
        cases = {"- item": "\\- item", "+ item": "\\+ item", "* item": "\\* item", "# heading": "\\# heading",
                 "1. one": "1\\. one", "2) two": "2\\) two", "--- rule": "\\--- rule", "=== rule": "\\=== rule",
                 "> quote": "&gt; quote"}
        for text, want in cases.items():
            self.assertEqual(guides.md_text(text), want, text)

    def test_inline_markdown_entities_and_bare_urls_stay_literal(self):
        self.assertEqual(guides.md_text("~~gone~~"), "\\~\\~gone\\~\\~")
        self.assertEqual(guides.md_text("&amp; and a & b"), "&amp;amp; and a &amp; b")
        self.assertNotIn("://", guides.md_text("see https://evil.example now"))
        self.assertNotRegex(guides.md_text("www.evil.example"), r"(?<!\\)www\.")
        self.assertEqual(guides.md_text("Max+ 395 from US$589.99, 17 W."), "Max+ 395 from US$589.99, 17 W.")

    def test_multi_line_text_is_refused(self):
        with self.assertRaises(ValueError):
            guides.md_text("one\n- two")


LITERAL_CASES = ["1. literal text", "---", "Research &amp; Development", "See [[apple-mac-mini]].",
                 "  1. indented ordered item", "  - indented bullet item", "    indented code", "  ---",
                 "Email test@example.invalid", "see https://a.example and www.b.example", "> quote", "+ plus",
                 "# hash", "~~strike~~ and ! bang", "Ends with [[apple-mac-mini]]"]
BLOCK_START = re.compile(r"^(?: |\t|[-+*>#=_~`|]|\d+[.)])")


class ParsedMarkdownTest(unittest.TestCase):
    """The guide Markdown, read by a GitHub Flavored Markdown parser, holds one plain paragraph per
    guide paragraph and no links except the generated entry links."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_site_for_parse", ROOT / "site" / "build_site.py")
        cls.site = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.site)
        e = {"id": "apple-mac-mini", "category": "Hardware", "name": "Apple Mac mini"}
        g = {"name": "Hardware", "guide": {"title": "Which set-up?", "sections": [{
            "heading": "Literal text control", "paragraphs": LITERAL_CASES, "sources": ["https://example.invalid/"]}]}}
        cls.lines = cls.site.guide_md(g, {"apple-mac-mini": e})

    def test_every_guide_line_starts_as_a_plain_paragraph(self):
        body = [l for l in self.lines if l and not l.startswith(("## ", "### ", "Sources: "))]
        self.assertEqual(len(body), len(LITERAL_CASES))
        for line in body:
            self.assertNotRegex(line, BLOCK_START, line)
            self.assertNotRegex(line, r"(?<!\\)@", line)
            self.assertNotIn("://", line.replace("https://gearlist.build/tools/apple-mac-mini/", ""))

    def test_a_gfm_parser_sees_only_paragraphs_and_entry_links(self):
        import shutil
        import subprocess
        if not shutil.which("pandoc"):
            self.skipTest("pandoc is not installed; the line checks above still run")
        md = "\n".join(self.lines)
        ast = json.loads(subprocess.run(["pandoc", "-f", "gfm", "-t", "json"], input=md, capture_output=True,
                                        text=True, check=True).stdout)
        blocks = ast["blocks"]
        self.assertEqual([b["t"] for b in blocks], ["Header", "Header"] + ["Para"] * (len(LITERAL_CASES) + 1))
        links = []

        def walk(x):
            if isinstance(x, dict):
                if x.get("t") == "Link":
                    links.append(x["c"][2][0])
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)

        walk(blocks[:-1])
        self.assertEqual(set(links), {"https://gearlist.build/tools/apple-mac-mini/"})
        plain = subprocess.run(["pandoc", "-f", "gfm", "-t", "plain", "--wrap=none"], input=md, capture_output=True,
                               text=True, check=True).stdout.splitlines()
        for case in LITERAL_CASES:
            want = case.replace("[[apple-mac-mini]]", "Apple Mac mini")
            self.assertIn(want, plain, case)


class SiteBuilderTest(unittest.TestCase):
    """site/build_site.py checks guides.json itself and writes literal Markdown."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_site_for_guides", ROOT / "site" / "build_site.py")
        cls.site = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.site)

    def load_with(self, data, entries):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "guides.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            old = self.site.GUIDES_FILE
            self.site.GUIDES_FILE = path
            try:
                return self.site.load_guides(entries)
            finally:
                self.site.GUIDES_FILE = old

    def test_the_standalone_builder_refuses_bad_guides(self):
        entries = [{"id": "apple-mac-mini", "category": "Hardware", "name": "Apple Mac mini"}]
        for bad in (guide(sources=("javascript:alert(1)",)), guide(sources=("http://apple.com/",)),
                    guide(paragraph="Has <script>x</script>."), guide(paragraph="Links [[nope]].")):
            with self.assertRaises(SystemExit):
                self.load_with(bad, entries)
        self.assertIn("Hardware", self.load_with(guide(), entries))

    def test_a_standalone_build_stops_on_a_bad_guide_before_writing(self):
        import tempfile
        from unittest import mock
        bad = json.loads((ROOT / "guides.json").read_text())
        first = next(iter(bad["groups"].values()))
        first["sections"][0]["sources"] = ["javascript:alert(1)"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "guides.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            wrote = []
            with mock.patch.object(self.site, "GUIDES_FILE", path), \
                    mock.patch.object(self.site, "build_pages", side_effect=lambda *a, **k: wrote.append(1)), \
                    mock.patch.object(self.site.sys, "argv", ["build_site.py"]):
                with self.assertRaises(SystemExit) as stop:
                    self.site.main()
            self.assertIn("must be one https URL", str(stop.exception))
            self.assertEqual(wrote, [])

    def test_generated_markdown_keeps_links_and_escapes_text(self):
        e = {"id": "apple-mac-mini", "category": "Hardware", "name": "Apple Mac mini"}
        g = {"name": "Hardware", "guide": {"title": "Which set-up?", "sections": [{
            "heading": "- Host", "paragraphs": ["- Start with [[apple-mac-mini]], 1. then ~~x~~ &amp; https://a.example"],
            "sources": ["https://www.apple.com/mac-mini/"]}]}}
        lines = self.site.guide_md(g, {"apple-mac-mini": e})
        body = [l for l in lines if l and not l.startswith("Sources:")]
        self.assertIn("[Apple Mac mini](https://gearlist.build/tools/apple-mac-mini/)", "\n".join(body))
        for line in body:
            self.assertNotRegex(line, r"^(?:[-+*>]\s|\d+[.)]\s)", line)
            self.assertNotIn("~~", line.replace("\\~", ""))
        text = "\n".join(body).replace("https://gearlist.build/tools/apple-mac-mini/", "")
        self.assertNotIn("://", text)
        self.assertIn("&amp;amp;", text)
        self.assertIn("### \\- Host", lines)


if __name__ == "__main__":
    unittest.main()
