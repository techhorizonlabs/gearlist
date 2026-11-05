#!/usr/bin/env python3
"""Build the Gearlist website into site/dist from ../resources.json.

Python 3 standard library only. No network access. Run from anywhere:

    python3 site/build_site.py
"""
import base64
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
SRC = SITE / "src"
DIST = SITE / "dist"

BASE_URL = "https://gearlist.build/"
REPO_URL = "https://github.com/techhorizonlabs/gearlist"
REPO_LABEL = "github.com/techhorizonlabs/gearlist"
CONTRIBUTING_URL = REPO_URL + "/blob/main/CONTRIBUTING.md"
INSTALL = "npx skills add techhorizonlabs/gearlist"
COPIED = ["llms.txt", "llms-full.txt", "resources.json", "AGENTS.md", "social-preview.png"]

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


def render_index(data, groups, css, head_js, app_js, sizes):
    entries = [e for g in groups for e in g["entries"]]
    total = len(entries)
    reserved = {g["slug"] for g in groups} | {
        "top", "main", "catalog", "agents", "q", "status", "empty", "clear",
        "copy", "cmd", "copy-status", "checks", "kit",
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
        ("llms.txt", "Start here. A short index with links to the other files.", "gold"),
        ("llms-full.txt", "Every entry as plain text: purpose, audience, access and check date.", "pink"),
        ("resources.json", "The canonical records as JSON. The other files are built from it.", "teal"),
        ("AGENTS.md", "House rules for an agent reading or changing the list.", "gold"),
    ]
    file_cards = "".join(
        f'<li><a class="file c-{colour}" href="/{name}"><b>{name}</b><span>{esc(text)}</span>'
        f"<small>{file_size(sizes[name])}</small></a></li>"
        for name, text, colour in files
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
<div class="cmd"><code id="cmd">{esc(INSTALL)}</code><button type="button" id="copy" class="js-only">Copy</button></div>
<span class="sr" id="copy-status" aria-live="polite"></span>
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
<h2 id="h-agents">For agents</h2>
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
    return f"""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Content-Security-Policy: {csp}

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

    index = render_index(data, groups, css, head_js, app_js, sizes)
    (DIST / "index.html").write_text(index, encoding="utf-8")
    (DIST / "404.html").write_text(render_404(css), encoding="utf-8")
    (DIST / "_headers").write_text(render_headers([csp_hash(head_js), csp_hash(app_js)], csp_hash(css)), encoding="utf-8")

    updated = data.get("updated", max(e["source_checked"] for e in entries))
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")
    urls = [BASE_URL] + [BASE_URL + name for name in ("llms.txt", "llms-full.txt", "resources.json", "AGENTS.md")]
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
