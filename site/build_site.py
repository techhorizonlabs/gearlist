#!/usr/bin/env python3
"""Build the Gearlist website into site/dist from ../resources.json.

Python 3 standard library only. No network access. Run from anywhere:

    python3 site/build_site.py
"""
import base64
import hashlib
import html
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
SRC = SITE / "src"
DIST = SITE / "dist"
SKILLS = ROOT / "skills"

BASE_URL = "https://gearlist.build/"
REPO_URL = "https://github.com/techhorizonlabs/gearlist"
REPO_LABEL = "github.com/techhorizonlabs/gearlist"
CONTRIBUTING_URL = REPO_URL + "/blob/main/CONTRIBUTING.md"
INSTALL = "npx skills add techhorizonlabs/gearlist"
COPIED = ["llms.txt", "llms-full.txt", "resources.json", "AGENTS.md", "social-preview.png"]

# The MCP server and JSON API run in the Worker (site/worker). Keep in step with
# site/worker/mcp.mjs and site/src/agent-prompt.txt.
MCP_URL = BASE_URL + "mcp"
CLAUDE_ADD = f"claude mcp add --transport http gearlist {MCP_URL}"
SKILLS_SCHEMA = "https://schemas.agentskills.io/discovery/0.2.0/schema.json"

# robots.txt Content-Signal (https://contentsignals.org/). The catalog is public,
# MIT-licensed reference data that is meant to be found and recommended, so all
# three uses are allowed. Change ai-train to "no" here to opt out of training.
CONTENT_SIGNAL = "search=yes, ai-input=yes, ai-train=yes"

# Wording from README.md. Keep these in step with build.py.
SUMMARY = (
    "A source-checked stack of agent tools, MCP servers and skills. Each entry says what it is, "
    "who it is for, and the access it needs, so a person can scan it and an agent can load it."
)
CHECK_NOTE = (
    "Documentation checked means the source was read. "
    "It does not mean the software was installed, tested or security audited."
)
TITLE = "Gearlist: source-checked agent tools, MCP servers and skills"
META_DESCRIPTION = (
    "A source-checked stack of agent tools, MCP servers and skills. "
    "Each entry says what it is, who it is for, and the access it needs."
)
OG_ALT = (
    "Gearlist, the kit for your AI agent. Source-checked tools, MCP servers and skills, "
    "each with the access it needs."
)

# Icon and colour per group, after the social card. Unknown groups get a fallback.
GROUP_STYLE = {
    "Agent tools": ("wrench", "teal"),
    "MCP and integrations": ("plug", "gold"),
    "Security and governance": ("shield", "teal"),
    "Platforms": ("grid", "gold"),
    "Protocols": ("arrows", "pink"),
    "Skills and learning": ("layers", "pink"),
    "APIs and data": ("braces", "gold"),
}
FALLBACK_COLOURS = ["gold", "pink", "teal"]

ICONS = {
    "plug": "M9 3v4.5M15 3v4.5M6.5 7.5h11V11a5.5 5.5 0 0 1-11 0zM12 16.5V21",
    "layers": "M12 3.5 3 8.5l9 5 9-5zM3 12.5l9 5 9-5M3 16.5l9 5 9-5",
    "shield": "M12 3 4.5 6v5.5c0 4.6 3.1 8.1 7.5 9.5 4.4-1.4 7.5-4.9 7.5-9.5V6zM8.75 12.25l2.25 2.25 4.25-4.5",
    "wrench": (
        "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94"
        "l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"
    ),
    "grid": "M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z",
    "arrows": "M4 8h15M15.5 4.5 19 8l-3.5 3.5M20 16H5M8.5 12.5 5 16l3.5 3.5",
    "braces": (
        "M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5c0 1.1.9 2 2 2h1"
        "M16 21h1a2 2 0 0 0 2-2v-5c0-1.1.9-2 2-2a2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1"
    ),
    "list": "M9 6h11M9 12h11M9 18h11M4.5 6h.01M4.5 12h.01M4.5 18h.01",
}

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

