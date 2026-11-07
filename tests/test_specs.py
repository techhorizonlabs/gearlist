"""Comparison specs stay plain text: specs.check refuses bad specs, and the Markdown table built
from them cannot be broken out of by a hostile label, value or name."""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import specs  # noqa: E402

spec = importlib.util.spec_from_file_location("build_site", ROOT / "site" / "build_site.py")
build_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_site)

HOSTILE_ONE_LINE = [
    "x | y",
    "back\\slash|pipe",
    "a \\| b",
    "<script>alert(1)</script>",
    "<b>bold</b> & more",
    "[link](https://evil.example)",
    "![img](https://evil.example/x.png)",
    "https://evil.example/path",
    "www.evil.example",
    "`code` and *stars* and _under_",
    "~~gone~~ # not a heading",
]
MULTI_LINE = [
    "fine\n\n# Heading",
    "a\rb",
    "tab\there",
    "line separator",
    "para separator",
    "next\x85line",
]


def unescaped_pipes(line):
    """Pipes not preceded by an odd run of backslashes."""
    return len(re.findall(r"(?<!\\)(?:\\\\)*\|", line))


def group(entries):
    return {"name": "Hardware", "entries": entries}


def entry(i, pairs, name=None):
    return {"id": f"e{i}", "name": name or f"Entry {i}", "specs": pairs}


class CheckTest(unittest.TestCase):
    def test_the_real_list_passes(self):
        import json
        data = json.loads((ROOT / "resources.json").read_text())
        self.assertEqual(specs.check(data["resources"]), [])

    def test_multi_line_labels_and_values_are_refused(self):
        for text in MULTI_LINE:
            for pairs in ([[text, "ok"]], [["ok", text]]):
                problems = specs.check([entry(1, pairs)])
                self.assertTrue(any("one line" in p for p in problems), (text, pairs, problems))

    def test_shape_length_dash_and_repeat_rules(self):
        cases = [
            [],
            [["only label"]],
            [["label", 3]],
            [["", "value"]],
            [[" padded", "value"]],
            [["x" * 41, "value"]],
            [["label", "y" * 121]],
            [["label", "a \u2014 b"]],
            [["same", "1"], ["same", "2"]],
        ]
        for pairs in cases:
            self.assertTrue(specs.check([entry(1, pairs)]), pairs)

    def test_messages_have_no_en_or_em_dashes(self):
        for pairs in ([["label", "a \u2014 b"]], [["x\ny", "v"]]):
            for p in specs.check([entry(1, pairs)]):
                self.assertNotRegex(p, "[\u2013\u2014]")


class MarkdownCellTest(unittest.TestCase):
    def test_hostile_text_stays_in_one_cell_as_plain_text(self):
        for text in HOSTILE_ONE_LINE:
            out = specs.md_cell(text)
            self.assertNotIn("\n", out)
            self.assertEqual(unescaped_pipes(out), 0, (text, out))
            self.assertNotRegex(out, r"[<>]", (text, out))
            self.assertNotRegex(out, r"(?<!\\)(?:\\\\)*[\[\]`*_~#!]", (text, out))
            self.assertNotIn("://", out)
            self.assertNotRegex(out.lower(), r"(?<!\\)www\.")

    def test_multi_line_text_is_refused(self):
        for text in MULTI_LINE[:2] + MULTI_LINE[3:]:
            with self.assertRaises(ValueError):
                specs.md_cell(text)

    def test_ordinary_values_read_the_same(self):
        self.assertEqual(specs.md_cell("US$0.10 / US$0.50"), "US$0.10 / US$0.50")
        self.assertEqual(specs.md_cell("32 GB GDDR6, 640 GB/s"), "32 GB GDDR6, 640 GB/s")


class CompareTableTest(unittest.TestCase):
    def test_hostile_labels_values_and_names_keep_the_table_shape(self):
        rows = []
        for i, text in enumerate(HOSTILE_ONE_LINE):
            rows.append(entry(i, [[text[:40], text], ["Plain", "ok"]], name=text))
        lines = build_site.compare_md(group(rows))
        table = [line for line in lines if line.startswith("|")]
        header_pipes = unescaped_pipes(table[0])
        self.assertEqual(len(table), len(rows) + 2)
        for line in table:
            self.assertEqual(unescaped_pipes(line), header_pipes, line)
            self.assertNotRegex(line, r"[<>]")
        html = build_site.render_compare(group(rows))
        self.assertNotIn("<script>", html)
        self.assertNotIn("<b>", html)

    def test_a_multi_line_value_stops_the_markdown_build(self):
        bad = group([entry(1, [["Memory", "1 GB"]]), entry(2, [["Memory", "x\n\n# Heading"]])])
        with self.assertRaises(ValueError):
            build_site.compare_md(bad)


if __name__ == "__main__":
    unittest.main()
