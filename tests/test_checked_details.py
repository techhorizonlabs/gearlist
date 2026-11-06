"""Offline tests for the "What we checked" box on Gearlist entry pages (site/build_site.py).

The built pages only exercise the fields resources.json has today. These fixture entries
cover the other cases: a licence that is present, and a verification that is missing or
blank, which must be left out rather than filled in.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

spec = importlib.util.spec_from_file_location("build_site", ROOT / "site" / "build_site.py")
build_site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_site)

BASE = {
    "id": "fixture",
    "name": "Fixture",
    "category": "Agent tools",
    "url": "https://example.com/",
    "description": "A test entry.",
    "for_whom": "Tests.",
    "access_notes": "None beyond a public clone.",
    "source_url": "https://example.com/docs",
    "source_checked": "2026-11-07",
    "thl_project": False,
}
GROUP = {"name": "Agent tools", "slug": "agent-tools", "entries": [BASE]}
OG = ("https://gearlist.build/social-preview.png", 1280, 640, "alt")


def labels(entry):
    return [label for label, _ in build_site.checked_fields(entry)]


class CheckedDetailsTest(unittest.TestCase):
    def test_date_and_source_always_show(self):
        self.assertEqual(labels(BASE), ["Last checked", "Source read"])
        html = build_site.render_checked(BASE)
        self.assertIn('<h2 id="h-checked">What we checked</h2>', html)
        self.assertIn('<time datetime="2026-11-07">7 November 2026</time>', html)
        self.assertIn('<a href="https://example.com/docs">example.com/docs</a>', html)

    def test_licence_and_scope_show_only_when_present(self):
        entry = dict(BASE, verification="Repository README reviewed; not installed", licence="MIT")
        self.assertEqual(labels(entry), ["Last checked", "Source read", "How it was checked", "Licence"])
        html = build_site.render_checked(entry)
        self.assertIn("<dt>How it was checked</dt><dd>Repository README reviewed; not installed</dd>", html)
        self.assertIn("<dt>Licence</dt><dd>MIT</dd>", html)

    def test_missing_or_blank_fields_are_left_out(self):
        for entry in (BASE, dict(BASE, verification="", licence="  "), dict(BASE, licence=None)):
            html = build_site.render_checked(entry)
            self.assertNotIn("How it was checked", html)
            self.assertNotIn("Licence", html)
            self.assertNotIn("unknown", html.lower())

    def test_values_are_escaped_as_written(self):
        entry = dict(BASE, licence="Apache-2.0 <with> \"notes\"")
        self.assertIn("<dd>Apache-2.0 &lt;with&gt; &quot;notes&quot;</dd>", build_site.render_checked(entry))

    def test_markdown_copy_lists_the_same_fields(self):
        entry = dict(BASE, licence="MIT")
        md = build_site.render_tool_md(entry, GROUP, [], title="Fixture", description="d", og=OG)
        self.assertIn(
            "## What we checked\n\n- Last checked: 7 November 2026\n- Source read: https://example.com/docs\n"
            "- Licence: MIT\n",
            md,
        )
        self.assertIn('licence: "MIT"', md)
        plain = build_site.render_tool_md(BASE, GROUP, [], title="Fixture", description="d", og=OG)
        self.assertNotIn("Licence", plain)
        self.assertNotIn("licence:", plain)


if __name__ == "__main__":
    unittest.main()