REQUIRED = (
    "id", "name", "category", "url", "description", "for_whom",
    "access_notes", "source_url", "source_checked",
)


def esc(text):
    return html.escape(str(text), quote=True)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def long_date(iso):
    y, m, d = (int(p) for p in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def short_date(iso):
    y, m, d = (int(p) for p in iso.split("-"))
    return f"{d} {MONTHS[m - 1][:3]} {y}"


def file_size(n):
    if n < 1024:
        return f"{n} bytes"
    kb = n / 1024
    return f"{kb:.1f} KB" if kb < 10 else f"{round(kb)} KB"


def csp_hash(text):
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def fail(message):
    sys.exit("build_site.py: " + message)


def load_entries():
    data = json.loads((ROOT / "resources.json").read_text(encoding="utf-8"))
    entries = data["resources"]
    if not entries:
        fail("resources.json has no entries")
    ids, urls = set(), set()
    for e in entries:
        missing = [k for k in REQUIRED if not e.get(k)]
        if missing:
            fail(f"entry {e.get('id', '?')} is missing {', '.join(missing)}")
        if not (e["url"].startswith("https://") and e["source_url"].startswith("https://")):
            fail(f"entry {e['id']} needs https links")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", e["source_checked"]):
            fail(f"entry {e['id']} has a source_checked date that is not YYYY-MM-DD")
        if e["id"] in ids or e["url"] in urls:
            fail(f"entry {e['id']} repeats an id or url")
        ids.add(e["id"])
        urls.add(e["url"])
    return data, entries


def group_entries(entries):
    """Groups in first-appearance order, the same order build.py writes into README.md."""
    order = list(dict.fromkeys(e["category"] for e in entries))
    groups = []
    for i, name in enumerate(order):
        icon_name, colour = GROUP_STYLE.get(name, ("list", FALLBACK_COLOURS[i % 3]))
        groups.append({
            "name": name,
            "slug": slug(name),
            "icon": icon_name,
            "colour": colour,
            "entries": [e for e in entries if e["category"] == name],
        })
    return groups


def check_readme(groups):
    """Warn when README.md lists different groups or counts from resources.json."""
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    found = re.findall(r"^- \[([^\]]+)\]\(#[^)]+\) \((\d+)\)$", readme.read_text(encoding="utf-8"), re.M)
    expected = [(g["name"], str(len(g["entries"]))) for g in groups]
    if found != expected:
        print("Note: README.md contents differ from resources.json. Run python3 build.py at the repo root.")


def entry_ids(entries, reserved):
    out = {}
    for e in entries:
        anchor = slug(e["id"]) or "entry"
        if anchor in reserved or anchor in out.values():
            anchor = "entry-" + anchor
        out[e["id"]] = anchor
    return out


def split_name(name):
    head, sep, tail = name.partition(" and ")
    return (head, "and " + tail) if sep else (name, "")


def render_entry(e, anchor):
    thl = '<p class="thl">Tech Horizon Labs project</p>' if e.get("thl_project") else ""
    checked = e["source_checked"]
    return (
        f'<article class="e" id="{esc(anchor)}"><div>'
        f'<h3><a href="{esc(e["url"])}">{esc(e["name"])}</a></h3>'
        f'<p class="d">{esc(e["description"])}</p>{thl}'
        f'<p class="src"><a href="{esc(e["source_url"])}">Source checked '
        f'<time datetime="{checked}">{short_date(checked)}</time>'
        f'<span class="sr">, {esc(e["name"])} official source</span></a></p>'
        f'</div><dl><dt>For</dt><dd>{esc(e["for_whom"])}</dd>'
        f'<dt>Access and use</dt><dd>{esc(e["access_notes"])}</dd></dl></article>'
    )


def render_index(data, groups, css, head_js, app_js, sizes, prompt):
    entries = [e for g in groups for e in g["entries"]]
    total = len(entries)
    reserved = {g["slug"] for g in groups} | {
        "top", "main", "catalog", "agents", "q", "status", "empty", "clear",
        "copy", "cmd", "copy-status", "checks", "kit", "agent-prompt", "prompt-text",
        "h-agents", "h-files",
    }
    anchors = entry_ids(entries, reserved)
    updated = data.get("updated", max(e["source_checked"] for e in entries))

    sprite = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24"><path d="{v}"/></symbol>' for k, v in ICONS.items())

    tiles = []
    for g in groups:
        head, tail = split_name(g["name"])
        n = len(g["entries"])
        sub = f'<span class="tile-sub">{esc(tail)}</span>'
        tiles.append(
            f'<li><a class="tile c-{g["colour"]}" href="#{g["slug"]}" data-filter="{g["slug"]}" '
            f'aria-label="{esc(g["name"])}, {n} {"entry" if n == 1 else "entries"}">'
            f'<span class="tile-top">{icon(g["icon"])}<span class="tile-n">{n}</span></span>'
            f'<span><span class="tile-name">{esc(head)}</span>{sub}</span></a></li>'
        )
    tiles.append(
        f'<li><a class="tile c-cream" href="#catalog" data-filter="all" aria-label="All entries, {total} entries">'
        f'<span class="tile-top">{icon("list")}<span class="tile-n">{total}</span></span>'
        f'<span><span class="tile-name">All entries</span><span class="tile-sub">in one list</span></span></a></li>'
    )

    chips = [
        '<li><button type="button" class="chip c-cream" data-filter="all" aria-pressed="true">All</button></li>'
    ]
    for g in groups:
        head, _ = split_name(g["name"])
        chips.append(
            f'<li><button type="button" class="chip c-{g["colour"]}" data-filter="{g["slug"]}" aria-pressed="false" '
            f'aria-label="{esc(g["name"])}">{esc(head)}</button></li>'
        )

    sections = []
    for g in groups:
        n = len(g["entries"])
        rows = "\n".join(render_entry(e, anchors[e["id"]]) for e in g["entries"])
        sections.append(
            f'<section class="group c-{g["colour"]}" id="{g["slug"]}" data-cat="{g["slug"]}" data-total="{n}" '
            f'aria-labelledby="h-{g["slug"]}">\n'
            f'<h2 class="group-head" id="h-{g["slug"]}">{icon(g["icon"])}<span class="group-name">{esc(g["name"])}</span>'
            f'<span class="group-n">{n}</span></h2>\n<div class="list">\n{rows}\n</div>\n</section>'
        )

    files = [
        ("/llms.txt", "llms.txt", "Start here. A short index with links to the other files.", "gold",
         file_size(sizes["llms.txt"])),
        ("/llms-full.txt", "llms-full.txt", "Every entry as plain text: purpose, audience, access and check date.",
         "pink", file_size(sizes["llms-full.txt"])),
        ("/resources.json", "resources.json", "The canonical records as JSON. The other files are built from it.",
         "teal", file_size(sizes["resources.json"])),
        ("/AGENTS.md", "AGENTS.md", "House rules for an agent reading or changing the list.", "gold",
         file_size(sizes["AGENTS.md"])),
        ("/mcp", "MCP server", "Search the list from your agent. Read-only, no sign-in, Streamable HTTP.", "pink",
         "4 tools"),
        ("/agent-prompt.txt", "agent-prompt.txt", "The prompt above as plain text, with setup for each client.",
         "teal", file_size(len(prompt.encode("utf-8")))),
        ("/openapi.json", "openapi.json", "The same search as JSON at /api/search, described for tools.", "gold",
         "OpenAPI 3.1"),
        ("/.well-known/ai-catalog.json", "ai-catalog.json", "A discovery file naming the MCP server and the skills.",
         "pink", "AI Catalog"),
    ]
    file_cards = "".join(
        f'<li><a class="file c-{colour}" href="{href}"><b>{esc(title)}</b><span>{esc(text)}</span>'
        f"<small>{esc(small)}</small></a></li>"
        for href, title, text, colour, small in files
    )

    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": BASE_URL + "#website",
                "url": BASE_URL,
                "name": "Gearlist",
                "description": SUMMARY,
                "inLanguage": "en-AU",
                "dateModified": updated,
                "publisher": {"@type": "Organization", "name": "Tech Horizon Labs"},
            },
            {
                "@type": "ItemList",
                "@id": BASE_URL + "#entries",
                "name": "Gearlist entries",
                "numberOfItems": total,
                "itemListOrder": "https://schema.org/ItemListUnordered",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i,
                        "name": e["name"],
                        "url": e["url"],
                        "description": e["description"],
                    }
                    for i, e in enumerate(entries, 1)
                ],
            },
        ],
    }
    ld = json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))
    ld = ld.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

    group_count = len(groups)
    nl = "\n"
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(TITLE)}</title>
<meta name="description" content="{esc(META_DESCRIPTION)}">
<link rel="canonical" href="{BASE_URL}">
<link rel="alternate" type="text/plain" href="/llms.txt" title="llms.txt">
<link rel="alternate" type="application/json" href="/resources.json" title="Gearlist records">
<link rel="alternate" type="text/markdown" href="/index.md" title="This page as Markdown">
<link rel="api-catalog" href="/.well-known/api-catalog">
<link rel="ai-catalog" href="/.well-known/ai-catalog.json">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#14161a">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Gearlist">
<meta property="og:locale" content="en_AU">
<meta property="og:url" content="{BASE_URL}">
<meta property="og:title" content="{esc(TITLE)}">
<meta property="og:description" content="{esc(META_DESCRIPTION)}">
<meta property="og:image" content="{BASE_URL}social-preview.png">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="640">
<meta property="og:image:alt" content="{esc(OG_ALT)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(TITLE)}">
<meta name="twitter:description" content="{esc(META_DESCRIPTION)}">
<meta name="twitter:image" content="{BASE_URL}social-preview.png">
<meta name="twitter:image:alt" content="{esc(OG_ALT)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&amp;family=Space+Mono:wght@400;700&amp;display=swap">
<script>{head_js}</script>
<style>{css}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<svg width="0" height="0" class="sr" aria-hidden="true" focusable="false"><defs>{sprite}</defs></svg>
<a class="skip" href="#catalog">Skip to the entries</a>
<header class="top wrap" id="top">
<a class="home" href="/">gearlist.build</a>
<nav aria-label="Site"><a href="#catalog">Entries</a><a href="#agents">For agents</a><a href="{REPO_URL}">GitHub</a></nav>
</header>
<main id="main">
<div class="hero wrap">
<div>
<p class="eyebrow">Pack the kit</p>
<h1>Gearlist</h1>
<p class="tag">The kit for your AI agent.</p>
<p class="lede">{esc(SUMMARY)}</p>
<p class="facts">{total} entries in {group_count} groups. Updated {long_date(updated)}.</p>
<div class="install">
<p>Install the Gearlist skills, including the YouTube creator pack:</p>
<div class="cmd"><code id="cmd">{esc(INSTALL)}</code><button type="button" id="copy" class="js-only" data-copy="cmd">Copy</button></div>
<span class="sr" id="copy-status" aria-live="polite"></span>
<p class="alt">Working with an agent? <a href="#agent-prompt">Give it the Gearlist prompt</a>. It connects to the read-only MCP server at <code>gearlist.build/mcp</code>.</p>
</div>
</div>
<nav aria-label="Groups"><ul class="kit" id="kit">
{nl.join(tiles)}
</ul></nav>
</div>

