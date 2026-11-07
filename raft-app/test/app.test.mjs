// Tests for the Gearlist Raft App, run against its fetch handler with a fake ASSETS that
// serves the built site/dist folder and a fake Raft API. No network access.
//
//   python3 build.py && python3 site/build_site.py && node --test raft-app/test/
//
// Each action's result is compared with the MCP tool's result from site/worker for the
// same input, through the real MCP endpoint.

import { test, describe, before, after } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { handle, MESSAGES, HINTS } from "../src/index.mjs";
import { ACTIONS, CONTEXT_PATH, MANIFEST_PATH, CALLBACK_PATH, DESCRIPTION, CONTEXT_DESCRIPTION } from "../src/manifest.mjs";
import { COOKIE_NAME } from "../src/session.mjs";
import { STYLE, homePage } from "../src/home.mjs";
import site from "../../site/worker/index.mjs";
import { NOTICE } from "../../site/worker/catalog.mjs";
import { MAX_BODY, TOOL_NAMES, toolList } from "../../site/worker/mcp.mjs";

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DIST = path.resolve(APP, "..", "site", "dist");
const ORIGIN = "https://raft.gearlist.build";
const CLIENT_ID = "gearlist-test";
const CLIENT_SECRET = "raft-client-secret-for-tests-7f3a9c";
const SESSION_SECRET = "session-secret-for-tests-0123456789abcdef";
const ACCESS = "raft-access-token-for-tests-5d1e8b";
const CODE = "one-time-code-for-tests-91c2";
const SERVER_ID = "bb191bdf-efe0-4733-b30e-cd26bf37d609";
const AGENT = {
  sub: "27a3edb7-4e03-4a42-a61d-63fc04fce62c",
  type: "agent",
  scope: "openid profile",
  client_id: CLIENT_ID,
  client_name: "Gearlist",
  server_id: SERVER_ID,
  server_slug: "thl",
  server_role: "member",
  preferred_username: "helm",
  name: "HELM",
};
const TOOL_ACTIONS = ACTIONS.filter((a) => a.tool);

// A stand-in for env.ASSETS that serves site/dist, as site/test does.
function fakeAssets() {
  return {
    async fetch(input, init) {
      const request = input instanceof Request ? input : new Request(input, init);
      const file = decodeURIComponent(new URL(request.url).pathname);
      const full = path.join(DIST, file);
      try {
        if (!full.startsWith(DIST) || !(await stat(full)).isFile()) throw new Error("not a file");
        return new Response(await readFile(full), { headers: { "Content-Type": "application/json" } });
      } catch {
        return new Response("Not found", { status: 404 });
      }
    },
  };
}

// A stand-in for the Raft API. Each endpoint answers from `state`, which a test can change:
// { status, body, headers }, a function returning a Response, or an Error to throw.
function fakeRaft(overrides = {}) {
  const calls = [];
  const state = {
    token: { status: 200, body: { access_token: ACCESS, token_type: "Bearer", expires_in: 3600, scope: "openid profile" } },
    userinfo: { status: 200, body: AGENT },
    serverinfo: { status: 200, body: { id: SERVER_ID, slug: "thl", name: "THL", is_paid: false, plan_tier: "free" } },
    ...overrides,
  };
  const paths = { "/api/oauth/token": "token", "/api/oauth/userinfo": "userinfo", "/api/oauth/serverinfo": "serverinfo" };
  async function upstream(input, init = {}) {
    const url = new URL(input);
    calls.push({ url, method: init.method, headers: new Headers(init.headers), body: init.body, redirect: init.redirect });
    const answer = state[paths[url.pathname]];
    if (!answer) return new Response("{}", { status: 404 });
    if (answer instanceof Error) throw answer;
    if (typeof answer === "function") return answer();
    const body = answer.body === undefined ? null : JSON.stringify(answer.body);
    return new Response(body, { status: answer.status, headers: answer.headers || { "Content-Type": "application/json" } });
  }
  return { upstream, calls, state };
}

let assets;
let env;
let records;
let clock;
const seen = [];
const logs = [];
const saved = {};

function baseEnv(extra = {}) {
  return {
    ASSETS: assets,
    APP_ORIGIN: ORIGIN,
    RAFT_API_ORIGIN: "https://api.raft.build",
    RAFT_CLIENT_ID: CLIENT_ID,
    RAFT_CLIENT_SECRET: CLIENT_SECRET,
    SESSION_SECRET,
    ...extra,
  };
}

// Calls the app and keeps every response's headers and body for the secret checks.
async function call(pathname, init = {}, raft = fakeRaft(), testEnv = env) {
  const res = await handle(new Request(ORIGIN + pathname, init), testEnv, { upstream: raft.upstream, now: () => clock });
  const text = await res.text();
  seen.push([...res.headers].map(([k, v]) => `${k}: ${v}`).join("\n") + "\n\n" + text);
  let json = null;
  try {
    json = JSON.parse(text);
  } catch {
    json = null;
  }
  return { res, text, json, raft };
}

