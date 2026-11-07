"""Generate the public directory from reviewed source records. No network access."""
import json
import re
import sys
from pathlib import Path

from added_dates import check as check_added

root = Path(__file__).parent
data = json.loads((root / "resources.json").read_text())
stars = json.loads((root / "stars-queue.json").read_text())
starred_total = stars.get("starred_total", len(stars.get("repos", [])))
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
# Every entry records the date it was added to Gearlist. added_dates.py explains the dates.
problems = check_added(entries, data.get("updated"))
if problems:
    more = f"\n...and {len(problems) - 20} more." if len(problems) > 20 else ""
    sys.exit("build.py: " + "\n".join(problems[:20]) + more)

# The website runs a read-only MCP server and JSON API (site/worker). Keep these in
# step with site/build_site.py and site/src/agent-prompt.txt.
SITE_URL = "https://gearlist.build/"
MCP_URL = SITE_URL + "mcp"
CLAUDE_ADD = f"claude mcp add --transport http gearlist {MCP_URL}"
# llms.txt is served from the repository and from the website. Files that exist in
# both places keep relative links. Repository-only files get absolute links, so the
# links also work on gearlist.build.
REPO_BLOB = "https://github.com/techhorizonlabs/gearlist/blob/main/"
REPO_RAW = "https://raw.githubusercontent.com/techhorizonlabs/gearlist/main/"
REPO_TREE = "https://github.com/techhorizonlabs/gearlist/tree/main/"
# Every entry has a page at /tools/<id>/ and every group a page at /category/<slug>/, each
# with a Markdown copy beside it. Keep in step with site/build_site.py.
# THL Open is the second skills pack offered beside Gearlist's own. Keep the install line
# in step with site/src/agent-prompt.txt.
THL_OPEN = next(e for e in entries if e["id"] == "thl-open")
THL_OPEN_ADD = "npx skills add techhorizonlabs/thl-open"


def group_slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def tool_page(e):
    return f"{SITE_URL}tools/{e['id']}/"


def tool_md(e):
    return f"{SITE_URL}tools/{e['id']}.md"