<div class="wrap" id="checks"><div class="note">
{icon("shield")}
<div>
<h2>What a source check covers</h2>
<p>{esc(CHECK_NOTE)}</p>
<p>Reading an entry does not authorise installation, credential access or spending. Entries are grouped by purpose, in no particular order. Tech Horizon Labs projects are labelled, and there are no affiliate links or paid placement.</p>
</div>
</div></div>

<div class="catalog" id="catalog">
<div class="bar js-only">
<div class="bar-in wrap">
<div class="search"><label class="search-label" for="q">Search</label><input id="q" type="search" placeholder="Try browser" autocomplete="off" spellcheck="false"></div>
<p class="status" id="status" role="status">{total} entries</p>
<ul class="chips" aria-label="Filter by group">
{nl.join(chips)}
</ul>
</div>
</div>
<div class="wrap">
{nl.join(sections)}
<div class="empty" id="empty" hidden><p>No entries match that search.</p><button type="button" class="btn" id="clear">Show all entries</button></div>
</div>
</div>

<section class="agents wrap" id="agents" aria-labelledby="h-agents">
<h2 id="h-agents">Give this to your agent</h2>
<p>Paste this prompt into your agent. It tells the agent to read <code>llms.txt</code>, search Gearlist through the read-only MCP server, show you each tool's access notes and ask you before it installs anything.</p>
<div class="prompt" id="agent-prompt">
<div class="prompt-bar"><span>agent-prompt.txt</span><button type="button" class="js-only" data-copy="prompt-text">Copy prompt</button></div>
<pre id="prompt-text" tabindex="0">{esc(prompt.strip())}</pre>
</div>
<p class="also">The same text is at <a href="/agent-prompt.txt">gearlist.build/agent-prompt.txt</a>. The MCP server is <code>{esc(MCP_URL)}</code>. It needs no sign-in and changes nothing.</p>
<h3 id="h-files">Agent files</h3>
<p>Load <code>llms.txt</code> first, then <code>llms-full.txt</code> or <code>resources.json</code>. <code>AGENTS.md</code> is the house rules. Do not install anything from an entry until a person authorises it.</p>
<ul class="files">{file_cards}</ul>
</section>
</main>
<footer class="wrap"><div class="foot">
<nav aria-label="Project"><a href="{REPO_URL}">{REPO_LABEL}</a><a href="{CONTRIBUTING_URL}">Suggest an entry</a></nav>
<span>by Tech Horizon Labs</span>
</div></footer>
<script>{app_js}</script>
</body>
</html>
"""


def render_404(css):
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found: Gearlist</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta name="theme-color" content="#14161a">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&amp;family=Space+Mono:wght@400;700&amp;display=swap">
<style>{css}</style>
</head>
<body>
<header class="top wrap"><a class="home" href="/">gearlist.build</a></header>
<main class="lost wrap">
<p class="eyebrow">Not found</p>
<h1>Gearlist</h1>
<p class="lede">That address is not part of the site. Every entry is on the home page.</p>
<p><a class="btn" href="/">Go to the home page</a></p>
</main>
</body>
</html>
"""