function cookieFrom(res) {
  const header = res.headers.get("Set-Cookie");
  return header ? header.split(";")[0] : null;
}

// Signs in through the callback and returns the cookie pair to send back.
async function login(raft = fakeRaft(), testEnv = env) {
  const out = await call(`${CALLBACK_PATH}?code=${CODE}`, {}, raft, testEnv);
  assert.equal(out.res.status, 200, out.text);
  return cookieFrom(out.res);
}

function invoke(action, args, cookie, raft = fakeRaft(), extra = {}) {
  const spec = ACTIONS.find((a) => a.name === action);
  const headers = { ...(cookie ? { Cookie: cookie } : {}), ...(extra.headers || {}) };
  if (spec.method === "GET") {
    const query = args && Object.keys(args).length ? "?" + new URLSearchParams(args) : "";
    return call(spec.path + query, { method: "GET", headers }, raft);
  }
  if (!headers["Content-Type"]) headers["Content-Type"] = "application/json";
  const body = extra.body !== undefined ? extra.body : JSON.stringify(args);
  return call(spec.path, { method: "POST", headers, body }, raft);
}

async function mcp(name, args) {
  const res = await site.fetch(
    new Request("https://gearlist.build/mcp", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json", "MCP-Protocol-Version": "2025-06-18" },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name, arguments: args } }),
    }),
    { ASSETS: assets },
  );
  return (await res.json()).result;
}

before(async () => {
  try {
    await stat(path.join(DIST, "index.md"));
  } catch {
    throw new Error("site/dist is missing or out of date. Run python3 site/build_site.py first.");
  }
  assets = fakeAssets();
  env = baseEnv();
  records = JSON.parse(await readFile(path.join(DIST, "resources.json"), "utf8"));
  clock = Date.parse("2026-11-07T00:00:00Z");
  for (const level of ["log", "info", "warn", "error", "debug"]) {
    saved[level] = console[level];
    console[level] = (...args) => logs.push(args.map(String).join(" "));
  }
});

after(() => {
  for (const [level, fn] of Object.entries(saved)) console[level] = fn;
});

describe("manifest", () => {
  test("is valid JSON in the raft-agent-manifest.v0 shape with the declared actions", async () => {
    const { res, text, json } = await call(MANIFEST_PATH);
    assert.equal(res.status, 200);
    assert.match(res.headers.get("Content-Type"), /^application\/json/);
    assert.deepEqual(JSON.parse(text), json);
    assert.equal(json.schema, "raft-agent-manifest.v0");
    assert.equal(json.name, "Gearlist");
    assert.equal(json.service, CLIENT_ID);
    assert.equal(json.description, DESCRIPTION);
    assert.equal(json.docs_url, ORIGIN + "/");
    assert.equal(json.app_origin, ORIGIN);
    assert.deepEqual(json.execution, { mode: "http_api", base_url: ORIGIN });
    assert.deepEqual(json.auth, { type: "login_with_raft" });
    assert.deepEqual(json.context_check, { url: ORIGIN + CONTEXT_PATH, method: "GET" });
    assert.deepEqual(
      json.actions.map((a) => a.name),
      ["get_session_context", "search_gear", "get_gear", "recommend_stack", "list_categories", "list_skills"],
    );
    assert.equal(new Set(json.actions.map((a) => a.name)).size, json.actions.length);
    for (const action of json.actions) {
      assert.match(action.name, /^[A-Za-z0-9._:-]+$/);
      assert.ok(["GET", "POST"].includes(action.endpoint.method));
      assert.match(action.endpoint.path, /^\/[a-z_/]+$/, "a relative path with no query or fragment");
      assert.equal(typeof action.description, "string");
      assert.ok(action.description.length > 20);
      for (const spec of Object.values(action.parameters)) {
        assert.ok(["string", "integer"].includes(spec.type));
        assert.equal(typeof spec.description, "string");
      }
    }
  });

  test("each Gearlist action copies the MCP tool's description and parameters", async () => {
    const { json } = await call(MANIFEST_PATH);
    const tools = new Map(toolList({ categories: [] }).map((t) => [t.name, t]));
    assert.deepEqual(TOOL_ACTIONS.map((a) => a.tool).sort(), [...TOOL_NAMES].sort());
    for (const action of json.actions) {
      if (action.name === "get_session_context") {
        assert.equal(action.description, CONTEXT_DESCRIPTION);
        assert.deepEqual(action.parameters, {});
        continue;
      }
      const tool = tools.get(action.name);
      assert.equal(action.description, tool.description);
      const props = tool.inputSchema.properties || {};
      assert.deepEqual(Object.keys(action.parameters), Object.keys(props));
      for (const [name, spec] of Object.entries(action.parameters)) {
        assert.equal(spec.type, props[name].type);
        assert.equal(spec.description, props[name].description);
        assert.equal(spec.required === true, (tool.inputSchema.required || []).includes(name));
      }
      assert.equal(action.endpoint.method, Object.keys(props).length ? "POST" : "GET");
    }
  });

  test("holds no secret and is served without a session", async () => {
    const { text, raft } = await call(MANIFEST_PATH);
    for (const secret of [CLIENT_SECRET, SESSION_SECRET]) assert.ok(!text.includes(secret));
    assert.equal(raft.calls.length, 0);
  });

  test("leaves out service until the client ID is set", async () => {
    const { res, json } = await call(MANIFEST_PATH, {}, fakeRaft(), baseEnv({ RAFT_CLIENT_ID: "" }));
    assert.equal(res.status, 200);
    assert.equal(json.service, undefined);
  });
});

