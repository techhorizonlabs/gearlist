// Configuration and the three Login with Raft calls this app makes: the code exchange,
// userinfo and serverinfo. Nothing else here talks to the network.
// Contract: https://docs.raft.build/developers/login-with-raft.md

import { readBody } from "../../site/worker/http.mjs";

export const DEFAULT_APP_ORIGIN = "https://raft.gearlist.build";
export const DEFAULT_RAFT_API_ORIGIN = "https://api.raft.build";
export const UPSTREAM_TIMEOUT_MS = 8000;
const MAX_UPSTREAM_BODY = 64 * 1024;
const USER_AGENT = "gearlist-raft/1.0";
const CLIENT_ID = /^[A-Za-z0-9._-]{1,100}$/;
export const MIN_SESSION_SECRET = 32;

// An origin from config: https, or plain http on localhost for local runs. No path,
// query, fragment or credentials. Returns null when the value is not one.
function cleanOrigin(value, fallback) {
  const raw = value === undefined || value === null || value === "" ? fallback : String(value).trim();
  let url;
  try {
    url = new URL(raw);
  } catch {
    return null;
  }
  const local = url.protocol === "http:" && ["localhost", "127.0.0.1"].includes(url.hostname);
  if (url.protocol !== "https:" && !local) return null;
  if (url.origin !== raw.replace(/\/$/, "")) return null;
  return url.origin;
}

// Every origin and credential comes from the Worker's own config, never from the request.
// RAFT_CLIENT_SECRET and SESSION_SECRET are Worker secrets. `ready` is false until all of
// them are present, and login and every action refuse until then.
export function readConfig(env) {
  const appOrigin = cleanOrigin(env.APP_ORIGIN, DEFAULT_APP_ORIGIN);
  const apiOrigin = cleanOrigin(env.RAFT_API_ORIGIN, DEFAULT_RAFT_API_ORIGIN);
  const id = typeof env.RAFT_CLIENT_ID === "string" ? env.RAFT_CLIENT_ID.trim() : "";
  const clientId = CLIENT_ID.test(id) ? id : "";
  const clientSecret = typeof env.RAFT_CLIENT_SECRET === "string" ? env.RAFT_CLIENT_SECRET : "";
  const sessionSecret = typeof env.SESSION_SECRET === "string" ? env.SESSION_SECRET : "";
  return {
    appOrigin,
    apiOrigin,
    clientId,
    clientSecret,
    sessionSecret,
    secureCookie: appOrigin !== null && appOrigin.startsWith("https:"),
    ready: Boolean(appOrigin && apiOrigin && clientId && clientSecret && sessionSecret.length >= MIN_SESSION_SECRET),
  };
}

function basicAuth(id, secret) {
  let binary = "";
  for (const byte of new TextEncoder().encode(`${id}:${secret}`)) binary += String.fromCharCode(byte);
  return "Basic " + btoa(binary);
}

// One call to the Raft API. Redirects are refused so credentials never follow a
// Location header, the body is read up to a fixed size, and the call times out.
// Returns { status, body }, where status 0 means the call did not complete.
async function call(deps, url, init) {
  let res;
  try {
    res = await deps.upstream(url, {
      ...init,
      redirect: "manual",
      signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
    });
  } catch {
    return { status: 0, body: null };
  }
  if (res.type === "opaqueredirect" || (res.status >= 300 && res.status < 400)) {
    try {
      await res.body?.cancel();
    } catch {
      // Nothing to read.
    }
    return { status: 0, body: null, redirected: true };
  }
  // A body that cannot be read in full, is too large, or is not JSON counts as no
  // answer (status 0), so a cut-off reply is never taken as Raft refusing the app.
  let read;
  try {
    read = await readBody(res, MAX_UPSTREAM_BODY);
  } catch {
    return { status: 0, body: null };
  }
  if (read.tooLarge) return { status: 0, body: null };
  if (!read.text) return { status: res.status, body: null };
  try {
    return { status: res.status, body: JSON.parse(read.text) };
  } catch {
    return { status: 0, body: null };
  }
}

// Exchanges the one-time code from the callback for an access token, server side, with
// HTTP Basic client authentication. Returns { token, expiresIn } or { status }.
export async function exchangeCode(cfg, deps, code) {
  const out = await call(deps, `${cfg.apiOrigin}/api/oauth/token`, {
    method: "POST",
    headers: {
      Authorization: basicAuth(cfg.clientId, cfg.clientSecret),
      "Content-Type": "application/json",
      Accept: "application/json",
      "User-Agent": USER_AGENT,
    },
    body: JSON.stringify({ grant_type: "authorization_code", code }),
  });
  const body = out.body;
  if (out.status !== 200 || body === null || typeof body !== "object") return { status: out.status };
  if (typeof body.access_token !== "string" || !body.access_token) return { status: out.status };
  // Raft documents expires_in in seconds (one hour). A missing, zero or negative value is
  // refused rather than replaced, so a session never outlives its token.
  const raw = typeof body.expires_in === "number" ? body.expires_in : NaN;
  if (!Number.isFinite(raw) || raw <= 0) return { status: 0, invalidLifetime: true };
  return { token: body.access_token, expiresIn: Math.floor(raw) };
}

function bearerGet(cfg, deps, path, token) {
  return call(deps, cfg.apiOrigin + path, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}`, Accept: "application/json", "User-Agent": USER_AGENT },
  });
}

export function fetchUserinfo(cfg, deps, token) {
  return bearerGet(cfg, deps, "/api/oauth/userinfo", token);
}

// Raft checks on every serverinfo call, live, that the app is available on that server,
// that the principal may act there and that the token is still good. Returns "ok",
// "rejected" (Raft refused the token: 401), "unavailable" (403 or another refusal) or
// "unreachable" (no answer, a redirect or a server error).
export async function checkServer(cfg, deps, token, serverId) {
  const out = await bearerGet(cfg, deps, `/api/oauth/serverinfo?server_id=${encodeURIComponent(serverId)}`, token);
  if (out.status === 200) {
    const body = out.body;
    return body !== null && typeof body === "object" && body.id === serverId ? "ok" : "unavailable";
  }
  if (out.status === 401) return "rejected";
  if (out.status === 0 || out.status >= 500) return "unreachable";
  return "unavailable";
}

// One structured line per failure, with status numbers and codes only. Codes, tokens,
// secrets, cookies and profiles never reach a log.
export function logEvent(event, fields = {}) {
  console.warn(JSON.stringify({ app: "gearlist-raft", event, ...fields }));
}
