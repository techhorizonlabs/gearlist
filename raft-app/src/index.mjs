// Gearlist Raft App: the Worker behind https://raft.gearlist.build.
//
//   /                                       public home page (the manifest's docs_url)
//   /.well-known/raft-agent-manifest.json   agent behaviour manifest
//   /login/raft/callback                    Login with Raft callback, agents only
//   /api/raft/context                       get_session_context
//   /api/raft/actions/<name>                the five Gearlist tools
//
// Every action needs a session cookie from the callback, and Raft must still confirm
// (at most 60 seconds ago) that the app is available to that agent on its server.
// The actions run the same code as the MCP tools in site/worker and read the same
// catalog files through the ASSETS binding. The only network calls go to the Raft API
// for Login with Raft. Nothing is stored apart from the per-IP rate limit counter and,
// in memory, the sessions Raft confirmed in the last 60 seconds.

import { loadCatalog } from "../../site/worker/catalog.mjs";
import { MAX_BODY, runTool } from "../../site/worker/mcp.mjs";
import { rateLimited, readBody, respond } from "../../site/worker/http.mjs";
import { checkServer, exchangeCode, fetchUserinfo, logEvent, readConfig } from "./raft.mjs";
import {
  MAX_COOKIE, MAX_SESSION_SECONDS, clearCookie, forgetChecked, isRaftId, markChecked, newSessionId, open,
  readCookie, recentlyChecked, seal, sessionCookie, shortText,
} from "./session.mjs";
import { ACTIONS, CALLBACK_PATH, MANIFEST_PATH, buildManifest } from "./manifest.mjs";
import { homePage, styleHashSource } from "./home.mjs";

const NO_STORE = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" };
const CODE = /^[\x21-\x7e]{1,1024}$/;

export const MESSAGES = {
  NOT_CONFIGURED: "Gearlist on Raft is not set up yet. Try again later.",
  RATE_LIMITED: "Too many requests. Wait a minute and try again.",
  SESSION_REQUIRED: "No valid Gearlist session. Sign in with raft integration login, then try again.",
  SESSION_REJECTED: "Raft no longer accepts this session. Sign in again with raft integration login.",
  APP_NOT_AVAILABLE:
    "Raft says Gearlist is not available to this agent on this server. A server owner or admin can install it " +
    "in Raft under Settings, then Applications, or from the Install App card an agent posts. Then sign in again.",
  RAFT_UNREACHABLE: "Gearlist could not check this session with Raft. Try again shortly.",
  CROSS_SITE: "Requests from other websites are refused.",
  UNSUPPORTED_MEDIA_TYPE: "Send the parameters as JSON with Content-Type: application/json.",
  PAYLOAD_TOO_LARGE: `Request body is larger than ${MAX_BODY} bytes.`,
  INVALID_JSON: "The body is not valid JSON.",
  NOT_AN_OBJECT: "Send the parameters as a JSON object.",
  NOT_FOUND: "Not found. The manifest at /.well-known/raft-agent-manifest.json lists the actions.",
  INTERNAL: "Internal error. Try again shortly.",
};

// Typed answers for a refused sign-in. The Raft CLI shows `error` and `hint` to the agent.
export const HINTS = {
  METHOD_NOT_ALLOWED: "Open this address with GET.",
  NOT_CONFIGURED: MESSAGES.NOT_CONFIGURED,
  RATE_LIMITED: MESSAGES.RATE_LIMITED,
  AGENT_ONLY:
    "This address is for Raft agents signing in to Gearlist. People can use https://gearlist.build without signing in.",
  UNEXPECTED_STATE: "Gearlist does not start a browser sign-in, so this link is not valid. Agents sign in with raft integration login.",
  MISSING_CODE: "The sign-in link has no valid code. Run raft integration login again.",
  CODE_USED_OR_EXPIRED: "This sign-in code was already used or has expired. Run raft integration login again for a fresh one.",
  SIGN_IN_FAILED: "Raft did not complete the sign-in. Try again shortly.",
  WRONG_APP: "This sign-in was issued for a different app.",
  APP_NOT_AVAILABLE: MESSAGES.APP_NOT_AVAILABLE,
};

