// Tests for the entry pages (/tools/<id>/), the group pages (/category/<slug>/), their
// Markdown copies, the Open Graph images, the sitemaps and the IndexNow key file.
// They read the built site/dist folder:
//
//   python3 build.py && python3 site/build_site.py && node --test "site/test/*.test.mjs"
//
// node:test only. No network access.

import { test, describe, before } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, readdir, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DIST = path.join(SITE, "dist");
const ROOT = path.dirname(SITE);
const ORIGIN = "https://gearlist.build";
// Paths the Worker answers (wrangler.jsonc run_worker_first), so they have no file in dist.
const WORKER_PATHS = new Set(["/mcp", "/mcp/server-card", "/api/search", "/openapi.json"]);
// Properties the data has no source for. A page must never claim them.
const INVENTED = ["aggregateRating", "review", "offers", "softwareVersion", "price", "ratingValue", "downloadUrl"];

const slug = (text) => text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
const githubRepo = (url) => /^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$/.test(url);
const escHtml = (s) =>
  s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
const unescape = (s) =>
  s.replace(/&quot;/g, '"').replace(/&#x27;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");

async function exists(file) {
  try {
    return (await stat(file)).isFile();
  } catch {
    return false;
  }
}

function meta(html, attr, name) {
  const re = new RegExp(`<meta ${attr}="${name}" content="([^"]*)">`);
  const m = re.exec(html);
  return m ? unescape(m[1]) : null;
}

function canonical(html) {
  const m = /<link rel="canonical" href="([^"]+)">/.exec(html);
  return m && m[1];
}

function jsonLd(html) {
  return [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].map((m) => JSON.parse(m[1]));
}

function graphNodes(docs) {
  return docs.flatMap((d) => d["@graph"] || [d]);
}

function walkKeys(value, out = new Set()) {
  if (Array.isArray(value)) value.forEach((v) => walkKeys(v, out));
  else if (value && typeof value === "object") {
    for (const [k, v] of Object.entries(value)) {
      out.add(k);
      walkKeys(v, out);
    }
  }
  return out;
}

// The file Workers static assets would serve for a path, with html_handling auto-trailing-slash.
function fileFor(pathname) {
  if (pathname.endsWith("/")) return path.join(DIST, pathname, "index.html");
  return path.join(DIST, pathname);
}

let records;
let groups;
const pages = new Map(); // pathname -> html

before(async () => {
  try {
    await stat(path.join(DIST, "tools"));
  } catch {
    throw new Error("site/dist has no entry pages. Run python3 site/build_site.py first.");
  }
  records = JSON.parse(await readFile(path.join(ROOT, "resources.json"), "utf8")).resources;
  groups = [...new Set(records.map((e) => e.category))].map((name) => ({
    name,
    slug: slug(name),
    entries: records.filter((e) => e.category === name),
  }));
  pages.set("/", await readFile(path.join(DIST, "index.html"), "utf8"));
  for (const g of groups) pages.set(`/category/${g.slug}/`, await readFile(fileFor(`/category/${g.slug}/`), "utf8"));
  for (const e of records) pages.set(`/tools/${e.id}/`, await readFile(fileFor(`/tools/${e.id}/`), "utf8"));
});

