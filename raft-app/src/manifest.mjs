// The agent behaviour manifest (raft-agent-manifest.v0). Each Gearlist action copies its
// description and parameters from the matching MCP tool in site/worker/mcp.mjs, so the
// two surfaces describe the same tool in the same words.

import { toolList } from "../../site/worker/mcp.mjs";

export const MANIFEST_PATH = "/.well-known/raft-agent-manifest.json";
export const CALLBACK_PATH = "/login/raft/callback";
export const CONTEXT_PATH = "/api/raft/context";
export const ACTION_PREFIX = "/api/raft/actions/";

export const CONTEXT_DESCRIPTION =
  "Check this agent's Gearlist session: who signed in, on which Raft server, and when the session ends. " +
  "Call this first when another action is refused.";

export const DESCRIPTION =
  "Search Gearlist, a source-checked list of AI agent tools, MCP servers and skills by Tech Horizon Labs. " +
  "Each agent signs in as itself with Login with Raft. The actions only read the list. A server owner or admin " +
  "installs the app once for the whole server, in Raft under Settings, then Applications, or from the Install App " +
  "card an agent posts.";

// Actions with a `tool` run that Gearlist MCP tool. Actions that take parameters use POST
// with a JSON body. The others use GET.
export const ACTIONS = [
  { name: "get_session_context", tool: null, method: "GET", path: CONTEXT_PATH },
  { name: "search_gear", tool: "search_gear", method: "POST" },
  { name: "get_gear", tool: "get_gear", method: "POST" },
  { name: "recommend_stack", tool: "recommend_stack", method: "POST" },
  { name: "list_categories", tool: "list_categories", method: "GET" },
  { name: "list_skills", tool: "list_skills", method: "GET" },
].map((action) => ({ ...action, path: action.path || ACTION_PREFIX + action.name }));

function parameters(inputSchema) {
  const out = {};
  const required = inputSchema.required || [];
  for (const [name, spec] of Object.entries(inputSchema.properties || {})) {
    out[name] = { type: spec.type, description: spec.description };
    if (required.includes(name)) out[name].required = true;
  }
  return out;
}

function returns(tool) {
  return {
    ok: { type: "boolean", description: "True when the action ran." },
    result: {
      type: "object",
      description: tool
        ? `The same JSON as the ${tool} tool on the Gearlist MCP server returns.`
        : "Who signed in, on which Raft server, and when the session ends.",
    },
    error: { type: "object", description: "When ok is false: a code, and a message that says why." },
  };
}

export function buildManifest(cfg, catalog) {
  const tools = new Map(toolList(catalog).map((t) => [t.name, t]));
  const origin = cfg.appOrigin;
  const manifest = { schema: "raft-agent-manifest.v0", name: "Gearlist" };
  if (cfg.clientId) manifest.service = cfg.clientId;
  Object.assign(manifest, {
    description: DESCRIPTION,
    docs_url: origin + "/",
    app_origin: origin,
    execution: { mode: "http_api", base_url: origin },
    auth: { type: "login_with_raft" },
    actions: ACTIONS.map((action) => {
      const tool = action.tool ? tools.get(action.tool) : null;
      return {
        name: action.name,
        description: tool ? tool.description : CONTEXT_DESCRIPTION,
        endpoint: { method: action.method, path: action.path },
        parameters: tool ? parameters(tool.inputSchema) : {},
        returns: returns(action.tool),
      };
    }),
    context_check: { url: origin + CONTEXT_PATH, method: "GET" },
  });
  return manifest;
}
