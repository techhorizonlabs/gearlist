# Gearlist website

The site is static files plus a small Worker script, both on the `gearlist-site` Cloudflare Worker at gearlist.build and www.gearlist.build.

## Build

Run `python3 build.py`, then `python3 site/build_site.py`, from the repository root, so the site and the README list the same entries. Both scripts use the Python 3 standard library, except that `site/og_image.py` uses Pillow for the social images (see below).

`build_site.py` reads `resources.json` and the `skills/` folder and writes `site/dist`:

- `index.html`, a 404 page, `robots.txt` (with a Content-Signal line), and a `_headers` file with the security headers and the Link headers.
- A page for every entry at `/tools/<id>/`, where `<id>` is the entry's id in `resources.json` (the same id `get_gear` takes), and a page for every group at `/category/<slug>/`. Each page has its own title, description, canonical link, breadcrumb, JSON-LD and social image, and the documentation-checked caveat. Entry pages also carry a prompt for that one tool and links to up to six related entries from the same group.
- A Markdown copy beside each of those pages, at `/tools/<id>.md` and `/category/<slug>.md`. Each HTML page links its copy with `<link rel="alternate" type="text/markdown">`, and each copy sends a `Link: rel="canonical"` header back to its HTML page.
- `og/tools/<id>.png` and `og/category/<slug>.png`: a 1200 by 630 social image per page, drawn by `site/og_image.py` in the style of `social-preview.png`.
- `sitemap.xml`, a sitemap index pointing at `sitemap-pages.xml` (the home page and agent files), `sitemap-categories.xml` and `sitemap-tools.xml`. An entry's `lastmod` is its `source_checked` date; a group's is the latest date among its entries.
- `<key>.txt`, the IndexNow key file. The key lives in `site/src/indexnow-key.txt`, which is committed so the key stays the same. If the file is missing, the build writes a new random key; commit it.
- `index.md`: the catalog page as Markdown. The Worker sends it for `/` when a request asks for `text/markdown`.
- `agent-prompt.txt`: the prompt from `site/src/agent-prompt.txt`, also shown on the home page under "Give this to your agent".
- `.well-known/ai-catalog.json` (names the MCP server card and the skills), `.well-known/api-catalog` (RFC 9727 list of the APIs), and `.well-known/agent-skills/` (each skill's `SKILL.md`, a zip for skills that ship scripts, and `index.json` with SHA-256 digests).
- Copies of `llms.txt`, `llms-full.txt`, `resources.json`, `AGENTS.md` and `social-preview.png`.

Styles and the page script live in `site/src` and are inlined at build time. The build hashes them into the Content-Security-Policy, so rebuild after any change.

Every page inlines the same `style.css` and `app.js`, so one Content-Security-Policy covers the home page, the entry pages and the group pages.

### Titles and descriptions

An entry page is titled `<Name>: <short description> | Gearlist`, for example `Firecrawl: Crawl and scrape sites | Gearlist`. The short description is the entry's own description, cut at a clause break so the name and description stay near 60 characters. GitHub entries add the repository, as in `Jevgrep (dzhng/jevgrep): ...`, when that still leaves room. The meta description is the entry's description, then who it is for, then its access notes, up to about 200 characters. `site/SEO-NOTES.md` explains the choice.

### Social images

`site/og_image.py` needs Pillow (`python3 -m pip install Pillow`) and the Space Grotesk and Space Mono fonts. It looks for the fonts in `GEARLIST_FONT_DIR`, then in the usual font folders on macOS and Linux. Space Grotesk can be the variable font (`SpaceGrotesk[wght].ttf`) or the static files. Without Pillow or the fonts, the build prints a note and every page uses `social-preview.png` instead. The images add about 5.8 MB to `dist`.

## The Worker

`site/worker` is plain JavaScript with no dependencies. `wrangler.jsonc` sends only these paths to it first (`run_worker_first`). Everything else is served straight from `dist`.

- `/`: passes the HTML page through, or returns `index.md` when the request prefers `text/markdown`. Both carry `Vary: Accept`.
- `/mcp`: the MCP server. Streamable HTTP, stateless, no sign-in, read-only. Tools: `search_gear`, `get_gear`, `list_categories`, `list_skills`. It speaks MCP 2026-07-28 (per-request metadata and `server/discover`) and the older `initialize` handshake (2025-11-25, 2025-06-18 and 2025-03-26). A plain GET returns a short text explanation.
- `/mcp/server-card`: the MCP Server Card.
- `/api/search?q=`: the same search as JSON. `/openapi.json` describes it.

The Worker reads `resources.json` and `.well-known/agent-skills/index.json` from the deployed files through the `ASSETS` binding, so the MCP server, the API and the page always describe the same deploy. It makes no other fetches, keeps no data and needs no secrets. The only state is the rate limit counter below, which Cloudflare keeps per IP address.

Responses that the Worker passes through from `ASSETS` keep their `_headers` rules, including the page CSP. Responses that the Worker builds itself set their own security headers in `site/worker/http.mjs`.

`/mcp` and `/api/search` share one rate limit per IP address (120 requests a minute per Cloudflare location), through the `RATE_LIMITER` binding in `wrangler.jsonc`.

## Test

```bash
python3 build.py && python3 site/build_site.py
node --test "site/test/*.test.mjs"
python3 -m unittest discover
```

The Worker tests use `node:test` and call the Worker's fetch handler with a fake `ASSETS` that serves `site/dist`. `site/test/pages.test.mjs` reads `site/dist` and checks that every entry has exactly one page and one Markdown copy, that titles and descriptions are unique, that canonical links and JSON-LD are right, that every internal link resolves, that every social image exists at the stated size, and that the sitemaps list every page. They need Node 18 or later and no packages.

To run the site locally, run `wrangler dev` in the `site` folder. If your Wrangler does not support the 2026-11-01 compatibility date yet, pass an earlier date, for example `wrangler dev --compatibility-date 2026-09-10`. Do not change the date in `wrangler.jsonc` for this.

## Deploy

1. Build, then run the tests above.
2. Check that the rate limit `namespace_id` in `wrangler.jsonc` (4271) is not used by another Worker on the account. Two Workers with the same id share counters.
3. From the `site` folder, run `wrangler deploy`.
4. Check the live site:

```bash
curl -sI https://gearlist.build/ | grep -i -E "content-security-policy|^link|^vary"
curl -s https://gearlist.build/ -H "Accept: text/markdown" | head -5
curl -s https://gearlist.build/mcp -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_gear","arguments":{"query":"browser","limit":2}}}'
curl -s https://gearlist.build/robots.txt
```

The first command must show the page CSP, the Link header and `Vary: Accept`. Then rescan at https://isitagentready.com/gearlist.build.

Also check one entry page and its Markdown copy:

```bash
curl -sI https://gearlist.build/tools/firecrawl/ | grep -i -E "content-security"
curl -sI https://gearlist.build/tools/firecrawl.md | grep -i -E "^link|content-type"
curl -s https://gearlist.build/sitemap.xml
```

## Tell search engines about changes (IndexNow)

IndexNow tells Bing and the other IndexNow search engines which pages changed. Google does not use it. Only submit after a deploy, once the key file is live at `https://gearlist.build/<key>.txt`, and only with the owner's approval. This one line sends every page:

```bash
python3 site/build_site.py --indexnow-payload | curl -sS -X POST "https://api.indexnow.org/indexnow" -H "Content-Type: application/json; charset=utf-8" --data-binary @-
```

`--indexnow-payload` prints the request body and builds nothing. A 200 or 202 response means the list was accepted.

## Cost

Requests that reach the Worker are billed as Worker requests. Static files are free. Because `/` runs the Worker first (for Markdown negotiation), every home page visit counts. On the Workers Free plan, requests past the daily limit get a 429 instead of falling back to the static page. To avoid that, remove `"/"` from `run_worker_first`. The home page then stays static and loses only Markdown negotiation, and `/index.md` still works.
