// Gearlist MCP server: read-only, stateless, no sign-in, Streamable HTTP.
//
// It serves both protocol eras on one endpoint, as the 2026-07-28 revision allows:
//   Modern (2026-07-28): no handshake. Each request carries its protocol version
//     and client capabilities in params._meta, mirrored in MCP-Protocol-Version,
//     Mcp-Method and Mcp-Name headers. server/discover is supported.
//   Legacy (2025-11-25, 2025-06-18, 2025-03-26): initialize, notifications and
//     ping, without sessions. Every tool answer is the same for every caller,
//     so no state is kept between requests in either era.
// Spec: https://modelcontextprotocol.io/specification/2026-07-28

import {
  MAX_ID, MAX_QUERY, MAX_STACK, NOTICE, SITE, REPO, STACK_LIMIT, loadCatalog, parseSearchArgs, searchPayload,
  lookup, gearPayload, parseStackArgs, stackPayload, categoriesPayload, skillsPayload, schemas,
} from "./catalog.mjs";
import { json, rateLimited, readBody, respond, sha256Hex } from "./http.mjs";

export const MODERN_VERSION = "2026-07-28";
export const LEGACY_VERSIONS = ["2025-11-25", "2025-06-18", "2025-03-26"];
export const SUPPORTED_VERSIONS = [MODERN_VERSION, ...LEGACY_VERSIONS];
export const SERVER_INFO = { name: "gearlist", title: "Gearlist", version: "1.0.0" };
export const MCP_URL = SITE + "/mcp";
export const MAX_BODY = 64 * 1024;
const TTL_MS = 3600000;

const META_VERSION = "io.modelcontextprotocol/protocolVersion";
const META_CAPABILITIES = "io.modelcontextprotocol/clientCapabilities";
const META_SERVER = "io.modelcontextprotocol/serverInfo";

const PARSE_ERROR = -32700;
const INVALID_REQUEST = -32600;
const METHOD_NOT_FOUND = -32601;
const INVALID_PARAMS = -32602;
const INTERNAL_ERROR = -32603;
const HEADER_MISMATCH = -32020;
const UNSUPPORTED_VERSION = -32022;
// Outside the JSON-RPC reserved range, where the MCP spec asks new codes to go.
const RATE_LIMITED = -31429;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers":
    "Content-Type, Accept, MCP-Protocol-Version, Mcp-Method, Mcp-Name, Mcp-Session-Id, Last-Event-ID",
  "Access-Control-Max-Age": "86400",
};
const RPC_HEADERS = { ...CORS, "Cache-Control": "no-store" };

class RpcError extends Error {
  constructor(code, message, status = 200, data) {
    super(message);
    this.code = code;
    this.status = status;
    this.data = data;
  }
}

function rpcResult(id, result) {
  return json({ jsonrpc: "2.0", id, result }, 200, RPC_HEADERS);
}

function rpcError(id, code, message, status, data, extra = {}) {
  const error = data === undefined ? { code, message } : { code, message, data };
  return json({ jsonrpc: "2.0", id, error }, status, { ...RPC_HEADERS, ...extra });
}

function methodNotAllowed(message) {
  return respond(message + "\n", 405, "text/plain; charset=utf-8", { ...CORS, Allow: "GET, POST, OPTIONS" });
}

export function instructions(catalog) {
  return (
    `Gearlist is a read-only catalog of ${catalog.entries.length} source-checked AI agent tools, MCP servers ` +
    "and skills, maintained by Tech Horizon Labs. Use search_gear to find entries, get_gear to read one, " +
    "list_categories for the groups, list_skills for the skills in the Gearlist repository and recommend_stack " +
    "for a short set of entries for one job. " +
    NOTICE
  );
}

const READ_ONLY = { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false };
const NO_ARGS = { type: "object", additionalProperties: false };

