# Gearlist Raft App

This folder makes Gearlist a Raft App. Agents on a Raft server where the app is installed sign in as themselves with Login with Raft. They then call the Gearlist tools as Raft actions, for example `raft integration invoke --service <client ID> --action search_gear`.

It is its own Cloudflare Worker, `gearlist-raft`, meant for https://raft.gearlist.build. It is separate from the `gearlist-site` Worker in `site/`. It is not live yet: the Worker has no route, and workers.dev and preview URLs are off.

## What it serves

| Path | What it does |
| --- | --- |
| `/` | A short public page: what the app is and how to install it. It is the manifest's `docs_url`. |
| `/.well-known/raft-agent-manifest.json` | The agent behaviour manifest (`raft-agent-manifest.v0`). |
| `/login/raft/callback` | The Login with Raft callback. Agents only. |
| `GET /api/raft/context` | `get_session_context`: who signed in, on which server, and when the session ends. The manifest's `context_check`. |
| `POST /api/raft/actions/search_gear` | The MCP tool `search_gear`. |
| `POST /api/raft/actions/get_gear` | The MCP tool `get_gear`. |
| `POST /api/raft/actions/recommend_stack` | The MCP tool `recommend_stack`. |
| `GET /api/raft/actions/list_categories` | The MCP tool `list_categories`. |
| `GET /api/raft/actions/list_skills` | The MCP tool `list_skills`. |

Actions that take parameters use POST with a JSON body. The others use GET. A success answers `{"ok": true, "result": ...}`. A refusal answers `{"ok": false, "error": {"code": ..., "message": ...}}`.

## How it works

1. **Sign-in.** The agent runs `raft integration login`. Raft sends its client to `/login/raft/callback?code=...`. The Worker exchanges the code at `https://api.raft.build/api/oauth/token` with HTTP Basic client authentication. It reads `/api/oauth/userinfo` and accepts the login only when `type` is `agent` and `client_id` is this app's. It then reads `/api/oauth/serverinfo?server_id=...`. Raft answers that call only when the app is available to that agent on that server. The callback refuses browser visits, links that carry a `state` value (this app never starts a browser sign-in), a person's login, a token issued to another app, and a server where the app is not available. Each refusal is typed JSON, `{"error": ..., "hint": ...}`, which the Raft CLI shows to the agent. A used or expired code gets a 409, so the CLI asks for a fresh one.
2. **Session.** On success the callback sets one cookie, `gearlist_raft_session`: `Path=/`, `HttpOnly`, `SameSite=Strict`, `Secure`, and `Max-Age` equal to the access token's lifetime, at most one hour. The cookie holds the session encrypted with AES-GCM under a key derived from `SESSION_SECRET`. The Raft access token is inside it, so the agent's client cannot read or change it. Raft issues no refresh token, so the agent signs in again after an hour. The response body never holds the token, the code or the cookie value.
3. **Every action.** The Worker opens the cookie. A missing, altered, expired or foreign session gets a 401. It then asks Raft again, through serverinfo, whether the app is still available to that agent on that server. It reuses a yes for at most 60 seconds, as the Login with Raft guide requires. If Raft refuses the token the answer is a 401, if Raft says the app is not available it is a 403, and either way the cookie is cleared. If Raft cannot be reached the answer is a 503. Nothing runs until these checks pass.
4. **Results.** The five Gearlist actions call `runTool` in `site/worker/mcp.mjs`, the same function the MCP server's `tools/call` uses, and read the same `resources.json` and `.well-known/agent-skills/index.json` through an `ASSETS` binding. So `result` is byte for byte the MCP tool's `structuredContent` for the same input, with the same notice, `next_step` text and access notes. Invalid input gets the MCP tool's own message. One transport difference: `limit` may also arrive as digits in a string, as `/api/search` already accepts.

The only network calls are the three Login with Raft calls above, to the Raft API origin in config. Redirects are refused, so the client secret and tokens never follow a `Location` header. There are no model calls and no writes. The Worker keeps no database. The only state is the rate limit counter, and a per-isolate list of sessions Raft confirmed in the last 60 seconds.

## Files

- `src/index.mjs`: routes, the callback, the session checks and the actions.
- `src/raft.mjs`: config, and the token, userinfo and serverinfo calls.
- `src/session.mjs`: the encrypted session cookie and the 60 second check cache.
- `src/manifest.mjs`: the manifest. Each Gearlist action copies its description and parameters from the MCP tool definition in `site/worker/mcp.mjs`.
- `src/home.mjs`: the home page.
- `scripts/copy-catalog.mjs`: copies the two catalog files from `site/dist` to `catalog/`. Wrangler runs it before `wrangler dev` and `wrangler deploy`.
- `test/app.test.mjs`: the tests.
- `wrangler.jsonc`: the Worker config. `.dev.vars.example`: local values for `wrangler dev`.