describe("sign-in callback", () => {
  test("an agent gets an HttpOnly, Secure, SameSite=Strict session cookie and no token in the body", async () => {
    const raft = fakeRaft();
    const { res, text, json } = await call(`${CALLBACK_PATH}?code=${CODE}`, {}, raft);
    assert.equal(res.status, 200);
    assert.equal(json.ok, true);
    assert.equal(json.result.principal_type, "agent");
    const header = res.headers.get("Set-Cookie");
    assert.ok(header.startsWith(COOKIE_NAME + "=v1."));
    for (const attr of ["Path=/", "Max-Age=3600", "HttpOnly", "SameSite=Strict", "Secure"]) {
      assert.ok(header.split("; ").includes(attr), `${attr} in ${header}`);
    }
    assert.equal(res.headers.get("Cache-Control"), "no-store");
    for (const secret of [ACCESS, CODE, CLIENT_SECRET, SESSION_SECRET]) {
      assert.ok(!text.includes(secret));
      assert.ok(!header.includes(secret));
      assert.ok(!header.includes(Buffer.from(secret).toString("base64url")));
    }
  });

  test("the code is exchanged once, server side, with Basic auth and no redirects", async () => {
    const raft = fakeRaft();
    await login(raft);
    assert.deepEqual(raft.calls.map((c) => c.url.pathname), ["/api/oauth/token", "/api/oauth/userinfo", "/api/oauth/serverinfo"]);
    const [token, userinfo, serverinfo] = raft.calls;
    assert.equal(token.url.origin, "https://api.raft.build");
    assert.equal(token.method, "POST");
    assert.equal(token.headers.get("Authorization"), "Basic " + Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString("base64"));
    assert.deepEqual(JSON.parse(token.body), { grant_type: "authorization_code", code: CODE });
    assert.equal(userinfo.headers.get("Authorization"), `Bearer ${ACCESS}`);
    assert.equal(serverinfo.url.searchParams.get("server_id"), SERVER_ID);
    for (const c of raft.calls) assert.equal(c.redirect, "manual");
  });

  test("a local http origin gets the cookie without Secure", async () => {
    const local = baseEnv({ APP_ORIGIN: "http://localhost:8787" });
    const { res } = await call(`${CALLBACK_PATH}?code=${CODE}`, {}, fakeRaft(), local);
    assert.equal(res.status, 200);
    assert.ok(!res.headers.get("Set-Cookie").includes("Secure"));
  });

  const refusals = [
    ["a person's sign-in", { userinfo: { status: 200, body: { ...AGENT, type: "human" } } }, 403, "AGENT_ONLY", 2],
    ["a token issued to another app", { userinfo: { status: 200, body: { ...AGENT, client_id: "other" } } }, 403, "WRONG_APP", 2],
    ["a used or expired code", { token: { status: 400, body: { error: "request_already_consumed" } } }, 409, "CODE_USED_OR_EXPIRED", 1],
    ["a failed exchange", { token: { status: 500, body: {} } }, 502, "SIGN_IN_FAILED", 1],
    ["a token endpoint that redirects", { token: { status: 302, headers: { Location: "https://example.com/" } } }, 502, "SIGN_IN_FAILED", 1],
    ["an unreachable Raft API", { token: new TypeError("network") }, 502, "SIGN_IN_FAILED", 1],
    ["a failed userinfo", { userinfo: { status: 401, body: { error: "Invalid or expired access token" } } }, 502, "SIGN_IN_FAILED", 2],
    ["userinfo with no server", { userinfo: { status: 200, body: { ...AGENT, server_id: null } } }, 502, "SIGN_IN_FAILED", 2],
    ["a server where the app is not available", { serverinfo: { status: 403, body: { error: "server_access_denied" } } }, 403, "APP_NOT_AVAILABLE", 3],
    ["a token too long to fit in a cookie", { token: { status: 200, body: { access_token: "t".repeat(4000), expires_in: 3600 } } }, 502, "SIGN_IN_FAILED", 3],
  ];
  for (const [label, overrides, status, error, upstreamCalls] of refusals) {
    test(`${label} is refused with typed JSON and no cookie`, async () => {
      const raft = fakeRaft(overrides);
      const { res, json } = await call(`${CALLBACK_PATH}?code=${CODE}`, {}, raft);
      assert.equal(res.status, status);
      assert.deepEqual(json, { error, hint: HINTS[error] });
      assert.equal(res.headers.get("Set-Cookie"), null);
      assert.equal(raft.calls.length, upstreamCalls);
    });
  }

  const early = [
    ["a missing code", CALLBACK_PATH, {}, 400, "MISSING_CODE"],
    ["a malformed code", `${CALLBACK_PATH}?code=${encodeURIComponent("a b")}`, {}, 400, "MISSING_CODE"],
    ["a state value, which this app never issues", `${CALLBACK_PATH}?code=${CODE}&state=x`, {}, 400, "UNEXPECTED_STATE"],
    ["a browser visit", `${CALLBACK_PATH}?code=${CODE}`, { headers: { "Sec-Fetch-Mode": "navigate" } }, 403, "AGENT_ONLY"],
    ["a POST", `${CALLBACK_PATH}?code=${CODE}`, { method: "POST" }, 405, "METHOD_NOT_ALLOWED"],
  ];
  for (const [label, pathname, init, status, error] of early) {
    test(`${label} is refused before any call to Raft`, async () => {
      const { res, json, raft } = await call(pathname, init);
      assert.equal(res.status, status);
      assert.equal(json.error, error);
      assert.equal(raft.calls.length, 0);
    });
  }

  test("without the client ID or secrets, sign-in and actions refuse", async () => {
    for (const missing of [{ RAFT_CLIENT_ID: "" }, { RAFT_CLIENT_SECRET: undefined }, { SESSION_SECRET: "short" }]) {
      const testEnv = baseEnv(missing);
      const signIn = await call(`${CALLBACK_PATH}?code=${CODE}`, {}, fakeRaft(), testEnv);
      assert.equal(signIn.res.status, 503);
      assert.equal(signIn.json.error, "NOT_CONFIGURED");
      assert.equal(signIn.raft.calls.length, 0);
      const res = await handle(new Request(ORIGIN + CONTEXT_PATH), testEnv, { upstream: fakeRaft().upstream, now: () => clock });
      assert.equal(res.status, 503);
    }
  });
});

