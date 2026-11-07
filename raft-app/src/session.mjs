// The agent's Gearlist session. The callback mints it as one HttpOnly cookie after Raft
// proves the caller is an agent and the app is available on its server. The cookie
// holds the session encrypted with AES-GCM under a key derived from SESSION_SECRET, so
// the agent's client cannot read or change it, and the Worker keeps no session store.
// The Raft access token inside it lets each action ask Raft again whether the app is
// still available. That answer is reused for at most 60 seconds, as the Login with Raft
// guide requires for any role or membership read.

export const COOKIE_NAME = "gearlist_raft_session";
export const MAX_SESSION_SECONDS = 3600;
export const CHECK_TTL_MS = 60 * 1000;
export const MAX_COOKIE = 3800;
const MAX_CHECKED = 1000;
const MAX_FIELD = 200;
const AAD = new TextEncoder().encode(COOKIE_NAME + " v1");

const keys = new Map();

async function sessionKey(secret) {
  const hit = keys.get(secret);
  if (hit) return hit;
  const enc = new TextEncoder();
  const base = await crypto.subtle.importKey("raw", enc.encode(secret), "HKDF", false, ["deriveKey"]);
  const key = await crypto.subtle.deriveKey(
    { name: "HKDF", hash: "SHA-256", salt: enc.encode("gearlist-raft"), info: enc.encode("session cookie v1") },
    base,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
  keys.clear();
  keys.set(secret, key);
  return key;
}

function toBase64Url(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(text) {
  if (!/^[A-Za-z0-9_-]+$/.test(text)) throw new TypeError("bad encoding");
  const padded = text.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((text.length + 3) % 4);
  return Uint8Array.from(atob(padded), (c) => c.charCodeAt(0));
}

export function newSessionId() {
  return [...crypto.getRandomValues(new Uint8Array(16))].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// A short display string from Raft, or "" when it is missing or not a string.
export function shortText(value) {
  return typeof value === "string" ? value.replace(/[\u0000-\u001f\u007f]/g, "").slice(0, MAX_FIELD) : "";
}

export function isRaftId(value) {
  return typeof value === "string" && value.length > 0 && value.length <= MAX_FIELD && /^[\x21-\x7e]+$/.test(value);
}

export async function seal(session, secret) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const plain = new TextEncoder().encode(JSON.stringify(session));
  const sealed = await crypto.subtle.encrypt({ name: "AES-GCM", iv, additionalData: AAD }, await sessionKey(secret), plain);
  return "v1." + toBase64Url(iv) + "." + toBase64Url(new Uint8Array(sealed));
}

// Returns the session, or null when the cookie is missing, altered, expired or was
// issued for another client ID.
export async function open(value, cfg, nowMs) {
  if (typeof value !== "string" || value.length > MAX_COOKIE) return null;
  const parts = value.split(".");
  if (parts.length !== 3 || parts[0] !== "v1") return null;
  let session;
  try {
    const iv = fromBase64Url(parts[1]);
    if (iv.length !== 12) return null;
    const plain = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv, additionalData: AAD },
      await sessionKey(cfg.sessionSecret),
      fromBase64Url(parts[2]),
    );
    session = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(plain));
  } catch {
    return null;
  }
  if (session === null || typeof session !== "object" || session.v !== 1) return null;
  if (!/^[0-9a-f]{32}$/.test(session.sid) || !isRaftId(session.sub) || !isRaftId(session.srv)) return null;
  if (typeof session.tok !== "string" || !session.tok || session.cid !== cfg.clientId) return null;
  if (typeof session.name !== "string" || typeof session.slug !== "string") return null;
  if (!Number.isInteger(session.exp) || session.exp * 1000 <= nowMs) return null;
  return session;
}

export function readCookie(request) {
  const header = request.headers.get("Cookie");
  if (!header) return null;
  for (const part of header.split(";")) {
    const i = part.indexOf("=");
    if (i < 0) continue;
    if (part.slice(0, i).trim() === COOKIE_NAME) return part.slice(i + 1).trim();
  }
  return null;
}

// Path=/ so the cookie reaches every action path, HttpOnly, SameSite=Strict, and Secure
// whenever the app runs on https. A local http origin needs the cookie without Secure.
export function sessionCookie(value, maxAge, cfg) {
  return `${COOKIE_NAME}=${value}; Path=/; Max-Age=${maxAge}; HttpOnly; SameSite=Strict${cfg.secureCookie ? "; Secure" : ""}`;
}

export function clearCookie(cfg) {
  return sessionCookie("", 0, cfg);
}

// Sessions Raft confirmed in the last 60 seconds, by session ID, in this isolate only.
const checked = new Map();

export function recentlyChecked(sid, nowMs) {
  const until = checked.get(sid);
  if (until === undefined) return false;
  if (until > nowMs) return true;
  checked.delete(sid);
  return false;
}

export function markChecked(sid, nowMs) {
  checked.delete(sid);
  checked.set(sid, nowMs + CHECK_TTL_MS);
  while (checked.size > MAX_CHECKED) checked.delete(checked.keys().next().value);
}

export function forgetChecked(sid) {
  checked.delete(sid);
}
