// Tests for the Gearlist Worker, run against its fetch handler with a fake
// ASSETS binding that serves the built site/dist folder.
//
//   python3 build.py && python3 site/build_site.py && node --test site/test/
//
// node:test only. No network access.

import { test, describe, before } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, readdir, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import worker, { prefersMarkdown } from "../worker/index.mjs";
import { NOTICE } from "../worker/catalog.mjs";
import { MAX_BODY, MODERN_VERSION, SUPPORTED_VERSIONS } from "../worker/mcp.mjs";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DIST = path.join(SITE, "dist");
const ROOT = path.dirname(SITE);
const ORIGIN = "https://gearlist.build";

const TYPES = {
  ".html": "text/html", ".json": "application/json", ".txt": "text/plain", ".md": "text/markdown",
  ".xml": "application/xml", ".svg": "image/svg+xml", ".png": "image/png", ".zip": "application/zip",
};

// Parses the subset of _headers syntax the build writes: path lines, then indented "Name: value" lines.
function parseHeaders(text) {
  const rules = [];
  let current = null;
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    if (!/^\s/.test(line)) {
      current = { pattern: line.trim(), headers: [] };
      rules.push(current);
    } else if (current) {
      const i = line.indexOf(":");
      current.headers.push([line.slice(0, i).trim(), line.slice(i + 1).trim()]);
    }
  }
  return rules;
}

function matches(pattern, pathname) {
  if (pattern.startsWith("https://")) return false;
  if (pattern.endsWith("/*")) return pathname.startsWith(pattern.slice(0, -1));
  return pattern === pathname;
}

// A stand-in for env.ASSETS. Like the real binding it applies _headers rules
// to what it serves, so the tests can check the Worker keeps them.
function fakeAssets(rules) {
  const calls = [];
  return {
    calls,
    async fetch(input, init) {
      const request = input instanceof Request ? input : new Request(input, init);
      const url = new URL(request.url);
      calls.push(url.pathname);
      let file = decodeURIComponent(url.pathname);
      if (file.endsWith("/")) file += "index.html";
      const full = path.join(DIST, file);
      let body;
      let status = 200;
      try {
        if (!full.startsWith(DIST) || !(await stat(full)).isFile()) throw new Error("not a file");
        body = await readFile(full);
      } catch {
        status = 404;
        body = await readFile(path.join(DIST, "404.html"));
        file = "/404.html";
      }
      const headers = new Headers({ "Content-Type": TYPES[path.extname(file)] || "application/octet-stream" });
      headers.set("ETag", '"' + createHash("sha256").update(body).digest("hex").slice(0, 16) + '"');
      for (const rule of rules) {
        if (!matches(rule.pattern, url.pathname)) continue;
        for (const [name, value] of rule.headers) {
          if (name.toLowerCase() === "content-type" || !headers.has(name)) headers.set(name, value);
          else headers.set(name, headers.get(name) + ", " + value);
        }
      }
      const inm = request.headers.get("If-None-Match");
      if (status === 200 && inm && inm === headers.get("ETag")) return new Response(null, { status: 304, headers });
      return new Response(request.method === "HEAD" ? null : body, { status, headers });
    },
  };
}

let env;
let records;

before(async () => {
  try {
    await stat(path.join(DIST, "index.md"));
  } catch {
    throw new Error("site/dist is missing or out of date. Run python3 site/build_site.py first.");
  }
  const rules = parseHeaders(await readFile(path.join(DIST, "_headers"), "utf8"));
  env = { ASSETS: fakeAssets(rules) };
  records = JSON.parse(await readFile(path.join(DIST, "resources.json"), "utf8"));
});

function call(pathname, init = {}, testEnv = env) {
  return worker.fetch(new Request(ORIGIN + pathname, init), testEnv);
}

let nextId = 1;

// A legacy (pre 2026-07-28) request: no _meta, optional MCP-Protocol-Version header.
async function legacy(method, params, version = "2025-06-18", extra = {}) {
  const headers = { "Content-Type": "application/json", Accept: "application/json, text/event-stream", ...extra };
  if (version) headers["MCP-Protocol-Version"] = version;
  const body = { jsonrpc: "2.0", id: nextId++, method };
  if (params !== undefined) body.params = params;
  const res = await call("/mcp", { method: "POST", headers, body: JSON.stringify(body) });
  return { res, json: res.status === 202 ? null : await res.json() };
}

// A modern (2026-07-28) request with the per-request _meta and mirrored headers.
async function modern(method, params = {}, override = {}) {
  const meta = {
    "io.modelcontextprotocol/protocolVersion": MODERN_VERSION,
    "io.modelcontextprotocol/clientInfo": { name: "test", version: "1.0.0" },
    "io.modelcontextprotocol/clientCapabilities": {},
  };
  const headers = {
    "Content-Type": "application/json",
    Accept: "application/json, text/event-stream",
    "MCP-Protocol-Version": MODERN_VERSION,
    "Mcp-Method": method,
  };
  if (params.name) headers["Mcp-Name"] = params.name;
  Object.assign(headers, override.headers || {});
  for (const [k, v] of Object.entries(headers)) if (v === null) delete headers[k];
  const body = {
    jsonrpc: "2.0",
    id: nextId++,
    method,
    params: { ...params, _meta: override.meta === undefined ? meta : override.meta },
  };
  if (override.meta === null) delete body.params._meta;
  const res = await call("/mcp", { method: "POST", headers, body: JSON.stringify(body) });
  return { res, json: await res.json() };
}

async function tool(name, args) {
  const { res, json } = await legacy("tools/call", { name, arguments: args });
  assert.equal(res.status, 200);
  assert.ok(json.result, JSON.stringify(json));
  return json.result;
}