describe("every action refuses without a valid session", () => {
  for (const spec of ACTIONS) {
    test(`${spec.name} without a cookie`, async () => {
      const { res, json, raft } = await invoke(spec.name, spec.tool === "search_gear" ? { query: "browser" } : {}, null);
      assert.equal(res.status, 401);
      assert.deepEqual(json, { ok: false, error: { code: "SESSION_REQUIRED", message: MESSAGES.SESSION_REQUIRED } });
      assert.equal(raft.calls.length, 0);
    });
  }

  test("an altered, foreign or expired cookie is refused and cleared", async () => {
    const good = await login();
    const value = good.split("=")[1];
    const flipped = value.slice(0, -2) + (value.at(-2) === "A" ? "B" : "A") + value.at(-1);
    const otherKey = await login(fakeRaft(), baseEnv({ SESSION_SECRET: "another-session-secret-0123456789abcdef" }));
    for (const cookie of [`${COOKIE_NAME}=${flipped}`, `${COOKIE_NAME}=v1.abc.def`, `${COOKIE_NAME}=junk`, otherKey]) {
      const { res, json, raft } = await invoke("list_categories", {}, cookie);
      assert.equal(res.status, 401);
      assert.equal(json.error.code, "SESSION_REQUIRED");
      assert.match(res.headers.get("Set-Cookie"), new RegExp(`^${COOKIE_NAME}=; Path=/; Max-Age=0`));
      assert.equal(raft.calls.length, 0);
    }
    const saved = clock;
    clock += 3601 * 1000;
    const expired = await invoke("list_categories", {}, good);
    clock = saved;
    assert.equal(expired.res.status, 401);
    assert.equal(expired.raft.calls.length, 0);
  });

  test("a session from another client ID is refused", async () => {
    const cookie = await login();
    const res = await handle(
      new Request(ORIGIN + CONTEXT_PATH, { headers: { Cookie: cookie } }),
      baseEnv({ RAFT_CLIENT_ID: "a-different-client" }),
      { upstream: fakeRaft().upstream, now: () => clock },
    );
    assert.equal(res.status, 401);
  });
});

