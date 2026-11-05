// Gearlist Worker. Static assets serve almost every path. wrangler.jsonc sends
// only these paths here first (run_worker_first):
//   /                   HTML, or Markdown when the request prefers text/markdown
//   /mcp                the read-only MCP server (Streamable HTTP)
//   /mcp/server-card    the MCP Server Card
//   /api/*              a small JSON search API
//   /openapi.json       the OpenAPI description of that API
// Read-only: no stored data, no secrets, and no fetches beyond the ASSETS binding.
// The only state is the per-IP counter kept by the RATE_LIMITER binding.

import { NOTICE, SITE, REPO, loadCatalog, parseSearchArgs, searchPayload, schemas } from "./catalog.mjs";
import { SERVER_INFO, handleMcp, handleServerCard } from "./mcp.mjs";
import { addVary, json, rateLimited, respond } from "./http.mjs";

const API_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "X-Robots-Tag": "noindex",
};

// True when Accept names text/markdown and ranks it at least as high as HTML.
// A bare */* (curl, most crawlers) or a browser Accept still gets HTML.
export function prefersMarkdown(accept) {
  if (!accept) return false;
  const q = { md: 0, html: null, text: null, any: null };
  for (const part of accept.split(",")) {
    const [range, ...params] = part.split(";");
    let weight = 1;
    for (const param of params) {
      const [key, value] = param.split("=");
      if (key && key.trim().toLowerCase() === "q") {
        const n = Number(value);
        weight = Number.isFinite(n) ? n : 0;
      }
    }
    const type = range.trim().toLowerCase();
    const slot = { "text/markdown": "md", "text/x-markdown": "md", "text/html": "html", "text/*": "text", "*/*": "any" }[type];
    if (slot) q[slot] = Math.max(q[slot] || 0, weight);
  }
  const html = q.html ?? q.text ?? q.any ?? 0;
  return q.md > 0 && q.md >= html;
}

async function homepage(request, env) {
  if (request.method === "GET" || request.method === "HEAD") {
    if (prefersMarkdown(request.headers.get("Accept"))) {
      const md = await env.ASSETS.fetch(new Request(new URL("/index.md", request.url), request));
      if (md.status === 200 || md.status === 304) {
        const out = new Response(md.body, md);
        out.headers.set("Content-Type", "text/markdown; charset=utf-8");
        out.headers.set("Content-Location", "/index.md");
        addVary(out.headers, "Accept");
        return out;
      }
    }
    // The asset response keeps its _headers rules (CSP, Link and the rest).
    const page = await env.ASSETS.fetch(request);
    const out = new Response(page.body, page);
    addVary(out.headers, "Accept");
    return out;
  }
  return env.ASSETS.fetch(request);
}

async function apiSearch(request, env, url) {
  if (request.method === "OPTIONS") return respond(null, 204, null, API_HEADERS);
  if (request.method !== "GET" && request.method !== "HEAD") {
    return json({ error: "Use GET." }, 405, { ...API_HEADERS, Allow: "GET, HEAD, OPTIONS" });
  }
  if (await rateLimited(request, env)) {
    return json({ error: "Too many requests. Wait a minute and try again." }, 429, { ...API_HEADERS, "Retry-After": "60" });
  }
  const p = url.searchParams;
  const limit = p.get("limit");
  const args = {
    query: p.get("q") ?? "",
    category: p.get("category") ?? undefined,
    limit: limit === null ? undefined : /^\d{1,3}$/.test(limit) ? Number(limit) : NaN,
  };
  const catalog = await loadCatalog(env);
  const parsed = parseSearchArgs(catalog, args, false);
  if (parsed.error) return json({ error: parsed.error, notice: NOTICE }, 400, API_HEADERS);
  const body = request.method === "HEAD" ? null : JSON.stringify(searchPayload(catalog, parsed.value));
  return respond(body, 200, "application/json; charset=utf-8", { ...API_HEADERS, "Cache-Control": "public, max-age=300" });
}

export function openApi(catalog) {
  const s = schemas(catalog);
  const error = {
    description: "The request was refused. The message says why.",
    content: { "application/json": { schema: { $ref: "#/components/schemas/Error" } } },
  };
  return {
    openapi: "3.1.0",
    info: {
      title: "Gearlist search API",
      version: SERVER_INFO.version,
      description:
        "Read-only search over Gearlist, a source-checked catalog of AI agent tools, MCP servers and skills by " +
        "Tech Horizon Labs. The same search is available as the MCP tool search_gear at " + SITE + "/mcp. " + NOTICE,
      license: { name: "MIT", identifier: "MIT" },
      contact: { name: "Tech Horizon Labs", url: REPO },
    },
    servers: [{ url: SITE }],
    externalDocs: { description: "Agent prompt and MCP setup", url: SITE + "/agent-prompt.txt" },
    paths: {
      "/api/search": {
        get: {
          operationId: "searchGear",
          summary: "Search Gearlist entries",
          description:
            "Matches the words of q against the name, category, description, audience and access notes. Entries " +
            "that match every word come first, then entries that match some of them, and match is then partial.",
          parameters: [
            {
              name: "q",
              in: "query",
              description: "Words to look for. May be empty when category is set.",
              schema: { type: "string", maxLength: 200 },
            },
            {
              name: "category",
              in: "query",
              description: "Optional. Limit results to one category.",
              schema: { type: "string", enum: s.categoryNames },
            },
            {
              name: "limit",
              in: "query",
              description: "How many entries to return.",
              schema: { type: "integer", minimum: 1, maximum: 50, default: 10 },
            },
          ],
          responses: {
            200: {
              description: "Matching entries, best first.",
              content: { "application/json": { schema: { $ref: "#/components/schemas/SearchResult" } } },
            },
            400: error,
            429: error,
          },
        },
      },
    },
    components: {
      schemas: {
        Entry: s.entry,
        SearchResult: {
          ...s.search,
          properties: { ...s.search.properties, results: { type: "array", items: { $ref: "#/components/schemas/Entry" } } },
        },
        Error: {
          type: "object",
          properties: { error: { type: "string" }, notice: { type: "string" } },
          required: ["error"],
        },
      },
    },
  };
}

async function route(request, env, url) {
  const path = url.pathname;
  if (path === "/") return homepage(request, env);
  if (path === "/mcp" || path === "/mcp/") return handleMcp(request, env);
  if (path === "/mcp/server-card") return handleServerCard(request);
  if (path === "/api/search") return apiSearch(request, env, url);
  if (path.startsWith("/api/")) {
    return json({ error: "Not found. The API is GET /api/search, described at /openapi.json." }, 404, API_HEADERS);
  }
  if (path === "/openapi.json" && (request.method === "GET" || request.method === "HEAD")) {
    const body = request.method === "HEAD" ? null : JSON.stringify(openApi(await loadCatalog(env)), null, 2);
    return respond(body, 200, "application/json; charset=utf-8", {
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "public, max-age=3600",
    });
  }
  return env.ASSETS.fetch(request);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    let response;
    try {
      response = await route(request, env, url);
    } catch {
      response = json({ error: "Internal error. Try again shortly." }, 500, { "Cache-Control": "no-store" });
    }
    // Keep preview hosts out of search results, as _headers does for assets.
    if (url.hostname.endsWith(".workers.dev") && !response.headers.has("X-Robots-Tag")) {
      response = new Response(response.body, response);
      response.headers.set("X-Robots-Tag", "noindex");
    }
    return response;
  },
};