// Checks a value against the subset of JSON Schema used in the tool output schemas.
function conforms(schema, value, where = "value") {
  if (schema.type === "object") {
    assert.ok(value && typeof value === "object" && !Array.isArray(value), `${where} is an object`);
    for (const key of schema.required || []) assert.ok(key in value, `${where}.${key} is present`);
    for (const [key, sub] of Object.entries(schema.properties || {})) {
      if (key in value) conforms(sub, value[key], `${where}.${key}`);
    }
  } else if (schema.type === "array") {
    assert.ok(Array.isArray(value), `${where} is an array`);
    value.forEach((item, i) => conforms(schema.items, item, `${where}[${i}]`));
  } else if (schema.type === "integer") {
    assert.ok(Number.isInteger(value), `${where} is an integer`);
  } else if (schema.type) {
    assert.equal(typeof value, schema.type, `${where} is a ${schema.type}`);
  }
  if (schema.enum) assert.ok(schema.enum.includes(value), `${where} is one of ${schema.enum}`);
}

function assertNotice(result) {
  assert.equal(result.content[0].type, "text");
  assert.match(result.content[0].text, /documentation-checked only/);
  assert.match(result.content[0].text, /unless a human authorises it/);
}

describe("MCP lifecycle (legacy handshake)", () => {
  test("initialize echoes a supported version and describes the server", async () => {
    const { res, json } = await legacy("initialize", {
      protocolVersion: "2025-06-18",
      capabilities: {},
      clientInfo: { name: "test", version: "1" },
    }, null);
    assert.equal(res.status, 200);
    assert.equal(res.headers.get("Content-Type"), "application/json; charset=utf-8");
    assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
    assert.equal(res.headers.get("Mcp-Session-Id"), null, "stateless: no session id");
    assert.equal(json.result.protocolVersion, "2025-06-18");
    assert.deepEqual(json.result.capabilities, { tools: {} });
    assert.equal(json.result.serverInfo.name, "gearlist");
    assert.match(json.result.instructions, new RegExp(`${records.resources.length} source-checked`));
    assert.match(json.result.instructions, /not installed, tested or security audited/);
  });

  test("initialize with an unknown version offers the newest legacy version", async () => {
    const { json } = await legacy("initialize", { protocolVersion: "2024-01-01", capabilities: {} }, null);
    assert.equal(json.result.protocolVersion, "2025-11-25");
  });

  test("notifications get 202 with no body", async () => {
    const res = await call("/mcp", {
      method: "POST",
      headers: { "Content-Type": "application/json", "MCP-Protocol-Version": "2025-06-18" },
      body: JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }),
    });
    assert.equal(res.status, 202);
    assert.equal(await res.text(), "");
  });

  test("a notification with a mismatched or unsupported version is refused", async () => {
    const send = (version, meta) =>
      call("/mcp", {
        method: "POST",
        headers: { "Content-Type": "application/json", "MCP-Protocol-Version": version },
        body: JSON.stringify({
          jsonrpc: "2.0",
          method: "notifications/cancelled",
          params: { _meta: { "io.modelcontextprotocol/protocolVersion": meta } },
        }),
      });
    const mismatch = await send("2025-11-25", MODERN_VERSION);
    assert.equal(mismatch.status, 400);
    assert.equal((await mismatch.json()).error.code, -32020);
    const unknown = await send("2099-01-01", "2099-01-01");
    assert.equal(unknown.status, 400);
    assert.equal((await unknown.json()).error.code, -32022);
    assert.equal((await send(MODERN_VERSION, MODERN_VERSION)).status, 202);
  });

  test("ping returns an empty result", async () => {
    const { json } = await legacy("ping");
    assert.deepEqual(json.result, {});
  });

  test("a request without the version header is served as 2025-03-26", async () => {
    const { res, json } = await legacy("tools/list", undefined, null);
    assert.equal(res.status, 200);
    assert.equal(json.result.tools.length, 5);
  });
});

describe("tools/list", () => {
  test("lists five read-only tools in a fixed order", async () => {
    const { json } = await legacy("tools/list");
    const tools = json.result.tools;
    assert.deepEqual(tools.map((t) => t.name), ["search_gear", "get_gear", "list_categories", "list_skills", "recommend_stack"]);
    for (const t of tools) {
      assert.equal(t.annotations.readOnlyHint, true);
      assert.equal(t.annotations.destructiveHint, false);
      assert.equal(t.inputSchema.type, "object");
      assert.equal(t.outputSchema.type, "object");
      assert.ok(t.description.length > 20);
    }
    const search = tools[0].inputSchema;
    assert.deepEqual(search.required, ["query"]);
    assert.equal(search.properties.limit.maximum, 50);
    assert.equal(search.properties.limit.default, 10);
    const categories = [...new Set(records.resources.map((e) => e.category))];
    assert.deepEqual(search.properties.category.enum, categories);
    const stack = tools[4];
    assert.deepEqual(stack.inputSchema.required, ["job"]);
    assert.equal(stack.inputSchema.properties.limit.maximum, 10);
    assert.equal(stack.inputSchema.properties.limit.default, 6);
    assert.equal(stack.inputSchema.additionalProperties, false);
    assert.match(stack.description, /Matches are on words, so check each entry suits the job before suggesting it\.$/, "recommend_stack says it matches words, so the agent checks fit");
    assert.equal(json.result.resultType, undefined, "legacy results carry no modern fields");
  });

  test("a cursor is refused because there is one page", async () => {
    const { json } = await legacy("tools/list", { cursor: "abc" });
    assert.equal(json.error.code, -32602);
  });
});