describe("every action refuses when Raft says the app is not available", () => {
  for (const spec of ACTIONS) {
    test(`${spec.name} after an uninstall`, async () => {
      const cookie = await login();
      const saved = clock;
      clock += 61 * 1000;
      const raft = fakeRaft({ serverinfo: { status: 403, body: { error: "server_access_denied" } } });
      const { res, json } = await invoke(spec.name, spec.tool === "search_gear" ? { query: "browser" } : {}, cookie, raft);
      clock = saved;
      assert.equal(res.status, 403);
      assert.deepEqual(json, { ok: false, error: { code: "APP_NOT_AVAILABLE", message: MESSAGES.APP_NOT_AVAILABLE } });
      assert.match(res.headers.get("Set-Cookie"), /Max-Age=0/);
      assert.deepEqual(raft.calls.map((c) => c.url.pathname), ["/api/oauth/serverinfo"]);
    });
  }

  test("a token Raft no longer accepts is a 401, and an unreachable Raft is a 503", async () => {
    const cases = [
      [{ serverinfo: { status: 401, body: { error: "Invalid or expired access token" } } }, 401, "SESSION_REJECTED"],
      [{ serverinfo: { status: 200, body: { id: "another-server" } } }, 403, "APP_NOT_AVAILABLE"],
      [{ serverinfo: { status: 500, body: {} } }, 503, "RAFT_UNREACHABLE"],
      [{ serverinfo: new TypeError("network") }, 503, "RAFT_UNREACHABLE"],
      [{ serverinfo: { status: 307, headers: { Location: "https://example.com/" } } }, 503, "RAFT_UNREACHABLE"],
    ];
    for (const [overrides, status, code] of cases) {
      const cookie = await login();
      const saved = clock;
      clock += 61 * 1000;
      const { res, json } = await invoke("list_skills", {}, cookie, fakeRaft(overrides));
      clock = saved;
      assert.equal(res.status, status);
      assert.equal(json.error.code, code);
    }
  });

  test("Raft's answer is reused for at most 60 seconds", async () => {
    const cookie = await login();
    const start = clock;
    const within = fakeRaft();
    clock = start + 59 * 1000;
    assert.equal((await invoke("list_categories", {}, cookie, within)).res.status, 200);
    assert.equal(within.calls.length, 0);
    const later = fakeRaft();
    clock = start + 61 * 1000;
    assert.equal((await invoke("list_categories", {}, cookie, later)).res.status, 200);
    assert.equal(later.calls.length, 1);
    assert.equal(later.calls[0].headers.get("Authorization"), `Bearer ${ACCESS}`);
    clock = start;
  });
});