def render_headers(script_hashes, style_hash):
    csp = "; ".join([
        "default-src 'none'",
        "script-src " + " ".join(script_hashes),
        "style-src " + style_hash + " https://fonts.googleapis.com",
        "font-src https://fonts.gstatic.com",
        "img-src 'self'",
        "base-uri 'none'",
        "form-action 'none'",
        "frame-ancestors 'none'",
    ])
    # The Worker serves / through the ASSETS binding, and asset responses fetched
    # that way still get these rules, so the CSP and Link headers hold for /.
    return f"""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Content-Security-Policy: {csp}

/
  Link: </llms.txt>; rel="describedby"; type="text/plain"
  Link: </index.md>; rel="alternate"; type="text/markdown"
  Link: </.well-known/api-catalog>; rel="api-catalog"
  Link: </.well-known/ai-catalog.json>; rel="ai-catalog"; type="application/ai-catalog+json"

/index.md
  Content-Type: text/markdown; charset=utf-8
  Access-Control-Allow-Origin: *

/agent-prompt.txt
  Content-Type: text/plain; charset=utf-8
  Access-Control-Allow-Origin: *

/.well-known/api-catalog
  Content-Type: application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"
  Link: </.well-known/api-catalog>; rel="api-catalog"
  Access-Control-Allow-Origin: *

/.well-known/ai-catalog.json
  Content-Type: application/ai-catalog+json
  Access-Control-Allow-Origin: *

/.well-known/agent-skills/*
  Access-Control-Allow-Origin: *

/llms.txt
  Content-Type: text/plain; charset=utf-8
  Access-Control-Allow-Origin: *

/llms-full.txt
  Content-Type: text/plain; charset=utf-8
  Access-Control-Allow-Origin: *

/resources.json
  Access-Control-Allow-Origin: *

/AGENTS.md
  Content-Type: text/markdown; charset=utf-8
  Access-Control-Allow-Origin: *

https://:name.:account.workers.dev/*
  X-Robots-Tag: noindex
"""