describe("tools/call", () => {
  test("search_gear returns matching entries with every field and the notice", async () => {
    const list = (await legacy("tools/list")).json.result.tools;
    const result = await tool("search_gear", { query: "browser" });
    assert.equal(result.isError, false);
    assertNotice(result);
    const data = result.structuredContent;
    conforms(list[0].outputSchema, data, "search_gear");
    assert.deepEqual(JSON.parse(result.content[1].text), data, "text block is the serialised structured content");
    assert.equal(data.notice, NOTICE);
    assert.equal(data.match, "all");
    assert.ok(data.count > 0 && data.count <= 10, "default limit is 10");
    for (const e of data.results) {
      for (const key of ["id", "name", "category", "url", "description", "for_whom", "access_notes", "source_url", "source_checked"]) {
        assert.equal(typeof e[key], "string", key);
      }
      const text = [e.name, e.id, e.category, e.description, e.for_whom, e.access_notes].join(" ").toLowerCase();
      assert.ok(text.includes("browser"), `${e.id} matches the query`);
    }
  });

  test("search_gear ranks a name match first", async () => {
    const target = records.resources.find((e) => e.id === "playwright-mcp") || records.resources[0];
    const data = (await tool("search_gear", { query: target.name })).structuredContent;
    assert.equal(data.results[0].id, target.id);
  });

  test("search_gear filters by category and honours limit", async () => {
    const data = (await tool("search_gear", { query: "", category: "MCP and integrations", limit: 50 })).structuredContent;
    const expected = records.resources.filter((e) => e.category === "MCP and integrations").length;
    assert.equal(data.total_matches, expected);
    assert.equal(data.count, Math.min(50, expected));
    assert.ok(data.results.every((e) => e.category === "MCP and integrations"));
    const slugged = (await tool("search_gear", { query: "", category: "mcp-and-integrations", limit: 3 })).structuredContent;
    assert.equal(slugged.count, 3);
    assert.equal(slugged.category, "MCP and integrations");
  });

  test("search_gear falls back to partial matches", async () => {
    const data = (await tool("search_gear", { query: "browser zzqqxxnotaword" })).structuredContent;
    assert.equal(data.match, "partial");
    assert.ok(data.count > 0);
    const none = (await tool("search_gear", { query: "zzqqxxnotaword" })).structuredContent;
    assert.equal(none.match, "none");
    assert.equal(none.count, 0);
  });

  test("search_gear lists full matches before partial ones", async () => {
    const data = (await tool("search_gear", { query: "browser automation", limit: 50 })).structuredContent;
    assert.ok(data.full_matches >= 1 && data.full_matches < data.count);
    const words = (e) => [e.name, e.id, e.category, e.description, e.for_whom, e.access_notes].join(" ").toLowerCase();
    const full = data.results.slice(0, data.full_matches);
    assert.ok(full.every((e) => words(e).includes("brows") && words(e).includes("autom")));
  });

  test("search_gear ignores common words and matches word forms", async () => {
    const plain = (await tool("search_gear", { query: "send email", limit: 50 })).structuredContent;
    const chatty = (await tool("search_gear", { query: "find me a tool to send emails", limit: 50 })).structuredContent;
    assert.deepEqual(chatty.results.map((e) => e.id), plain.results.map((e) => e.id));
    const one = (await tool("search_gear", { query: "website scraper", limit: 50 })).structuredContent;
    const other = (await tool("search_gear", { query: "websites scraping", limit: 50 })).structuredContent;
    assert.deepEqual(other.results.map((e) => e.id), one.results.map((e) => e.id));
  });

  for (const [label, args, pattern] of [
    ["a limit above 50", { query: "mcp", limit: 51 }, /limit must be a whole number from 1 to 50/],
    ["a fractional limit", { query: "mcp", limit: 2.5 }, /limit must be/],
    ["a non-string query", { query: 42 }, /query must be a string/],
    ["an overlong query", { query: "x".repeat(201) }, /200 characters or fewer/],
    ["an unknown category", { query: "mcp", category: "Toasters" }, /Unknown category: Toasters\. Use one of: Agent tools/],
    ["an unknown argument", { query: "mcp", sort: "name" }, /Unknown argument: sort/],
    ["an empty query with no category", { query: "  " }, /Give a query, a category, or both/],
  ]) {
    test(`search_gear reports ${label} as a tool error`, async () => {
      const result = await tool("search_gear", args);
      assert.equal(result.isError, true);
      assert.match(result.content[0].text, pattern);
      assert.match(result.content[0].text, /documentation-checked only/);
    });
  }

  test("get_gear returns one entry", async () => {
    const list = (await legacy("tools/list")).json.result.tools;
    const want = records.resources[0];
    const result = await tool("get_gear", { id: want.id });
    assert.equal(result.isError, false);
    assertNotice(result);
    conforms(list[1].outputSchema, result.structuredContent, "get_gear");
    assert.deepEqual(result.structuredContent.entry, want);
  });

  test("get_gear shows what was checked, copied from the entry's own fields", async () => {
    const list = (await legacy("tools/list")).json.result.tools;
    for (const want of records.resources) {
      const data = (await tool("get_gear", { id: want.id })).structuredContent;
      conforms(list[1].outputSchema, data, `get_gear ${want.id}`);
      const expected = {};
      for (const key of ["source_checked", "source_url", "verification", "access_notes", "licence"]) {
        if (typeof want[key] === "string" && want[key].trim()) expected[key] = want[key];
      }
      assert.deepEqual(data.checked, expected, want.id);
      assert.deepEqual(Object.keys(data.checked), Object.keys(expected), `${want.id} keeps the field order`);
    }
  });

  test("get_gear leaves out checked fields an entry does not have and never says unknown", async () => {
    // A two-entry catalog served by its own fake ASSETS: one entry has a licence and no
    // verification, the other has an empty verification.
    const base = {
      category: "Agent tools", description: "A test entry.", for_whom: "Tests.", access_notes: "None beyond a clone.",
      source_checked: "2026-11-07", thl_project: false,
    };
    const fixture = {
      updated: "2026-11-07",
      resources: [
        { ...base, id: "with-licence", name: "With licence", url: "https://example.com/a", source_url: "https://example.com/a/docs", licence: "MIT" },
        { ...base, id: "no-check-scope", name: "No check scope", url: "https://example.com/b", source_url: "https://example.com/b/docs", verification: "" },
      ],
    };
    const assets = {
      async fetch(input) {
        const { pathname } = new URL(input instanceof Request ? input.url : input);
        if (pathname === "/resources.json") return Response.json(fixture);
        if (pathname === "/.well-known/agent-skills/index.json") return Response.json({ skills: [] });
        return new Response("not found", { status: 404 });
      },
    };
    const ask = async (id) => {
      const res = await call("/mcp", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name: "get_gear", arguments: { id } } }),
      }, { ASSETS: assets });
      return (await res.json()).result;
    };
    const a = await ask("with-licence");
    assert.deepEqual(a.structuredContent.checked, {
      source_checked: "2026-11-07", source_url: "https://example.com/a/docs", access_notes: "None beyond a clone.", licence: "MIT",
    });
    assert.equal(a.structuredContent.entry.licence, "MIT");
    const b = await ask("no-check-scope");
    assert.deepEqual(Object.keys(b.structuredContent.checked), ["source_checked", "source_url", "access_notes"]);
    assert.equal("licence" in b.structuredContent.entry, false);
    for (const r of [a, b]) assert.doesNotMatch(r.content[1].text, /unknown/i);
  });

  test("get_gear explains an unknown id and suggests close ones", async () => {
    const result = await tool("get_gear", { id: "playwright" });
    assert.equal(result.isError, true);
    assert.match(result.content[0].text, /No Gearlist entry has the id "playwright"\. Close matches: /);
    const missing = await tool("get_gear", {});
    assert.equal(missing.isError, true);
    assert.match(missing.content[0].text, /id must be a non-empty string/);
  });

  test("list_categories counts every entry", async () => {
    const list = (await legacy("tools/list")).json.result.tools;
    const result = await tool("list_categories", {});
    assertNotice(result);
    const data = result.structuredContent;
    conforms(list[2].outputSchema, data, "list_categories");
    assert.equal(data.total_entries, records.resources.length);
    assert.equal(data.categories.reduce((n, c) => n + c.count, 0), records.resources.length);
    assert.equal(data.catalog_updated, records.updated);
  });

  test("list_skills lists the repository skills with install commands", async () => {
    const list = (await legacy("tools/list")).json.result.tools;
    const result = await tool("list_skills", {});
    assertNotice(result);
    const data = result.structuredContent;
    conforms(list[3].outputSchema, data, "list_skills");
    const folders = (await readdir(path.join(ROOT, "skills"), { withFileTypes: true }))
      .filter((d) => d.isDirectory()).map((d) => d.name).sort();
    assert.deepEqual(data.skills.map((s) => s.name), folders);
    assert.equal(data.install_all, "npx skills add techhorizonlabs/gearlist");
    for (const s of data.skills) {
      assert.equal(s.install, `npx skills add techhorizonlabs/gearlist --skill ${s.name}`);
      assert.ok(s.artifact_url.startsWith("https://gearlist.build/.well-known/agent-skills/"));
    }
    assert.ok(data.skills.some((s) => s.includes_scripts), "the YouTube skills ship scripts");
  });

  test("list tools reject arguments", async () => {
    const result = await tool("list_categories", { verbose: true });
    assert.equal(result.isError, true);
    assert.match(result.content[0].text, /takes no arguments/);
  });

  test("an unknown tool is a protocol error", async () => {
    const { json } = await legacy("tools/call", { name: "delete_everything", arguments: {} });
    assert.equal(json.error.code, -32602);
    assert.match(json.error.message, /Unknown tool: delete_everything/);
  });

  test("a missing tool name or non-object arguments is a protocol error", async () => {
    assert.equal((await legacy("tools/call", { arguments: {} })).json.error.code, -32602);
    assert.equal((await legacy("tools/call", { name: "search_gear", arguments: [1] })).json.error.code, -32602);
  });
});