function jsonResponse(value, status, extra = {}) {
  return respond(JSON.stringify(value), status, "application/json; charset=utf-8", { ...NO_STORE, ...extra });
}

function fail(status, code, message = MESSAGES[code], extra = {}) {
  return jsonResponse({ ok: false, error: { code, message } }, status, extra);
}

function refuseLogin(status, error, extra = {}) {
  return jsonResponse({ error, hint: HINTS[error] }, status, extra);
}

function isBrowserNavigation(request) {
  const mode = (request.headers.get("Sec-Fetch-Mode") || "").toLowerCase();
  const dest = (request.headers.get("Sec-Fetch-Dest") || "").toLowerCase();
  return mode === "navigate" || dest === "document";
}

// The agent handoff: Raft sends the agent's client here with ?code=. No browser state is
// expected, so the code is accepted only after userinfo proves the caller is an agent of
// this app, and serverinfo confirms the app is available on its server. Browser visits
// and links carrying a state value are refused before any exchange.
async function callback(request, url, env, cfg, deps) {
  if (request.method !== "GET") return refuseLogin(405, "METHOD_NOT_ALLOWED", { Allow: "GET" });
  if (await rateLimited(request, env)) return refuseLogin(429, "RATE_LIMITED", { "Retry-After": "60" });
  if (!cfg.ready) return refuseLogin(503, "NOT_CONFIGURED");
  if (isBrowserNavigation(request)) return refuseLogin(403, "AGENT_ONLY");
  if (url.searchParams.has("state")) return refuseLogin(400, "UNEXPECTED_STATE");
  const code = url.searchParams.get("code");
  if (code === null || !CODE.test(code)) return refuseLogin(400, "MISSING_CODE");

  const startedMs = deps.now();
  const exchanged = await exchangeCode(cfg, deps, code);
  if (!exchanged.token) {
    logEvent(exchanged.invalidLifetime ? "token_lifetime_invalid" : "token_exchange_failed", { status: exchanged.status });
    return exchanged.status === 400 ? refuseLogin(409, "CODE_USED_OR_EXPIRED") : refuseLogin(502, "SIGN_IN_FAILED");
  }
  const info = await fetchUserinfo(cfg, deps, exchanged.token);
  const user = info.body;
  if (info.status !== 200 || user === null || typeof user !== "object") {
    logEvent("userinfo_failed", { status: info.status });
    return refuseLogin(502, "SIGN_IN_FAILED");
  }
  if (user.client_id !== cfg.clientId) return refuseLogin(403, "WRONG_APP");
  if (user.type !== "agent") return refuseLogin(403, "AGENT_ONLY");
  if (!isRaftId(user.sub) || !isRaftId(user.server_id)) {
    logEvent("userinfo_incomplete");
    return refuseLogin(502, "SIGN_IN_FAILED");
  }
  const server = await checkServer(cfg, deps, exchanged.token, user.server_id);
  if (server !== "ok") {
    logEvent("serverinfo_refused_at_login", { result: server });
    return server === "unreachable" ? refuseLogin(502, "SIGN_IN_FAILED") : refuseLogin(403, "APP_NOT_AVAILABLE");
  }

  // The session ends when the token does, counted from before the exchange, and never
  // later than MAX_SESSION_SECONDS from now.
  const now = deps.now();
  const tokenEnd = Math.floor(startedMs / 1000) + exchanged.expiresIn;
  const exp = Math.min(tokenEnd, Math.floor(now / 1000) + MAX_SESSION_SECONDS);
  const seconds = exp - Math.floor(now / 1000);
  if (seconds <= 0) {
    logEvent("token_expired_at_login");
    return refuseLogin(502, "SIGN_IN_FAILED");
  }
  const session = {
    v: 1,
    sid: newSessionId(),
    sub: user.sub,
    name: shortText(user.name) || shortText(user.preferred_username),
    srv: user.server_id,
    slug: shortText(user.server_slug),
    cid: cfg.clientId,
    exp,
    tok: exchanged.token,
  };
  const sealed = await seal(session, cfg.sessionSecret);
  if (sealed.length > MAX_COOKIE) {
    logEvent("session_too_large", { length: sealed.length });
    return refuseLogin(502, "SIGN_IN_FAILED");
  }
  markChecked(session.sid, now);
  const cookie = sessionCookie(sealed, seconds, cfg);
  return jsonResponse(
    {
      ok: true,
      result: {
        signed_in: true,
        principal_type: "agent",
        server_slug: session.slug,
        session_expires_at: new Date(session.exp * 1000).toISOString(),
        next_step: "Call get_session_context to check the session, then use the Gearlist actions.",
      },
    },
    200,
    { "Set-Cookie": cookie },
  );
}