## Test

From the repository root:

```bash
python3 build.py && (cd site && python3 build_site.py)
node --test "site/test/*.test.mjs" "raft-app/test/*.test.mjs"
python3 -m unittest discover
```

The tests use `node:test` and no packages. They call the Worker's handler with a fake `ASSETS` that serves `site/dist` and a fake Raft API. They check the manifest, every refusal, the 60 second check, that each action's result equals the MCP tool's result for the same input, input validation, and that no secret, token or code reaches a response or a log.

## Run it locally

```bash
cd raft-app
cp .dev.vars.example .dev.vars   # then fill in values; .dev.vars is ignored by git
wrangler dev
```

`.dev.vars` sets `APP_ORIGIN=http://localhost:8787`, so the cookie is set without `Secure`. If your Wrangler does not support the 2026-11-01 compatibility date yet, pass an earlier one, for example `wrangler dev --compatibility-date 2026-09-10`. A real sign-in needs a registered app and a callback Raft can reach, so locally you can check the home page, the manifest and the refusals:

```bash
curl -s http://localhost:8787/.well-known/raft-agent-manifest.json
curl -s -X POST http://localhost:8787/api/raft/actions/search_gear -H "Content-Type: application/json" -d '{"query":"browser"}'
```

The second command answers 401 with `SESSION_REQUIRED`.

## Register in Raft

A server owner or admin registers the app once, under Settings, then Applications, then My Apps. An agent can prepare the same registration with `raft integration app prepare register`, which posts a card for an owner or admin to approve.

| Field | Value |
| --- | --- |
| App name | Gearlist |
| Description | Lets your agents search Gearlist, a source-checked list of AI agent tools, MCP servers and skills by Tech Horizon Labs, with read-only actions. It asks only for openid and profile, so each agent signs in as itself and the app knows which server it is on. |
| Category | Developer Tools |
| Homepage URL | https://raft.gearlist.build/ |
| Callback (return) URL | https://raft.gearlist.build/login/raft/callback |
| Agent manifest URL | https://raft.gearlist.build/.well-known/raft-agent-manifest.json |
| Scopes | `openid profile` |
| Setup page URL | None |

The callback URL must match byte for byte, with no trailing slash and no query.

## Deploy after registration

Run these from `raft-app/`, on account `4357dc09ae3d87062853043304b53fe6`.

1. Build the site and run the tests (see Test). The deploy copies the catalog from `site/dist`, so deploy this Worker again after each site deploy to keep the two in step.
2. Put the client ID Raft gave at registration in `vars.RAFT_CLIENT_ID` in `wrangler.jsonc`. It is not a secret.
3. Generate a client secret in Raft (the app owner does this; Raft shows it once), then store it and a session secret as Worker secrets. Never paste either into chat, a file in the repository or a command line that is logged.
   ```bash
   wrangler secret put RAFT_CLIENT_SECRET
   openssl rand -base64 48 | wrangler secret put SESSION_SECRET
   ```
   Changing `SESSION_SECRET` signs every agent out.
4. Check that rate limit `namespace_id` 4272 is not used by another Worker on the account.
5. Add the route to `wrangler.jsonc`: `"routes": [{ "pattern": "raft.gearlist.build", "custom_domain": true }]`.
6. Run `wrangler deploy`.
7. Check the live app:
   ```bash
   curl -sI https://raft.gearlist.build/ | grep -i content-security-policy
   curl -s https://raft.gearlist.build/.well-known/raft-agent-manifest.json | python3 -m json.tool | head -20
   curl -s https://raft.gearlist.build/api/raft/context
   ```
   The last command answers 401 with `SESSION_REQUIRED`. Then have one agent run `raft integration login --service <client ID>` and `raft integration invoke --service <client ID> --action get_session_context`. A successful action is the proof that sign-in works. A 200 from the callback alone does not prove it.

## Built from

The official scaffold, `create-raft-app` 0.2.0 on npm, template `hosted-http-action-service`. From it this app keeps the action envelope (`ok`, `result`, `error` with `code` and `message`), the structured errors and the request size limit. That template has no Login with Raft and serves a different manifest shape at `/.well-known/raft-app-manifest.json`. The Raft CLI reads `/.well-known/raft-agent-manifest.json` in the `raft-agent-manifest.v0` shape, as the Login with Raft guide and the package's `hono-react-cfworker` template define, so this app follows that. The callback path `/login/raft/callback` and the variable names `RAFT_CLIENT_ID`, `RAFT_CLIENT_SECRET`, `RAFT_API_ORIGIN` and `APP_ORIGIN` follow the guide and that template. `SESSION_SECRET` follows the package's Login with Raft templates.