describe("recommend_stack", () => {
  const stack = async (args) => {
    const result = await tool("recommend_stack", args);
    assert.equal(result.isError, false, JSON.stringify(result.content));
    return result;
  };

  // Every item must be a real entry, with its fields copied as written and its quotes
  // taken word for word from the field they name.
  function checkItems(data) {
    const ids = new Set();
    for (const item of data.items) {
      const e = records.resources.find((r) => r.id === item.id);
      assert.ok(e, `${item.id} is a Gearlist entry`);
      assert.ok(!ids.has(item.id), `${item.id} is listed once`);
      ids.add(item.id);
      assert.equal(item.name, e.name);
      assert.equal(item.group, e.category);
      assert.equal(item.url, e.url);
      assert.equal(item.access_notes, e.access_notes);
      assert.equal(item.source_url, e.source_url);
      assert.equal(item.source_checked, e.source_checked);
      assert.ok(item.why_it_fits.length >= 1, `${item.id} says why it fits`);
      for (const why of item.why_it_fits) {
        const text = String(e[why.field]);
        assert.ok(text.includes(why.quote), `${item.id} ${why.field} quote is copied from the entry`);
        assert.ok(why.quote.length <= 200, `${item.id} ${why.field} quote is short`);
        assert.ok(why.words.length >= 1);
        for (const word of why.words) assert.ok(text.includes(word), `${item.id} ${why.field} has the word ${word}`);
        assert.ok(why.words.some((w) => why.quote.includes(w)), `${item.id} ${why.field} quote holds a matched word`);
      }
    }
  }

  for (const [job, expected] of [
    ["review my code for security risks", ["node9", "ecc", "orchestkit"]],
    ["research a YouTube creator", ["vidiq-mcp", "youtube-js", "noxinfluencer-api"]],
    ["test my web app in a real browser", ["agent-tars", "oz-skills"]],
  ]) {
    test(`"${job}" returns real entries from at least three groups`, async () => {
      const list = (await legacy("tools/list")).json.result.tools;
      const result = await stack({ job });
      assertNotice(result);
      const data = result.structuredContent;
      conforms(list[4].outputSchema, data, "recommend_stack");
      assert.deepEqual(JSON.parse(result.content[1].text), data, "text block is the serialised structured content");
      assert.equal(data.job, job);
      assert.equal(data.match, "found");
      assert.ok(data.count >= 3 && data.count <= 6, `default limit is 6, got ${data.count}`);
      assert.equal(data.count, data.items.length);
      checkItems(data);
      const ids = data.items.map((i) => i.id);
      for (const id of expected) assert.ok(ids.includes(id), `${job}: expected ${id}, got ${ids.join(", ")}`);
      const groups = new Set(data.items.map((i) => i.group));
      assert.ok(groups.size >= 3, `${job}: ${[...groups].join(", ")}`);
    });
  }

  test("a browser test job brings in a browser-testing MCP server", async () => {
    const ids = (await stack({ job: "test my web app in a real browser" })).structuredContent.items.map((i) => i.id);
    // alumnium on the catalog of 7 Nov 2026; playwright-mcp if it has been added since.
    assert.ok(ids.includes("alumnium") || ids.includes("playwright-mcp"), ids.join(", "));
  });

  test("the best entry of each kind goes in before a kind repeats", async () => {
    // Every top match for "browser" is an agent tool; the stack still reaches other groups.
    const data = (await stack({ job: "browser", limit: 6 })).structuredContent;
    checkItems(data);
    const groups = data.items.map((i) => i.group);
    assert.ok(groups.includes("Agent tools"));
    assert.ok(new Set(groups).size >= 3, groups.join(", "));
    const search = (await tool("search_gear", { query: "browser", limit: 3 })).structuredContent.results;
    assert.ok(search.every((e) => e.category === "Agent tools"), "search_gear alone would give only agent tools");
  });

  test("an unknown job gets an honest no-match and a pointer to search_gear", async () => {
    for (const job of ["bake sourdough bread", "zzqqxx"]) {
      const data = (await stack({ job })).structuredContent;
      assert.equal(data.match, "none");
      assert.equal(data.count, 0);
      assert.equal(data.total_matches, 0);
      assert.deepEqual(data.items, []);
      assert.match(data.next_step, /^Nothing in Gearlist matches this job well\./);
      assert.match(data.next_step, /search_gear with other words/);
    }
  });

  test("a word found only in setup notes does not make an entry fit", async () => {
    // "track my brand in AI answers": entries that only mention AI or answers in their
    // access notes stay out; what is left has two of the job's words in what it does.
    const data = (await stack({ job: "track my brand in AI answers" })).structuredContent;
    checkItems(data);
    for (const item of data.items) {
      const fields = item.why_it_fits.filter((w) => w.field !== "access_notes");
      const words = fields.flatMap((w) => w.words.map((x) => x.toLowerCase()));
      const hit = data.words.filter((t) => words.some((w) => w.startsWith(t)));
      assert.ok(hit.length >= 2, `${item.id} has ${hit.join(", ")}`);
    }
  });

  test("the limit is honoured, from 1 to 10, with 6 by default", async () => {
    const broad = "browser";
    for (const limit of [1, 3, 10]) {
      const data = (await stack({ job: broad, limit })).structuredContent;
      assert.equal(data.count, limit);
      assert.ok(data.total_matches > 10, "the job fits more entries than any limit");
      checkItems(data);
    }
    assert.equal((await stack({ job: broad })).structuredContent.count, 6);
    for (const [label, args, pattern] of [
      ["a limit above 10", { job: broad, limit: 11 }, /limit must be a whole number from 1 to 10/],
      ["a zero limit", { job: broad, limit: 0 }, /limit must be/],
      ["a fractional limit", { job: broad, limit: 2.5 }, /limit must be/],
      ["a missing job", {}, /job must be a non-empty string/],
      ["a blank job", { job: "   " }, /job must be a non-empty string/],
      ["an overlong job", { job: "x".repeat(201) }, /200 characters or fewer/],
      ["an unknown argument", { job: broad, category: "Agent tools" }, /Unknown argument: category/],
    ]) {
      const result = await tool("recommend_stack", args);
      assert.equal(result.isError, true, label);
      assert.match(result.content[0].text, pattern, label);
      assert.match(result.content[0].text, /documentation-checked only/, label);
    }
  });

  test("the output is identical across runs and across a fresh catalog", async () => {
    const job = "test my web app in a real browser";
    const first = (await stack({ job })).structuredContent;
    const second = (await stack({ job })).structuredContent;
    assert.deepEqual(second, first);
    const rules = parseHeaders(await readFile(path.join(DIST, "_headers"), "utf8"));
    const res = await call("/mcp", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ jsonrpc: "2.0", id: 7, method: "tools/call", params: { name: "recommend_stack", arguments: { job } } }),
    }, { ASSETS: fakeAssets(rules) });
    assert.equal(JSON.stringify((await res.json()).result.structuredContent), JSON.stringify(first));
  });

  test("it reads only the deployed catalog files and makes no network calls", async () => {
    const rules = parseHeaders(await readFile(path.join(DIST, "_headers"), "utf8"));
    const fresh = { ASSETS: fakeAssets(rules) };
    const realFetch = globalThis.fetch;
    globalThis.fetch = () => {
      throw new Error("recommend_stack made a network call");
    };
    try {
      const res = await call("/mcp", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 8, method: "tools/call", params: { name: "recommend_stack", arguments: { job: "send email" } } }),
      }, fresh);
      assert.equal((await res.json()).result.isError, false);
    } finally {
      globalThis.fetch = realFetch;
    }
    assert.deepEqual([...fresh.ASSETS.calls].sort(), ["/.well-known/agent-skills/index.json", "/resources.json"]);
  });
});