describe("Entry and group pages", () => {
  test("every entry has exactly one page and one Markdown copy, and there are no others", async () => {
    const ids = records.map((e) => e.id).sort();
    const listing = await readdir(path.join(DIST, "tools"), { withFileTypes: true });
    const dirs = listing.filter((d) => d.isDirectory()).map((d) => d.name).sort();
    const md = listing.filter((d) => d.isFile() && d.name.endsWith(".md")).map((d) => d.name.slice(0, -3)).sort();
    assert.deepEqual(dirs, ids);
    assert.deepEqual(md, ids);
    assert.equal(new Set(ids).size, ids.length, "ids are unique");
    for (const id of ids) assert.match(id, /^[a-z0-9]+(-[a-z0-9]+)*$/, `${id} is a clean path segment`);
    const cats = (await readdir(path.join(DIST, "category"), { withFileTypes: true }))
      .filter((d) => d.isDirectory()).map((d) => d.name).sort();
    assert.deepEqual(cats, groups.map((g) => g.slug).sort());
  });

  test("titles and descriptions are present and unique, and name the entry", () => {
    const titles = new Map();
    const descriptions = new Map();
    for (const [p, html] of pages) {
      const title = unescape(/<title>([^<]+)<\/title>/.exec(html)[1]);
      const description = meta(html, "name", "description");
      assert.ok(title.trim(), `${p} has a title`);
      assert.ok(description && description.trim().length >= 50, `${p} has a description`);
      assert.ok(!titles.has(title), `${p} repeats the title of ${titles.get(title)}`);
      assert.ok(!descriptions.has(description), `${p} repeats the description of ${descriptions.get(description)}`);
      titles.set(title, p);
      descriptions.set(description, p);
    }
    for (const e of records) {
      const html = pages.get(`/tools/${e.id}/`);
      const title = unescape(/<title>([^<]+)<\/title>/.exec(html)[1]);
      assert.ok(title.startsWith(e.name), `${e.id} title starts with its name`);
      assert.ok(title.endsWith(" | Gearlist"), `${e.id} title ends with the site name`);
      assert.ok(title.length <= 72 + " | Gearlist".length, `${e.id} title is ${title.length} characters`);
      const lead = title.slice(0, -" | Gearlist".length);
      assert.doesNotMatch(lead, /[,;:(]$/, `${e.id} title ends on punctuation`);
      const last = lead.split(" ").at(-1).toLowerCase();
      assert.ok(!["a", "an", "and", "or", "of", "the", "to", "for", "with", "that", "which", "each", "up", "by", "in", "on"].includes(last), `${e.id} title ends on "${last}"`);
      assert.ok(html.includes(`<h1>${escHtml(e.name)}</h1>`), `${e.id} h1 is the name`);
      assert.ok(meta(html, "name", "description").startsWith(e.description.slice(0, 40)), `${e.id} description leads with the entry`);
    }
  });

  test("titles that the cutter stopped mid-phrase now read as whole phrases", () => {
    // PR #9 review, 6 Nov 2026: the cutter stopped these on a word that needs its object.
    const expected = {
      opensandbox: "OpenSandbox: Isolated Docker or Kubernetes sandboxes for agents",
      "public-apis": "Public APIs: Community list of free APIs, grouped by topic",
      brag: "/brag: Agent skill that turns your project into a launch video",
      whisperx: "WhisperX: Transcription with word timestamps and speaker labels",
      agentos: "agentOS: WebAssembly sandbox with files, a shell and networking",
      "ai-phone": "ai-phone: SIP phone daemon that lets an agent receive and place calls",
      "claude-devtools": "claude-devtools: App that rebuilds Claude Code sessions from local logs",
      "claude-plugins-official": "Claude plugins official: Anthropic's Claude Code plugin marketplace",
      cashclaw: "CashClaw: Node agent that quotes and does paid marketplace tasks",
      "agent-reach": "Agent Reach: CLI that lets coding agents read sites web search misses",
      "compound-engineering": "Compound Engineering: Skills that run a plan, build and review loop",
      "claude-squad": "Claude Squad: Terminal app that manages several agent sessions at once",
      "audio-cpp": "audio.cpp: C++ inference engine on ggml that runs local audio models",
      paseo: "Paseo: Run Claude Code, Codex and other coding agents side by side",
      happy: "Happy: Run Claude, Codex and Grok agents from desktop and phone",
      "dns-aid-checker": "Are you found by AI? DNS-AID checker: Check a domain's DNS-AID record",
      "playwright-mcp": "Playwright MCP: Let an agent drive a real browser",
      "sentry-mcp": "Sentry MCP: Sentry errors and traces for coding agents",
      "atlassian-mcp-server": "Atlassian MCP Server: Work in Jira and Confluence from an agent",
      "stripe-mcp": "Stripe MCP: Read and write Stripe data from an agent",
      "linear-mcp": "Linear MCP server: Find, create and update Linear issues",
      "figma-mcp-server": "Figma MCP server: Figma design context for coding agents",
      "slack-mcp-server": "Slack MCP server: Search, read and send Slack messages",
      "zapier-mcp": "Zapier MCP: Run actions in your apps through Zapier",
      "snyk-agent-scan": "Snyk Agent Scan: Check MCP servers and skills for risks",
      toolhive: "ToolHive: Run each MCP server in an isolated container",
      "nemo-guardrails": "NeMo Guardrails: Programmable guardrails for LLM apps",
      "owasp-agentic-top-10": "OWASP Top 10 for Agentic Applications: Agent security risks",
      "universal-commerce-protocol": "Universal Commerce Protocol (UCP): Checkout standard for agents",
      "agentic-commerce-protocol": "Agentic Commerce Protocol (ACP): Agent checkout from OpenAI and Stripe",
    };
    for (const [id, lead] of Object.entries(expected)) {
      const html = pages.get(`/tools/${id}/`);
      assert.ok(html, `/tools/${id}/ exists`);
      const title = unescape(/<title>([^<]+)<\/title>/.exec(html)[1]);
      assert.equal(title, `${lead} | Gearlist`);
    }
    // The cut-off endings themselves must not come back on any page.
    for (const e of records) {
      const lead = unescape(/<title>([^<]+)<\/title>/.exec(pages.get(`/tools/${e.id}/`))[1]).slice(0, -" | Gearlist".length);
      const last = lead.split(" ").at(-1).toLowerCase();
      assert.ok(!["gives", "built", "grouped", "turns", "isolated", "receive", "already", "access", "does"].includes(last), `${e.id} title ends on "${last}"`);
    }
  });

  test("canonical and og:url are the page's own address", () => {
    for (const [p, html] of pages) {
      assert.equal(canonical(html), ORIGIN + p, `${p} canonical`);
      assert.equal(meta(html, "property", "og:url"), ORIGIN + p, `${p} og:url`);
    }
  });

  test("each page keeps the documentation-checked caveat and links its Markdown copy", async () => {
    for (const [p, html] of pages) {
      assert.match(html, /Documentation checked means the source was read\. It does not mean the software was installed, tested or security audited\./, p);
      const alt = /<link rel="alternate" type="text\/markdown" href="([^"]+)"/.exec(html);
      assert.ok(alt, `${p} links a Markdown copy`);
      assert.ok(await exists(fileFor(alt[1])), `${p} Markdown copy ${alt[1]} exists`);
    }
    for (const e of records) {
      const md = await readFile(path.join(DIST, "tools", `${e.id}.md`), "utf8");
      assert.ok(md.startsWith("---\n"), `${e.id}.md has front matter`);
      assert.match(md, new RegExp(`^url: "${ORIGIN}/tools/${e.id}/"$`, "m"));
      assert.ok(md.includes(e.access_notes), `${e.id}.md quotes the access notes`);
      assert.match(md, /Documentation checked means the source was read/);
    }
  });

  test("entry pages show every field verbatim, with the official link and source", () => {
    const esc = escHtml;
    for (const e of records) {
      const html = pages.get(`/tools/${e.id}/`);
      for (const field of ["description", "for_whom", "access_notes"]) assert.ok(html.includes(esc(e[field])), `${e.id} ${field}`);
      assert.ok(html.includes(`href="${esc(e.url)}"`), `${e.id} official link`);
      assert.ok(html.includes(`href="${esc(e.source_url)}"`), `${e.id} source link`);
      assert.ok(html.includes(`datetime="${e.source_checked}"`), `${e.id} check date`);
      assert.ok(html.includes(`get_gear with id &quot;${e.id}&quot;`), `${e.id} agent prompt names the id`);
      if (e.thl_project) assert.match(html, /Tech Horizon Labs project/);
    }
  });

  test("JSON-LD parses and describes only what the data says", () => {
    for (const [p, html] of pages) {
      const docs = jsonLd(html);
      assert.ok(docs.length >= 1, `${p} has JSON-LD`);
      const keys = walkKeys(docs);
      for (const k of INVENTED) assert.ok(!keys.has(k), `${p} JSON-LD has no ${k}`);
    }
    for (const e of records) {
      const url = `${ORIGIN}/tools/${e.id}/`;
      const nodes = graphNodes(jsonLd(pages.get(`/tools/${e.id}/`)));
      const page = nodes.find((n) => n["@type"] === "ItemPage");
      assert.equal(page.url, url);
      assert.equal(page.lastReviewed, e.source_checked);
      const thing = nodes.find((n) => n["@id"] === url + "#entry");
      assert.equal(thing.name, e.name);
      assert.equal(thing.url, e.url);
      assert.equal(thing.description, e.description);
      if (githubRepo(e.url)) {
        assert.equal(thing["@type"], "SoftwareSourceCode", e.id);
        assert.equal(thing.codeRepository, e.url);
      } else {
        assert.ok(["SoftwareApplication", "CreativeWork"].includes(thing["@type"]), e.id);
      }
      const crumbs = nodes.find((n) => n["@type"] === "BreadcrumbList");
      assert.deepEqual(crumbs.itemListElement.map((i) => [i.position, i.name, i.item]), [
        [1, "Gearlist", ORIGIN + "/"],
        [2, e.category, `${ORIGIN}/category/${slug(e.category)}/`],
        [3, e.name, url],
      ]);
    }
  });

  test("group pages list every entry in an ItemList that points at entry pages", () => {
    for (const g of groups) {
      const html = pages.get(`/category/${g.slug}/`);
      const nodes = graphNodes(jsonLd(html));
      const list = nodes.find((n) => n["@type"] === "ItemList");
      assert.equal(list.numberOfItems, g.entries.length);
      assert.deepEqual(list.itemListElement.map((i) => i.url), g.entries.map((e) => `${ORIGIN}/tools/${e.id}/`));
      assert.deepEqual(list.itemListElement.map((i) => i.position), g.entries.map((_, i) => i + 1));
      for (const e of g.entries) assert.ok(html.includes(`href="/tools/${e.id}/"`), `${g.slug} links ${e.id}`);
      const crumbs = nodes.find((n) => n["@type"] === "BreadcrumbList");
      assert.equal(crumbs.itemListElement.length, 2);
    }
    const home = graphNodes(jsonLd(pages.get("/"))).find((n) => n["@type"] === "ItemList");
    const grouped = groups.flatMap((g) => g.entries);
    assert.deepEqual(home.itemListElement.map((i) => i.url), grouped.map((e) => `${ORIGIN}/tools/${e.id}/`));
  });

  test("related entries come from the same group", () => {
    for (const e of records) {
      const html = pages.get(`/tools/${e.id}/`);
      const block = /<section class="related"[\s\S]*?<\/section>/.exec(html)[0];
      const linked = [...block.matchAll(/href="\/tools\/([^/"]+)\/"/g)].map((m) => m[1]);
      const group = records.filter((r) => r.category === e.category).length;
      assert.equal(linked.length, Math.min(6, group - 1), e.id);
      assert.ok(!linked.includes(e.id), `${e.id} does not list itself`);
      for (const id of linked) assert.equal(records.find((r) => r.id === id).category, e.category, `${e.id} -> ${id}`);
    }
  });

  test("the home page links every card to its entry page and keeps the official link", () => {
    const html = pages.get("/");
    for (const e of records) {
      assert.ok(html.includes(`<h3><a href="/tools/${e.id}/">`), `${e.id} card opens its page`);
    }
    for (const g of groups) assert.ok(html.includes(`<a href="/category/${g.slug}/">`), `${g.slug} heading links its page`);
    // Search reads these elements; they must still be on every card.
    assert.equal((html.match(/<article class="e"/g) || []).length, records.length);
    assert.equal((html.match(/<p class="d">/g) || []).length, records.length);
  });
});