describe("actions give the same result as the MCP tools", () => {
  let cookie;
  before(async () => {
    cookie = await login();
  });

  const cases = () => [
    ["search_gear", { query: "browser" }],
    ["search_gear", { query: "send email", limit: 3 }],
    ["search_gear", { query: "", category: "Protocols" }],
    ["search_gear", { query: "mcp server", category: "mcp-and-integrations", limit: 50 }],
    ["search_gear", { query: "zzzzqqqxx" }],
    ["get_gear", { id: records.resources[0].id }],
    ["get_gear", { id: records.resources[5].id.toUpperCase() }],
    ["recommend_stack", { job: "test my web app in a real browser" }],
    ["recommend_stack", { job: "send email from an agent", limit: 10 }],
    ["recommend_stack", { job: "qwertyuiop asdfghjkl" }],
    ["list_categories", {}],
    ["list_skills", {}],
  ];

  test("for the same input, result is the MCP tool's structuredContent, byte for byte", async () => {
    for (const [name, args] of cases()) {
      const expected = await mcp(name, args);
      assert.equal(expected.isError, false, `${name} ${JSON.stringify(args)}`);
      const { res, json, text } = await invoke(name, args, cookie);
      assert.equal(res.status, 200, text);
      assert.equal(json.ok, true);
      assert.deepEqual(json.result, expected.structuredContent);
      assert.equal(JSON.stringify(json.result), JSON.stringify(expected.structuredContent));
      assert.equal(JSON.stringify(json), `{"ok":true,"result":${JSON.stringify(expected.structuredContent)}}`);
    }
  });

  test("recommend_stack keeps the next_step text and the access notes wording", async () => {
    const { json } = await invoke("recommend_stack", { job: "test my web app in a real browser" }, cookie);
    const found = (await mcp("recommend_stack", { job: "test my web app in a real browser" })).structuredContent;
    assert.equal(json.result.next_step, found.next_step);
    assert.equal(json.result.notice, NOTICE);
    assert.ok(json.result.items.length > 0);
    for (const item of json.result.items) {
      const entry = records.resources.find((r) => r.id === item.id);
      assert.equal(item.access_notes, entry.access_notes);
    }
    const none = await invoke("recommend_stack", { job: "qwertyuiop asdfghjkl" }, cookie);
    assert.equal(none.json.result.next_step, (await mcp("recommend_stack", { job: "qwertyuiop asdfghjkl" })).structuredContent.next_step);
  });

  test("invalid input gets the MCP tool's own message", async () => {
    const errors = [
      ["search_gear", { query: 5 }],
      ["search_gear", { query: "x".repeat(201) }],
      ["search_gear", { query: "browser", limit: 0 }],
      ["search_gear", { query: "browser", limit: 51 }],
      ["search_gear", { query: "browser", limit: 2.5 }],
      ["search_gear", { query: "browser", category: "Nope" }],
      ["search_gear", { query: "browser", extra: true }],
      ["search_gear", {}],
      ["get_gear", {}],
      ["get_gear", { id: "" }],
      ["get_gear", { id: "x".repeat(101) }],
      ["get_gear", { id: records.resources[0].id, more: 1 }],
      ["recommend_stack", { job: "" }],
      ["recommend_stack", { job: "browser", limit: 11 }],
      ["recommend_stack", { job: "x".repeat(201) }],
      ["recommend_stack", { task: "browser" }],
      ["list_categories", { verbose: "1" }],
      ["list_skills", { page: "2" }],
    ];
    for (const [name, args] of errors) {
      const expected = await mcp(name, args);
      assert.equal(expected.isError, true, `${name} ${JSON.stringify(args)}`);
      const { res, json } = await invoke(name, args, cookie);
      assert.equal(res.status, 400, `${name} ${JSON.stringify(args)}`);
      assert.equal(json.error.code, "INVALID_PARAMS");
      assert.equal(json.error.message + "\n\n" + NOTICE, expected.content[0].text);
    }
  });

  test("an unknown id is a 404 with the MCP message and close matches", async () => {
    const expected = await mcp("get_gear", { id: "playwright" });
    const { res, json } = await invoke("get_gear", { id: "playwright" }, cookie);
    assert.equal(res.status, 404);
    assert.equal(json.error.code, "ENTRY_NOT_FOUND");
    assert.equal(json.error.message + "\n\n" + NOTICE, expected.content[0].text);
  });

  // raft integration invoke sends --param values as text, so the Raft App reads limit as
  // digits in a string. The MCP tool refuses a string limit. This is the one known difference.
  test("limit may be sent as digits in a string, which the MCP tool refuses", async () => {
    assert.equal((await mcp("search_gear", { query: "browser", limit: "5" })).isError, true);
    assert.equal((await mcp("recommend_stack", { job: "test my web app in a real browser", limit: "3" })).isError, true);
    const stack = await invoke("recommend_stack", { job: "test my web app in a real browser", limit: "3" }, cookie);
    assert.deepEqual(stack.json.result, (await mcp("recommend_stack", { job: "test my web app in a real browser", limit: 3 })).structuredContent);
    const expected = await mcp("search_gear", { query: "browser", limit: 5 });
    const { json } = await invoke("search_gear", { query: "browser", limit: "5" }, cookie);
    assert.deepEqual(json.result, expected.structuredContent);
    const bad = await invoke("search_gear", { query: "browser", limit: "5x" }, cookie);
    assert.equal(bad.res.status, 400);
    assert.equal(bad.json.error.message + "\n\n" + NOTICE, (await mcp("search_gear", { query: "browser", limit: "5x" })).content[0].text);
  });

  test("get_session_context reports the agent, server and expiry", async () => {
    const { res, json } = await invoke("get_session_context", {}, cookie);
    assert.equal(res.status, 200);
    assert.deepEqual(json.result, {
      signed_in: true,
      principal: { type: "agent", id: AGENT.sub, name: "HELM" },
      server: { id: SERVER_ID, slug: "thl" },
      client_id: CLIENT_ID,
      session_expires_at: new Date(clock + 3600 * 1000).toISOString(),
      actions: ACTIONS.map((a) => a.name),
    });
    const extra = await invoke("get_session_context", { x: "1" }, cookie);
    assert.equal(extra.res.status, 400);
  });
});

