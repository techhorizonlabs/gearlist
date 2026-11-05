// Small HTTP helpers shared by the Worker routes.

// _headers rules only reach static asset responses, so every response the
// Worker builds itself carries these. The page CSP from _headers is for HTML;
// JSON and text responses need none of it, so they get the strictest policy.
export const SECURITY_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Content-Security-Policy": "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
};

export function respond(body, status, type, extra = {}) {
  const headers = new Headers(SECURITY_HEADERS);
  if (type) headers.set("Content-Type", type);
  for (const [name, value] of Object.entries(extra)) headers.set(name, value);
  return new Response(body, { status, headers });
}

export function json(value, status = 200, extra = {}) {
  return respond(JSON.stringify(value), status, "application/json; charset=utf-8", extra);
}

export function addVary(headers, name) {
  const current = headers.get("Vary");
  if (!current) {
    headers.set("Vary", name);
  } else if (!current.split(",").some((v) => v.trim().toLowerCase() === name.toLowerCase())) {
    headers.set("Vary", current + ", " + name);
  }
}

// One shared per-IP budget for the MCP endpoint and the JSON API, through the
// Workers rate limiting binding. Without the binding (tests, some local runs)
// nothing is limited. A failing limiter lets the request through rather than
// taking the read-only service down.
export async function rateLimited(request, env) {
  const limiter = env && env.RATE_LIMITER;
  if (!limiter || typeof limiter.limit !== "function") return false;
  const key = request.headers.get("CF-Connecting-IP") || "unknown";
  try {
    const { success } = await limiter.limit({ key });
    return !success;
  } catch {
    return false;
  }
}

// Reads a request body up to `max` bytes. Returns { text } or { tooLarge: true }.
// Throws a TypeError when the bytes are not valid UTF-8.
export async function readBody(request, max) {
  const declared = request.headers.get("Content-Length");
  if (declared !== null && Number(declared) > max) return { tooLarge: true };
  if (!request.body) return { text: "" };
  const reader = request.body.getReader();
  const chunks = [];
  let size = 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > max) {
      await reader.cancel();
      return { tooLarge: true };
    }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, offset);
    offset += chunk.byteLength;
  }
  return { text: new TextDecoder("utf-8", { fatal: true }).decode(bytes) };
}

export async function sha256Hex(text) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
