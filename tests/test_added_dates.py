"""Offline tests for the added dates: added_dates.py (the check and the git history backfill),
the checks in build.py and site/build_site.py, and the What's new feed.

The history tests build a small git repository in a temporary folder. No network access.
"""

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


added_dates = load("added_dates", ROOT / "added_dates.py")
build_site = load("build_site_for_added", ROOT / "site" / "build_site.py")

FIRST = added_dates.EARLIEST_ADDED
ATOM = "{http://www.w3.org/2005/Atom}"


def entry(ident, **extra):
    base = {
        "id": ident,
        "name": ident.title(),
        "category": "Agent tools",
        "url": f"https://example.com/{ident}",
        "description": f"The {ident} test entry.",
        "for_whom": "Tests.",
        "access_notes": "None beyond a public clone.",
        "source_url": f"https://example.com/{ident}/docs",
        "source_checked": "2026-11-01",
        "verification": "Official documentation reviewed; not independently tested",
        "thl_project": False,
    }
    base.update(extra)
    return base


def real_data():
    return json.loads((ROOT / "resources.json").read_text(encoding="utf-8"))


class CheckTest(unittest.TestCase):
    def test_the_real_list_passes(self):
        data = real_data()
        self.assertEqual(added_dates.check(data["resources"], data["updated"]), [])
        for e in data["resources"]:
            keys = list(e)
            self.assertEqual(keys.index("added"), keys.index("source_checked") + 1, f"{e['id']} keeps added beside source_checked")

    def test_the_earliest_date_and_the_updated_date_are_allowed(self):
        entries = [entry("a", added=FIRST), entry("b", added="2026-11-07")]
        self.assertEqual(added_dates.check(entries, "2026-11-07"), [])

    def test_a_missing_or_empty_date_is_refused(self):
        for e in (entry("a"), entry("a", added=""), entry("a", added=None)):
            problems = added_dates.check([e], "2026-11-07")
            self.assertEqual(len(problems), 1)
            self.assertIn("Entry a has no added date", problems[0])

    def test_a_date_that_is_not_a_real_iso_date_is_refused(self):
        for value in ("2026-11-31", "2026-02-29", "7 November 2026", "2026-11-7", "2026/11/07", 20261107, "2026-11-07T00:00:00Z"):
            problems = added_dates.check([entry("a", added=value)], "2026-11-07")
            self.assertEqual(len(problems), 1, value)
            self.assertIn("not a real YYYY-MM-DD date", problems[0])

    def test_a_date_before_the_earliest_date_is_refused(self):
        problems = added_dates.check([entry("a", added="2026-10-29")], "2026-11-07")
        self.assertEqual(len(problems), 1)
        self.assertIn(f"before {FIRST}, the earliest date Gearlist records", problems[0])

    def test_a_date_after_the_updated_date_is_refused(self):
        problems = added_dates.check([entry("a", added="2026-11-08")], "2026-11-07")
        self.assertEqual(len(problems), 1)
        self.assertIn("after the list's updated date of 2026-11-07", problems[0])
        self.assertIn("Set updated", problems[0])

    def test_a_bad_updated_date_is_reported(self):
        problems = added_dates.check([entry("a", added=FIRST)], "soon")
        self.assertTrue(any("needs an updated date" in p for p in problems))

    def test_messages_have_no_en_or_em_dashes(self):
        cases = [entry("a"), entry("b", added="x"), entry("c", added="2026-01-01"), entry("d", added="2027-01-01")]
        for problem in added_dates.check(cases, "2026-11-07"):
            self.assertNotRegex(problem, "[\u2013\u2014]")