export function toolList(catalog) {
  const s = schemas(catalog);
  const tool = (name, title, description, inputSchema, outputSchema) => ({
    name, title, description, inputSchema, outputSchema, annotations: { title, ...READ_ONLY },
  });
  return [
    tool(
      "search_gear",
      "Search Gearlist",
      "Search the Gearlist catalog of source-checked AI agent tools, MCP servers and skills. Matches words in the " +
        "name, category, description, audience and access notes, best match first. Each result includes its access " +
        "notes, which you should show the human. Entries are documentation-checked only, not installed or audited.",
      {
        type: "object",
        properties: {
          query: {
            type: "string",
            maxLength: 200,
            description:
              "Words to look for, for example 'browser automation' or 'send email'. Entries that match every word " +
              "come first, then entries that match some of them. Common words such as 'the' or 'tool' are ignored. " +
              "Use an empty string with a category to list that category.",
          },
          category: {
            type: "string",
            enum: s.categoryNames,
            description: "Optional. Limit results to one category. list_categories gives the names and counts.",
          },
          limit: {
            type: "integer",
            minimum: 1,
            maximum: 50,
            default: 10,
            description: "How many entries to return, from 1 to 50. Default 10.",
          },
        },
        required: ["query"],
        additionalProperties: false,
      },
      s.search,
    ),
    tool(
      "get_gear",
      "Get a Gearlist entry",
      "Get one Gearlist entry by its id, as returned by search_gear, with what was checked and when. Entries are " +
        "documentation-checked only. Nothing was installed or audited.",
      {
        type: "object",
        properties: { id: { type: "string", maxLength: MAX_ID, description: "Entry id, for example 'playwright-mcp'." } },
        required: ["id"],
        additionalProperties: false,
      },
      s.gear,
    ),
    tool(
      "list_categories",
      "List Gearlist categories",
      "List the Gearlist categories with the number of entries in each.",
      NO_ARGS,
      s.categories,
    ),
    tool(
      "list_skills",
      "List Gearlist skills",
      "List the agent skills published in the Gearlist repository, with the command that installs each one. " +
        "Ask the human before running any install command.",
      NO_ARGS,
      s.skills,
    ),
    tool(
      "recommend_stack",
      "Find Gearlist entries for a job",
      "Find a short set of Gearlist entries whose own text shares the most words with a job you describe, spread " +
        "across groups, quoting where each match appears. Matches are on words, so check each entry suits the job " +
        "before suggesting it.",
      {
        type: "object",
        properties: {
          job: {
            type: "string",
            maxLength: MAX_QUERY,
            description:
              "The job in plain words, for example 'test my web app in a real browser'. Common words such as 'my' " +
              "or 'the' are ignored.",
          },
          limit: {
            type: "integer",
            minimum: 1,
            maximum: MAX_STACK,
            default: STACK_LIMIT,
            description: `How many entries to return, from 1 to ${MAX_STACK}. Default ${STACK_LIMIT}.`,
          },
        },
        required: ["job"],
        additionalProperties: false,
      },
      s.stack,
    ),
  ];
}

function toolResult(structured) {
  return {
    content: [
      { type: "text", text: NOTICE },
      { type: "text", text: JSON.stringify(structured, null, 2) },
    ],
    structuredContent: structured,
    isError: false,
  };
}

function toolError(message) {
  return { content: [{ type: "text", text: message + "\n\n" + NOTICE }], isError: true };
}

function unknownArgument(args, allowed, tool) {
  const extra = Object.keys(args).filter((k) => !allowed.includes(k));
  if (!extra.length) return null;
  const takes = allowed.length ? `takes ${allowed.join(", ")}` : "takes no arguments";
  return `Unknown argument: ${extra[0]}. ${tool} ${takes}.`;
}

export const TOOL_NAMES = ["search_gear", "get_gear", "list_categories", "list_skills", "recommend_stack"];

// What each tool does with its arguments, shared by this MCP server and the Raft App in
// raft-app/, so both give the same answer for the same input. `args` must already be a
// plain object and `name` one of TOOL_NAMES. Returns { value } with the structured
// result, or { error } with a plain message. An unknown get_gear id also sets `missing`.
export function runTool(catalog, name, args) {
  if (name === "search_gear") {
    const parsed = parseSearchArgs(catalog, args, true);
    return parsed.error ? { error: parsed.error } : { value: searchPayload(catalog, parsed.value) };
  }
  if (name === "get_gear") {
    const bad = unknownArgument(args, ["id"], name);
    if (bad) return { error: bad };
    if (typeof args.id !== "string" || !args.id.trim() || args.id.length > MAX_ID) {
      return { error: `id must be a non-empty string of ${MAX_ID} characters or fewer.` };
    }
    const found = lookup(catalog, args.id);
    if (found.entry) return { value: gearPayload(found.entry) };
    const near = found.suggestions.length ? ` Close matches: ${found.suggestions.join(", ")}.` : "";
    return {
      error: `No Gearlist entry has the id ${JSON.stringify(args.id)}.${near} Use search_gear to find ids.`,
      missing: true,
    };
  }
  if (name === "recommend_stack") {
    const parsed = parseStackArgs(args);
    return parsed.error ? { error: parsed.error } : { value: stackPayload(catalog, parsed.value) };
  }
  const bad = unknownArgument(args, [], name);
  if (bad) return { error: bad };
  return { value: name === "list_categories" ? categoriesPayload(catalog) : skillsPayload(catalog) };
}