describe("Modern requests (2026-07-28)", () => {
  test("server/discover lists versions, capabilities and identity", async () => {
    const { res, json } = await modern("server/discover");
    assert.equal(res.status, 200);
    const r = json.result;
    assert.equal(r.resultType, "complete");
    assert.deepEqual(r.supportedVersions, SUPPORTED_VERSIONS);
    assert.deepEqual(r.capabilities, { tools: {} });
    assert.equal(r._meta["io.modelcontextprotocol/serverInfo"].name, "gearlist");
    assert.ok(r.ttlMs > 0);
    assert.equal(r.cacheScope, "public");
  });

  test("tools/list carries resultType and caching hints", async () => {
    const { json } = await modern("tools/list");
    assert.equal(json.result.resultType, "complete");
    assert.equal(json.result.tools.length, 5);
    assert.ok(Number.isInteger(json.result.ttlMs) && json.result.ttlMs >= 0);
  });

  test("tools/call works with the Mcp-Name header", async () => {
    const { json } = await modern("tools/call", { name: "search_gear", arguments: { query: "mcp", limit: 2 } });
    assert.equal(json.result.resultType, "complete");
    assert.equal(json.result.structuredContent.count, 2);
    assertNotice(json.result);
  });

  test("a base64 Mcp-Name header is decoded before comparison", async () => {
    const encoded = "=?base64?" + Buffer.from("list_skills").toString("base64") + "?=";
    const { res } = await modern("tools/call", { name: "list_skills", arguments: {} }, { headers: { "Mcp-Name": encoded } });
    assert.equal(res.status, 200);
  });

  for (const [label, method, params, override, status, code] of [
    ["a version header that disagrees with _meta", "tools/list", {}, { headers: { "MCP-Protocol-Version": "2025-11-25" } }, 400, -32020],
    ["a missing Mcp-Method header", "tools/list", {}, { headers: { "Mcp-Method": null } }, 400, -32020],
    ["an Mcp-Method that disagrees with the body", "tools/list", {}, { headers: { "Mcp-Method": "tools/call" } }, 400, -32020],
    ["an Mcp-Name that disagrees with the body", "tools/call", { name: "get_gear", arguments: { id: "a2a" } }, { headers: { "Mcp-Name": "list_skills" } }, 400, -32020],
    ["a missing Mcp-Name header", "tools/call", { name: "get_gear", arguments: { id: "a2a" } }, { headers: { "Mcp-Name": null } }, 400, -32020],
    ["a modern version header with no _meta", "tools/list", {}, { meta: null }, 400, -32602],
    ["missing client capabilities", "tools/list", {}, { meta: { "io.modelcontextprotocol/protocolVersion": MODERN_VERSION } }, 400, -32602],
    ["an unknown method", "resources/list", {}, {}, 404, -32601],
    ["ping, which 2026-07-28 removed", "ping", {}, {}, 404, -32601],
  ]) {
    test(`rejects ${label}`, async () => {
      const { res, json } = await modern(method, params, override);
      assert.equal(res.status, status);
      assert.equal(json.error.code, code);
    });
  }

  test("an unsupported version lists the supported ones", async () => {
    const meta = {
      "io.modelcontextprotocol/protocolVersion": "2099-01-01",
      "io.modelcontextprotocol/clientCapabilities": {},
    };
    const { res, json } = await modern("tools/list", {}, { meta, headers: { "MCP-Protocol-Version": "2099-01-01" } });
    assert.equal(res.status, 400);
    assert.equal(json.error.code, -32022);
    assert.deepEqual(json.error.data, { supported: SUPPORTED_VERSIONS, requested: "2099-01-01" });
  });

  test("an unknown legacy method is a JSON-RPC error with status 200", async () => {
    const { res, json } = await legacy("resources/list");
    assert.equal(res.status, 200);
    assert.equal(json.error.code, -32601);
  });
});