class GitRepo:
    """A throwaway repository whose commits carry chosen author and committer dates."""

    def __init__(self, folder):
        self.folder = Path(folder)
        self.git("init", "-q", "-b", "main")

    def git(self, *args, day=None):
        env = dict(os.environ)
        for key in [k for k in env if k.startswith("GIT_")]:
            del env[key]
        if day:
            env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = f"{day}T09:00:00+00:00"
        return subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "-c", "commit.gpgsign=false",
             "-c", "core.hooksPath=/dev/null", *args],
            cwd=self.folder, env=env, check=True, capture_output=True, text=True,
        ).stdout

    def commit(self, day, ids, message):
        data = {"title": "Gearlist", "updated": day, "resources": [entry(i) for i in ids]}
        (self.folder / "resources.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.git("add", "resources.json")
        self.git("commit", "-q", "-m", message, day=day)


class HistoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which("git") is None:
            raise unittest.SkipTest("git is not installed")

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = GitRepo(self.tmp.name)
        r = self.repo
        r.commit("2026-10-28", ["alpha", "older"], "Before the earliest date")
        r.commit(FIRST, ["alpha", "beta", "older"], "Add beta")
        r.commit("2026-11-05", ["alpha", "beta", "older", "gamma"], "Add gamma")
        r.commit("2026-11-06", ["alpha", "older", "gamma", "delta"], "Drop beta, add delta")
        # A side branch adds epsilon on 1 November. It reaches main in a merge on 7 November,
        # and the first commit on main to hold it is the merge.
        r.git("checkout", "-q", "-b", "side", "HEAD~2")
        r.commit("2026-11-01", ["alpha", "beta", "older", "epsilon"], "Add epsilon on a branch")
        r.git("checkout", "-q", "main")
        r.git("merge", "-q", "--no-ff", "--no-commit", "-s", "ours", "side")
        r.commit("2026-11-07", ["alpha", "older", "gamma", "delta", "epsilon"], "Merge side")

    def tearDown(self):
        self.tmp.cleanup()

    def test_each_id_gets_the_date_of_the_first_commit_on_main_that_holds_it(self):
        seen = added_dates.first_seen(self.repo.folder)
        self.assertEqual(seen["alpha"], "2026-10-28")
        self.assertEqual(seen["beta"], FIRST, "a dropped id keeps its first date")
        self.assertEqual(seen["gamma"], "2026-11-05")
        self.assertEqual(seen["delta"], "2026-11-06")
        self.assertEqual(seen["epsilon"], "2026-11-07", "a branch commit is not on main; the merge is")

    def test_a_date_before_the_earliest_date_is_recorded_as_the_earliest_date(self):
        dates = added_dates.history_dates(self.repo.folder)
        self.assertEqual(dates["alpha"], FIRST)
        self.assertEqual(dates["older"], FIRST)
        self.assertEqual(dates["gamma"], "2026-11-05")

    def test_backfill_sets_only_missing_dates_beside_source_checked(self):
        seen = added_dates.history_dates(self.repo.folder)
        entries = [entry("alpha"), entry("gamma", added="2026-11-06"), entry("zeta")]
        before = [dict(e) for e in entries]
        unknown = added_dates.backfill(entries, seen)
        self.assertEqual(unknown, ["zeta"])
        self.assertEqual(entries[0]["added"], FIRST)
        self.assertEqual(list(entries[0]), [*list(before[0])[:9], "added", *list(before[0])[9:]])
        self.assertEqual(entries[1], before[1], "a date already set is kept")
        self.assertNotIn("added", entries[2])
        for after, was in zip(entries, before):
            self.assertEqual({k: v for k, v in after.items() if k != "added"}, {k: v for k, v in was.items() if k != "added"})

    def test_the_command_writes_the_dates_and_check_compares_them(self):
        folder = self.repo.folder
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(added_dates.main([], root=folder), 0)
        text = (folder / "resources.json").read_text(encoding="utf-8")
        data = json.loads(text)
        self.assertEqual(text, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        self.assertEqual({e["id"]: e["added"] for e in data["resources"]},
                         {"alpha": FIRST, "older": FIRST, "gamma": "2026-11-05", "delta": "2026-11-06", "epsilon": "2026-11-07"})
        with contextlib.redirect_stdout(io.StringIO()) as report:
            self.assertEqual(added_dates.main(["--check"], root=folder), 0)
        self.assertIn("Every date matches the history.", report.getvalue())
        next(e for e in data["resources"] if e["id"] == "gamma")["added"] = "2026-11-06"
        (folder / "resources.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()) as report:
            self.assertEqual(added_dates.main(["--check"], root=folder), 1)
        self.assertIn("resources.json has 2026-11-06, the history gives 2026-11-05", report.getvalue())


class SameDateEverywhereTest(unittest.TestCase):
    def test_the_worker_and_the_site_use_the_same_earliest_date(self):
        catalog = (ROOT / "site" / "worker" / "catalog.mjs").read_text(encoding="utf-8")
        self.assertEqual(re.findall(r'EARLIEST_ADDED = "([^"]+)"', catalog), [FIRST])
        self.assertEqual(build_site.EARLIEST_ADDED, FIRST)
        self.assertEqual(min(e["added"] for e in real_data()["resources"]), FIRST)


class BuildValidationTest(unittest.TestCase):
    """build.py run as a script in a temporary copy of the repository root."""

    def run_build(self, mutate=None):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for name in ("build.py", "added_dates.py", "specs.py", "guides.py", "stars-queue.json"):
                shutil.copyfile(ROOT / name, folder / name)
            data = real_data()
            if mutate:
                mutate(data)
            (folder / "resources.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            return subprocess.run([sys.executable, "build.py"], cwd=folder, capture_output=True, text=True)

    def test_the_real_list_builds(self):
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Generated and validated", result.stdout)

    def test_bad_added_dates_stop_the_build(self):
        def drop(data):
            del data["resources"][0]["added"]

        def early(data):
            data["resources"][1]["added"] = "2026-10-01"

        def late(data):
            data["resources"][2]["added"] = "2026-12-01"

        def fake(data):
            data["resources"][3]["added"] = "2026-11-31"

        data = real_data()
        for mutate, ident, message in (
            (drop, data["resources"][0]["id"], "has no added date"),
            (early, data["resources"][1]["id"], "the earliest date Gearlist records"),
            (late, data["resources"][2]["id"], "after the list's updated date"),
            (fake, data["resources"][3]["id"], "not a real YYYY-MM-DD date"),
        ):
            result = self.run_build(mutate)
            self.assertNotEqual(result.returncode, 0, message)
            self.assertIn(f"Entry {ident} ", result.stderr)
            self.assertIn(message, result.stderr)


class BuildSiteValidationTest(unittest.TestCase):
    def test_the_site_build_refuses_a_bad_added_date(self):
        data = real_data()
        data["resources"][0]["added"] = "2026-10-29"
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "resources.json").write_text(json.dumps(data), encoding="utf-8")
            saved = build_site.ROOT
            build_site.ROOT = Path(tmp)
            try:
                with self.assertRaises(SystemExit) as stop:
                    build_site.load_entries()
            finally:
                build_site.ROOT = saved
        self.assertIn(f"Entry {data['resources'][0]['id']} has an added date of 2026-10-29", str(stop.exception))


class FeedTest(unittest.TestCase):
    def feed(self, groups):
        return ET.fromstring(build_site.render_feed(groups).encode("utf-8"))

    def test_the_feed_parses_and_lists_the_latest_additions_newest_first(self):
        data = real_data()
        groups = build_site.group_entries(data["resources"])
        root = self.feed(groups)
        self.assertEqual(root.tag, ATOM + "feed")
        self.assertEqual(root.findtext(ATOM + "title"), "New on Gearlist")
        entries = root.findall(ATOM + "entry")
        later = [e for g in groups for e in g["entries"] if e["added"] != FIRST]
        self.assertEqual(len(entries), min(build_site.FEED_LIMIT, len(later)))
        self.assertLessEqual(len(entries), 50)
        by_id = {e["id"]: e for e in data["resources"]}
        dates = []
        for node in entries:
            link = node.find(ATOM + "link").get("href")
            ident = re.fullmatch(r"https://gearlist\.build/tools/([a-z0-9-]+)/", link)[1]
            e = by_id[ident]
            self.assertEqual(node.findtext(ATOM + "title"), e["name"])
            self.assertEqual(node.findtext(ATOM + "summary"), e["description"])
            self.assertEqual(node.findtext(ATOM + "id"), f"tag:gearlist.build,2026:tools/{ident}")
            self.assertEqual(node.findtext(ATOM + "updated"), e["added"] + "T00:00:00Z")
            self.assertEqual(node.find(ATOM + "category").get("term"), e["category"])
            self.assertNotEqual(e["added"], FIRST, "entries with the earliest date stay out of the feed")
            dates.append(e["added"])
        self.assertEqual(dates, sorted(dates, reverse=True))
        self.assertEqual(root.findtext(ATOM + "updated"), dates[0] + "T00:00:00Z")

    def test_a_short_history_gives_a_short_feed_and_escapes_text(self):
        entries = [
            entry("one", added=FIRST),
            entry("two", added="2026-11-05", description='Says "hi" & <waves>.'),
            entry("three", added="2026-11-06", category="Platforms"),
        ]
        root = self.feed(build_site.group_entries(entries))
        got = [(n.findtext(ATOM + "title"), n.findtext(ATOM + "summary")) for n in root.findall(ATOM + "entry")]
        self.assertEqual(got, [("Three", "The three test entry."), ("Two", 'Says "hi" & <waves>.')])

    def test_the_first_commit_line_counts_its_entries(self):
        self.assertEqual(
            build_site.first_batch_line([entry("a")]),
            "1 entry was added on or before 30 October 2026, the earliest date Gearlist records.",
        )
        self.assertTrue(build_site.first_batch_line([entry("a"), entry("b")]).startswith("2 entries were added on or before"))


if __name__ == "__main__":
    unittest.main()