describe("Links, images and headers", () => {
  test("every internal link resolves to a file or a Worker route", async () => {
    const ids = new Map();
    for (const [p, html] of pages) ids.set(p, new Set([...html.matchAll(/ id="([^"]+)"/g)].map((m) => m[1])));
    const checked = new Map();
    for (const [p, html] of pages) {
      for (const [, raw] of html.matchAll(/ (?:href|src)="([^"]+)"/g)) {
        const href = unescape(raw);
        let target;
        if (href.startsWith("#")) target = new URL(p + href, ORIGIN);
        else if (href.startsWith("/") && !href.startsWith("//")) target = new URL(href, ORIGIN);
        else if (href.startsWith(ORIGIN + "/")) target = new URL(href);
        else continue;
        const pathname = decodeURIComponent(target.pathname);
        if (target.hash) {
          const anchors = ids.get(pathname);
          if (anchors) assert.ok(anchors.has(target.hash.slice(1)), `${p} links ${href}, an anchor that does not exist`);
        }
        if (WORKER_PATHS.has(pathname)) continue;
        if (!checked.has(pathname)) checked.set(pathname, await exists(fileFor(pathname)));
        assert.ok(checked.get(pathname), `${p} links ${href}, which would be a 404`);
        if (!pathname.endsWith("/") && (await exists(path.join(DIST, pathname, "index.html")))) {
          assert.fail(`${p} links ${href} without its trailing slash, which redirects`);
        }
      }
    }
  });

  test("every page has a social image that exists, at 1200 x 630 when it is per page", async () => {
    for (const [p, html] of pages) {
      const image = meta(html, "property", "og:image");
      assert.ok(image && image.startsWith(ORIGIN + "/"), `${p} og:image`);
      const file = fileFor(new URL(image).pathname);
      assert.ok(await exists(file), `${p} og:image ${image} exists`);
      const width = Number(meta(html, "property", "og:image:width"));
      const height = Number(meta(html, "property", "og:image:height"));
      const png = await readFile(file);
      assert.equal(png.subarray(1, 4).toString("latin1"), "PNG");
      assert.equal(png.readUInt32BE(16), width, `${p} image width`);
      assert.equal(png.readUInt32BE(20), height, `${p} image height`);
      if (image.includes("/og/")) assert.deepEqual([width, height], [1200, 630]);
      assert.ok(meta(html, "property", "og:image:alt"), `${p} og:image:alt`);
    }
  });

  test("the CSP hashes cover the inline script and style on every page", async () => {
    const headers = await readFile(path.join(DIST, "_headers"), "utf8");
    const csp = /Content-Security-Policy: (.*)/.exec(headers)[1];
    const hash = (s) => "'sha256-" + createHash("sha256").update(s, "utf8").digest("base64") + "'";
    for (const [p, html] of pages) {
      for (const [, body] of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) assert.ok(csp.includes(hash(body)), `${p} script`);
      for (const [, body] of html.matchAll(/<style>([\s\S]*?)<\/style>/g)) assert.ok(csp.includes(hash(body)), `${p} style`);
      assert.doesNotMatch(html, /<img /, `${p} has no images the CSP would block`);
    }
  });

  test("Markdown copies get a canonical Link header and a Markdown type", async () => {
    // Placeholder rules as Workers static assets apply them: ":name" matches one path segment
    // and can be used again in the header value.
    const rules = [];
    let current = null;
    for (const line of (await readFile(path.join(DIST, "_headers"), "utf8")).split("\n")) {
      if (!line.trim()) continue;
      if (!/^\s/.test(line)) rules.push((current = { pattern: line.trim(), headers: [] }));
      else current.headers.push([line.slice(0, line.indexOf(":")).trim(), line.slice(line.indexOf(":") + 1).trim()]);
    }
    assert.ok(rules.length <= 100, "Cloudflare allows 100 header rules");
    function headersFor(pathname) {
      const out = [];
      for (const rule of rules) {
        if (rule.pattern.startsWith("https://")) continue;
        const names = [];
        const source = rule.pattern
          .replace(/[.+?^${}()|[\]\\]/g, "\\$&")
          .replace(/\*/g, "(?<splat>.*)")
          .replace(/:([A-Za-z]\w*)/g, (_, n) => (names.push(n), `(?<${n}>[^/]+)`));
        const m = new RegExp(`^${source}$`).exec(pathname);
        if (!m) continue;
        for (const [k, v] of rule.headers) out.push([k, v.replace(/:([A-Za-z]\w*)/g, (s, n) => (m.groups && m.groups[n]) ?? s)]);
      }
      return out;
    }
    const e = records[0];
    const md = headersFor(`/tools/${e.id}.md`);
    assert.deepEqual(md.find(([k]) => k === "Link"), ["Link", `<${ORIGIN}/tools/${e.id}/>; rel="canonical"`]);
    // The placeholder rules also match missing files. Setting Content-Type there would serve
    // the 404 page as Markdown, so it is left to the asset server, which sends .md as text/markdown.
    assert.equal(md.find(([k]) => k === "Content-Type"), undefined);
    assert.equal(headersFor(`/tools/${e.id}/`).find(([k]) => k === "Link"), undefined);
    const g = groups[0];
    assert.deepEqual(headersFor(`/category/${g.slug}.md`).find(([k]) => k === "Link"), ["Link", `<${ORIGIN}/category/${g.slug}/>; rel="canonical"`]);
  });

  test("no en or em dashes in the built pages", async () => {
    const data = await readFile(path.join(ROOT, "resources.json"), "utf8");
    if (/[\u2013\u2014]/.test(data)) return; // entry text is quoted as written
    for (const [p, html] of pages) assert.doesNotMatch(html, /[\u2013\u2014]/, p);
    for (const e of records) assert.doesNotMatch(await readFile(path.join(DIST, "tools", `${e.id}.md`), "utf8"), /[\u2013\u2014]/);
  });
});

describe("Sitemaps, robots.txt and IndexNow", () => {
  test("the sitemap index lists sitemaps that hold every page once", async () => {
    const robots = await readFile(path.join(DIST, "robots.txt"), "utf8");
    assert.match(robots, /^Sitemap: https:\/\/gearlist\.build\/sitemap\.xml$/m);
    const index = await readFile(path.join(DIST, "sitemap.xml"), "utf8");
    assert.match(index, /<sitemapindex xmlns="http:\/\/www\.sitemaps\.org\/schemas\/sitemap\/0\.9">/);
    const maps = [...index.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
    assert.ok(maps.length >= 3);
    const listed = new Map();
    for (const map of maps) {
      assert.ok(map.startsWith(ORIGIN + "/sitemap") && !new URL(map).pathname.slice(1).includes("/"), `${map} sits at the root`);
      const xml = await readFile(path.join(DIST, new URL(map).pathname), "utf8");
      for (const [, loc, lastmod] of xml.matchAll(/<url><loc>([^<]+)<\/loc><lastmod>([^<]+)<\/lastmod><\/url>/g)) {
        assert.ok(!listed.has(loc), `${loc} is listed once`);
        assert.match(lastmod, /^\d{4}-\d{2}-\d{2}$/);
        listed.set(loc, lastmod);
        assert.ok(await exists(fileFor(new URL(loc).pathname)), `${loc} exists`);
      }
    }
    for (const p of pages.keys()) assert.ok(listed.has(ORIGIN + p), `${p} is in a sitemap`);
    for (const e of records) assert.equal(listed.get(`${ORIGIN}/tools/${e.id}/`), e.source_checked, `${e.id} lastmod`);
    for (const g of groups) {
      const latest = g.entries.map((e) => e.source_checked).sort().at(-1);
      assert.equal(listed.get(`${ORIGIN}/category/${g.slug}/`), latest, `${g.slug} lastmod`);
    }
  });

  test("the IndexNow key file is served from the root and matches the committed key", async () => {
    const key = (await readFile(path.join(SITE, "src", "indexnow-key.txt"), "utf8")).trim();
    assert.match(key, /^[A-Za-z0-9-]{8,128}$/);
    assert.equal(await readFile(path.join(DIST, `${key}.txt`), "utf8"), key);
  });
});
