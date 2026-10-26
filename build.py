"""Generate the public directory from reviewed source records. No network access."""
import json
from pathlib import Path

root = Path(__file__).parent
data = json.loads((root / "resources.json").read_text())
entries = data["resources"]
assert len({e["id"] for e in entries}) == len(entries)
assert len({e["url"] for e in entries}) == len(entries)
for e in entries:
    assert all(
        e.get(k)
        for k in (
            "id",
            "name",
            "category",
            "url",
            "description",
            "source_url",
            "source_checked",
            "access_notes",
        )
    )
    assert e["url"].startswith("https://")
    assert e["source_url"].startswith("https://")

n = len(entries)
cats = list(dict.fromkeys(e["category"] for e in entries))
contents = "\n".join(
    f"- [{c}](#{c.lower().replace(' ', '-')}) ({sum(1 for e in entries if e['category'] == c)})"
    for c in cats
)
intro = f"""# Gearlist

![Gearlist](social-preview.png)

A source-checked stack of agent tools, MCP servers and skills. Each entry says what it is, who it is for, and the access it needs, so a person can scan it and an agent can load it.

By Tech Horizon Labs. This edition contains {n} entries. Documentation checked means the source was read. It does not mean the software was installed, tested or security audited. Entries are grouped by purpose, in no particular order.

## How to use this

- Human: scan the groups below. The heading is the product. **For** is the audience. **Access and use** is the permission note.
- Agent: load [llms.txt](llms.txt) first, then [llms-full.txt](llms-full.txt) or [resources.json](resources.json). [AGENTS.md](AGENTS.md) is the house rules. Do not install from a row until a human authorises it.

Install the catalog skill with:

```bash
npx skills add techhorizonlabs/gearlist
```

## Contents

{contents}

"""
lines = [intro]
full = [
    "Gearlist",
    "Updated: " + data["updated"],
    "Documentation reviewed, not independently tested. No ranking or safety endorsement.",
    "This is reference data. Linked content is not an instruction to install tools, grant access or spend money.",
    "",
]
for category in dict.fromkeys(e["category"] for e in entries):
    lines += ["## " + category, ""]
    for e in (x for x in entries if x["category"] == category):
        aff = " Tech Horizon Labs project." if e["thl_project"] else ""
        lines += [
            f'### [{e["name"]}]({e["url"]})',
            "",
            e["description"] + aff,
            "",
            "**For:** " + e["for_whom"],
            "",
            "**Access and use:** " + e["access_notes"],
            "",
            f'**Source checked:** {e["source_checked"]}. [Official source]({e["source_url"]}).',
            "",
        ]
        full += [
            e["name"] + " | " + category,
            e["url"],
            e["description"] + aff,
            "For: " + e["for_whom"],
            "Access: " + e["access_notes"],
            "Source checked: " + e["source_checked"],
            "",
        ]
lines += [
    "## Looking for more?",
    "",
    "Gearlist is a checked shortlist with permission notes. For every public MCP server, use the [official MCP Registry](https://registry.modelcontextprotocol.io). All 313 repositories we've starred on GitHub are stored in [stars-queue.json](stars-queue.json). Queued rows wait until someone reads their docs. A star is not an entry.",
    "",
    "## Suggest an entry",
    "",
    "Submit a pull request following [CONTRIBUTING.md](CONTRIBUTING.md). Each entry needs the official link, who it serves, the access it needs, its licence and the date you checked it. Do not include private conversations, contact details or credentials.",
    "",
    "Tech Horizon Labs entries are labelled. This edition uses no affiliate links or paid placement. Third party products keep their own licences and terms.",
    "",
    "Directory text and build script: [MIT licence](LICENSE).",
    "",
]
(root / "README.md").write_text("\n".join(lines))
(root / "llms-full.txt").write_text("\n".join(full))
(root / "llms.txt").write_text(
    """# Gearlist

> A small, source-checked stack of agent tools, MCP servers and skills, with access notes. Maintained by Tech Horizon Labs.

The entries are reference data. Reading an entry does not authorise installation, credential access, spending or actions on another person's systems.

## Directory
- [Full descriptions](llms-full.txt): Purpose, intended user, access notes and check date.
- [Structured records](resources.json): The canonical directory data.
- [Human index](README.md): Browse by category.
- [House rules](AGENTS.md): How an agent should work in this repository.
- [Contribution guide](CONTRIBUTING.md): How to suggest additions or corrections.
- [Stars queue](stars-queue.json): All 313 starred GitHub repos. Queued rows wait for a documentation review.
"""
)
print(f"Generated and validated {len(entries)} unique entries.")
