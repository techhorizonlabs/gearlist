# Gearlist

![Gearlist](social-preview.png)

A source-checked stack of agent tools, MCP servers and skills. Each entry says what it is, who it is for, and the access it needs, so a person can scan it and an agent can load it.

By Tech Horizon Labs. This edition contains 60 entries. Documentation checked means the source was read. It does not mean the software was installed, tested or security audited. Entries are grouped by purpose, in no particular order.

## How to use this

- Human: scan the groups below. The heading is the product. **For** is the audience. **Access and use** is the permission note.
- Agent: load [llms.txt](llms.txt) first, then [llms-full.txt](llms-full.txt) or [resources.json](resources.json). [AGENTS.md](AGENTS.md) is the house rules. Do not install from a row until a human authorises it.

Install the catalog skill with:

```bash
npx skills add techhorizonlabs/gearlist
```

## Contents

- [Agent tools](#agent-tools) (25)
- [MCP and integrations](#mcp-and-integrations) (11)
- [Security and governance](#security-and-governance) (4)
- [Platforms](#platforms) (4)
- [Protocols](#protocols) (1)
- [Skills and learning](#skills-and-learning) (15)


## Agent tools

### [Agent Deck](https://agentdeck.site/)

A Mac interface for coding agent sessions, project context and skills.

**For:** Developers coordinating coding sessions.

**Access and use:** Sessions may run tools with access to local files and connected services.

**Source checked:** 2026-10-25. [Official source](https://agentdeck.site/).

### [Hunk](https://hunk.dev/)

A terminal interface for reviewing code changes with agent notes beside the diff.

**For:** Developers reviewing agent generated changes.

**Access and use:** Review changes before applying them; installation and repository access are separate decisions.

**Source checked:** 2026-10-25. [Official source](https://hunk.dev/).

### [Jevgrep](https://github.com/dzhng/jevgrep)

Search a codebase with a question and receive relevant files and source excerpts.

**For:** Coding agents and developers exploring an unfamiliar repository.

**Access and use:** Requires an AI provider connection; check what repository content is sent to that provider.

**Source checked:** 2026-10-25. [Official source](https://github.com/dzhng/jevgrep).

### [Needle](https://github.com/cactus-compute/needle)

Models and runtimes for local tool calling, structured extraction and embeddings.

**For:** Developers building applications on devices.

**Access and use:** Your application defines and executes the tools; constrain their permissions.

**Source checked:** 2026-10-25. [Official source](https://github.com/cactus-compute/needle).

### [Firecrawl](https://github.com/firecrawl/firecrawl)

Crawl and scrape sites into markdown and structured data for agents.

**For:** Agents and developers who need page content from the public web.

**Access and use:** The hosted API needs a key and spends credits. AGPL-3.0 on the open repository. Do not scrape sites that forbid it. LinkedIn and similar sites may be blocked.

**Source checked:** 2026-10-26. [Official source](https://github.com/firecrawl/firecrawl).

### [REA](https://github.com/morluto/rea)

A local MCP and CLI for investigating application behaviour, from JavaScript bundles to native binaries.

**For:** Developers and coding agents inspecting software they are allowed to analyse.

**Access and use:** Install with npx rea-agents@latest setup. Setup shows a plan and asks before writing agent config or installing Hopper. Native and runtime workflows can execute or attach to programs. DISCLAIMER.md forbids DRM circumvention and copying proprietary software. MIT. npm package rea-agents. MCP registry name io.github.morluto/rea.

**Source checked:** 2026-10-26. [Official source](https://github.com/morluto/rea).

### [OpenCLI](https://opencli.info/)

A CLI and Chrome Browser Bridge that lets agents navigate, click, fill forms and extract from sites through a logged-in Chrome profile.

**For:** People whose agents need to operate websites they are already signed into, or reuse site-specific CLI adapters.

**Access and use:** Install npm package @jackwener/opencli (Node.js 20.18.1 or later) or the desktop app, plus the OpenCLI Chrome extension. Browser commands act through the signed-in Chrome profile, including cookies for the target site. Treat that as the same access the person has in the browser. Apache-2.0. Skills install with npx skills add jackwener/opencli.

**Source checked:** 2026-10-27. [Official source](https://github.com/jackwener/OpenCLI).

### [Graphify](https://www.graphify.com)

Turns a codebase, docs, SQL schemas, configs and PDFs into a local queryable knowledge graph for coding agents.

**For:** People whose agents need a map of a repository without sending the tree to a hosted vector store.

**Access and use:** Install the CLI with uv tool install graphifyy, then graphify install. It reads local project files and writes graphify-out. Apache-2.0.

**Source checked:** 2026-10-27. [Official source](https://github.com/Graphify-Labs/graphify).

### [OpenContext](https://0xranx.github.io/OpenContext/en/)

A local GUI and CLI that stores project context, skills and notes so a coding agent can reuse them across sessions.

**For:** People who already run Claude Code, Codex or OpenCode and want a persistent memory for that work.

**Access and use:** Install with npm install -g @aicontextlab/cli, then oc init in a project. Desktop app from GitHub releases. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/0xranx/OpenContext).

### [Stash](https://joinstash.ai)

Captures agent runs and human corrections, then serves that history back as knowledge, skills, REST, MCP and a CLI.

**For:** Teams whose agents should remember lessons from earlier work.

**Access and use:** Python client is pip install stash-sdk. It reads STASH_API_KEY and optional STASH_URL. The GitHub repo is MIT. Hosted and self-hosted paths are separate accounts.

**Source checked:** 2026-10-28. [Official source](https://github.com/Fergana-Labs/stash).

### [Browsentic](https://browsentic.com)

An agentic browser harness: a desktop app, npm CLI and Chrome or Firefox extension that lets an agent drive a signed-in browser.

**For:** People whose agents need to use the browser they already use, including logged-in sites.

**Access and use:** Installer is curl -fsSL https://browsentic.com/install.sh | sh. Read the script before running it. Or npx browsentic@latest setup. The extension acts through the signed-in browser. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/imshaikot/browsentic).

### [Trail-code](https://github.com/trailhq/Trail-Code)

A local map of a codebase plus team learnings, so coding agents go to the right files and pick up earlier decisions.

**For:** People running Claude Code, Cursor, Codex or similar on a repository they control.

**Access and use:** Install with npm install -g @trailhq/trail-code && trail init. It reads the repo on the machine and writes .trail/. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/trailhq/Trail-Code).

### [obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)

A local markdown vault an agent can grow, lint and query as a digital brain.

**For:** People who want durable notes an agent can read and write in a folder they own.

**Access and use:** Install with pip install obsidian-wiki, then obsidian-wiki setup --vault ~/brain. MIT. The vault is local files.

**Source checked:** 2026-10-28. [Official source](https://github.com/Ar9av/obsidian-wiki).

### [earshot](https://github.com/Leonxlnx/earshot)

A local CLI, Python API and MCP server that lets coding agents describe, score and generate sound on CPU.

**For:** People whose agents make or review audio, film or game sound without a GPU.

**Access and use:** Python 3.10 or later and ffmpeg on PATH. Clone the repo, venv, CPU torch, then pip install -e ".[mcp,llm,dev]". First model use downloads about 1.1 GB into a local cache. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/Leonxlnx/earshot).

### [PromptDirector](https://github.com/wchao6891/PromptDirector)

A free local-first Chrome extension that saves images, prompts and references from the web for later reuse.

**For:** People collecting visual and prompt references while they browse.

**Access and use:** Chrome Web Store listing iahakaahijddcjjldidbclicedibgpjm. Optional local video component. Apache-2.0. Treat saved pages as the same access the signed-in browser has.

**Source checked:** 2026-10-28. [Official source](https://github.com/wchao6891/PromptDirector).

### [ECC](https://ecc.tools)

An agent harness that adds planning, review, memory, skills and AgentShield security scanning to Claude Code and other coding agents.

**For:** People running Claude Code, Codex or similar who want that workflow installed once rather than restated every session.

**Access and use:** Guided setup is npx ecc-universal@2.2.3 setup (Node.js 18 or later). Claude Code plugin is ecc@ecc from github.com/affaan-m/ECC. Install only from those official sources. Hooks run with the agent's permissions. OSS is MIT. ECC Pro GitHub App is a separate paid product for private repos.

**Source checked:** 2026-10-28. [Official source](https://github.com/affaan-m/ECC).

### [Agent Reach](https://github.com/Panniantong/Agent-Reach)

A CLI that gives coding agents read access to platforms generic web search misses, including GitHub, YouTube, Bilibili, V2EX and login-walled social sites.

**For:** People whose agents need those sources, including Chinese platforms and logged-in feeds.

**Access and use:** Point the agent at https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md. The PyPI package named agent-reach is a different project. Login channels copy that site's Chrome session into a dedicated local browser; they do not read the password store. Prefer a secondary account. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/Panniantong/Agent-Reach).

### [Ruflo](https://github.com/ruvnet/ruflo)

An agent harness around Claude Code and Codex: plugins, a console, optional MCP, and coordinated multi-agent workflows.

**For:** People who want swarm, memory and policy tools on top of an existing coding agent.

**Access and use:** Prefer npx ruflo@latest init wizard, or in Claude Code /plugin marketplace add ruvnet/ruflo. There is also curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh | bash. Read the script before running it. Mods run with your account's permissions; review them before installing. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/ruvnet/ruflo).

### [agentglass](https://sirallap.github.io/agentglass/)

A local desktop workspace that gathers coding-agent terminals, diffs, pull requests, approvals and a browser they can drive into one window.

**For:** People running Claude Code, Codex, Gemini CLI or OpenCode on their own machine, often several at once.

**Access and use:** Download from GitHub releases. macOS builds are unsigned. Opening it is your call. Data stays in local SQLite. Agents run with your permissions. It controls what they can approve, but it doesn't sandbox them. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/SirAllap/agentglass).

### [Oya Browser](https://oyabrowser.com)

A browser people and agents share: desktop app, Node SDK, remote MCP, and optional self-host, with human takeover when a task needs it.

**For:** People whose agents need a signed-in browser they can watch and take over.

**Access and use:** Desktop app from oyabrowser.com. SDK is npm install @oya-ai/browser with OYA_API_KEY. Remote MCP is https://oyabrowser.com/mcp/pool with that key. Self-host installer is curl -fsSL https://raw.githubusercontent.com/OyadotAI/oya-browser/main/install.sh | sh. Read the script before running it. Can reuse logins imported from Chrome, Arc, Brave, Edge or Firefox. SDK and CLI are MIT. The rest of the project is under the Sustainable Use License.

**Source checked:** 2026-10-28. [Official source](https://github.com/OyadotAI/oya-browser).

### [apra-fleet](https://github.com/Apra-Labs/apra-fleet)

A local control plane that registers real machines as fleet members and runs durable multi-agent workflows across Claude, Codex, Copilot and other providers.

**For:** People coordinating coding agents on more than one machine they already own.

**Access and use:** Requires Node.js 22.16 or later. npm install -g @apralabs/apra-fleet, then apra-fleet install and apra-fleet start. MCP is http://localhost:7523/mcp by default. Secrets are entered out of band and never shown to the model. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/Apra-Labs/apra-fleet).

### [CodeGraph](https://colbymchenry.github.io/codegraph/)

A local code knowledge graph that answers with symbols, call paths and blast radius so coding agents spend fewer file reads.

**For:** People whose Claude Code, Cursor, Codex, Gemini, OpenCode, Copilot or similar agent needs a live map of a repository.

**Access and use:** Install with npm i -g @colbymchenry/codegraph, then codegraph install and, in each project, codegraph init. The README also offers curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh. Read the script before running it. Indexes live in .codegraph/ as local SQLite. The installer asks about anonymous usage telemetry; turn it off with codegraph telemetry off. Hosted product waitlist is getcodegraph.com. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/colbymchenry/codegraph).

### [Jev Ultrafast](https://github.com/browser-use/jev-ultrafast)

A local Chrome agent from Browser Use. One model chooses each click or field, and a smaller model writes text only when a field needs typing.

**For:** People who want a Chrome agent for a single goal, with a local inspector they can pause before a click.

**Access and use:** Clone the repo, uv sync, then set TYPESAFE_API_KEY and TEXT_MODEL_API_KEY in .env. TEXT_MODEL_API_KEY is an OpenRouter key in the example. Chrome connects through Browser Harness; allow remote debugging when prompted. Owned tabs share your existing Chrome profile. Local inspector is http://127.0.0.1:8766. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/browser-use/jev-ultrafast).

### [Boop](https://github.com/chrisgreg/boop)

A self-hosted notification inbox: apps POST events, they land in local SQLite, and an iOS app you build can show them on your phone.

**For:** Developers and agents that need a private event inbox they run themselves.

**Access and use:** Clone then docker compose up, or run a GitHub release binary. Data lives in a local SQLite file. APNs credentials are optional. Set BOOP_ADMIN_USER and BOOP_ADMIN_PASSWORD for the web UI, or put the server behind your own proxy. Read-only MCP is POST /mcp with BOOP_MCP_TOKEN; Settings can turn that endpoint off. You build and sign the iOS app. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/chrisgreg/boop).

### [Laya](https://nandhakishorm.github.io/laya/)

A local decision model that answers typed choice, score and yes/no questions over text in one forward pass, with a router that picks a checkpoint per request.

**For:** People whose agents need typed choice, score or yes/no answers over text.

**Access and use:** Python 3.10 or later. python -m pip install laya. The first predict downloads a Hugging Face checkpoint. Optional MCP: pip install "laya[mcp]" then laya-mcp-server. Optional HTTP playground: pip install "laya[serve]". Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/NandhaKishorM/laya).

## MCP and integrations

### [Are you found by AI? MCP server](https://github.com/techhorizonlabs/foundbyai-mcp)

Connect an MCP client to saved AI visibility measurements and evidence. Tech Horizon Labs project.

**For:** Businesses and agencies using their own AI to inspect visibility data.

**Access and use:** Account access is scoped by the connection. Review the rescan action separately from read tools.

**Source checked:** 2026-10-25. [Official source](https://github.com/techhorizonlabs/foundbyai-mcp).

### [gogcli](https://gogcli.sh/)

A command line interface for Google Workspace services with structured output.

**For:** People and agents automating Workspace tasks.

**Access and use:** OAuth scopes can allow reads and writes. Choose the account and access needed for the task.

**Source checked:** 2026-10-25. [Official source](https://gogcli.sh/).

### [GitHub MCP Server](https://github.com/github/github-mcp-server)

GitHub's official MCP server for repositories, issues, pull requests and Actions.

**For:** Agents and developers working on GitHub data they are allowed to access.

**Access and use:** Needs a GitHub OAuth login or personal access token. Scopes can read and write repositories. Use a read-only token unless a write is required.

**Source checked:** 2026-10-26. [Official source](https://github.com/github/github-mcp-server).

### [GitMCP](https://gitmcp.io/)

A remote MCP server that turns a public GitHub project into documentation an agent can query.

**For:** People pointing an agent at a public repository without cloning it.

**Access and use:** Works on public GitHub content. Last upstream push observed 2026-05-08. Confirm the target repo is public before connecting.

**Source checked:** 2026-10-26. [Official source](https://github.com/idosal/git-mcp).

### [XERJ](https://xerj.org)

A local-first search engine and MCP server that indexes code, docs, logs and PDFs for agents.

**For:** People who want cited local search and agent memory without a hosted search cluster.

**Access and use:** Installer is curl -fsSL https://xerj.org/get | sh. Read the script before running it. The binary indexes local paths and can serve an Elasticsearch-compatible API on localhost. Apache-2.0.

**Source checked:** 2026-10-27. [Official source](https://github.com/xerj-org/xerj).

### [Supabase MCP](https://supabase.com/docs/guides/ai-tools/mcp)

Supabase's official remote MCP server for docs, account, database, functions and related project tools.

**For:** Developers whose agents need to work on a Supabase project they control.

**Access and use:** Remote URL https://mcp.supabase.com/mcp with OAuth. Can list, query and change project data. Read Supabase's MCP security notes and restrict feature groups before connecting production.

**Source checked:** 2026-10-27. [Official source](https://supabase.com/docs/guides/ai-tools/mcp).

### [Notion MCP](https://developers.notion.com/guides/mcp/overview)

Notion's hosted MCP server for searching, reading, creating and updating pages and databases in a workspace the user can access.

**For:** People whose agents need live Notion context they already have permission to see.

**Access and use:** Remote URL https://mcp.notion.com/mcp with OAuth. Can read and write workspace content. Workspace owners can manage which clients connect. Prefer the hosted server over the unmaintained self-hosted repo.

**Source checked:** 2026-10-27. [Official source](https://developers.notion.com/guides/mcp/get-started-with-mcp).

### [Cloudflare MCP](https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/)

Cloudflare's hosted API MCP server covering DNS, Workers, R2, Zero Trust and the rest of the Cloudflare API, plus docs search.

**For:** People whose agents work on a Cloudflare account they control.

**Access and use:** Remote URL https://mcp.cloudflare.com/mcp with OAuth, or a scoped API token as a bearer. Can change account configuration. Grant the smallest permission set. Other product-specific Cloudflare MCP URLs exist; this is the main API server.

**Source checked:** 2026-10-27. [Official source](https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/).

### [OmniSeek](https://github.com/Battam1111/omniseek)

A local MCP add-on that searches places web search often misses, including Bilibili, Zhihu and scholarly papers.

**For:** People whose agents need those sources in Claude Code, Cursor or Codex.

**Access and use:** Install with uv tool install omniseek, then claude mcp add omniseek -- omniseek. Runs on your computer. Apache-2.0. Python 3.11 or later.

**Source checked:** 2026-10-28. [Official source](https://github.com/Battam1111/omniseek).

### [Context Mode](https://github.com/mksglu/context-mode)

An MCP server and hooks layer that sandboxes large tool output, keeps a local session index, and can run analysis scripts so agents do not dump whole files into context.

**For:** People running Claude Code or other supported clients whose context windows fill with tool output.

**Access and use:** In Claude Code: /plugin marketplace add mksglu/context-mode then /plugin install context-mode@context-mode. MCP-only: claude mcp add context-mode -- npx -y context-mode. ctx_execute can run code on your machine. Elastic License 2.0: you may not offer it as a hosted service that exposes its features.

**Source checked:** 2026-10-28. [Official source](https://github.com/mksglu/context-mode).

### [jCodeMunch MCP](https://github.com/jgravelle/jcodemunch-mcp)

A local MCP server that indexes a codebase with tree-sitter and returns the function or class an agent asked for, instead of whole files.

**For:** People whose coding agents spend context reading large files in Claude Code, Cursor, Codex or other MCP clients.

**Access and use:** Install with uv tool install jcodemunch-mcp, then jcodemunch-mcp init. Indexes live at ~/.code-index/. Free for personal use. Commercial use needs a paid licence. Default install sends an anonymous savings counter; set share_savings false to opt out.

**Source checked:** 2026-10-28. [Official source](https://github.com/jgravelle/jcodemunch-mcp).

## Security and governance

### [CISO AI](https://cisoai.au/)

Security briefings, analysis and governance resources.

**For:** Teams following security developments and governance topics.

**Access and use:** Read the linked primary sources and check dates before using advice in an operational decision.

**Source checked:** 2026-10-25. [Official source](https://cisoai.au/).

### [node9](https://node9.ai/)

Access control for AI agents. It decides what Claude Code, Codex, Gemini, Cursor and MCP servers may do, and can block or review risky actions.

**For:** People running coding agents against Slack, GitHub, email, files or databases.

**Access and use:** Install with brew tap node9-ai/node9 && brew install node9, or npm install -g node9-ai. Needs Node.js 22 or later. Local protection needs no account. Optional dashboard login. Apache-2.0.

**Source checked:** 2026-10-27. [Official source](https://github.com/node9-ai/node9-proxy).

### [ClawSecCheck](https://github.com/gl0di/clawseccheck)

A local, read-only security audit for an OpenClaw agent. It looks for config, prompt-injection and supply-chain risks and can vet a skill before install.

**For:** People running OpenClaw who want a local A to F grade without sending config off the machine.

**Access and use:** Python 3.10 or later. Install with pipx from the GitHub repo. The scanner reports and does not change OpenClaw config. Official docs say the scanner makes no network calls. MIT.

**Source checked:** 2026-10-27. [Official source](https://github.com/gl0di/clawseccheck).

### [GuardStein](https://guardstein.com/)

A document and deal room service that describes browser encryption and controlled sharing.

**For:** Teams evaluating document sharing for deals and reviews.

**Access and use:** Encryption claims are the provider's. Review its security model and recovery process before uploading sensitive documents.

**Source checked:** 2026-10-25. [Official source](https://guardstein.com/).

## Platforms

### [Raft](https://github.com/botiverse/raft-source)

A shared workspace where people and persistent AI agents collaborate in messages and tasks.

**For:** Teams working with agents across projects and machines.

**Access and use:** Source available under FSL, not an unrestricted open source licence. Agents need explicit access to their tools and data.

**Source checked:** 2026-10-25. [Official source](https://github.com/botiverse/raft-source).

### [Official MCP Registry](https://registry.modelcontextprotocol.io)

The official hosted registry of publicly available Model Context Protocol servers, with a REST API and server.json metadata.

**For:** MCP clients, aggregators and people looking up a server by name.

**Access and use:** The registry is in preview. Breaking changes or data resets may occur before general availability. Listing a server is not a security audit. Installing a listed server still needs its own credentials and terms.

**Source checked:** 2026-10-26. [Official source](https://modelcontextprotocol.io/registry/about).

### [OmniRoute](https://github.com/cheaper-inference/OmniRoute)

A local AI gateway that routes coding tools to many provider accounts through one OpenAI-compatible endpoint.

**For:** People who already have provider accounts and want one local endpoint with fallback.

**Access and use:** Install with npm install -g omniroute. It runs locally (default http://localhost:20128). Bring your own provider credentials. OmniRoute does not grant tokens. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/cheaper-inference/OmniRoute).

### [Overmind](https://www.overmindlab.ai/)

A hosted or self-hosted platform that turns production traces into evals, prompt experiments and fine-tuned models for an agent you already run.

**For:** Teams who want to train and score a specialised agent from their own traces.

**Access and use:** SDK and CLI: pip install overmind, then overmind init and overmind sync. Hosted console is console.overmindlab.ai with a project API key. MCP is https://api.overmindlab.ai/api/mcp/ with X-Api-Key. Self-host is docker compose; the API needs OpenRouter, Modal, AWS and Hugging Face keys before it boots. SDK and CLI are MIT. The platform is AGPL-3.0. SDK and CLI send anonymous usage to PostHog; opt out with OVERMIND_ANALYTICS_ENABLED=false or DO_NOT_TRACK=1.

**Source checked:** 2026-10-28. [Official source](https://github.com/overmind-core/overmind).

## Protocols

### [x402](https://x402.org/)

An open protocol for payments over HTTP using the 402 response.

**For:** Developers building services that charge per request.

**Access and use:** Connecting a payment client can spend funds. Set explicit transaction limits.

**Source checked:** 2026-10-25. [Official source](https://x402.org/).

## Skills and learning

### [THL Open](https://github.com/techhorizonlabs/thl-open)

Agent skills and reporting tools for AI readiness audits and fix plans. Tech Horizon Labs project.

**For:** Agencies, consultants and teams evaluating their own or authorised client sites.

**Access and use:** Skills may use external services or scan a site. Obtain target permission and review dependencies before running them.

**Source checked:** 2026-10-25. [Official source](https://github.com/techhorizonlabs/thl-open).

### [AGENTS.md](https://agents.md)

An open markdown format at the root of a repository that tells coding agents how the project works.

**For:** Repository maintainers and coding agents.

**Access and use:** A file in a clone. It does not grant credentials. Agents that read it will follow those instructions, so keep secrets out of it.

**Source checked:** 2026-10-26. [Official source](https://github.com/agentsmd/agents.md).

### [npx skills](https://github.com/vercel-labs/skills)

A command line installer that copies Agent Skills (SKILL.md folders) into the skill directories of local coding agents.

**For:** People installing portable skills into Claude Code, Codex, Cursor and similar agents.

**Access and use:** Writes files onto the machine. Treat a skill as untrusted code and instructions until you have read it. Example: npx skills add techhorizonlabs/thl-open.

**Source checked:** 2026-10-26. [Official source](https://github.com/vercel-labs/skills).

### [Anthropic skills](https://github.com/anthropics/skills)

Public Agent Skills from Anthropic for coding agents that read SKILL.md.

**For:** People installing first-party examples of the Agent Skills format.

**Access and use:** Public git clone or npx skills add. GitHub licence field was empty on 26 October 2026. Read the repository licence files before reuse.

**Source checked:** 2026-10-26. [Official source](https://github.com/anthropics/skills).

### [Hyperresearch](https://github.com/jordan-gibbs/hyperresearch)

A deep research skill and CLI that collects web and scholarly sources into a persistent vault and writes a cited report.

**For:** People running long research jobs in Claude Code or Codex, or using the hosted site.

**Access and use:** pip install writes skills, hooks and project files. Runs need network and write access. Hosted product at hyperresearch.ai is a separate account. MIT. Check what the vault stores before pointing it at private material.

**Source checked:** 2026-10-27. [Official source](https://github.com/jordan-gibbs/hyperresearch).

### [Tech Horizon Academy](https://academy.techhorizonlabs.com/)

A free academy of Claude skills, prompts and AI tools for Australian small businesses. Tech Horizon Labs project.

**For:** Australian operators and the agents they run.

**Access and use:** Public site. Skills and prompts are instructions; tools in the directory may need their own accounts. Indexes on 27 Oct 2026: 67 skills, 206 tools, 1217 prompt titles. Indexes are names and notes, not skill bodies or prompt text. Some academy tool pages carry partner flags; Gearlist omits referral parameters.

**Source checked:** 2026-10-27. [Official source](https://academy.techhorizonlabs.com/skills).

### [Claude Academy](https://academy.claude.com/)

Anthropic's official courses on Claude, Claude Code, MCP, skills and the Claude API.

**For:** People learning Claude products and MCP.

**Access and use:** Free courses at academy.claude.com. Some lessons need a Claude account.

**Source checked:** 2026-10-27. [Official source](https://academy.claude.com/courses).

### [Claude plugins official](https://github.com/anthropics/claude-plugins-official)

Anthropic's official Claude Code plugin marketplace. 315 plugins counted on 27 Oct 2026, mostly partner connectors.

**For:** Claude Code users installing plugins with /plugin.

**Access and use:** Claude Code adds this marketplace on first interactive session. A plugin can install MCP servers and write config. Review a plugin before enabling it. Names and homepages are in indexes/claude-plugins-official.json. Not a security audit of each plugin.

**Source checked:** 2026-10-27. [Official source](https://code.claude.com/docs/en/plugins/anthropic-marketplaces).

### [SkillsMP](https://skillsmp.com/)

A community index of Agent Skills scraped from GitHub. Not run by Anthropic.

**For:** People searching for community skills at their own risk.

**Access and use:** Unvetted. Individual skills keep their upstream licences. Anonymous API is rate limited. Treat a listed skill as untrusted code until you have read it. Optional paid API plans.

**Source checked:** 2026-10-27. [Official source](https://skillsmp.com/).

### [Anthropic Cybersecurity Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)

An independent community library of 818 cybersecurity skills in the agentskills.io format, mapped to MITRE ATT&CK, NIST CSF 2.0 and related frameworks. Not affiliated with Anthropic.

**For:** Security practitioners whose agents need structured playbooks for authorised testing, defence and education.

**Access and use:** Install with npx skills add mukul975/Anthropic-Cybersecurity-Skills. Apache-2.0. Includes offensive and dual-use techniques. Use only on systems you own or have written permission to test. A listed skill is not a security audit of your environment.

**Source checked:** 2026-10-28. [Official source](https://github.com/mukul975/Anthropic-Cybersecurity-Skills).

### [OrchestKit](https://orchestkit.dev)

A free Claude Code plugin of skills, agents and hooks for review, testing, security and memory, with a smaller pack for Cursor and Codex.

**For:** People who want those playbooks and quality gates on Claude Code or a compatible host.

**Access and use:** Claude Code: claude plugin marketplace add yonatangross/orchestkit && claude plugin install ork@orchestkit, then /ork:setup. Hooks read tool events and write local metrics under ~/.local/state/orchestkit/. Prompt text is not recorded. Network telemetry is off unless you set a destination. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/yonatangross/orchestkit).

### [UX/UI Agent Skills](https://plugin87.github.io/ux-ui-agent-skills/)

A design-system kit for coding agents (also called XIAS): tokens, 26 skills, 52 objective gates, and a library of design-system specs.

**For:** People whose agents design or review UI in Claude Code, Codex, Cursor, Gemini CLI or an MCP client.

**Access and use:** Claude Code: /plugin marketplace add plugin87/ux-ui-agent-skills then /plugin install ux-ui-agent-skills@ux-ui-agent-skills. Other hosts: npx ux-ui-agent-skills init, or Homebrew plugin87/tap/ux-ui-agent-skills. MCP is claude mcp add ux-ui-gates -- npx -y --package=ux-ui-agent-skills ux-ui-mcp. 34 of the 52 gates open a real browser using Chrome on the machine or npx playwright install chrome. Live demo needs no install. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/plugin87/ux-ui-agent-skills).

### [AI Marketing Skills](https://github.com/ericosiu/ai-marketing-skills)

Open-source Claude Code skills for growth experiments, sales pipeline, content ops, outbound, SEO, finance and related marketing workflows, published by Single Grain.

**For:** Marketing and sales teams whose coding agent should run those playbooks.

**Access and use:** Clone the repo, then copy each skill directory (SKILL.md plus any scripts, references or agents) into your agent's skills folder. Categories also ship Python scripts; pip install -r requirements.txt and fill .env with the API keys that category needs. Local usage logs live at ~/.ai-marketing-skills/analytics/. Remote telemetry stays off until you opt in. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/ericosiu/ai-marketing-skills).

### [Solid Glass](https://deeplethe.github.io/solid-glass)

A shadcn/ui stylesheet and component registry for agent workspaces: status, composer, tool steps, diffs and related screens.

**For:** People building agent UIs on React 19, Tailwind CSS 4 and shadcn/ui.

**Access and use:** Start from a shadcn/ui project, then npx shadcn@latest add deeplethe/solid-glass/solid-glass and import the stylesheet after Tailwind and shadcn. Extra components such as status-glyph install the same way. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/deeplethe/solid-glass).

### [Product Launch Motion](https://github.com/AbubakrChan/product-launch-motion)

A Claude Code skill that reads a website URL and renders a local launch film with Playwright, FFmpeg and music-timed springs.

**For:** People who want a product launch video directed from their site inside Claude Code.

**Access and use:** npx skills add AbubakrChan/product-launch-motion. Needs Claude Code, Node 20 or later, Playwright, FFmpeg, and Python with numpy. Renders on the local machine. MIT on the skill and references. The sample films belong to Cheerful, and the MIT licence doesn't cover them.

**Source checked:** 2026-10-28. [Official source](https://github.com/AbubakrChan/product-launch-motion).

## Looking for more?

Gearlist is a checked shortlist with permission notes. For every public MCP server, use the [official MCP Registry](https://registry.modelcontextprotocol.io). All 313 repositories we've starred on GitHub are stored in [stars-queue.json](stars-queue.json). Official Claude Code plugins are listed in [indexes/claude-plugins-official.json](indexes/claude-plugins-official.json). Tech Horizon Academy skills, tools and prompt titles are in [indexes/thl-academy-skills.json](indexes/thl-academy-skills.json), [indexes/thl-academy-tools.json](indexes/thl-academy-tools.json) and [indexes/thl-academy-prompts.json](indexes/thl-academy-prompts.json). Queued rows wait until someone reads their docs. A star, a marketplace listing or an index row is not an entry.

## Suggest an entry

Submit a pull request following [CONTRIBUTING.md](CONTRIBUTING.md). Each entry needs the official link, who it serves, the access it needs, its licence and the date you checked it. Do not include private conversations, contact details or credentials.

Tech Horizon Labs entries are labelled. This edition uses no affiliate links or paid placement. Third party products keep their own licences and terms.

Directory text and build script: [MIT licence](LICENSE).
