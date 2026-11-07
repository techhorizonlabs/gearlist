"""Group guides (guides.json) stay plain sentences with checked entry links and named sources."""
import json
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
        ]
        for case in cases:
            self.assertTrue(guides.check(case, ENTRIES), case)

    def test_messages_have_no_en_or_em_dashes(self):
        for p in guides.check(guide(paragraph="An en dash \u2013 here."), ENTRIES):
            self.assertNotRegex(p, "[\u2013\u2014]")


if __name__ == "__main__":
    unittest.main()