describe("HTTP handling on /mcp", () => {
  const post = (body, headers = {}) =>
    call("/mcp", { method: "POST", headers: { "Content-Type": "application/json", ...headers }, body });

  test("bad JSON is a parse error", async () => {
    const res = await post("{not json");
    assert.equal(res.status, 400);
    const json = await res.json();
    assert.equal(json.error.code, -32700);
    assert.equal(json.id, null);
  });

  test("batches, wrong versions and bad ids are invalid requests", async () => {
    for (const body of [
      "[]",
      JSON.stringify({ jsonrpc: "1.0", id: 1, method: "ping" }),
      JSON.stringify({ jsonrpc: "2.0", id: null, method: "ping" }),
      JSON.stringify({ jsonrpc: "2.0", id: 1.5, method: "ping" }),
      JSON.stringify({ jsonrpc: "2.0", id: 1, result: {} }),
      '"just a string"',
    ]) {
      const res = await post(body);
      assert.equal(res.status, 400, body);
      assert.equal((await res.json()).error.code, -32600, body);
    }
  });

  test("an oversized body is refused by Content-Length", async () => {
    const res = await post(JSON.stringify({ jsonrpc: "2.0", id: 1, method: "ping", pad: "x".repeat(MAX_BODY) }));
    assert.equal(res.status, 413);
    assert.equal((await res.json()).error.code, -32600);
  });

  test("an oversized streamed body is refused while reading", async () => {
    const chunk = new TextEncoder().encode("x".repeat(16 * 1024));
    let sent = 0;
    const body = new ReadableStream({
      pull(controller) {
        if (sent++ < 8) controller.enqueue(chunk);
        else controller.close();
      },
    });
    const res = await worker.fetch(
      new Request(ORIGIN + "/mcp", { method: "POST", headers: { "Content-Type": "application/json" }, body, duplex: "half" }),
      env,
    );
    assert.equal(res.status, 413);
  });

  test("a non-JSON content type is refused", async () => {
    const res = await call("/mcp", { method: "POST", headers: { "Content-Type": "text/plain" }, body: "{}" });
    assert.equal(res.status, 415);
  });

  test("an Accept header without JSON is refused", async () => {
    const res = await post(JSON.stringify({ jsonrpc: "2.0", id: 1, method: "ping" }), { Accept: "text/html" });
    assert.equal(res.status, 406);
  });

  test("a malformed Origin is refused, a real one is served", async () => {
    const ping = JSON.stringify({ jsonrpc: "2.0", id: 1, method: "ping" });
    assert.equal((await post(ping, { Origin: "null" })).status, 403);
    assert.equal((await post(ping, { Origin: "not a url" })).status, 403);
    assert.equal((await post(ping, { Origin: "https://example.com" })).status, 200);
  });

  test("OPTIONS answers the CORS preflight", async () => {
    const res = await call("/mcp", { method: "OPTIONS" });
    assert.equal(res.status, 204);
    assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
    assert.match(res.headers.get("Access-Control-Allow-Headers"), /MCP-Protocol-Version/);
    assert.match(res.headers.get("Access-Control-Allow-Headers"), /Mcp-Name/);
  });

  test("GET explains the endpoint, an SSE GET gets 405, DELETE gets 405", async () => {
    const res = await call("/mcp");
    assert.equal(res.status, 200);
    assert.match(res.headers.get("Content-Type"), /^text\/plain/);
    const text = await res.text();
    assert.match(text, /claude mcp add --transport http gearlist https:\/\/gearlist\.build\/mcp/);
    assert.match(text, /documentation-checked only/);
    assert.equal((await call("/mcp", { headers: { Accept: "text/event-stream" } })).status, 405);
    assert.equal((await call("/mcp", { method: "DELETE" })).status, 405);
  });

  test("the rate limiter returns 429 when the budget is spent", async () => {
    const limited = { ...env, RATE_LIMITER: { limit: async () => ({ success: false }) } };
    const res = await call("/mcp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "ping" }),
    }, limited);
    assert.equal(res.status, 429);
    assert.equal(res.headers.get("Retry-After"), "60");
    const api = await call("/api/search?q=mcp", {}, limited);
    assert.equal(api.status, 429);
  });

  test("a failing rate limiter does not take the server down", async () => {
    const broken = { ...env, RATE_LIMITER: { limit: async () => { throw new Error("down"); } } };
    const { status } = await call("/api/search?q=mcp", {}, broken);
    assert.equal(status, 200);
  });
});