def render_markdown(data, groups):
    """The catalog page as Markdown, sent for / when a request prefers text/markdown.

    Entry text stays verbatim, as in README.md, so commands in access notes copy cleanly.
    """
    entries = [e for g in groups for e in g["entries"]]
    updated = data.get("updated", max(e["source_checked"] for e in entries))
    contents = "\n".join(f'- [{g["name"]}](#{g["slug"]}) ({len(g["entries"])})' for g in groups)
    lines = [
        "---",
        f"title: {json.dumps(TITLE)}",
        f"description: {json.dumps(META_DESCRIPTION)}",
        f"image: {BASE_URL}social-preview.png",
        f"url: {BASE_URL}",
        f"updated: {updated}",
        "---",
        "",
        "# Gearlist",
        "",
        "The kit for your AI agent. " + SUMMARY,
        "",
        f"{len(entries)} entries in {len(groups)} groups. Updated {long_date(updated)}. By Tech Horizon Labs.",
        "",
        CHECK_NOTE + " Reading an entry does not authorise installation, credential access or spending. "
        "Entries are grouped by purpose, in no particular order. Tech Horizon Labs projects are labelled, "
        "and there are no affiliate links or paid placement.",
        "",
        "## For agents",
        "",
        f"- MCP server: {MCP_URL} (Streamable HTTP, read-only, no sign-in). Tools: search_gear, get_gear, "
        "list_categories, list_skills.",
        f"- Claude Code: `{CLAUDE_ADD}`",
        f"- Prompt to give your agent, with setup for other clients: {BASE_URL}agent-prompt.txt",
        f"- JSON search: {BASE_URL}api/search?q=browser, described at {BASE_URL}openapi.json",
        f"- Files: {BASE_URL}llms.txt, {BASE_URL}llms-full.txt, {BASE_URL}resources.json, {BASE_URL}AGENTS.md",
        f"- Skills: `{INSTALL}` (asks which ones you want)",
        "",
        "Do not install anything from an entry until a person authorises it.",
        "",
        "## Contents",
        "",
        contents,
        "",
    ]
    for g in groups:
        lines += [f'## {g["name"]}', ""]
        for e in g["entries"]:
            lines += [f'### [{e["name"]}]({e["url"]})', "", e["description"], ""]
            if e.get("thl_project"):
                lines += ["Tech Horizon Labs project.", ""]
            lines += [
                "- For: " + e["for_whom"],
                "- Access and use: " + e["access_notes"],
                f'- Source checked: {short_date(e["source_checked"])}, [official source]({e["source_url"]})',
                f'- Id: `{e["id"]}`',
                "",
            ]
    lines += [f"Suggest an entry: {CONTRIBUTING_URL}", ""]
    return "\n".join(lines)


