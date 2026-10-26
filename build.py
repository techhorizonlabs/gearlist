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
intro = f"""# Gearlist

A small, source-checked stack of agent tools, MCP servers and skills, with the access each one needs, so you can point an agent at this repo and it can set itself up.

By Tech Horizon Labs. This edition contains {n} entries. Documentation checked means the source was read. It does not mean the software was installed, tested or security audited. Entries are grouped by purpose, not ranked.

For an AI assistant, load [llms.txt](llms.txt) for the index or [llms-full.txt](llms-full.txt) for the descriptions. [resources.json](resources.json) contains the structured records. [AGENTS.md](AGENTS.md) is the house rules for an agent working in this repository.

Install the catalog skill with:

```bash
npx skills add techhorizonlabs/gearlist
```

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
    "## What this is not",
    "",
    "Gearlist is a checked shortlist with permission notes. It is not a scrape of every MCP server. Volume discovery belongs at the [official MCP Registry](https://registry.modelcontextprotocol.io). Starred GitHub repositories that might belong later live in [stars-queue.json](stars-queue.json) until someone reads their docs.",
    "",
    "## Suggest an entry",
    "",
    "Open an issue using the resource suggestion template, or submit a pull request following [CONTRIBUTING.md](CONTRIBUTING.md). Include the official link, who it serves and the permissions it needs. Do not include private conversations, contact details or credentials.",
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
- [Stars queue](stars-queue.json): Starred GitHub repos waiting for a documentation review.
"""
)
print(f"Generated and validated {len(entries)} unique entries.")