// Returns { session } or { response } with the refusal. Runs before any parameter is read.
async function authorise(request, cfg, deps) {
  if (!cfg.ready) return { response: fail(503, "NOT_CONFIGURED") };
  const raw = readCookie(request);
  const now = deps.now();
  const session = raw === null ? null : await open(raw, cfg, now);
  if (!session) {
    const extra = raw === null ? {} : { "Set-Cookie": clearCookie(cfg) };
    return { response: fail(401, "SESSION_REQUIRED", undefined, extra) };
  }
  return confirm(session, cfg, deps);
}

// Confirms a session that has already been opened: it has not expired by the clock now,
// and Raft said the app is available within CHECK_TTL_MS. Called before parameters are
// read, and again just before a tool runs, so a slow request body cannot outlast either.
async function confirm(session, cfg, deps) {
  const now = deps.now();
  if (!Number.isInteger(session.exp) || session.exp * 1000 <= now) {
    forgetChecked(session.sid);
    return { response: fail(401, "SESSION_REQUIRED", undefined, { "Set-Cookie": clearCookie(cfg) }) };
  }
  if (recentlyChecked(session.sid, now)) return { session };
  const result = await checkServer(cfg, deps, session.tok, session.srv);
  if (result === "ok") {
    markChecked(session.sid, now);
    return { session };
  }
  forgetChecked(session.sid);
  logEvent("serverinfo_refused", { result });
  if (result === "unreachable") return { response: fail(503, "RAFT_UNREACHABLE", undefined, { "Retry-After": "30" }) };
  const extra = { "Set-Cookie": clearCookie(cfg) };
  return result === "rejected"
    ? { response: fail(401, "SESSION_REJECTED", undefined, extra) }
    : { response: fail(403, "APP_NOT_AVAILABLE", undefined, extra) };
}

// The parameters of one call: the JSON body for POST, the query string for GET.
async function readArgs(request, url, method) {
  if (method === "GET") return { args: Object.fromEntries(url.searchParams) };
  let body;
  try {
    body = await readBody(request, MAX_BODY);
  } catch {
    return { response: fail(400, "INVALID_JSON") };
  }
  if (body.tooLarge) return { response: fail(413, "PAYLOAD_TOO_LARGE") };
  if (body.text === "") return { args: {} };
  const type = request.headers.get("Content-Type") || "";
  if (!/^application\/json\s*(;|$)/i.test(type.trim())) return { response: fail(415, "UNSUPPORTED_MEDIA_TYPE") };
  if (!body.text.trim()) return { args: {} };
  let args;
  try {
    args = JSON.parse(body.text);
  } catch {
    return { response: fail(400, "INVALID_JSON") };
  }
  if (args === null || typeof args !== "object" || Array.isArray(args)) return { response: fail(400, "NOT_AN_OBJECT") };
  // raft integration invoke sends each --param value as text, so limit may arrive as
  // digits in a string. This is the one input the Raft App reads differently from the MCP
  // server, which takes limit only as a number. /api/search accepts digits the same way.
  if (typeof args.limit === "string" && /^\d{1,3}$/.test(args.limit)) args = { ...args, limit: Number(args.limit) };
  return { args };
}

function crossSite(request, cfg) {
  const origin = request.headers.get("Origin");
  return origin !== null && origin !== cfg.appOrigin;
}