def read_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    if not text.startswith("---\n") or end == -1:
        fail(f"{path.relative_to(ROOT)} has no YAML frontmatter")
    meta = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            meta[key.strip()] = value.strip()
    return meta


def skill_files(folder):
    """Files a skill ships, minus caches and editor litter."""
    out = []
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder)
        if path.is_symlink():
            fail(f"{path.relative_to(ROOT)} is a symlink; skill archives must not contain links")
        if any(p == "__pycache__" or p == ".DS_Store" or p.endswith(".pyc") for p in rel.parts):
            continue
        if path.is_file():
            out.append((rel.as_posix(), path))
    return out


def zip_bytes(files):
    """A reproducible zip: fixed timestamps and modes, so the digest only moves when content does."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for rel, path in files:
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes(), compresslevel=9)
    return buf.getvalue()


def build_skills():
    """Agent Skills discovery index (Cloudflare RFC v0.2.0) at /.well-known/agent-skills/index.json.

    A skill that is only SKILL.md is served as that file. A skill with scripts is
    served as a zip with SKILL.md at the root. SKILL.md is also published on its own
    so it can be read before anything is downloaded.
    """
    out = DIST / ".well-known" / "agent-skills"
    skills = []
    for folder in sorted(p for p in SKILLS.iterdir() if p.is_dir() and (p / "SKILL.md").exists()):
        meta = read_frontmatter(folder / "SKILL.md")
        name, description = meta.get("name", ""), meta.get("description", "")
        if name != folder.name or len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            fail(f"skills/{folder.name}/SKILL.md needs a name that matches its folder")
        if not description or len(description) > 1024:
            fail(f"skills/{folder.name}/SKILL.md needs a description of 1 to 1024 characters")
        files = skill_files(folder)
        (out / name).mkdir(parents=True)
        shutil.copyfile(folder / "SKILL.md", out / name / "SKILL.md")
        if [rel for rel, _ in files] == ["SKILL.md"]:
            kind, url, blob = "skill-md", f"/.well-known/agent-skills/{name}/SKILL.md", (folder / "SKILL.md").read_bytes()
        else:
            kind, url, blob = "archive", f"/.well-known/agent-skills/{name}.zip", zip_bytes(files)
            (out / f"{name}.zip").write_bytes(blob)
        skills.append({
            "name": name,
            "type": kind,
            "description": description,
            "url": url,
            "digest": "sha256:" + hashlib.sha256(blob).hexdigest(),
        })
    if not skills:
        fail("no skills found in skills/")
    index = {"$schema": SKILLS_SCHEMA, "skills": skills}
    (out / "index.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return skills


def ai_catalog(skills):
    """AI Catalog at /.well-known/ai-catalog.json. The MCP Server Card extension (SEP-2127)
    uses it for domain-level discovery of the card at /mcp/server-card."""
    entries = [{
        "identifier": "urn:air:gearlist.build:mcp:gearlist",
        "displayName": "Gearlist MCP server",
        "type": "application/mcp-server-card+json",
        "url": MCP_URL + "/server-card",
        "description": "Read-only search over the Gearlist catalog of source-checked AI agent tools, MCP servers and skills.",
        "tags": ["mcp", "catalog", "agent-tools"],
    }]
    for s in skills:
        entries.append({
            "identifier": f"urn:air:gearlist.build:skill:{s['name']}",
            "displayName": s["name"],
            "type": "application/agent-skills+md" if s["type"] == "skill-md" else "application/agent-skills+zip",
            "url": BASE_URL.rstrip("/") + s["url"],
            "description": s["description"],
        })
    return {
        "specVersion": "1.0",
        "host": {
            "displayName": "Tech Horizon Labs",
            "identifier": "gearlist.build",
            "documentationUrl": BASE_URL + "llms.txt",
        },
        "entries": entries,
    }


def api_catalog():
    """RFC 9727 API catalog, in the RFC 9264 linkset format."""
    return {
        "linkset": [
            {
                "anchor": BASE_URL + "api/search",
                "service-desc": [{"href": BASE_URL + "openapi.json", "type": "application/json"}],
                "service-doc": [{"href": BASE_URL + "agent-prompt.txt", "type": "text/plain"}],
            },
            {
                "anchor": MCP_URL,
                "service-doc": [{"href": MCP_URL, "type": "text/plain"}],
                "service-meta": [{"href": MCP_URL + "/server-card", "type": "application/mcp-server-card+json"}],
            },
        ]
    }


def read_prompt():
    prompt = (SRC / "agent-prompt.txt").read_text(encoding="utf-8")
    for needed in (BASE_URL + "llms.txt", MCP_URL, CLAUDE_ADD, INSTALL):
        if needed not in prompt:
            fail(f"site/src/agent-prompt.txt must include {needed}")
    if re.search("[\u2013\u2014]", prompt):
        fail("site/src/agent-prompt.txt contains an en or em dash")
    return prompt


def main():
    data, entries = load_entries()
    groups = group_entries(entries)
    check_readme(groups)

    if DIST.exists():
        if DIST.parent != SITE or DIST.name != "dist":
            fail("refusing to clear an unexpected output folder")
        shutil.rmtree(DIST)
    DIST.mkdir()

    for name in COPIED:
        src = ROOT / name
        if not src.exists():
            fail(f"{name} is missing from the repository root")
        shutil.copyfile(src, DIST / name)
    shutil.copyfile(SRC / "favicon.svg", DIST / "favicon.svg")
    sizes = {name: (ROOT / name).stat().st_size for name in COPIED}

    css = (SRC / "style.css").read_text(encoding="utf-8").strip()
    app_js = (SRC / "app.js").read_text(encoding="utf-8").strip()
    head_js = 'document.documentElement.classList.add("js");'
    for block, label in ((css, "style.css"), (app_js, "app.js")):
        if re.search(r"</(style|script)", block, re.I):
            fail(f"{label} contains a closing tag")

    prompt = read_prompt()
    index = render_index(data, groups, css, head_js, app_js, sizes, prompt)
    (DIST / "index.html").write_text(index, encoding="utf-8")
    (DIST / "index.md").write_text(render_markdown(data, groups), encoding="utf-8")
    (DIST / "agent-prompt.txt").write_text(prompt, encoding="utf-8")
    (DIST / "404.html").write_text(render_404(css), encoding="utf-8")
    (DIST / "_headers").write_text(render_headers([csp_hash(head_js), csp_hash(app_js)], csp_hash(css)), encoding="utf-8")

    skills = build_skills()
    well_known = DIST / ".well-known"
    (well_known / "ai-catalog.json").write_text(json.dumps(ai_catalog(skills), indent=2) + "\n", encoding="utf-8")
    (well_known / "api-catalog").write_text(json.dumps(api_catalog(), indent=2) + "\n", encoding="utf-8")

    updated = data.get("updated", max(e["source_checked"] for e in entries))
    (DIST / "robots.txt").write_text(
        "# Content signals, see https://contentsignals.org/\n"
        "# search: building a search index. ai-input: using pages as input to AI answers.\n"
        "# ai-train: training or fine-tuning AI models.\n"
        f"User-agent: *\nContent-Signal: {CONTENT_SIGNAL}\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n",
        encoding="utf-8",
    )
    urls = [BASE_URL] + [
        BASE_URL + name for name in ("llms.txt", "llms-full.txt", "resources.json", "AGENTS.md", "agent-prompt.txt")
    ]
    sitemap = "".join(f"  <url><loc>{esc(u)}</loc><lastmod>{updated}</lastmod></url>\n" for u in urls)
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + sitemap + "</urlset>\n",
        encoding="utf-8",
    )

    print(f"Built {DIST.relative_to(ROOT)} with {len(entries)} entries in {len(groups)} groups:")
    for g in groups:
        print(f"  {g['name']}: {len(g['entries'])}")
    print(f"  index.html: {file_size(len(index.encode('utf-8')))}")


if __name__ == "__main__":
    main()
