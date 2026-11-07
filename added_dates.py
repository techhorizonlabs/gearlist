"""When each Gearlist entry was added, and the checks build.py and site/build_site.py run on it.

Every entry in resources.json has an `added` date (YYYY-MM-DD). The dates for the entries that
existed before the field did were taken from the git history of resources.json: each entry got
the author date (`git log --date=short`) of the first commit on main whose resources.json holds
its id.

EARLIEST_ADDED (30 October 2026) is the earliest date Gearlist records. The clone the dates were
first taken from begins at commit 578921b on that day, and the repository on GitHub has earlier
commits that the clone did not hold. So an entry dated 30 October 2026 was added on or before
that day, and a date from the history that is earlier still is recorded as 30 October 2026.

    python3 added_dates.py           fill in `added` for any entry that has none, from the history
    python3 added_dates.py --check   compare every `added` date with the history and change nothing

Run it on an up-to-date main. It reads the repository with git and makes no network calls.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = "resources.json"

# The earliest added date Gearlist records. An entry with this date was added on or before it.
# Keep in step with EARLIEST_ADDED in site/worker/catalog.mjs.
EARLIEST_ADDED = "2026-10-30"

ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def is_date(value):
    """True for a real calendar date written as YYYY-MM-DD."""
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def check(entries, updated):
    """Problems with the `added` dates, one plain sentence each. An empty list means none.

    Each entry needs an `added` date that is a real YYYY-MM-DD date, no earlier than
    EARLIEST_ADDED and no later than the list's `updated` date."""
    problems = []
    if not is_date(updated):
        problems.append(f"resources.json needs an updated date written as YYYY-MM-DD, and has {updated!r}.")
    for e in entries:
        name = e.get("id", "?")
        value = e.get("added")
        if value is None or value == "":
            problems.append(
                f"Entry {name} has no added date. Set added to the date you add the entry, as YYYY-MM-DD."
            )
        elif not is_date(value):
            problems.append(f"Entry {name} has an added date that is not a real YYYY-MM-DD date: {value!r}.")
        elif value < EARLIEST_ADDED:
            problems.append(
                f"Entry {name} has an added date of {value}, before {EARLIEST_ADDED}, the earliest date Gearlist "
                f"records. Entries from before then use {EARLIEST_ADDED}."
            )
        elif is_date(updated) and value > updated:
            problems.append(
                f"Entry {name} has an added date of {value}, after the list's updated date of {updated}. "
                "Set updated at the top of resources.json to today's date too."
            )
    return problems


def _git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def first_seen(repo=ROOT, ref="HEAD", path=DATA):
    """{id: date} for every id that has ever been in `path`: the author date of the first commit
    on the first-parent line of `ref` whose copy of the file holds that id."""
    log = _git(repo, "log", "--first-parent", "--reverse", "--format=%H%x09%ad", "--date=short", ref, "--", path)
    seen = {}
    for line in log.splitlines():
        if not line.strip():
            continue
        commit, day = line.split("\t")
        try:
            records = json.loads(_git(repo, "show", f"{commit}:{path}"))
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            # The commit deleted the file or left it unreadable. Later commits still count.
            continue
        for e in records.get("resources", []):
            if isinstance(e, dict) and isinstance(e.get("id"), str):
                seen.setdefault(e["id"], day)
    return seen


def history_dates(repo=ROOT, ref="HEAD"):
    """{id: added date} from the history: first_seen, with any date before EARLIEST_ADDED
    recorded as EARLIEST_ADDED."""
    return {ident: max(day, EARLIEST_ADDED) for ident, day in first_seen(repo, ref).items()}


def with_added(entry, day):
    """A copy of `entry` with `added` set to `day`, placed just after `source_checked`."""
    out = {}
    for key, value in entry.items():
        if key == "added":
            continue
        out[key] = value
        if key == "source_checked":
            out["added"] = day
    if "added" not in out:
        out["added"] = day
    return out


def backfill(entries, seen):
    """Sets `added` from `seen` on each entry that has none, in place. An entry that already has
    a date keeps it, and no other field changes. Returns the ids that are not in the history."""
    unknown = []
    for i, e in enumerate(entries):
        if e.get("added"):
            continue
        day = seen.get(e.get("id"))
        if day is None:
            unknown.append(e.get("id", "?"))
            continue
        entries[i] = with_added(e, day)
    return unknown


def summary(entries):
    counts = Counter(e.get("added") for e in entries)
    return [f"  {day}: {n}" for day, n in sorted(counts.items(), key=lambda kv: str(kv[0]), reverse=True)]


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description="Set or check each Gearlist entry's added date from git history.")
    parser.add_argument("--check", action="store_true", help="compare the dates with the history and change nothing")
    parser.add_argument("--ref", default="HEAD", help="the commit to read the history from (default HEAD)")
    args = parser.parse_args(argv)

    file = Path(root) / DATA
    data = json.loads(file.read_text(encoding="utf-8"))
    entries = data["resources"]
    seen = history_dates(root, args.ref)

    if args.check:
        differ = [(e["id"], e.get("added"), seen.get(e["id"])) for e in entries if e.get("added") != seen.get(e["id"])]
        print(f"{len(entries)} entries. Added dates:")
        print("\n".join(summary(entries)))
        for ident, have, history in differ:
            found = f"the history gives {history}" if history else "it is not in the history yet"
            print(f"  {ident}: resources.json has {have}, {found}")
        print("Every date matches the history." if not differ else f"{len(differ)} dates differ from the history.")
        return 1 if differ else 0

    unknown = backfill(entries, seen)
    file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(entries)} entries. Added dates:")
    print("\n".join(summary(entries)))
    if unknown:
        print("Not in the history yet, so set added by hand: " + ", ".join(unknown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