describe("request handling", () => {
  let cookie;
  before(async () => {
    cookie = await login();
  });

  test("bodies must be JSON objects within the MCP size limit", async () => {
    const wrongType = await invoke("search_gear", null, cookie, fakeRaft(), { headers: { "Content-Type": "text/plain" }, body: '{"query":"x"}' });
    assert.equal(wrongType.res.status, 415);
    const badJson = await invoke("search_gear", null, cookie, fakeRaft(), { body: "{nope" });
    assert.equal(badJson.res.status, 400);
    assert.equal(badJson.json.error.code, "INVALID_JSON");
    const array = await invoke("search_gear", null, cookie, fakeRaft(), { body: "[1]" });
    assert.equal(array.res.status, 400);
    assert.equal(array.json.error.code, "NOT_AN_OBJECT");
    const big = await invoke("search_gear", null, cookie, fakeRaft(), { body: JSON.stringify({ query: "x".repeat(MAX_BODY) }) });
    assert.equal(big.res.status, 413);
    const empty = await invoke("search_gear", null, cookie, fakeRaft(), { body: "" });
    assert.equal(empty.res.status, 400);
    assert.equal(empty.json.error.message + "\n\n" + NOTICE, (await mcp("search_gear", {})).content[0].text);
  });

  test("each action takes one method", async () => {
    const get = await call("/api/raft/actions/search_gear", { headers: { Cookie: cookie } });
    assert.equal(get.res.status, 405);
    assert.equal(get.res.headers.get("Allow"), "POST");
    const post = await call("/api/raft/actions/list_categories", { method: "POST", headers: { Cookie: cookie } });
    assert.equal(post.res.status, 405);
    assert.equal(post.res.headers.get("Allow"), "GET");
  });

  test("requests from other websites are refused, and there are no CORS headers", async () => {
    const res = await invoke("search_gear", { query: "browser" }, cookie, fakeRaft(), {
      headers: { Origin: "https://evil.example", "Content-Type": "application/json" },
    });
    assert.equal(res.res.status, 403);
    assert.equal(res.json.error.code, "CROSS_SITE");
    for (const pathname of ["/", MANIFEST_PATH, CONTEXT_PATH]) {
      const out = await call(pathname, { headers: { Cookie: cookie } });
      assert.equal(out.res.headers.get("Access-Control-Allow-Origin"), null);
    }
  });

  test("the rate limiter returns 429 for sign-in and actions", async () => {
    const limited = baseEnv({ RATE_LIMITER: { limit: async () => ({ success: false }) } });
    const signIn = await call(`${CALLBACK_PATH}?code=${CODE}`, {}, fakeRaft(), limited);
    assert.equal(signIn.res.status, 429);
    assert.equal(signIn.raft.calls.length, 0);
    const res = await handle(new Request(ORIGIN + CONTEXT_PATH, { headers: { Cookie: cookie } }), limited, {
      upstream: fakeRaft().upstream,
      now: () => clock,
    });
    assert.equal(res.status, 429);
  });

  test("unknown paths are 404", async () => {
    for (const pathname of ["/api/raft/actions/delete_everything", "/api/raft/actions/", "/login", "/mcp"]) {
      const { res, json } = await call(pathname, { headers: { Cookie: cookie } });
      assert.equal(res.status, 404);
      assert.equal(json.error.code, "NOT_FOUND");
    }
  });

  test("responses carry the security headers", async () => {
    for (const pathname of [MANIFEST_PATH, CONTEXT_PATH, CALLBACK_PATH]) {
      const { res } = await call(pathname);
      assert.equal(res.headers.get("X-Content-Type-Options"), "nosniff");
      assert.match(res.headers.get("Content-Security-Policy"), /default-src 'none'/);
    }
  });
});

describe("home page", () => {
  test("explains the app and how to install it, under a strict CSP", async () => {
    const { res, text } = await call("/");
    assert.equal(res.status, 200);
    assert.match(res.headers.get("Content-Type"), /^text\/html/);
    assert.ok(text.includes("from the Install App card the agent posts, or in Raft under Settings, then Applications."));
    assert.ok(text.includes("a server owner or admin installs it once for the whole server"));
    assert.ok(text.includes(`raft integration login --service ${CLIENT_ID}`));
    for (const action of ACTIONS) assert.ok(text.includes(`<code>${action.name}</code>`));
    const hash = createHash("sha256").update(STYLE).digest("base64");
    assert.ok(text.includes(`<style>${STYLE}</style>`));
    assert.equal(
      res.headers.get("Content-Security-Policy"),
      `default-src 'none'; style-src 'sha256-${hash}'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`,
    );
    const head = await call("/", { method: "HEAD" });
    assert.equal(head.text, "");
  });

  test("leaves out the commands before registration and escapes the client ID", () => {
    assert.ok(!homePage("").includes("raft integration login"));
    assert.ok(homePage("<x>").includes("&lt;x&gt;"));
  });
});