n = len(entries)
cats = list(dict.fromkeys(e["category"] for e in entries))
contents = "\n".join(
    f"- [{c}](#{c.lower().replace(' ', '-')}) ({sum(1 for e in entries if e['category'] == c)})"
    for c in cats
)
intro = f"""# Gearlist

![Gearlist](social-preview.png)

A source-checked stack of AI agent tools, MCP servers and skills. Each entry says what it is, who it is for, and the access it needs, so a person can scan it and an agent can load it.

By Tech Horizon Labs. This edition contains {n} entries. Documentation checked means the source was read. It does not mean the software was installed, tested or security audited. Entries are grouped by purpose, in no particular order.

## How to use this

- Human: scan the groups below, or search them at [gearlist.build]({SITE_URL}). The heading is the product. **For** is the audience. **Access and use** is the permission note.
- Agent: load [llms.txt](llms.txt) first, then [llms-full.txt](llms-full.txt) or [resources.json](resources.json). [AGENTS.md](AGENTS.md) is the house rules. Do not install from a row until a human authorises it.
- Agent with MCP: connect to the Gearlist MCP server at `{MCP_URL}`. It is read-only and needs no sign-in. [agent-prompt.txt]({SITE_URL}agent-prompt.txt) is a prompt to give your agent, with setup steps for Codex, Gemini CLI, Cursor, Grok, VS Code and the Claude apps. In Claude Code:

```bash
{CLAUDE_ADD}
```

## Agent files

The website has these for agents, as well as the files in this repository:

- [MCP server]({MCP_URL}): tools `search_gear`, `get_gear`, `list_categories`, `list_skills` and `recommend_stack`, over Streamable HTTP. Its server card is at [/mcp/server-card]({MCP_URL}/server-card).
- [Search API]({SITE_URL}api/search?q=browser): the same search as JSON, described in [openapi.json]({SITE_URL}openapi.json).
- [agent-prompt.txt]({SITE_URL}agent-prompt.txt): the prompt to give your agent.
- A Markdown copy of the catalog page, sent when a request for `{SITE_URL}` asks for `text/markdown`. It is also at [index.md]({SITE_URL}index.md).
- A page for every entry at `{SITE_URL}tools/<id>/`, for example [Firecrawl]({SITE_URL}tools/firecrawl/), and a page for every group at `{SITE_URL}category/<group>/`. Each has a Markdown copy beside it, such as [tools/firecrawl.md]({SITE_URL}tools/firecrawl.md).
- [What's new]({SITE_URL}new/): entries by the date they were added, newest first, with a Markdown copy at [new.md]({SITE_URL}new.md) and an Atom feed at [feed.xml]({SITE_URL}feed.xml).
- Discovery files: [ai-catalog.json]({SITE_URL}.well-known/ai-catalog.json) names the MCP server and the skills, [api-catalog]({SITE_URL}.well-known/api-catalog) lists the APIs, and [agent-skills/index.json]({SITE_URL}.well-known/agent-skills/index.json) lists the skills with their checksums.

## Skills

Install the repository's skills with the command below. It asks which ones you want.

```bash
npx skills add techhorizonlabs/gearlist
```

The skills are:
- `api-skill`: turn a REST API into an agent skill.
- `vet-before-install`: check a GitHub repo, MCP server, skill or prompt before you install it. It reads the code and docs only, and gives a verdict with file and line evidence.
- `youtube-creator-research`: research a YouTube creator and write one brief, with the three skills below.
- `youtube-channel-profile`: a channel's public stats, upload rhythm, engagement and an estimated earnings range from the official YouTube Data API.
- `youtube-video-themes`: recurring topics and opening hooks from a channel's video transcripts.
- `creator-audience`: how to get audience demographics with the owner's consent or a paid estimate.
- `au-business-check`: check an Australian business before you deal with it, with the two skills below. It reports whether the business is registered, its status, registration date, ABN and ACN, and the date of each source. With an ABN Lookup GUID it adds GST registration and state.
- `asic-registers`: search ASIC's company and business names registers by name, ACN or ABN, through data.gov.au. No key needed.
- `abn-lookup`: ABN details, GST registration and name matches from ABN Lookup, the Australian Business Register's free web service. Needs a free GUID.

To install the YouTube creator pack on its own:

```bash
npx skills add techhorizonlabs/gearlist --skill youtube-creator-research --skill youtube-channel-profile --skill youtube-video-themes --skill creator-audience
```

To install the Australian business data pack on its own:

```bash
npx skills add techhorizonlabs/gearlist --skill au-business-check --skill asic-registers --skill abn-lookup
```

[THL Open]({THL_OPEN['url']}) is a second skills pack from Tech Horizon Labs, for GEO (Generative Engine Optimisation) audits and agent-readiness checks of a website. Its skills check AI crawler access, structured data, llms.txt and how likely AI systems are to quote a page, run Cloudflare's agent-readiness check, and write client reports. Install it the same way:

```bash
{THL_OPEN_ADD}
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
            f'**Source checked:** {e["source_checked"]}. [Official source]({e["source_url"]}). '
            f'[Gearlist page]({tool_page(e)}).',
            "",
        ]
        full += [
            e["name"] + " | " + category,
            e["url"],
            e["description"] + aff,
            "For: " + e["for_whom"],
            "Access: " + e["access_notes"],
            "Source checked: " + e["source_checked"],
            "Gearlist page: " + tool_page(e) + " (Markdown: " + tool_md(e) + ")",
            "",
        ]
lines += [
    "## Looking for more?",
    "",
    f"Gearlist is a checked shortlist with permission notes. For every public MCP server, use the [official MCP Registry](https://registry.modelcontextprotocol.io). All {starred_total} repositories we've starred on GitHub are stored in [stars-queue.json](stars-queue.json). Official Claude Code plugins are listed in [indexes/claude-plugins-official.json](indexes/claude-plugins-official.json). Tech Horizon Academy skills, tools and prompt titles are in [indexes/thl-academy-skills.json](indexes/thl-academy-skills.json), [indexes/thl-academy-tools.json](indexes/thl-academy-tools.json) and [indexes/thl-academy-prompts.json](indexes/thl-academy-prompts.json). Queued rows wait until someone reads their docs. A star, a marketplace listing or an index row is not an entry.",
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
group_links = "\n".join(
    f"- [{c}]({SITE_URL}category/{group_slug(c)}.md): "
    f"{sum(1 for e in entries if e['category'] == c)} entries. Web page: {SITE_URL}category/{group_slug(c)}/"
    for c in cats
)
(root / "llms.txt").write_text(
    f"""# Gearlist