async function callTool(params, env) {
  const name = params.name;
  if (typeof name !== "string") throw new RpcError(INVALID_PARAMS, "params.name must be the tool name.");
  if (!TOOL_NAMES.includes(name)) {
    throw new RpcError(INVALID_PARAMS, `Unknown tool: ${name}`);
  }
  const args = params.arguments === undefined || params.arguments === null ? {} : params.arguments;
  if (typeof args !== "object" || Array.isArray(args)) {
    throw new RpcError(INVALID_PARAMS, "params.arguments must be an object.");
  }
  const out = runTool(await loadCatalog(env), name, args);
  return out.error === undefined ? toolResult(out.value) : toolError(out.error);
}

async function listTools(params, env) {
  if (params.cursor !== undefined && params.cursor !== null) {
    throw new RpcError(INVALID_PARAMS, "Invalid cursor. This server returns every tool in one page.");
  }
  return { tools: toolList(await loadCatalog(env)) };
}

async function discover(env) {
  return {
    supportedVersions: SUPPORTED_VERSIONS,
    capabilities: { tools: {} },
    instructions: instructions(await loadCatalog(env)),
  };
}

function modernResult(result, cacheable) {
  const out = { resultType: "complete", ...result, _meta: { [META_SERVER]: SERVER_INFO } };
  if (cacheable) Object.assign(out, { ttlMs: TTL_MS, cacheScope: "public" });
  return out;
}

// Header values may use the =?base64?...?= form for non-ASCII names.
function decodeHeader(value) {
  if (value === null) return null;
  const m = /^=\?base64\?(.*)\?=$/.exec(value);
  if (!m) return value;
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(atob(m[1]), (c) => c.charCodeAt(0)));
  } catch {
    return undefined;
  }
}

async function modern(method, params, meta, request, env) {
  const header = request.headers.get("MCP-Protocol-Version");
  const version = meta ? meta[META_VERSION] : undefined;
  if (header === null) throw new RpcError(HEADER_MISMATCH, "The MCP-Protocol-Version header is missing.", 400);
  if (version !== undefined && version !== header) {
    throw new RpcError(
      HEADER_MISMATCH,
      `Header mismatch: MCP-Protocol-Version header '${header}' does not match body value '${version}'.`,
      400,
    );
  }
  if (LEGACY_VERSIONS.includes(header)) return legacy(method, params, env);
  if (header !== MODERN_VERSION) {
    throw new RpcError(UNSUPPORTED_VERSION, "Unsupported protocol version", 400, {
      supported: SUPPORTED_VERSIONS,
      requested: header,
    });
  }
  if (version === undefined) {
    throw new RpcError(INVALID_PARAMS, `params._meta["${META_VERSION}"] is required.`, 400);
  }
  const caps = meta[META_CAPABILITIES];
  if (caps === null || typeof caps !== "object" || Array.isArray(caps)) {
    throw new RpcError(INVALID_PARAMS, `params._meta["${META_CAPABILITIES}"] is required.`, 400);
  }
  const mcpMethod = request.headers.get("Mcp-Method");
  if (mcpMethod !== method) {
    const why = mcpMethod === null ? "The Mcp-Method header is missing." :
      `Header mismatch: Mcp-Method header '${mcpMethod}' does not match body value '${method}'.`;
    throw new RpcError(HEADER_MISMATCH, why, 400);
  }
  if (["tools/call", "prompts/get", "resources/read"].includes(method)) {
    const bodyName = method === "resources/read" ? params.uri : params.name;
    const name = decodeHeader(request.headers.get("Mcp-Name"));
    if (name === null) throw new RpcError(HEADER_MISMATCH, "The Mcp-Name header is missing.", 400);
    if (name !== bodyName) {
      throw new RpcError(HEADER_MISMATCH, "Header mismatch: Mcp-Name header does not match the body value.", 400);
    }
  }
  if (method === "server/discover") return modernResult(await discover(env), true);
  if (method === "tools/list") return modernResult(await listTools(params, env), true);
  if (method === "tools/call") return modernResult(await callTool(params, env), false);
  throw new RpcError(METHOD_NOT_FOUND, `Method not found: ${method}`, 404);
}