describe("fixes from the security review", () => {
  const SEARCH = ACTIONS.find((a) => a.name === "search_gear").path;

  // A request body that arrives only when read, running `onRead` first.
  function slowBody(onRead, text = '{"query":"browser"}') {
    return new ReadableStream(
      {
        pull(controller) {
          onRead();
          controller.enqueue(new TextEncoder().encode(text));
          controller.close();
        },
      },
      { highWaterMark: 0 },
    );
  }

  test("a session that ends while the body is still arriving gets no data", async () => {
    const start = clock;
    const raft = fakeRaft({ token: { status: 200, body: { access_token: ACCESS, expires_in: 120 } } });
    const cookie = await login(raft);
    try {
      const out = await call(SEARCH, {
        method: "POST",
        headers: { Cookie: cookie, "Content-Type": "application/json" },
        body: slowBody(() => { clock = start + 121 * 1000; }),
        duplex: "half",
      }, raft);
      assert.equal(out.res.status, 401, out.text);
      assert.equal(out.json.error.code, "SESSION_REQUIRED");
      assert.equal(out.json.result, undefined);
    } finally {
      clock = start;
    }
  });

  test("Raft is asked again before the tool runs when the body outlasts the 60 second check", async () => {
    const start = clock;
    const raft = fakeRaft();
    const cookie = await login(raft);
    try {
      const out = await call(SEARCH, {
        method: "POST",
        headers: { Cookie: cookie, "Content-Type": "application/json" },
        body: slowBody(() => {
          clock = start + 61 * 1000;
          raft.state.serverinfo = { status: 403, body: { error: "app_not_available" } };
        }),
        duplex: "half",
      }, raft);
      assert.equal(out.res.status, 403, out.text);
      assert.equal(out.json.error.code, "APP_NOT_AVAILABLE");
      assert.equal(out.json.result, undefined);
    } finally {
      clock = start;
    }
  });

  test("a Raft reply cut off after its headers is a 503, and the cookie is kept", async () => {
    const start = clock;
    const cookie = await login();
    const cut = fakeRaft({
      serverinfo: () => new Response(new ReadableStream({ start(c) { c.error(new Error("connection reset")); } }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    });
    try {
      clock = start + 61 * 1000;
      const out = await invoke("search_gear", { query: "browser" }, cookie, cut);
      assert.equal(out.res.status, 503, out.text);
      assert.equal(out.json.error.code, "RAFT_UNREACHABLE");
      assert.equal(out.res.headers.get("Set-Cookie"), null);
    } finally {
      clock = start;
    }
  });

  test("a session ends when its token does, and a token without a lifetime is refused", async () => {
    const start = clock;
    const short = fakeRaft({ token: { status: 200, body: { access_token: ACCESS, expires_in: 1 } } });
    const cookie = await login(short);
    try {
      clock = start + 2000;
      const out = await invoke("get_session_context", {}, cookie, short);
      assert.equal(out.res.status, 401, out.text);
    } finally {
      clock = start;
    }
    for (const expires of [undefined, 0, -5, "3600"]) {
      const body = { access_token: ACCESS };
      if (expires !== undefined) body.expires_in = expires;
      const out = await call(`${CALLBACK_PATH}?code=${CODE}`, {}, fakeRaft({ token: { status: 200, body } }));
      assert.equal(out.res.status, 502, `expires_in ${expires}`);
      assert.equal(out.res.headers.get("Set-Cookie"), null);
    }
  });

  test("a whitespace body still needs Content-Type: application/json", async () => {
    const cookie = await login();
    const out = await invoke("search_gear", null, cookie, fakeRaft(), { headers: { "Content-Type": "text/plain" }, body: "  " });
    assert.equal(out.res.status, 415);
  });

  test("an error's own name never reaches the log", async () => {
    const cookie = await login();
    const broken = baseEnv({ ASSETS: { fetch() { throw Object.assign(new Error("x"), { name: CLIENT_SECRET }); } } });
    const before = logs.length;
    const spec = ACTIONS.find((a) => a.name === "search_gear");
    const res = await handle(
      new Request(ORIGIN + spec.path, { method: "POST", headers: { Cookie: cookie, "Content-Type": "application/json" }, body: '{"query":"browser"}' }),
      broken,
      { upstream: fakeRaft().upstream, now: () => clock },
    );
    assert.equal(res.status, 500);
    const added = logs.slice(before).join("\n");
    assert.ok(!added.includes(CLIENT_SECRET));
    assert.match(added, /"event":"internal_error","name":"other"/);
  });
});

describe("writing rules and secrets", () => {
  test("no en or em dashes in any visible text", async () => {
    const texts = [
      homePage(CLIENT_ID),
      (await call(MANIFEST_PATH)).text,
      JSON.stringify(MESSAGES),
      JSON.stringify(HINTS),
      await readFile(path.join(APP, "README.md"), "utf8"),
    ];
    for (const text of texts) assert.ok(!/[\u2013\u2014]/.test(text));
  });

  test("no secret, token or code appears in any response or log", () => {
    assert.ok(seen.length > 50);
    const secrets = [CLIENT_SECRET, SESSION_SECRET, ACCESS, CODE];
    for (const text of [...seen, ...logs]) {
      for (const secret of secrets) assert.ok(!text.includes(secret), `found a secret in: ${text.slice(0, 200)}`);
    }
    assert.ok(logs.length > 0, "failures are logged");
    for (const line of logs) assert.match(line, /^\{"app":"gearlist-raft","event":"[a-z_]+"/);
  });
});