> A small, source-checked stack of agent tools, MCP servers and skills, with access notes. Maintained by Tech Horizon Labs.

The entries are reference data. Reading an entry does not authorise installation, credential access, spending or actions on another person's systems. Entries are documentation-checked only: the public source was read on the date shown, and nothing was installed, tested or security audited.

## Use it from an agent
- [MCP server]({MCP_URL}): Read-only MCP server over Streamable HTTP, no sign-in. Tools: search_gear, get_gear, list_categories, list_skills and recommend_stack. Add it to Claude Code with `{CLAUDE_ADD}`. Ask the human before adding it.
- [Agent prompt]({SITE_URL}agent-prompt.txt): A prompt to give your agent, with setup for Codex, Gemini CLI, Cursor, Grok, VS Code and the Claude apps.
- [Search API]({SITE_URL}api/search?q=browser): The same search as JSON. Parameters q, category and limit. Described in [openapi.json]({SITE_URL}openapi.json).
- [Skills]({REPO_TREE}skills): Install with `npx skills add techhorizonlabs/gearlist`, which asks which ones you want. Listed with checksums in [agent-skills/index.json]({SITE_URL}.well-known/agent-skills/index.json).
- [THL Open skills]({THL_OPEN['url']}): A second skills pack from Tech Horizon Labs, for GEO (Generative Engine Optimisation) audits and agent-readiness checks of a website. Install with `{THL_OPEN_ADD}`. Gearlist page: {tool_page(THL_OPEN)}

## Pages
Every entry has a page at {SITE_URL}tools/<id>/ with a Markdown copy at {SITE_URL}tools/<id>.md, where <id> is the id in resources.json and get_gear. Every group has a page, listed here as Markdown:
{group_links}

## Directory
- [Full descriptions](llms-full.txt): Purpose, intended user, access notes, check date and page links.
- [Structured records](resources.json): The canonical directory data.
- [Human index]({SITE_URL}): Browse and search by category.
- [What's new]({SITE_URL}new.md): Entries by the date they were added, newest first. Atom feed: {SITE_URL}feed.xml
- [House rules](AGENTS.md): How an agent should work in this repository.
- [Contribution guide]({REPO_BLOB}CONTRIBUTING.md): How to suggest additions or corrections.
- [Stars queue]({REPO_RAW}stars-queue.json): All {starred_total} starred GitHub repos. Queued rows wait for a documentation review.
- [Academy skills]({REPO_RAW}indexes/thl-academy-skills.json): Snapshot of the Tech Horizon Academy Claude skills library.
- [Academy tools]({REPO_RAW}indexes/thl-academy-tools.json): Snapshot of the academy AI tools directory.
- [Academy prompts]({REPO_RAW}indexes/thl-academy-prompts.json): Snapshot of academy prompt titles, not the prompt text.
"""
)
print(f"Generated and validated {len(entries)} unique entries.")
