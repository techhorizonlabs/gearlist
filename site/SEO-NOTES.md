# Search notes for gearlist.build

Written 6 November 2026. Google guidance below was read on that date at developers.google.com/search/docs (title links page updated 10 December 2025; snippets; software app, breadcrumb and carousel structured data pages updated 8 September 2026; sitemaps updated 8 July 2026; canonical URLs updated 10 July 2026).

## What the site now has

| Page | Address | Count |
| --- | --- | --- |
| Home | `/` | 1 |
| Group | `/category/<slug>/`, for example `/category/mcp-and-integrations/` | 7 |
| Entry | `/tools/<id>/`, for example `/tools/firecrawl/` | 302 |
| Markdown copy | `/tools/<id>.md` and `/category/<slug>.md` | 309 |
| Social image | `/og/tools/<id>.png` and `/og/category/<slug>.png`, 1200 by 630 | 309 |

The `<id>` is the entry id in `resources.json`, which is also the id the MCP tool `get_gear` takes, so a person, a search engine and an agent all use the same name for an entry. Ids are already lowercase words joined by hyphens; the build now refuses an id that is not, because the id is the address.

The home page cards now open the entry page from the name. The official link stays on every card, under the description, and the source link stays beside it.

## Entry page titles

Pattern: `<Name>: <short description> | Gearlist`. GitHub entries add the repository when it fits: `<Name> (<owner>/<repo>): <short description> | Gearlist`.

Examples from this build:

- `Agent Deck: Mac interface for coding agent sessions | Gearlist`
- `Jevgrep: Search a codebase | Gearlist`
- `Ruflo (ruvnet/ruflo): Agent harness around Claude Code and Codex | Gearlist`
- `Model Context Protocol: Open protocol that connects LLM applications | Gearlist`

Why this pattern:

1. People search for a tool by its name, often with the repository (`firecrawl/firecrawl`) when it lives on GitHub. The name leads, as in the gitmanual pages the founder pointed at.
2. Google's title link guidance asks for descriptive, concise titles and warns against "boilerplate" titles: long text that is the same on every page and varies by one piece of information. Its example is "Band Name - See videos, lyrics, posters, albums, reviews and concerts". A title such as "<Name>: what it does, who it's for and the access it needs" is that pattern, so it was not used. The short description comes from each entry's own description, so every title says something specific.
3. Google uses the page's main heading as an input to title links. Each entry page's `<h1>` is the name, and the description sits directly under it, so the title and the page agree.
4. The site name goes at the end after a pipe, as the guidance suggests. Google shows the site name on its own line in results, so it does not matter if the end of a long title is cut off.

Length: the name and short description aim for 60 characters. The description is cut before a word that starts a new clause ("that", "for", "with" and so on) or after the first item of a list, and never just after "that" or "which". When that leaves only a word or two, it runs on to the next clause, up to 72 characters. Median 53, longest 72, before " | Gearlist". Seventy-two of 302 run past 60; Google cuts those in the visible link and still reads the whole title.

Group pages use a search phrase from `GROUP_PAGES` in `build_site.py`, for example `MCP servers and integrations: 41 source-checked entries | Gearlist`. The count comes from the data at build time.

## Descriptions

Entry pages: the description, then "For" and the audience, then "Access and use:" and the access notes, cut at a sentence end or a word at about 200 characters. Google's snippet guidance says programmatic descriptions are encouraged for database sites when they are page specific and readable, and that there is no length limit, only display truncation. The access notes are the part no other directory has, so they are in the snippet when they fit.

## Structured data

Every entry page has one JSON-LD graph: `ItemPage` (with `lastReviewed` set to the source check date), the entry, `BreadcrumbList` (Gearlist, group, entry), `WebSite` and the Tech Horizon Labs `Organization`.