describe("Markdown negotiation on /", () => {
  test("Accept: text/markdown returns the Markdown catalog", async () => {
    const res = await call("/", { headers: { Accept: "text/markdown" } });
    assert.equal(res.status, 200);
    assert.equal(res.headers.get("Content-Type"), "text/markdown; charset=utf-8");
    assert.match(res.headers.get("Vary"), /Accept/);
    const text = await res.text();
    assert.ok(text.startsWith("---\ntitle: "), "YAML front matter first");
    assert.match(text, /^# Gearlist$/m);
    assert.match(text, /https:\/\/gearlist\.build\/mcp/);
    for (const e of records.resources) assert.ok(text.includes(`\`${e.id}\``), `${e.id} is in the Markdown`);
  });

  test("a browser gets HTML with the CSP and Link headers from _headers", async () => {
    const accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8";
    const res = await call("/", { headers: { Accept: accept } });
    assert.equal(res.headers.get("Content-Type"), "text/html");
    assert.match(res.headers.get("Vary"), /Accept/);
    const headersFile = await readFile(path.join(DIST, "_headers"), "utf8");
    const csp = /Content-Security-Policy: (.*)/.exec(headersFile)[1];
    assert.equal(res.headers.get("Content-Security-Policy"), csp, "the page CSP with its hashes is kept");
    assert.equal(res.headers.get("X-Content-Type-Options"), "nosniff");
    const link = res.headers.get("Link");
    assert.match(link, /<\/llms\.txt>; rel="describedby"/);
    assert.match(link, /<\/.well-known\/api-catalog>; rel="api-catalog"/);
    assert.match(link, /rel="ai-catalog"/);
    assert.match(await res.text(), /<h2 id="h-agents">Give this to your agent<\/h2>/);
  });

  test("the CSP hashes match the inline script and style in index.html", async () => {
    const html = await readFile(path.join(DIST, "index.html"), "utf8");
    const headersFile = await readFile(path.join(DIST, "_headers"), "utf8");
    const hash = (s) => "'sha256-" + createHash("sha256").update(s, "utf8").digest("base64") + "'";
    for (const [, body] of html.matchAll(/<script>([\s\S]*?)<\/script>/g)) assert.ok(headersFile.includes(hash(body)));
    for (const [, body] of html.matchAll(/<style>([\s\S]*?)<\/style>/g)) assert.ok(headersFile.includes(hash(body)));
  });

  test("Accept headers are ranked correctly", () => {
    assert.equal(prefersMarkdown("text/markdown"), true);
    assert.equal(prefersMarkdown("text/markdown, text/html;q=0.9"), true);
    assert.equal(prefersMarkdown("text/html, text/markdown;q=0.5"), false);
    assert.equal(prefersMarkdown("text/markdown;q=0"), false);
    assert.equal(prefersMarkdown("*/*"), false);
    assert.equal(prefersMarkdown(""), false);
    assert.equal(prefersMarkdown(null), false);
    assert.equal(prefersMarkdown("text/html,application/xhtml+xml,*/*;q=0.8"), false);
  });

  test("curl's default Accept gets HTML", async () => {
    const res = await call("/", { headers: { Accept: "*/*" } });
    assert.equal(res.headers.get("Content-Type"), "text/html");
  });
});

describe("Search API, OpenAPI and discovery", () => {
  test("GET /api/search returns JSON with CORS", async () => {
    const res = await call("/api/search?q=browser&limit=3");
    assert.equal(res.status, 200);
    assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
    const data = await res.json();
    assert.equal(data.count, 3);
    assert.equal(data.notice, NOTICE);
  });

  test("bad API input is a 400 with a reason", async () => {
    for (const [q, pattern] of [
      ["", /Give a query, a category, or both/],
      ["?q=mcp&limit=99", /limit must be/],
      ["?q=mcp&limit=abc", /limit must be/],
      ["?q=mcp&category=Toasters", /Unknown category/],
    ]) {
      const res = await call("/api/search" + q);
      assert.equal(res.status, 400, q);
      assert.match((await res.json()).error, pattern);
    }
    assert.equal((await call("/api/nothing")).status, 404);
    assert.equal((await call("/api/search?q=x", { method: "POST" })).status, 405);
  });

  test("/openapi.json describes /api/search", async () => {
    const res = await call("/openapi.json");
    assert.equal(res.status, 200);
    const doc = await res.json();
    assert.equal(doc.openapi, "3.1.0");
    assert.equal(doc.servers[0].url, ORIGIN);
    const op = doc.paths["/api/search"].get;
    assert.equal(op.operationId, "searchGear");
    assert.deepEqual(op.parameters.map((p) => p.name), ["q", "category", "limit"]);
    assert.ok(doc.components.schemas.Entry.required.includes("access_notes"));
  });

  test("the server card matches server/discover and supports If-None-Match", async () => {
    const res = await call("/mcp/server-card");
    assert.equal(res.status, 200);
    assert.equal(res.headers.get("Content-Type"), "application/mcp-server-card+json");
    assert.equal(res.headers.get("Access-Control-Allow-Origin"), "*");
    const card = await res.json();
    assert.equal(card.$schema, "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json");
    assert.match(card.name, /^[a-zA-Z0-9.-]+\/[a-zA-Z0-9._-]+$/);
    assert.ok(card.description.length <= 100);
    assert.equal(card.remotes[0].url, ORIGIN + "/mcp");
    const discover = (await modern("server/discover")).json.result;
    assert.deepEqual(card.remotes[0].supportedProtocolVersions, discover.supportedVersions);
    assert.equal(card.version, discover._meta["io.modelcontextprotocol/serverInfo"].version);
    const again = await call("/mcp/server-card", { headers: { "If-None-Match": res.headers.get("ETag") } });
    assert.equal(again.status, 304);
  });

  test("the skills index digests match the files it points to", async () => {
    const index = JSON.parse(await readFile(path.join(DIST, ".well-known/agent-skills/index.json"), "utf8"));
    assert.equal(index.$schema, "https://schemas.agentskills.io/discovery/0.2.0/schema.json");
    for (const s of index.skills) {
      const bytes = await readFile(path.join(DIST, s.url));
      assert.equal(s.digest, "sha256:" + createHash("sha256").update(bytes).digest("hex"), s.name);
      assert.ok(["skill-md", "archive"].includes(s.type));
    }
  });

  test("the AI Catalog points at the server card and every skill", async () => {
    const cat = JSON.parse(await readFile(path.join(DIST, ".well-known/ai-catalog.json"), "utf8"));
    assert.equal(cat.specVersion, "1.0");
    assert.equal(cat.entries[0].type, "application/mcp-server-card+json");
    assert.equal(cat.entries[0].url, ORIGIN + "/mcp/server-card");
    for (const e of cat.entries) assert.ok(e.identifier.startsWith("urn:air:gearlist.build:") && e.url && !e.data);
  });

  test("static paths are left to the assets", async () => {
    env.ASSETS.calls.length = 0;
    const res = await call("/llms.txt");
    assert.equal(res.status, 200);
    assert.deepEqual(env.ASSETS.calls, ["/llms.txt"]);
  });

  test("workers.dev responses are marked noindex", async () => {
    const res = await worker.fetch(new Request("https://gearlist-site.example.workers.dev/mcp"), env);
    assert.equal(res.headers.get("X-Robots-Tag"), "noindex");
  });
});