async function legacy(method, params, env) {
  if (method === "ping") return {};
  if (method === "tools/list") return listTools(params, env);
  if (method === "tools/call") return callTool(params, env);
  if (method === "server/discover") return modernResult(await discover(env), true);
  throw new RpcError(METHOD_NOT_FOUND, `Method not found: ${method}`);
}

async function initialize(params, env) {
  const requested = params.protocolVersion;
  return {
    protocolVersion: LEGACY_VERSIONS.includes(requested) ? requested : LEGACY_VERSIONS[0],
    capabilities: { tools: {} },
    serverInfo: SERVER_INFO,
    instructions: instructions(await loadCatalog(env)),
  };
}

// The endpoint is public, read-only and holds no user data, so any well-formed
// web origin may call it and CORS is open. The transport spec still asks servers
// to validate Origin, so a malformed value is refused with 403.
function badOrigin(request) {
  const origin = request.headers.get("Origin");
  if (origin === null) return false;
  try {
    const url = new URL(origin);
    return !(["https:", "http:"].includes(url.protocol) && url.origin === origin);
  } catch {
    return true;
  }
}

function acceptsJson(request) {
  const accept = request.headers.get("Accept");
  return !accept || /(^|,)\s*(application\/json|application\/\*|\*\/\*)\s*(;|,|$)/i.test(accept);
}

function info() {
  return `Gearlist MCP server

This is the read-only MCP endpoint for Gearlist, a source-checked catalog of AI agent tools, MCP servers and skills by Tech Horizon Labs. It speaks MCP over Streamable HTTP, so send JSON-RPC requests here with POST. It needs no sign-in and changes nothing.

Tools: search_gear, get_gear, list_categories, list_skills, recommend_stack.

Add it to Claude Code:
  claude mcp add --transport http gearlist ${MCP_URL}

Other clients, and a prompt to give your agent: ${SITE}/agent-prompt.txt
Server card: ${MCP_URL}/server-card
Plain JSON search: ${SITE}/api/search?q=browser
Source: ${REPO}

Entries are documentation-checked only. They were not installed, tested or security audited. Ask a human before installing anything.
`;
}