- The entry is `SoftwareSourceCode` with `codeRepository` when its official link is a GitHub repository (137 entries), `CreativeWork` for the seven protocols, and `SoftwareApplication` for the rest.
- Each entry carries only fields from `resources.json`: name, description, official link, audience (`for_whom`) and, for Tech Horizon Labs projects, the creator. The tests fail if any page has a rating, review, offer, price, version or download link.
- Google's software app rich result requires `offers.price` and a rating or review. The data has neither, so these pages will not get that rich result, and Search Console may list the `SoftwareApplication` items as not eligible. That is expected. The markup still names the entity, its link and its audience for search engines and AI answer engines.
- The Tech Horizon Labs `Organization` (`#org`) carries `url` (https://techhorizonlabs.com), `legalName` (Tech Horizon Labs Pty Ltd) and the GitHub organisation in `sameAs`, as techhorizonlabs.com does. It has no `logo`, because the repository holds no Tech Horizon Labs logo file. The `WebSite` node (`#website`, named Gearlist) lists in `sameAs` the repository and the MCP directories that give the Gearlist server a page of its own: Glama, Mcptry and AllMCPs. Added 14 November 2026, with the About page at `/about/` (an `AboutPage`).
- Group pages use `CollectionPage` with an `ItemList` whose items are position, URL and name, pointing at the entry pages on this site, which is Google's summary page pattern. Software is not one of the carousel types, so no carousel is expected.
- The home page `ItemList` now points at the entry pages, for the same reason. It used to point at the official links.

## Sitemaps, robots.txt and IndexNow

`/sitemap.xml` is now a sitemap index. It points at `sitemap-pages.xml`, `sitemap-categories.xml` and `sitemap-tools.xml`, which sit at the root so they can list any page. Entry `lastmod` is `source_checked`. robots.txt names the index.

The IndexNow key file is at `/<key>.txt`; the key is committed in `site/src/indexnow-key.txt`. The submit command is in `site/README.md`. Nothing has been submitted.

After deploy, someone with access should submit `https://gearlist.build/sitemap.xml` in Google Search Console and Bing Webmaster Tools, then run the IndexNow command once.

## Agents and AI answer engines

- Each entry page links a Markdown copy with `<link rel="alternate" type="text/markdown">`, and each copy sends `Link: rel="canonical"` back to the HTML page, so search engines treat the HTML page as the one to show. The header rule uses a placeholder (`/tools/:id.md`), since Cloudflare allows 100 header rules, so a mistyped `.md` address also gets the header on its 404. Search engines ignore a canonical on a 404.
- `llms.txt` lists the group pages as Markdown and gives the `/tools/<id>/` pattern. `llms-full.txt` and `index.md` give every entry's page and Markdown address.
- Each entry page has a "Give this to your agent" prompt for that one tool. It names the page, the official link, the `get_gear` id and the source check date, and asks the agent to quote the access notes and ask before installing anything.
- The Worker is unchanged. Two optional follow ups that would need a Worker change: return each entry's page address from `search_gear` and `get_gear`, so agents can cite the page; and Markdown negotiation on `/tools/*`, which would make every entry page view a Worker request.

## GitHub search: a proposal to apply by hand

GitHub's repository search matches the name, the description and the topics by default. The README is only searched with `in:readme`. So the description and topics matter most there; the README matters for Google, which indexes the GitHub page.

### Description

Current: "Source-checked MCP servers, agent skills and tools, with access notes. Point an agent at this repo to bootstrap."

Proposed:

> Source-checked list of AI agent tools, MCP servers and agent skills, with the access each one needs. Search it at gearlist.build or from Claude Code, Codex or Cursor through its read-only MCP server.

Why: it holds the words people type ("AI agent tools", "MCP servers", "agent skills", "list", "Claude Code", "Codex", "Cursor"), keeps the access notes as the reason to choose it, and states only what is true today (the agent prompt has setup for those clients). It has no entry count, because a hand-written count goes stale.

### Topics (20)

GitHub allows 20. Counts are public repositories with each topic on 6 November 2026.

| Topic | Repos | Why |
| --- | --- | --- |
| `mcp` | 111,892 | Main term for the protocol. Already set. |
| `mcp-server` | 41,179 | Singular form people search. |
| `mcp-servers` | 1,369 | Plural form; small enough that Gearlist can be seen on the topic page. Already set. |
| `model-context-protocol` | 42,134 | Full name. |
| `ai-agents` | 135,037 | Broadest audience term. Already set. |
| `ai-agent` | 43,973 | Singular form. |
| `agentic-ai` | 29,652 | Common phrasing in 2026. |
| `ai-agent-tools` | 415 | Exact phrase for what the list is; small topic. |
| `agent-tools` | 2,229 | Same phrase without "ai". |
| `agent-skills` | 39,685 | The Agent Skills format the repo ships. Already set. |
| `claude-skills` | 14,468 | How Claude users name skills. Already set. |
| `claude-code` | 111,239 | Named in 75 entries, and the repo's skills target it. Already set. |
| `claude-code-skills` | 2,481 | Exact phrase; small topic. |
| `claude` | 65,868 | Broad Claude searches. |
| `codex` | 48,092 | Named in 51 entries, second to Claude Code. |
| `coding-agents` | 8,127 | The audience of most entries. |
| `llm-tools` | 5,870 | Tool lists for LLM work. |
| `ai-tools` | 17,766 | General "AI tools" searches. |
| `curated-list` | 4,790 | What the repo is. |
| `llms-txt` | 2,265 | The repo publishes llms.txt files. Already set. |

Left out on purpose: `awesome-list` and `awesome`, which carry the community "awesome list" format and are a hype word under the house voice; `developer-tools`, because the list also has entries for marketers, analysts, agencies and creators. `cursor` (20,169 repos, named in 20 entries) was the next candidate; swap it for `llm-tools` if client names should win.

### README

One change, applied through `build.py`: the opening sentence now says "AI agent tools", the phrase people search, where it said "agent tools". The home page summary, title and meta description use the same wording. Every README entry now also links its Gearlist page. BOSUN should read the README wording before a public push, as AGENTS.md asks.
