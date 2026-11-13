// Tests for the entry pages (/tools/<id>/), the group pages (/category/<slug>/), the What's new
// page (/new/), the build pages (/builds/<id>/), their Markdown copies, the Atom feed, the Open
// Graph images, the sitemaps and the IndexNow key file.
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

import { EARLIEST_ADDED } from "../worker/catalog.mjs";

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
let buildGroups; // the groups in builds.json
const pages = new Map(); // pathname -> html
const isBuildPage = (p) => p.startsWith("/builds/");

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
  pages.set("/new/", await readFile(fileFor("/new/"), "utf8"));
  for (const g of groups) pages.set(`/category/${g.slug}/`, await readFile(fileFor(`/category/${g.slug}/`), "utf8"));
  for (const e of records) pages.set(`/tools/${e.id}/`, await readFile(fileFor(`/tools/${e.id}/`), "utf8"));
  buildGroups = JSON.parse(await readFile(path.join(ROOT, "builds.json"), "utf8")).groups;
  for (const b of buildGroups) pages.set(`/builds/${b.id}/`, await readFile(fileFor(`/builds/${b.id}/`), "utf8"));
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
      // Vendor skill packs and MCP servers added 7 Nov 2026: the cutter stopped on whose they were.
      "cloudflare-skills": "Cloudflare Skills: Agent skills for building on Cloudflare",
      "cloudflare-security-audit-skill": "Cloudflare security-audit skill: Six-phase security audit of a codebase",
      "gemini-skills": "Gemini API skills: Agent skills for writing Gemini API code",
      "gemini-docs-mcp": "Gemini Docs MCP: Search and read the Gemini API docs from an agent",
      "google-skills": "Google Agent Skills: Skills for Google Cloud and other Google products",
      "google-developer-knowledge-mcp": "Google Developer Knowledge MCP: Search Google's developer docs",
      "google-maps-agent-skills": "Google Maps Platform agent skills: Add Google Maps features to an app",
      "maps-experience-agent-tools": "Maps Experience agent tools: Places, weather and routes for agents",
      "microsoft-graph-dev-skills": "Microsoft Graph Developer Skills: Copilot CLI plugin for Graph apps",
      "microsoft-skills": "Microsoft Agent Skills: Skills for Azure SDKs and Microsoft Foundry",
      "microsoft-mcp-server-for-enterprise": "Microsoft MCP Server for Enterprise: Ask about your Entra tenant",
      "notion-skills": "Notion Skills: Agent skills for the ntn CLI and Notion Apps",
      "notion-claude-code-plugin": "Notion plugin for Claude Code: Notion skills, commands and MCP server",
      "openrouter-skills": "OpenRouter Skills: Agent skills for building on OpenRouter",
      "openrouter-mcp": "OpenRouter MCP: Live models, prices and test messages from an agent",
      "nvidia-skills": "NVIDIA Agent Skills: Skills catalogue for NVIDIA software",
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
      // A build page is about prices, so it carries its own caveat, checked under "Build pages".
      if (!isBuildPage(p)) assert.match(html, /Documentation checked means the source was read\. It does not mean the software was installed, tested or security audited\./, p);
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

  test("entry pages show what we checked, with only the fields the entry has", async () => {
    const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const longDate = (iso) => {
      const [y, m, d] = iso.split("-").map(Number);
      return `${d} ${MONTHS[m - 1]} ${y}`;
    };
    const has = (e, key) => typeof e[key] === "string" && e[key].trim() !== "";
    for (const e of records) {
      const html = pages.get(`/tools/${e.id}/`);
      const block = /<section class="details" aria-labelledby="h-checked">([\s\S]*?)<\/section>/.exec(html);
      assert.ok(block, `${e.id} has a What we checked box`);
      assert.match(block[1], /<h2 id="h-checked">What we checked<\/h2>/);
      const rows = [...block[1].matchAll(/<dt>([^<]+)<\/dt><dd>([\s\S]*?)<\/dd>/g)].map((m) => [m[1], m[2]]);
      const expected = [
        ["Last checked", `<time datetime="${e.source_checked}">${longDate(e.source_checked)}</time>`],
        ["Source read", null],
      ];
      if (has(e, "verification")) expected.push(["How it was checked", escHtml(e.verification)]);
      if (has(e, "licence")) expected.push(["Licence", escHtml(e.licence)]);
      assert.deepEqual(rows.map(([label]) => label), expected.map(([label]) => label), `${e.id} shows only the fields it has`);
      for (const [i, [, value]] of expected.entries()) if (value !== null) assert.equal(rows[i][1], value, `${e.id} ${expected[i][0]}`);
      assert.match(rows[1][1], new RegExp(`^<a href="${escHtml(e.source_url).replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}">`), `${e.id} source link`);
      assert.doesNotMatch(block[1], /\bunknown\b/i, `${e.id} never fills a gap`);
      for (const [label, value] of rows) assert.doesNotMatch(value, /^\s*(n\/a|none|not recorded|-)?\s*$/i, `${e.id} ${label} has a value`);
      // The Markdown copy lists the same fields.
      const md = await readFile(path.join(DIST, "tools", `${e.id}.md`), "utf8");
      const section = /\n## What we checked\n\n((?:- .*\n)+)/.exec(md);
      assert.ok(section, `${e.id}.md has a What we checked list`);
      const lines = section[1].trim().split("\n");
      const want = [`- Last checked: ${longDate(e.source_checked)}`, `- Source read: ${e.source_url}`];
      if (has(e, "verification")) want.push(`- How it was checked: ${e.verification}`);
      if (has(e, "licence")) want.push(`- Licence: ${e.licence}`);
      assert.deepEqual(lines, want, `${e.id}.md`);
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

describe("Group guides", () => {
  test("each guide in guides.json renders on its group page and in its Markdown copy, with working entry links", async () => {
    const data = JSON.parse(await readFile(path.join(ROOT, "guides.json"), "utf8"));
    const names = Object.keys(data.groups || {});
    assert.ok(names.length >= 1, "at least one guide");
    for (const name of names) {
      const g = groups.find((x) => x.name === name);
      assert.ok(g, `${name} is a group`);
      const html = pages.get(`/category/${g.slug}/`);
      const guide = data.groups[name];
      assert.ok(html.includes(`<h2 id="h-guide">${escHtml(guide.title)}</h2>`), `${name} guide title`);
      const md = await readFile(path.join(DIST, "category", `${g.slug}.md`), "utf8");
      assert.ok(md.includes(`## ${guide.title}`), `${name} guide in Markdown`);
      for (const s of guide.sections) {
        assert.ok(html.includes(`<h3>${escHtml(s.heading)}</h3>`), `${name}: ${s.heading}`);
        for (const p of s.paragraphs) {
          for (const [, id] of p.matchAll(/\[\[([a-z0-9-]+)\]\]/g)) {
            const e = records.find((r) => r.id === id);
            assert.ok(html.includes(`<a href="/tools/${id}/">${escHtml(e.name)}</a>`), `${name} links ${id}`);
            assert.ok(md.includes(`](${ORIGIN}/tools/${id}/)`), `${name} Markdown links ${id}`);
          }
          assert.ok(!html.includes("[["), `${name} has no raw link markup`);
        }
        for (const u of s.sources) assert.ok(html.includes(`href="${escHtml(u)}" rel="noopener"`), `${name} cites ${u}`);
      }
    }
  });
});

describe("Comparison tables", () => {
  test("a group with two or more entries carrying specs gets one table row per such entry, with every label", () => {
    let tables = 0;
    for (const g of groups) {
      const html = pages.get(`/category/${g.slug}/`);
      const withSpecs = g.entries.filter((e) => Array.isArray(e.specs) && e.specs.length);
      if (withSpecs.length < 2) {
        assert.ok(!html.includes('class="compare-table"'), `${g.name} has no comparison table`);
        continue;
      }
      tables += 1;
      const table = /<table class="compare-table">([\s\S]*?)<\/table>/.exec(html);
      assert.ok(table, `${g.name} has a comparison table`);
      const rows = [...table[1].matchAll(/<tr><th scope="row"><a href="#([^"]+)">/g)].map((m) => m[1]);
      assert.deepEqual(rows, withSpecs.map((e) => e.id), `${g.name} rows follow the entries`);
      for (const e of withSpecs) {
        for (const [label, value] of e.specs) {
          assert.ok(table[1].includes(`<th scope="col">${escHtml(label)}</th>`), `${g.name} has a ${label} column`);
          assert.ok(table[1].includes(`<td>${escHtml(value)}</td>`), `${e.id} shows ${label}`);
        }
        assert.ok(html.includes(`id="${e.id}"`), `${e.id} row links to its card`);
      }
    }
    assert.ok(tables >= 1, "at least one group has a comparison table");
  });

  test("the group's Markdown copy carries the same table", async () => {
    for (const g of groups) {
      const withSpecs = g.entries.filter((e) => Array.isArray(e.specs) && e.specs.length);
      const md = await readFile(path.join(DIST, "category", `${g.slug}.md`), "utf8");
      assert.equal(md.includes("## Compare "), withSpecs.length >= 2, `${g.name} Markdown table`);
      for (const e of withSpecs.length >= 2 ? withSpecs : []) assert.ok(md.includes(`| [${e.name}](`), `${e.id} in Markdown table`);
    }
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
    // The What's new twin and the feed are exact paths, so they can set their own type.
    const newMd = headersFor("/new.md");
    assert.deepEqual(newMd.find(([k]) => k === "Link"), ["Link", `<${ORIGIN}/new/>; rel="canonical"`]);
    assert.deepEqual(newMd.find(([k]) => k === "Content-Type"), ["Content-Type", "text/markdown; charset=utf-8"]);
    // Build pages: the Markdown twin points back at its page, and the data can be read from anywhere.
    const b = buildGroups[0];
    const buildMd = headersFor(`/builds/${b.id}.md`);
    assert.deepEqual(buildMd.find(([k]) => k === "Link"), ["Link", `<${ORIGIN}/builds/${b.id}/>; rel="canonical"`]);
    assert.equal(buildMd.find(([k]) => k === "Content-Type"), undefined);
    assert.deepEqual(headersFor(`/builds/${b.id}.json`).find(([k]) => k === "Access-Control-Allow-Origin"), ["Access-Control-Allow-Origin", "*"]);
    assert.equal(headersFor(`/builds/${b.id}/`).find(([k]) => k === "Link"), undefined);
    const feed = headersFor("/feed.xml");
    assert.deepEqual(feed.find(([k]) => k === "Content-Type"), ["Content-Type", "application/atom+xml; charset=utf-8"]);
    assert.deepEqual(feed.find(([k]) => k === "Cache-Control"), ["Cache-Control", "public, max-age=3600"]);
  });

  test("no en or em dashes in the built pages", async () => {
    const data = await readFile(path.join(ROOT, "resources.json"), "utf8");
    if (/[\u2013\u2014]/.test(data)) return; // entry text is quoted as written
    for (const [p, html] of pages) assert.doesNotMatch(html, /[\u2013\u2014]|&[mn]dash;|&#x?(?:8211|8212|2013|2014);/i, p);
    for (const e of records) assert.doesNotMatch(await readFile(path.join(DIST, "tools", `${e.id}.md`), "utf8"), /[\u2013\u2014]/);
    for (const file of ["new.md", "feed.xml", "index.md"]) {
      assert.doesNotMatch(await readFile(path.join(DIST, file), "utf8"), /[\u2013\u2014]|&[mn]dash;|&#x?(?:8211|8212|2013|2014);/i, file);
    }
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

// What's new, the feed and the added dates ---------------------------------------------------

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const longDate = (iso) => {
  const [y, m, d] = iso.split("-").map(Number);
  return `${d} ${MONTHS[m - 1]} ${y}`;
};
const FEED_LINK = '<link rel="alternate" type="application/atom+xml" title="New on Gearlist" href="/feed.xml">';
const ATOM = "http://www.w3.org/2005/Atom";

// The days after EARLIEST_ADDED, newest first, each with its entries in list order (groups in
// first-appearance order, entries in file order).
function laterDays() {
  const days = new Map();
  for (const e of groups.flatMap((g) => g.entries)) {
    if (e.added === EARLIEST_ADDED) continue;
    if (!days.has(e.added)) days.set(e.added, []);
    days.get(e.added).push(e);
  }
  return [...days].sort((a, b) => (a[0] < b[0] ? 1 : -1));
}

// A small XML reader for the feed. It accepts the XML declaration, elements, attributes in
// double quotes, character data and the five named or numeric entity references, and fails on
// anything else, an unclosed or mismatched tag, or a second root element.
function parseXml(text) {
  const declaration = '<?xml version="1.0" encoding="utf-8"?>';
  assert.ok(text.startsWith(declaration + "\n"), "starts with the XML declaration");
  const NAMED = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'" };
  const decode = (raw) => {
    assert.doesNotMatch(raw.replace(/&(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);/g, ""), /[&<]/, `character data: ${raw}`);
    return raw.replace(/&(amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);/g, (_, ref) =>
      NAMED[ref] ?? String.fromCodePoint(ref[1] === "x" ? parseInt(ref.slice(2), 16) : Number(ref.slice(1))));
  };
  const TOKEN = /<(\/?)([A-Za-z_][\w.:-]*)((?:\s+[A-Za-z_][\w.:-]*="[^"<]*")*)\s*(\/?)>|([^<]+)/y;
  const doc = { name: "#document", children: [] };
  const stack = [doc];
  TOKEN.lastIndex = declaration.length;
  while (TOKEN.lastIndex < text.length) {
    const at = TOKEN.lastIndex;
    const m = TOKEN.exec(text);
    assert.ok(m, `well-formed XML at offset ${at}: ${text.slice(at, at + 40)}`);
    const top = stack.at(-1);
    if (m[5] !== undefined) {
      if (stack.length === 1) assert.match(m[5], /^\s*$/, "only white space outside the root element");
      else top.text += decode(m[5]);
      continue;
    }
    const [, close, name, rawAttrs, selfClose] = m;
    if (close) {
      assert.ok(!rawAttrs.trim() && !selfClose, `</${name}> is a plain end tag`);
      assert.equal(name, top.name, `</${name}> closes <${top.name}>`);
      stack.pop();
      continue;
    }
    const attrs = {};
    for (const [, key, value] of rawAttrs.matchAll(/([A-Za-z_][\w.:-]*)="([^"]*)"/g)) {
      assert.ok(!(key in attrs), `<${name}> repeats ${key}`);
      attrs[key] = decode(value);
    }
    const node = { name, attrs, children: [], text: "" };
    top.children.push(node);
    if (stack.length === 1) assert.equal(doc.children.length, 1, "one root element");
    if (!selfClose) stack.push(node);
  }
  assert.equal(stack.length, 1, `<${stack.at(-1).name}> is never closed`);
  return doc.children[0];
}
const kids = (node, name) => node.children.filter((c) => c.name === name);
const kid = (node, name) => kids(node, name)[0];

// Build pages --------------------------------------------------------------------------------

// A$8,630 for whole dollars, A$338.50 otherwise. Takes cents, so sums stay exact.
const money = (cents) => {
  const dollars = Math.floor(cents / 100);
  const rest = cents % 100;
  return `A$${dollars.toLocaleString("en-AU")}` + (rest ? `.${String(rest).padStart(2, "0")}` : "");
};
const cents = (amount) => Math.round(amount * 100);
const fill = (template, values) => template.replace(/\{(\w+)\}/g, (_, name) => values[name]);
const mainOf = (html) => html.slice(html.indexOf("<main"), html.indexOf("</main>"));

describe("Build pages", () => {
  const each = (fn) => async () => {
    assert.ok(buildGroups.length >= 1, "at least one build group");
    for (const b of buildGroups) {
      const html = pages.get(`/builds/${b.id}/`);
      const md = await readFile(path.join(DIST, "builds", `${b.id}.md`), "utf8");
      const rows = new Map(b.data.pricebook.map((r) => [r.id, r]));
      const shown = b.data.builds.filter((x) => !(x.id in (b.withheld || {})));
      await fn({ b, html, main: mainOf(html), md, rows, shown, page: b.page, data: b.data });
    }
  };

  test("each group has one page, one Markdown copy and one data file, and there are no others", async () => {
    const listing = await readdir(path.join(DIST, "builds"), { withFileTypes: true });
    const ids = buildGroups.map((b) => b.id).sort();
    assert.deepEqual(listing.filter((d) => d.isDirectory()).map((d) => d.name).sort(), ids);
    assert.deepEqual(listing.filter((d) => d.isFile()).map((d) => d.name).sort(), ids.flatMap((id) => [`${id}.json`, `${id}.md`]).sort());
    for (const id of ids) assert.match(id, /^[a-z0-9]+(-[a-z0-9]+)*$/);
  });

  test("the page opens with the title, the introduction and the date prices were read", each(({ b, html, main, md, page, data }) => {
    assert.ok(main.includes(`<h1>${escHtml(data.title)}</h1>`), "h1");
    assert.ok(main.includes(`<p class="lede">${escHtml(data.introduction)}</p>`), "introduction");
    const date = longDate(data.source_checked);
    assert.ok(main.includes(`<p class="when">${escHtml(fill(page.checked_line, { date }))}</p>`), "checked line");
    assert.ok(main.includes(`<p>${escHtml(fill(page.read_line, { date }))}</p>`), "read line");
    // What is left out and what is unverified are carried by the notes, which another test checks are printed as written.
    assert.match(fill(page.read_line, { date }), /each retailer's page/);
    assert.ok(html.includes(`<link rel="alternate" type="text/markdown" href="/builds/${b.id}.md"`));
    assert.ok(html.includes(`<link rel="alternate" type="application/json" href="/builds/${b.id}.json"`));
    assert.match(md, new RegExp(`^url: "${ORIGIN}/builds/${b.id}/"$`, "m"));
    assert.match(md, new RegExp(`^data: "${ORIGIN}/builds/${b.id}.json"$`, "m"));
    assert.ok(md.includes(`\n# ${data.title}\n`));
    assert.ok(md.includes(fill(page.read_line, { date })));
    const crumbs = graphNodes(jsonLd(html)).find((n) => n["@type"] === "BreadcrumbList");
    assert.deepEqual(crumbs.itemListElement.map((i) => [i.name, i.item]), [
      ["Gearlist", ORIGIN + "/"],
      [b.group, `${ORIGIN}/category/${slug(b.group)}/`],
      [data.title, `${ORIGIN}/builds/${b.id}/`],
    ]);
  }));

  test("every total in the data equals the sum of its parts, and the page shows that sum", each(({ main, md, rows, shown, data }) => {
    for (const x of data.builds) {
      const sum = x.parts.reduce((n, p) => n + cents(rows.get(p.id).price_aud) * p.quantity, 0);
      assert.equal(cents(x.total_aud), sum, `${x.id} total`);
    }
    assert.ok(shown.length >= 1);
    const table = /<table class="compare-table builds-table">([\s\S]*?)<\/table>/.exec(main)[1];
    const listed = [...table.matchAll(/<tr><th scope="row"><a href="#build-([^"]+)">([^<]+)<\/a>[\s\S]*?<td class="num">([^<]+)<\/td>/g)];
    assert.deepEqual(listed.map((m) => m[1]), shown.map((x) => x.id), "one row per build, in the data's order");
    for (const [i, x] of shown.entries()) {
      assert.equal(unescape(listed[i][2]), x.name);
      assert.equal(listed[i][3], money(cents(x.total_aud)), `${x.id} total on the page`);
      assert.ok(table.includes(`<td class="prose">${escHtml(x.main_tradeoff)}</td><td class="prose">${escHtml(x.upgrade_path)}</td>`), `${x.id} trade-off and upgrade path`);
      assert.ok(md.includes(`| ${money(cents(x.total_aud))} |`), `${x.id} total in Markdown`);
    }
  }));

  test("a build on the page uses only listings that can count towards a total, and withheld builds stay off it", each(({ b, main, md, rows, shown, data, page }) => {
    for (const x of shown) {
      for (const p of x.parts) {
        const row = rows.get(p.id);
        assert.equal(row.usable_in_component_total, true, `${x.id} uses ${p.id}`);
        assert.equal(row.stock_status, "in_stock", `${x.id} uses ${p.id}`);
      }
    }
    const held = data.builds.filter((x) => x.id in (b.withheld || {}));
    for (const x of held) {
      assert.ok(!main.includes(`id="build-${x.id}"`), `${x.id} has no parts table`);
      assert.ok(!main.includes(`href="#build-${x.id}"`), `${x.id} is not in the comparison`);
      if (!shown.some((s) => s.total_aud === x.total_aud)) {
        assert.ok(!main.includes(`>${money(cents(x.total_aud))}<`), `${x.id} total is not shown`);
        assert.ok(!md.includes(`| ${money(cents(x.total_aud))} |`), `${x.id} total is not in Markdown`);
      }
    }
    const note = fill(page.withheld_note, { names: held.map((x) => x.name).join("; ") });
    assert.equal(main.includes(escHtml(note)), held.length > 0, "the withheld builds are named, with no total");
    assert.ok(shown.some((x) => x.id === data.default_build), "the default build is on the page");
  }));

  test("the default build is marked in words, in the comparison and on its parts table", each(({ main, md, shown, data, page }) => {
    const mark = `<span class="pick">${escHtml(page.default_label)}</span>`;
    assert.equal(main.split(mark).length - 1, 2, "marked twice");
    const x = shown.find((s) => s.id === data.default_build);
    assert.ok(main.includes(`<a href="#build-${x.id}">${escHtml(x.name)}</a> ${mark}</th>`));
    assert.ok(new RegExp(`<details class="build" id="build-${x.id}" open>\\s*<summary><h3 id="h-build-${x.id}">[^<]+</h3> ${mark.replace(/[.*+?^${}()|[\]\\/]/g, "\\$&")}</summary>`).test(main));
    assert.equal((main.match(/<details class="build" id="build-[^"]+" open>/g) || []).length, 1, "only the default build starts open");
    assert.ok(md.includes(`| ${x.name} (${page.default_label}) |`));
  }));

  test("each build has a parts table with every part, its retailer, price, stock and listing link", each(({ b, main, rows, shown, page }) => {
    for (const x of shown) {
      const block = new RegExp(`<details class="build" id="build-${x.id}"[\\s\\S]*?</details>`).exec(main);
      assert.ok(block, `${x.id} parts table`);
      const summary = fill(page.build_summary, { name: x.name, total: money(cents(x.total_aud)) });
      assert.ok(block[0].includes(`<h3 id="h-build-${x.id}">${escHtml(summary)}</h3>`), `${x.id} heading`);
      const trs = [...block[0].matchAll(/<tr><th scope="row">([^<]*)<\/th><td[^>]*>([\s\S]*?)<\/tr>/g)];
      assert.equal(trs.length, x.parts.length + 1, `${x.id} has one row per part and a total row`);
      let sum = 0;
      for (const [i, p] of x.parts.entries()) {
        const row = rows.get(p.id);
        const tr = trs[i][0];
        const line = cents(row.price_aud) * p.quantity;
        sum += line;
        assert.equal(unescape(trs[i][1]), b.roles[p.id], `${x.id} ${p.id} role`);
        assert.ok(tr.includes(escHtml(row.part)), `${x.id} ${p.id} product`);
        assert.ok(tr.includes(`<small>${escHtml(fill(page.sku, { sku: row.sku }))}</small>`), `${x.id} ${p.id} SKU`);
        assert.ok(tr.includes(`<td>${escHtml(row.retailer)}</td><td class="num">${money(line)}`), `${x.id} ${p.id} retailer and price`);
        assert.ok(tr.includes(`<td class="prose">${escHtml(row.stock)}`), `${x.id} ${p.id} stock`);
        if (row.conditions) assert.ok(tr.includes(`<small>${escHtml(row.conditions)}</small>`), `${x.id} ${p.id} conditions`);
        assert.ok(tr.includes(`<a href="${escHtml(row.source)}" rel="noopener"`), `${x.id} ${p.id} listing link`);
        if (p.quantity > 1) {
          assert.ok(tr.includes(`<small>${escHtml(fill(page.each, { quantity: p.quantity, price: money(cents(row.price_aud)) }))}</small>`), `${x.id} ${p.id} unit price`);
        }
      }
      assert.ok(trs.at(-1)[0].includes(`<td class="num">${money(sum)}</td>`), `${x.id} total row is the sum of the rows above it`);
      assert.equal(sum, cents(x.total_aud));
    }
  }));

  test("the same part at different shops shows every price, and names the cheapest in-stock one in words", each(({ main, md, data, page }) => {
    const section = /<section class="compare" aria-labelledby="h-shops">([\s\S]*?)<\/section>/.exec(main);
    const bySku = new Map();
    for (const r of data.pricebook) bySku.set(r.sku, [...(bySku.get(r.sku) || []), r]);
    const multi = [...bySku.values()].filter((rs) => new Set(rs.map((r) => r.retailer)).size > 1);
    assert.equal(Boolean(section), multi.length > 0);
    if (!section) return;
    const trs = [...section[1].matchAll(/<tr><th scope="row">[\s\S]*?<\/tr>/g)].map((m) => m[0]);
    assert.equal(trs.length, multi.reduce((n, rs) => n + rs.length, 0), "one row per listing of a part sold at more than one shop");
    const buyable = (r) => r.usable_in_component_total === true && r.stock_status === "in_stock";
    for (const rs of multi) {
      const prices = rs.filter(buyable).map((r) => cents(r.price_aud));
      const low = Math.min(...prices);
      for (const r of rs) {
        const tr = trs.find((t) => t.includes(`href="${escHtml(r.source)}"`));
        assert.ok(tr, `${r.id} is in the table`);
        const price = cents(r.price_aud);
        let note;
        if (!buyable(r)) note = page.not_compared[r.stock_status];
        else if (price === low) note = prices.filter((p) => p === low).length === 1 ? page.lowest : page.equal_lowest;
        else note = fill(page.more, { amount: money(price - low) });
        assert.ok(tr.includes(`<td>${escHtml(r.retailer)}</td><td class="num">${money(price)}</td><td><strong>${escHtml(note)}</strong></td>`), `${r.id}: ${note}`);
        assert.ok(md.includes(`| ${r.retailer} | ${money(price)} | ${note} |`), `${r.id} in Markdown`);
      }
    }
    // An out-of-stock listing is never the lowest, even when its price is.
    for (const tr of trs.filter((t) => t.includes(`<strong>${escHtml(page.lowest)}</strong>`) || t.includes(`<strong>${escHtml(page.equal_lowest)}</strong>`))) {
      const r = data.pricebook.find((x) => tr.includes(`href="${escHtml(x.source)}"`));
      assert.ok(buyable(r), `${r.id} is marked lowest`);
    }
  }));

  test("the full pricebook is listed, one row per retailer listing", each(({ main, md, data }) => {
    const section = /<section class="compare" aria-labelledby="h-pricebook">([\s\S]*?)<\/section>/.exec(main)[1];
    const trs = [...section.matchAll(/<tr><th scope="row">[\s\S]*?<\/tr>/g)].map((m) => m[0]);
    assert.equal(trs.length, data.pricebook.length);
    for (const [i, r] of data.pricebook.entries()) {
      assert.ok(trs[i].includes(escHtml(r.part)) && trs[i].includes(`<td>${escHtml(r.retailer)}</td><td class="num">${money(cents(r.price_aud))}</td>`), r.id);
      assert.ok(trs[i].includes(`<td class="prose">${escHtml(r.stock)}`), `${r.id} stock`);
      assert.ok(trs[i].includes(`href="${escHtml(r.source)}"`), `${r.id} link`);
      assert.ok(md.includes(`](${r.source})`), `${r.id} link in Markdown`);
    }
  }));

  test("the model table shows each model's size, use, 32GB fit and link", each(({ b, main, md, data }) => {
    const section = /<section class="compare" aria-labelledby="h-models">([\s\S]*?)<\/section>/.exec(main)[1];
    for (const m of data.models) {
      const size = `${m.size_gb}GB`;
      assert.ok(section.includes(`<a href="${escHtml(m.url)}" rel="noopener"><code>${escHtml(m.tag)}</code></a>`), `${m.tag} link`);
      assert.ok(section.includes(`<td class="num">${size}</td><td class="prose">${escHtml(m.purpose)}</td><td class="prose">${escHtml(m.fit)}</td>`), `${m.tag} row`);
      assert.ok(md.includes(`](${m.url})`) && md.includes(`| ${size} |`), `${m.tag} in Markdown`);
      const entry = (b.model_entries || {})[m.tag];
      if (entry) assert.ok(section.includes(`<a href="/tools/${entry}/">`), `${m.tag} links its Gearlist entry`);
    }
  }));

  test("the notes are printed as written, on the page and in the Markdown copy", each(({ main, md, data }) => {
    const mdText = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/([\\`*_\[\]|#~!@])/g, "\\$1");
    for (const key of ["totals_exclude", "unverified", "capacity_note", "stock_note", "memory_note", "model_license_note", "evaluation_note", "selection_note"]) {
      assert.ok(main.includes(`>${escHtml(data[key])}</p>`), `${key} on the page`);
      assert.ok(md.includes(`\n${mdText(data[key])}\n`), `${key} in Markdown`);
    }
    for (const s of data.technical_sources) {
      assert.ok(main.includes(`<li><a href="${escHtml(s.url)}" rel="noopener">${escHtml(s.topic)}</a></li>`), s.topic);
      assert.ok(md.includes(`](${s.url})`), `${s.topic} in Markdown`);
    }
  }));

  test("listing fields kept for the record are not shown on the page or in the Markdown copy", each(({ main, md, data }) => {
    for (const r of data.pricebook) {
      for (const key of ["verification", "access_notes", "tax_basis"]) {
        assert.ok(r[key], `${r.id} has ${key} in the data`);
        assert.ok(!main.includes(escHtml(r[key])), `${r.id} ${key} is not on the page`);
        assert.ok(!md.includes(r[key]), `${r.id} ${key} is not in Markdown`);
      }
    }
  }));

  test("a part that has a Gearlist entry links its name to that entry's page", each(({ b, main, md, rows, shown }) => {
    const links = Object.entries(b.entries || {});
    assert.ok(links.length >= 1, "at least one part has an entry");
    for (const [rowId, entryId] of links) {
      assert.ok(records.some((e) => e.id === entryId), `${entryId} is an entry`);
      const row = rows.get(rowId);
      assert.ok(main.includes(`<a href="/tools/${entryId}/">${escHtml(row.part)}</a>`), `${rowId} links ${entryId}`);
      assert.ok(md.includes(`](${ORIGIN}/tools/${entryId}/)`), `${rowId} in Markdown`);
    }
    // In the comparison table, a build with a dedicated graphics card names it and links it.
    for (const x of shown.filter((s) => s.dedicated_gpu_included)) {
      const card = x.parts.map((p) => p.id).find((id) => b.roles[id] === "Graphics card");
      const tr = new RegExp(`<tr><th scope="row"><a href="#build-${x.id}">[\\s\\S]*?</tr>`).exec(main)[0];
      assert.ok(tr.includes(escHtml(rows.get(card).part)), `${x.id} names its card`);
      if (b.entries[card]) assert.ok(tr.includes(`href="/tools/${b.entries[card]}/"`), `${x.id} links its card`);
    }
  }));

  test("every table sits in the scrolling frame used for wide tables, and the page adds no script", each(({ html, main }) => {
    const tables = (main.match(/<table /g) || []).length;
    assert.ok(tables >= 4);
    assert.equal((main.match(/<div class="compare-wrap" tabindex="0" role="region" aria-labelledby="[^"]+">\n<table class="compare-table/g) || []).length, tables);
    // A visually hidden span inside a scrolling frame widens the whole page on a phone.
    for (const [frame] of main.matchAll(/<div class="compare-wrap"[\s\S]*?<\/table>\n<\/div>/g)) assert.ok(!frame.includes('class="sr"'));
    assert.equal((main.match(/<script/g) || []).length, 0);
    assert.doesNotMatch(main, / on[a-z]+="/, "no inline event handlers");
    const scripts = (page) => [...page.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
    assert.deepEqual(scripts(html), scripts(pages.get("/new/")), "the same inline scripts as every other page");
    assert.doesNotMatch(html, /<script[^>]+src=/);
  }));

  test("outside links are plain https with no query string, so no affiliate parameters", each(({ main, md }) => {
    const hrefs = [...main.matchAll(/<a href="([^"]+)"/g)].map((m) => unescape(m[1]));
    const outside = hrefs.filter((h) => !h.startsWith("/") && !h.startsWith("#"));
    assert.ok(outside.length >= 10);
    for (const h of outside) {
      assert.match(h, /^https:\/\/[a-z0-9.-]+\//, h);
      assert.doesNotMatch(h, /[?#]/, h);
    }
    for (const [, h] of md.matchAll(/\]\((https:[^)]+)\)/g)) assert.doesNotMatch(h, /[?#]/, h);
    assert.doesNotMatch(main + md, /JW Computers|jw\.com\.au|Computer Alliance|computeralliance|RamCity|ramcity/i);
  }));

  test("the data file is the group as it stands in builds.json, with the page addresses", each(async ({ b }) => {
    const served = JSON.parse(await readFile(path.join(DIST, "builds", `${b.id}.json`), "utf8"));
    const { url, markdown, ...rest } = served;
    assert.equal(url, `${ORIGIN}/builds/${b.id}/`);
    assert.equal(markdown, `${ORIGIN}/builds/${b.id}.md`);
    assert.deepEqual(rest, b);
    assert.ok(!JSON.stringify(served).includes("sha256"), "no capture hashes");
  }));

  test("the group page, its Markdown copy, llms.txt and the sitemap all point at the build page", each(async ({ b, data, page }) => {
    const date = longDate(data.source_checked);
    const [before, after] = fill(page.group_link, { date, link: "\u0000" }).split("\u0000");
    const g = groups.find((x) => x.name === b.group);
    const groupHtml = pages.get(`/category/${g.slug}/`);
    assert.ok(groupHtml.includes(`<p class="when">${escHtml(before)}<a href="/builds/${b.id}/">${escHtml(data.title)}</a>${escHtml(after)}</p>`), "one sentence on the group page");
    const groupMd = await readFile(path.join(DIST, "category", `${g.slug}.md`), "utf8");
    assert.ok(groupMd.includes(`[${data.title}](${ORIGIN}/builds/${b.id}/)`), "group Markdown");
    for (const other of groups.filter((x) => x !== g)) assert.ok(!pages.get(`/category/${other.slug}/`).includes(`/builds/${b.id}/`), `${other.name} does not link it`);
    const llms = await readFile(path.join(DIST, "llms.txt"), "utf8");
    assert.ok(llms.includes(`- [${data.title}](${ORIGIN}/builds/${b.id}.md): ${fill(page.llms_line, { date })} Web page: ${ORIGIN}/builds/${b.id}/ Data: ${ORIGIN}/builds/${b.id}.json`), "llms.txt");
    const xml = await readFile(path.join(DIST, "sitemap-pages.xml"), "utf8");
    assert.ok(xml.includes(`<url><loc>${ORIGIN}/builds/${b.id}/</loc><lastmod>${data.source_checked}</lastmod></url>`), "sitemap");
  }));

  test("no en or em dashes in the build page, its Markdown copy or its data", each(async ({ b, md }) => {
    assert.doesNotMatch(md, /[\u2013\u2014]/);
    assert.doesNotMatch(await readFile(path.join(DIST, "builds", `${b.id}.json`), "utf8"), /[\u2013\u2014]/);
  }));
});

describe("What's new, the feed and added dates", () => {
  test("every entry has an added date from the earliest date to the list's updated date", async () => {
    const updated = JSON.parse(await readFile(path.join(ROOT, "resources.json"), "utf8")).updated;
    for (const e of records) {
      assert.match(e.added, /^\d{4}-\d{2}-\d{2}$/, e.id);
      assert.ok(e.added >= EARLIEST_ADDED && e.added <= updated, `${e.id} added ${e.added}`);
    }
    assert.ok(records.some((e) => e.added === EARLIEST_ADDED), "some entries carry the earliest date");
  });

  test("the What's new page lists every later entry under its day, newest first", () => {
    const html = pages.get("/new/");
    const days = laterDays();
    const sections = [...html.matchAll(/<section class="day" id="added-([0-9-]+)" aria-labelledby="h-added-\1">([\s\S]*?)<\/section>/g)];
    assert.deepEqual(sections.map((m) => m[1]), [...days.map(([day]) => day), EARLIEST_ADDED]);
    for (const [i, [day, members]] of days.entries()) {
      const body = sections[i][2];
      const n = members.length;
      assert.ok(body.includes(`<time datetime="${day}">${longDate(day)}</time> <span class="day-n">${n} ${n === 1 ? "entry" : "entries"}</span></h2>`), day);
      assert.deepEqual([...body.matchAll(/href="\/tools\/([^/"]+)\/"/g)].map((m) => m[1]), members.map((e) => e.id), `${day} lists its entries in list order`);
      for (const e of members) {
        assert.ok(body.includes(`<b>${escHtml(e.name)}</b><span>${escHtml(e.description)}</span><small>${escHtml(e.category)}</small>`), `${e.id} card shows its description and group`);
      }
    }
    // The earliest day is one line with a count and a link to the full list.
    const first = records.filter((e) => e.added === EARLIEST_ADDED);
    const last = sections.at(-1)[2];
    assert.ok(last.includes(`On or before <time datetime="${EARLIEST_ADDED}">${longDate(EARLIEST_ADDED)}</time></h2>`));
    assert.ok(last.includes(`<p>${first.length} entries were added on or before ${longDate(EARLIEST_ADDED)}, the earliest date Gearlist records. <a href="/#catalog">See every entry in the full list</a>.</p>`));
    assert.doesNotMatch(last, /\/tools\//, "the earliest entries are not listed one by one");
    for (const e of first) assert.ok(!html.includes(`href="/tools/${e.id}/"`), `${e.id} is not listed`);
    const later = days.reduce((n, [, m]) => n + m.length, 0);
    assert.ok(html.includes(`<p class="when">${later} entries added after ${longDate(EARLIEST_ADDED)}. Latest addition ${longDate(days[0][0])}.</p>`));
    assert.ok(html.includes('<h1>What\'s new</h1>'));
    assert.ok(html.includes('The Atom feed is at <a href="/feed.xml">gearlist.build/feed.xml</a>.'));
  });

  test("the What's new Markdown twin lists the same entries under the same days", async () => {
    const md = await readFile(path.join(DIST, "new.md"), "utf8");
    assert.match(md, new RegExp(`^url: "${ORIGIN}/new/"$`, "m"));
    assert.match(md, new RegExp(`^feed: "${ORIGIN}/feed.xml"$`, "m"));
    assert.match(md, /Documentation checked means the source was read/);
    const days = laterDays();
    const headings = [...md.matchAll(/^## (.+)$/gm)].map((m) => m[1]);
    assert.deepEqual(headings, [...days.map(([day]) => longDate(day)), `On or before ${longDate(EARLIEST_ADDED)}`]);
    const parts = md.split(/^## .+$/m).slice(1);
    for (const [i, [, members]] of days.entries()) {
      const bullets = [...parts[i].matchAll(/^- \[(.+?)\]\(https:\/\/gearlist\.build\/tools\/([^/]+)\/\): (.*)$/gm)];
      assert.deepEqual(bullets.map((m) => m[2]), members.map((e) => e.id));
      for (const [j, e] of members.entries()) {
        assert.equal(bullets[j][1], e.name);
        assert.ok(bullets[j][3].includes(e.description.replace(/\.$/, "")), `${e.id} description`);
        assert.ok(bullets[j][3].includes(`Group: ${e.category}. Markdown: ${ORIGIN}/tools/${e.id}.md`), `${e.id} group`);
      }
    }
    const first = records.filter((e) => e.added === EARLIEST_ADDED).length;
    assert.ok(parts.at(-1).includes(`${first} entries were added on or before ${longDate(EARLIEST_ADDED)}, the earliest date Gearlist records.`));
    assert.doesNotMatch(parts.at(-1), /\/tools\//);
  });

  test("feed.xml is well-formed Atom with the 50 most recent additions, newest first", async () => {
    const feed = parseXml(await readFile(path.join(DIST, "feed.xml"), "utf8"));
    assert.equal(feed.name, "feed");
    assert.equal(feed.attrs.xmlns, ATOM);
    assert.equal(kid(feed, "title").text, "New on Gearlist");
    assert.match(kid(feed, "subtitle").text, /Documentation checked means the source was read\./);
    const links = kids(feed, "link").map((l) => [l.attrs.rel, l.attrs.type, l.attrs.href]);
    assert.deepEqual(links, [["self", "application/atom+xml", `${ORIGIN}/feed.xml`], ["alternate", "text/html", `${ORIGIN}/new/`]]);
    assert.ok(kid(feed, "id").text);
    assert.equal(kid(kid(feed, "author"), "name").text, "Tech Horizon Labs");
    const expected = laterDays().flatMap(([, members]) => members).slice(0, 50);
    const entries = kids(feed, "entry");
    assert.ok(entries.length <= 50, "50 entries at most");
    assert.equal(entries.length, expected.length);
    const ids = new Set();
    let previous = "9999";
    for (const [i, node] of entries.entries()) {
      const e = expected[i];
      assert.equal(kid(node, "title").text, e.name);
      const link = kid(node, "link");
      assert.deepEqual([link.attrs.rel, link.attrs.href], ["alternate", `${ORIGIN}/tools/${e.id}/`]);
      const id = kid(node, "id").text;
      assert.equal(id, `tag:gearlist.build,2026:tools/${e.id}`, "a stable id per entry");
      assert.ok(!ids.has(id));
      ids.add(id);
      const updated = kid(node, "updated").text;
      assert.equal(updated, `${e.added}T00:00:00Z`);
      assert.ok(updated <= previous, "newest first");
      previous = updated;
      assert.equal(kid(node, "summary").text, e.description);
      assert.equal(kid(node, "category").attrs.term, e.category);
      assert.notEqual(e.added, EARLIEST_ADDED);
    }
    assert.equal(kid(feed, "updated").text, kid(entries[0], "updated").text);
  });

  test("the home page and the What's new page link the feed in their heads", () => {
    for (const [p, html] of pages) {
      const head = html.slice(0, html.indexOf("</head>"));
      assert.equal(head.includes(FEED_LINK), p === "/" || p === "/new/", p);
    }
  });

  test("the home page links What's new beside the entry count, and every footer links it", () => {
    assert.match(pages.get("/"), /<p class="facts">\d+ entries in \d+ groups\. Updated \d{1,2} [A-Z][a-z]+ \d{4}\. <a href="\/new\/">See what's new<\/a>\.<\/p>/);
    for (const [p, html] of pages) {
      const footer = /<footer[\s\S]*?<\/footer>/.exec(html);
      assert.ok(footer, `${p} has a footer`);
      assert.match(footer[0], /<a href="\/new\/"(?: aria-current="page")?>What's new<\/a>/, `${p} footer links What's new`);
    }
  });

  test("entry pages and their Markdown copies say when the entry was added", async () => {
    let onOrBefore = 0;
    for (const e of records) {
      const html = pages.get(`/tools/${e.id}/`);
      const block = /<section class="details" aria-labelledby="h-details">([\s\S]*?)<\/section>/.exec(html)[1];
      const rows = [...block.matchAll(/<dt>([^<]+)<\/dt><dd>([\s\S]*?)<\/dd>/g)].map((m) => [m[1], m[2]]);
      assert.deepEqual(rows.map(([label]) => label), ["Official link", "Group", "Added to Gearlist", "Gearlist id", "Markdown"], e.id);
      const link = `<a href="/new/#added-${e.added}"><time datetime="${e.added}">${longDate(e.added)}</time></a>`;
      const early = e.added === EARLIEST_ADDED;
      if (early) onOrBefore += 1;
      assert.equal(rows[2][1], early ? `on or before ${link}` : link, e.id);
      const md = await readFile(path.join(DIST, "tools", `${e.id}.md`), "utf8");
      assert.match(md, new RegExp(`^added: "${e.added}"$`, "m"));
      assert.ok(md.includes(`\n- Added to Gearlist: ${early ? "on or before " : ""}${longDate(e.added)}\n`), `${e.id}.md`);
    }
    assert.equal(onOrBefore, records.filter((e) => e.added === EARLIEST_ADDED).length);
    assert.ok(onOrBefore < records.length, "later entries show a plain date");
  });

  test("the sitemap lists What's new with its latest added date", async () => {
    const xml = await readFile(path.join(DIST, "sitemap-pages.xml"), "utf8");
    const latest = records.map((e) => e.added).sort().at(-1);
    assert.ok(xml.includes(`<url><loc>${ORIGIN}/new/</loc><lastmod>${latest}</lastmod></url>`));
  });
});

describe("MCP Registry domain proof", () => {
  test("/.well-known/mcp-registry-auth serves only the committed public key line, as plain text", async () => {
    const committed = (await readFile(path.join(SITE, "src", "mcp-registry-auth.txt"), "utf8")).trim();
    const served = await readFile(path.join(DIST, ".well-known", "mcp-registry-auth"), "utf8");
    assert.match(committed, /^v=MCPv1; k=ed25519; p=[A-Za-z0-9+/]{43}=$/);
    assert.equal(served, committed + "\n");
    assert.ok(Buffer.byteLength(served) <= 4096);
    assert.doesNotMatch(served, /PRIVATE/);
    const headers = await readFile(path.join(DIST, "_headers"), "utf8");
    assert.match(headers, /\/\.well-known\/mcp-registry-auth\n  Content-Type: text\/plain; charset=utf-8/);
  });
});