export async function handleMcp(request, env) {
  const method = request.method;
  if (method === "OPTIONS") return respond(null, 204, null, CORS);
  if (method === "GET" || method === "HEAD") {
    // A GET that asks for text/event-stream is an older client opening a stream. This server offers none.
    if (/text\/event-stream/i.test(request.headers.get("Accept") || "")) {
      return methodNotAllowed("This MCP server does not offer an SSE stream. Send JSON-RPC requests with POST.");
    }
    return respond(method === "HEAD" ? null : info(), 200, "text/plain; charset=utf-8", {
      ...CORS,
      "Cache-Control": "public, max-age=3600",
    });
  }
  if (method !== "POST") {
    return methodNotAllowed("This MCP server keeps no sessions. Send JSON-RPC requests with POST.");
  }
  if (badOrigin(request)) return rpcError(null, INVALID_REQUEST, "Origin not allowed.", 403);
  if (await rateLimited(request, env)) {
    return rpcError(null, RATE_LIMITED, "Too many requests. Wait a minute and try again.", 429, undefined, {
      "Retry-After": "60",
    });
  }
  const type = request.headers.get("Content-Type") || "";
  if (!/^application\/json\s*(;|$)/i.test(type.trim())) {
    return rpcError(null, INVALID_REQUEST, "Send the JSON-RPC message with Content-Type: application/json.", 415);
  }
  if (!acceptsJson(request)) {
    return rpcError(null, INVALID_REQUEST, "This server answers with application/json. Include it in Accept.", 406);
  }

  let message;
  try {
    const body = await readBody(request, MAX_BODY);
    if (body.tooLarge) {
      return rpcError(null, INVALID_REQUEST, `Request body is larger than ${MAX_BODY} bytes.`, 413);
    }
    message = JSON.parse(body.text);
  } catch {
    return rpcError(null, PARSE_ERROR, "Parse error: the body is not valid JSON.", 400);
  }
  if (Array.isArray(message)) {
    return rpcError(null, INVALID_REQUEST, "Batch requests are not supported. Send one message per POST.", 400);
  }
  if (message === null || typeof message !== "object" || message.jsonrpc !== "2.0") {
    return rpcError(null, INVALID_REQUEST, 'Invalid request: expected a JSON-RPC 2.0 object with "jsonrpc": "2.0".', 400);
  }
  if (typeof message.method !== "string") {
    const why = "result" in message || "error" in message
      ? "This server sends no requests, so it does not accept responses."
      : "Invalid request: method must be a string.";
    return rpcError(null, INVALID_REQUEST, why, 400);
  }
  // Notifications (no id) need no answer, and this server acts on none of them. The
  // 2026-07-28 revision defines no header rules for notifications, so only the
  // protocol version is checked: it must be supported and agree with _meta.
  if (!("id" in message)) {
    const header = request.headers.get("MCP-Protocol-Version");
    const p = message.params;
    const meta = p !== null && typeof p === "object" && p._meta !== null && typeof p._meta === "object" ? p._meta : {};
    const version = meta[META_VERSION];
    if (header !== null && version !== undefined && header !== version) {
      return rpcError(null, HEADER_MISMATCH,
        `Header mismatch: MCP-Protocol-Version header '${header}' does not match body value '${version}'.`, 400);
    }
    const requested = header !== null ? header : version;
    if (requested !== undefined && !SUPPORTED_VERSIONS.includes(requested)) {
      return rpcError(null, UNSUPPORTED_VERSION, "Unsupported protocol version", 400, {
        supported: SUPPORTED_VERSIONS,
        requested,
      });
    }
    return respond(null, 202, null, RPC_HEADERS);
  }
  const id = message.id;
  if (!(typeof id === "string" || Number.isInteger(id))) {
    return rpcError(null, INVALID_REQUEST, "Invalid request: id must be a string or an integer.", 400);
  }
  const params = message.params === undefined ? {} : message.params;
  if (params === null || typeof params !== "object" || Array.isArray(params)) {
    return rpcError(id, INVALID_PARAMS, "params must be an object.", 400);
  }

  try {
    const meta = params._meta !== null && typeof params._meta === "object" ? params._meta : undefined;
    const header = request.headers.get("MCP-Protocol-Version");
    let result;
    if (message.method === "initialize") {
      result = await initialize(params, env);
    } else if ((meta && META_VERSION in meta) || (header !== null && !LEGACY_VERSIONS.includes(header))) {
      result = await modern(message.method, params, meta, request, env);
    } else {
      result = await legacy(message.method, params, env);
    }
    return rpcResult(id, result);
  } catch (err) {
    if (err instanceof RpcError) return rpcError(id, err.code, err.message, err.status, err.data);
    return rpcError(id, INTERNAL_ERROR, "Internal error. Try again shortly.", 500);
  }
}

export function serverCard() {
  return {
    $schema: "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json",
    name: "build.gearlist/gearlist",
    version: SERVER_INFO.version,
    title: SERVER_INFO.title,
    description: "Search a source-checked catalog of AI agent tools, MCP servers and skills. Read-only.",
    websiteUrl: SITE + "/",
    repository: { url: REPO, source: "github", subfolder: "site/worker" },
    remotes: [{ type: "streamable-http", url: MCP_URL, supportedProtocolVersions: SUPPORTED_VERSIONS }],
  };
}

// The Server Card (MCP extension io.modelcontextprotocol/server-card, SEP-2127),
// at the reserved <streamable-http-url>/server-card location.
export async function handleServerCard(request) {
  const headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, If-None-Match",
    "Access-Control-Expose-Headers": "ETag",
    "Cache-Control": "public, max-age=3600",
  };
  if (request.method === "OPTIONS") return respond(null, 204, null, headers);
  if (request.method !== "GET" && request.method !== "HEAD") {
    return respond("Use GET.\n", 405, "text/plain; charset=utf-8", { ...headers, Allow: "GET, HEAD, OPTIONS" });
  }
  const body = JSON.stringify(serverCard(), null, 2);
  const etag = `"${(await sha256Hex(body)).slice(0, 32)}"`;
  headers.ETag = etag;
  const match = request.headers.get("If-None-Match");
  if (match && match.split(",").some((t) => t.trim().replace(/^W\//, "") === etag)) {
    return respond(null, 304, null, headers);
  }
  return respond(request.method === "HEAD" ? null : body, 200, "application/mcp-server-card+json", headers);
}