async function action(request, url, env, cfg, deps, spec) {
  if (request.method !== spec.method) {
    return fail(405, "METHOD_NOT_ALLOWED", `Use ${spec.method} for this action.`, { Allow: spec.method });
  }
  if (crossSite(request, cfg)) return fail(403, "CROSS_SITE");
  if (await rateLimited(request, env)) return fail(429, "RATE_LIMITED", undefined, { "Retry-After": "60" });
  const auth = await authorise(request, cfg, deps);
  if (auth.response) return auth.response;
  const session = auth.session;

  if (!spec.tool) {
    const extra = [...url.searchParams.keys()];
    if (extra.length) {
      return fail(400, "INVALID_PARAMS", `Unknown argument: ${extra[0]}. ${spec.name} takes no arguments.`);
    }
    return jsonResponse({
      ok: true,
      result: {
        signed_in: true,
        principal: { type: "agent", id: session.sub, name: session.name },
        server: { id: session.srv, slug: session.slug },
        client_id: session.cid,
        session_expires_at: new Date(session.exp * 1000).toISOString(),
        actions: ACTIONS.map((a) => a.name),
      },
    }, 200);
  }

  const read = await readArgs(request, url, spec.method);
  if (read.response) return read.response;
  const catalog = await loadCatalog(env);
  const again = await confirm(session, cfg, deps);
  if (again.response) return again.response;
  const out = runTool(catalog, spec.tool, read.args);
  if (out.error !== undefined) {
    return out.missing ? fail(404, "ENTRY_NOT_FOUND", out.error) : fail(400, "INVALID_PARAMS", out.error);
  }
  return jsonResponse({ ok: true, result: out.value }, 200);
}

async function home(request, cfg) {
  if (request.method !== "GET" && request.method !== "HEAD") {
    return respond("Use GET.\n", 405, "text/plain; charset=utf-8", { Allow: "GET, HEAD" });
  }
  const csp =
    `default-src 'none'; style-src ${await styleHashSource()}; base-uri 'none'; form-action 'none'; frame-ancestors 'none'`;
  return respond(request.method === "HEAD" ? null : homePage(cfg.clientId), 200, "text/html; charset=utf-8", {
    "Content-Security-Policy": csp,
    "Cache-Control": "public, max-age=300",
  });
}

async function manifestRoute(request, env, cfg) {
  if (request.method !== "GET" && request.method !== "HEAD") {
    return fail(405, "METHOD_NOT_ALLOWED", "Use GET.", { Allow: "GET, HEAD" });
  }
  const body = JSON.stringify(buildManifest(cfg, await loadCatalog(env)), null, 2);
  return respond(request.method === "HEAD" ? null : body, 200, "application/json; charset=utf-8", {
    "Cache-Control": "public, max-age=300",
  });
}

const BY_PATH = new Map(ACTIONS.map((a) => [a.path, a]));

async function route(request, env, deps) {
  const url = new URL(request.url);
  const cfg = readConfig(env);
  if (!cfg.appOrigin) return fail(503, "NOT_CONFIGURED");
  const path = url.pathname;
  if (path === "/") return home(request, cfg);
  if (path === MANIFEST_PATH) return manifestRoute(request, env, cfg);
  if (path === CALLBACK_PATH) return callback(request, url, env, cfg, deps);
  const spec = BY_PATH.get(path);
  if (spec) return action(request, url, env, cfg, deps, spec);
  return fail(404, "NOT_FOUND");
}

// `deps.upstream` is the fetch used for the Raft API and `deps.now` the clock, so the
// tests can stand in for both.
export async function handle(request, env, deps = {}) {
  const resolved = { upstream: deps.upstream || ((input, init) => fetch(input, init)), now: deps.now || Date.now };
  try {
    return await route(request, env, resolved);
  } catch (err) {
    // Only a fixed set of error names is logged, so nothing an error carries can reach a log.
    const known = ["Error", "TypeError", "RangeError", "SyntaxError", "AbortError", "TimeoutError"];
    const name = err && known.includes(err.name) ? err.name : "other";
    logEvent("internal_error", { name });
    return fail(500, "INTERNAL");
  }
}

export default {
  fetch(request, env) {
    return handle(request, env);
  },
};
