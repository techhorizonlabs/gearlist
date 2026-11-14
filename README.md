# Gearlist

![Gearlist](social-preview.png)

A source-checked stack of AI agent tools, MCP servers and skills. Each entry says what it is, who it is for, and the access it needs, so a person can scan it and an agent can load it.

By Tech Horizon Labs. This edition contains 390 entries. Documentation checked means the source was read. It does not mean the software was installed, tested or security audited. Entries are grouped by purpose, in no particular order.

## How to use this

- Human: scan the groups below, or search them at [gearlist.build](https://gearlist.build/). The heading is the product. **For** is the audience. **Access and use** is the permission note.
- Agent: load [llms.txt](llms.txt) first, then [llms-full.txt](llms-full.txt) or [resources.json](resources.json). [AGENTS.md](AGENTS.md) is the house rules. Do not install from a row until a human authorises it.
- Agent with MCP: connect to the Gearlist MCP server at `https://gearlist.build/mcp`. It is read-only and needs no sign-in. [agent-prompt.txt](https://gearlist.build/agent-prompt.txt) is a prompt to give your agent, with setup steps for Codex, Gemini CLI, Cursor, Grok, VS Code and the Claude apps. In Claude Code:

```bash
claude mcp add --transport http gearlist https://gearlist.build/mcp
```

## Agent files

The website has these for agents, as well as the files in this repository:

- [MCP server](https://gearlist.build/mcp): tools `search_gear`, `get_gear`, `list_categories`, `list_skills` and `recommend_stack`, over Streamable HTTP. Its server card is at [/mcp/server-card](https://gearlist.build/mcp/server-card).
- [Search API](https://gearlist.build/api/search?q=browser): the same search as JSON, described in [openapi.json](https://gearlist.build/openapi.json).
- [agent-prompt.txt](https://gearlist.build/agent-prompt.txt): the prompt to give your agent.
- A Markdown copy of the catalog page, sent when a request for `https://gearlist.build/` asks for `text/markdown`. It is also at [index.md](https://gearlist.build/index.md).
- A page for every entry at `https://gearlist.build/tools/<id>/`, for example [Firecrawl](https://gearlist.build/tools/firecrawl/), and a page for every group at `https://gearlist.build/category/<group>/`. Each has a Markdown copy beside it, such as [tools/firecrawl.md](https://gearlist.build/tools/firecrawl.md).
- [What's new](https://gearlist.build/new/): entries by the date they were added, newest first, with a Markdown copy at [new.md](https://gearlist.build/new.md) and an Atom feed at [feed.xml](https://gearlist.build/feed.xml).
- Discovery files: [ai-catalog.json](https://gearlist.build/.well-known/ai-catalog.json) names the MCP server and the skills, [api-catalog](https://gearlist.build/.well-known/api-catalog) lists the APIs, and [agent-skills/index.json](https://gearlist.build/.well-known/agent-skills/index.json) lists the skills with their checksums.

## Skills

Install the repository's skills with the command below. It asks which ones you want.

```bash
npx skills add techhorizonlabs/gearlist
```

The skills are:
- `api-skill`: turn a REST API into an agent skill.
- `vet-before-install`: check a GitHub repo, MCP server, skill or prompt before you install it. It reads the code and docs only, and gives a verdict with file and line evidence.
- `youtube-creator-research`: research a YouTube creator and write one brief, with the three skills below.
- `youtube-channel-profile`: a channel's public stats, upload rhythm, engagement and an estimated earnings range from the official YouTube Data API.
- `youtube-video-themes`: recurring topics and opening hooks from a channel's video transcripts.
- `creator-audience`: how to get audience demographics with the owner's consent or a paid estimate.
- `au-business-check`: check an Australian business before you deal with it, with the two skills below. It reports whether the business is registered, its status, registration date, ABN and ACN, and the date of each source. With an ABN Lookup GUID it adds GST registration and state.
- `asic-registers`: search ASIC's company and business names registers by name, ACN or ABN, through data.gov.au. No key needed.
- `abn-lookup`: ABN details, GST registration and name matches from ABN Lookup, the Australian Business Register's free web service. Needs a free GUID.
- `company-check`: check a company in the official register of its country: Australia with the three skills above, and the United Kingdom, the United States and New Zealand with the three below. It says which sources ran, which did not, and the environment variable each one needs.
- `uk-companies-house`: a UK company's status, type, registered office, filing due dates and previous names from the Companies House public data API, by name or company number. Needs a free API key.
- `us-sec-edgar`: a company's SEC EDGAR record and recent filings, by name, ticker or CIK. No key, but it needs a name and contact email to declare to the SEC. EDGAR covers mostly public companies.
- `nz-companies-office`: a New Zealand business's record in the NZBN Register, by NZBN, name or company number, from MBIE's NZBN API. Needs a subscription key. MBIE charges no fee, but asks for a signed access agreement first.
- `nvidia-api-catalog`: list the models on NVIDIA's hosted API catalogue and check whether a model id is live or retired, with no key. It also shows how to call a model with a key in `NVIDIA_API_KEY`. NVIDIA's free developer access is for prototyping and testing only.

To install the YouTube creator pack on its own:

```bash
npx skills add techhorizonlabs/gearlist --skill youtube-creator-research --skill youtube-channel-profile --skill youtube-video-themes --skill creator-audience
```

To install the Australian business data pack on its own:

```bash
npx skills add techhorizonlabs/gearlist --skill au-business-check --skill asic-registers --skill abn-lookup
```

To install the business check pack for Australia, the United Kingdom, the United States and New Zealand:

```bash
npx skills add techhorizonlabs/gearlist --skill company-check --skill au-business-check --skill asic-registers --skill abn-lookup --skill uk-companies-house --skill us-sec-edgar --skill nz-companies-office
```

[THL Open](https://github.com/techhorizonlabs/thl-open) is a second skills pack from Tech Horizon Labs, for GEO (Generative Engine Optimisation) audits and agent-readiness checks of a website. Its skills check AI crawler access, structured data, llms.txt and how likely AI systems are to quote a page, run Cloudflare's agent-readiness check, and write client reports. Install it the same way:

```bash
npx skills add techhorizonlabs/thl-open
```

## Contents

- [Agent tools](#agent-tools) (109)
- [MCP and integrations](#mcp-and-integrations) (48)
- [Security and governance](#security-and-governance) (16)
- [Platforms](#platforms) (67)
- [Protocols](#protocols) (9)
- [Skills and learning](#skills-and-learning) (67)
- [APIs and data](#apis-and-data) (38)
- [Hardware](#hardware) (12)
- [Models](#models) (14)
- [Hosting](#hosting) (10)


## Agent tools

### [Agent Deck](https://agentdeck.site/)

A Mac interface for coding agent sessions, project context and skills.

**For:** Developers coordinating coding sessions.

**Access and use:** Sessions may run tools with access to local files and connected services.

**Source checked:** 2026-10-25. [Official source](https://agentdeck.site/). [Gearlist page](https://gearlist.build/tools/agent-deck/).

### [Hunk](https://hunk.dev/)

A terminal interface for reviewing code changes with agent notes beside the diff.

**For:** Developers reviewing agent generated changes.

**Access and use:** Review changes before applying them; installation and repository access are separate decisions.

**Source checked:** 2026-10-25. [Official source](https://hunk.dev/). [Gearlist page](https://gearlist.build/tools/hunk/).

### [Jevgrep](https://github.com/dzhng/jevgrep)

Search a codebase with a question and receive relevant files and source excerpts.

**For:** Coding agents and developers exploring an unfamiliar repository.

**Access and use:** Requires an AI provider connection; check what repository content is sent to that provider.

**Source checked:** 2026-10-25. [Official source](https://github.com/dzhng/jevgrep). [Gearlist page](https://gearlist.build/tools/jevgrep/).

### [Needle](https://github.com/cactus-compute/needle)

Models and runtimes for local tool calling, structured extraction and embeddings.

**For:** Developers building applications on devices.

**Access and use:** Your application defines and executes the tools; constrain their permissions.

**Source checked:** 2026-10-25. [Official source](https://github.com/cactus-compute/needle). [Gearlist page](https://gearlist.build/tools/needle/).

### [Firecrawl](https://github.com/firecrawl/firecrawl)

Crawl and scrape sites into markdown and structured data for agents.

**For:** Agents and developers who need page content from the public web.

**Access and use:** The hosted API needs a key and spends credits. AGPL-3.0 on the open repository. Do not scrape sites that forbid it. LinkedIn and similar sites may be blocked.

**Source checked:** 2026-10-26. [Official source](https://github.com/firecrawl/firecrawl). [Gearlist page](https://gearlist.build/tools/firecrawl/).

### [REA](https://github.com/morluto/rea)

A local MCP and CLI for investigating application behaviour, from JavaScript bundles to native binaries.

**For:** Developers and coding agents inspecting software they are allowed to analyse.

**Access and use:** Install with npx rea-agents@latest setup. Setup shows a plan and asks before writing agent config or installing Hopper. Native and runtime workflows can execute or attach to programs. DISCLAIMER.md forbids DRM circumvention and copying proprietary software. MIT. npm package rea-agents. MCP registry name io.github.morluto/rea.

**Source checked:** 2026-10-26. [Official source](https://github.com/morluto/rea). [Gearlist page](https://gearlist.build/tools/rea/).

### [OpenCLI](https://opencli.info/)

A CLI and Chrome Browser Bridge that lets agents navigate, click, fill forms and extract from sites through a logged-in Chrome profile.

**For:** People whose agents need to operate websites they are already signed into, or reuse site-specific CLI adapters.

**Access and use:** Install npm package @jackwener/opencli (Node.js 20.18.1 or later) or the desktop app, plus the OpenCLI Chrome extension. Browser commands act through the signed-in Chrome profile, including cookies for the target site. Treat that as the same access the person has in the browser. Apache-2.0. Skills install with npx skills add jackwener/opencli.

**Source checked:** 2026-10-27. [Official source](https://github.com/jackwener/OpenCLI). [Gearlist page](https://gearlist.build/tools/opencli/).

### [Graphify](https://www.graphify.com)

Turns a codebase, docs, SQL schemas, configs and PDFs into a local queryable knowledge graph for coding agents.

**For:** People whose agents need a map of a repository without sending the tree to a hosted vector store.

**Access and use:** Install the CLI with uv tool install graphifyy, then graphify install. It reads local project files and writes graphify-out. Apache-2.0.

**Source checked:** 2026-10-27. [Official source](https://github.com/Graphify-Labs/graphify). [Gearlist page](https://gearlist.build/tools/graphify/).

### [OpenContext](https://0xranx.github.io/OpenContext/en/)

A local GUI and CLI that stores project context, skills and notes so a coding agent can reuse them across sessions.

**For:** People who already run Claude Code, Codex or OpenCode and want a persistent memory for that work.

**Access and use:** Install with npm install -g @aicontextlab/cli, then oc init in a project. Desktop app from GitHub releases. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/0xranx/OpenContext). [Gearlist page](https://gearlist.build/tools/opencontext/).

### [Stash](https://joinstash.ai)

Captures agent runs and human corrections, then serves that history back as knowledge, skills, REST, MCP and a CLI.

**For:** Teams whose agents should remember lessons from earlier work.

**Access and use:** Python client is pip install stash-sdk. It reads STASH_API_KEY and optional STASH_URL. The GitHub repo is MIT. Hosted and self-hosted paths are separate accounts.

**Source checked:** 2026-10-28. [Official source](https://github.com/Fergana-Labs/stash). [Gearlist page](https://gearlist.build/tools/stash/).

### [Browsentic](https://browsentic.com)

An agentic browser harness: a desktop app, npm CLI and Chrome or Firefox extension that lets an agent drive a signed-in browser.

**For:** People whose agents need to use the browser they already use, including logged-in sites.

**Access and use:** Installer is curl -fsSL https://browsentic.com/install.sh | sh. Read the script before running it. Or npx browsentic@latest setup. The extension acts through the signed-in browser. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/imshaikot/browsentic). [Gearlist page](https://gearlist.build/tools/browsentic/).

### [Trail-code](https://github.com/trailhq/Trail-Code)

A local map of a codebase plus team learnings, so coding agents go to the right files and pick up earlier decisions.

**For:** People running Claude Code, Cursor, Codex or similar on a repository they control.

**Access and use:** Install with npm install -g @trailhq/trail-code && trail init. It reads the repo on the machine and writes .trail/. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/trailhq/Trail-Code). [Gearlist page](https://gearlist.build/tools/trail-code/).

### [obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)

A local markdown vault an agent can grow, lint and query as a digital brain.

**For:** People who want durable notes an agent can read and write in a folder they own.

**Access and use:** Install with pip install obsidian-wiki, then obsidian-wiki setup --vault ~/brain. MIT. The vault is local files.

**Source checked:** 2026-10-28. [Official source](https://github.com/Ar9av/obsidian-wiki). [Gearlist page](https://gearlist.build/tools/obsidian-wiki/).

### [earshot](https://github.com/Leonxlnx/earshot)

A local CLI, Python API and MCP server that lets coding agents describe, score and generate sound on CPU.

**For:** People whose agents make or review audio, film or game sound without a GPU.

**Access and use:** Python 3.10 or later and ffmpeg on PATH. Clone the repo, venv, CPU torch, then pip install -e ".[mcp,llm,dev]". First model use downloads about 1.1 GB into a local cache. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/Leonxlnx/earshot). [Gearlist page](https://gearlist.build/tools/earshot/).

### [PromptDirector](https://github.com/wchao6891/PromptDirector)

A free local-first Chrome extension that saves images, prompts and references from the web for later reuse.

**For:** People collecting visual and prompt references while they browse.

**Access and use:** Chrome Web Store listing iahakaahijddcjjldidbclicedibgpjm. Optional local video component. Apache-2.0. Treat saved pages as the same access the signed-in browser has.

**Source checked:** 2026-10-28. [Official source](https://github.com/wchao6891/PromptDirector). [Gearlist page](https://gearlist.build/tools/prompt-director/).

### [ECC](https://ecc.tools)

An agent harness that adds planning, review, memory, skills and AgentShield security scanning to Claude Code and other coding agents.

**For:** People running Claude Code, Codex or similar who want that workflow installed once rather than restated every session.

**Access and use:** Guided setup is npx ecc-universal@2.2.3 setup (Node.js 18 or later). Claude Code plugin is ecc@ecc from github.com/affaan-m/ECC. Install only from those official sources. Hooks run with the agent's permissions. OSS is MIT. ECC Pro GitHub App is a separate paid product for private repos.

**Source checked:** 2026-10-28. [Official source](https://github.com/affaan-m/ECC). [Gearlist page](https://gearlist.build/tools/ecc/).

### [Agent Reach](https://github.com/Panniantong/Agent-Reach)

A CLI that gives coding agents read access to platforms generic web search misses, including GitHub, YouTube, Bilibili, V2EX and login-walled social sites.

**For:** People whose agents need those sources, including Chinese platforms and logged-in feeds.

**Access and use:** Point the agent at https://raw.githubusercontent.com/Panniantong/Agent-Reach/main/docs/install.md. The PyPI package named agent-reach is a different project. Login channels copy that site's Chrome session into a dedicated local browser; they do not read the password store. Prefer a secondary account. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/Panniantong/Agent-Reach). [Gearlist page](https://gearlist.build/tools/agent-reach/).

### [Ruflo](https://github.com/ruvnet/ruflo)

An agent harness around Claude Code and Codex: plugins, a console, optional MCP, and coordinated multi-agent workflows.

**For:** People who want swarm, memory and policy tools on top of an existing coding agent.

**Access and use:** Prefer npx ruflo@latest init wizard, or in Claude Code /plugin marketplace add ruvnet/ruflo. There is also curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh | bash. Read the script before running it. Mods run with your account's permissions; review them before installing. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/ruvnet/ruflo). [Gearlist page](https://gearlist.build/tools/ruflo/).

### [agentglass](https://sirallap.github.io/agentglass/)

A local desktop workspace that gathers coding-agent terminals, diffs, pull requests, approvals and a browser they can drive into one window.

**For:** People running Claude Code, Codex, Gemini CLI or OpenCode on their own machine, often several at once.

**Access and use:** Download from GitHub releases. macOS builds are unsigned. Opening it is your call. Data stays in local SQLite. Agents run with your permissions. It controls what they can approve, but it doesn't sandbox them. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/SirAllap/agentglass). [Gearlist page](https://gearlist.build/tools/agentglass/).

### [Oya Browser](https://oyabrowser.com)

A browser people and agents share: desktop app, Node SDK, remote MCP, and optional self-host, with human takeover when a task needs it.

**For:** People whose agents need a signed-in browser they can watch and take over.

**Access and use:** Desktop app from oyabrowser.com. SDK is npm install @oya-ai/browser with OYA_API_KEY. Remote MCP is https://oyabrowser.com/mcp/pool with that key. Self-host installer is curl -fsSL https://raw.githubusercontent.com/OyadotAI/oya-browser/main/install.sh | sh. Read the script before running it. Can reuse logins imported from Chrome, Arc, Brave, Edge or Firefox. SDK and CLI are MIT. The rest of the project is under the Sustainable Use License.

**Source checked:** 2026-10-28. [Official source](https://github.com/OyadotAI/oya-browser). [Gearlist page](https://gearlist.build/tools/oya-browser/).

### [apra-fleet](https://github.com/Apra-Labs/apra-fleet)

A local control plane that registers real machines as fleet members and runs durable multi-agent workflows across Claude, Codex, Copilot and other providers.

**For:** People coordinating coding agents on more than one machine they already own.

**Access and use:** Requires Node.js 22.16 or later. npm install -g @apralabs/apra-fleet, then apra-fleet install and apra-fleet start. MCP is http://localhost:7523/mcp by default. Secrets are entered out of band and never shown to the model. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/Apra-Labs/apra-fleet). [Gearlist page](https://gearlist.build/tools/apra-fleet/).

### [CodeGraph](https://colbymchenry.github.io/codegraph/)

A local code knowledge graph that answers with symbols, call paths and blast radius so coding agents spend fewer file reads.

**For:** People whose Claude Code, Cursor, Codex, Gemini, OpenCode, Copilot or similar agent needs a live map of a repository.

**Access and use:** Install with npm i -g @colbymchenry/codegraph, then codegraph install and, in each project, codegraph init. The README also offers curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh. Read the script before running it. Indexes live in .codegraph/ as local SQLite. The installer asks about anonymous usage telemetry; turn it off with codegraph telemetry off. Hosted product waitlist is getcodegraph.com. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/colbymchenry/codegraph). [Gearlist page](https://gearlist.build/tools/codegraph/).

### [Jev Ultrafast](https://github.com/browser-use/jev-ultrafast)

A local Chrome agent from Browser Use. One model chooses each click or field, and a smaller model writes text only when a field needs typing.

**For:** People who want a Chrome agent for a single goal, with a local inspector they can pause before a click.

**Access and use:** Clone the repo, uv sync, then set TYPESAFE_API_KEY and TEXT_MODEL_API_KEY in .env. TEXT_MODEL_API_KEY is an OpenRouter key in the example. Chrome connects through Browser Harness; allow remote debugging when prompted. Owned tabs share your existing Chrome profile. Local inspector is http://127.0.0.1:8766. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/browser-use/jev-ultrafast). [Gearlist page](https://gearlist.build/tools/jev-ultrafast/).

### [Boop](https://github.com/chrisgreg/boop)

A self-hosted notification inbox: apps POST events, they land in local SQLite, and an iOS app you build can show them on your phone.

**For:** Developers and agents that need a private event inbox they run themselves.

**Access and use:** Clone then docker compose up, or run a GitHub release binary. Data lives in a local SQLite file. APNs credentials are optional. Set BOOP_ADMIN_USER and BOOP_ADMIN_PASSWORD for the web UI, or put the server behind your own proxy. Read-only MCP is POST /mcp with BOOP_MCP_TOKEN; Settings can turn that endpoint off. You build and sign the iOS app. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/chrisgreg/boop). [Gearlist page](https://gearlist.build/tools/boop/).

### [Laya](https://nandhakishorm.github.io/laya/)

A local decision model that answers typed choice, score and yes/no questions over text in one forward pass, with a router that picks a checkpoint per request.

**For:** People whose agents need typed choice, score or yes/no answers over text.

**Access and use:** Python 3.10 or later. python -m pip install laya. The first predict downloads a Hugging Face checkpoint. Optional MCP: pip install "laya[mcp]" then laya-mcp-server. Optional HTTP playground: pip install "laya[serve]". Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/NandhaKishorM/laya). [Gearlist page](https://gearlist.build/tools/laya/).

### [BrowserSkill](https://github.com/Tencent/BrowserSkill)

A CLI, Chromium extension and agent skill that drives Chrome or Edge through the profile you are already signed into, in a separate Agent Window.

**For:** People whose agents need to read, click and fill sites they already use, without a separate browser account.

**Access and use:** Installer is curl -fsSL https://raw.githubusercontent.com/Tencent/BrowserSkill/main/install.sh | sh. Read the script before running it. Then install the Chrome or Edge extension, enable the local connection, and run bsk install-skill. The Agent Window shares that profile's website logins. Optional remote pairing uses authenticated WSS from the browser. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/Tencent/BrowserSkill). [Gearlist page](https://gearlist.build/tools/browserskill/).

### [Page Agent](https://alibaba.github.io/page-agent/)

An in-page JavaScript library that lets an LLM read the DOM as text and act on the page it is embedded in.

**For:** People adding a copilot to a site they control, or trying one in the optional Chrome extension.

**Access and use:** npm install page-agent, then construct PageAgent with a model, baseURL and apiKey. The demo CDN script uses a free testing LLM API for evaluation only; that path processes data in Mainland China and is not for production. Bring your own key for real use. Optional Chrome extension sends task text and cleaned HTML to the configured LLM. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/alibaba/page-agent). [Gearlist page](https://gearlist.build/tools/page-agent/).

### [OfficeCLI](https://github.com/iOfficeAI/OfficeCLI)

A single-binary CLI that creates, reads and edits Word, Excel and PowerPoint files without installing Microsoft Office.

**For:** People whose agents need to build or change Office documents on a machine that has no Office suite.

**Access and use:** Installer is curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash. Read the script before running it. Also brew install officecli, npm install -g @officecli/officecli, or GitHub Releases. officecli install puts the binary on PATH and writes a skill into coding agents it finds. Auto-update is on by default; officecli config autoUpdate false or OFFICECLI_SKIP_UPDATE=1 turns it off. Config lives in ~/.officecli. Built-in MCP: officecli mcp claude. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/iOfficeAI/OfficeCLI). [Gearlist page](https://gearlist.build/tools/officecli/).

### [OpenCode](https://opencode.ai)

An open source coding agent you run in a terminal, with a desktop app and a read-only plan mode.

**For:** People who want a local coding agent they can switch between full-access build and read-only plan.

**Access and use:** Installer is curl -fsSL https://opencode.ai/v2/install | bash. Read the script before running it. Also npm i -g @opencode/cli@latest or brew install anomalyco/tap/opencode-v2. The script installs to $HOME/.opencode/bin. OpenCode 1 and OpenCode 2 both use the opencode command and cannot sit side by side under that name. Needs API keys for the models you use. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/anomalyco/opencode). [Gearlist page](https://gearlist.build/tools/opencode/).

### [Crawl4AI](https://docs.crawl4ai.com)

An open-source crawler that turns a page into LLM-ready Markdown, with a CLI, Python library and a Docker server.

**For:** People who want to scrape pages into Markdown on their own machine.

**Access and use:** pip install -U crawl4ai, then crawl4ai-setup to install the browser. CLI is crwl URL -o markdown. Docker server listens on port 11235 and needs CRAWL4AI_API_TOKEN; without a token it answers only inside the container. Optional hosted cloud at crawl4ai.com uses its own key and has a free plan alongside paid ones. Apache-2.0, plus a clause that any public use must credit the project in a README, About page or acknowledgments.

**Source checked:** 2026-10-28. [Official source](https://github.com/unclecode/crawl4ai). [Gearlist page](https://gearlist.build/tools/crawl4ai/).

### [Hindsight](https://hindsight.vectorize.io)

An agent memory server that retains, recalls and reflects, so an agent can learn across sessions.

**For:** People who want long-term memory for a coding agent or a custom agent they run themselves.

**Access and use:** Docker image ghcr.io/vectorize-io/hindsight:latest publishes API on localhost:8888 and UI on localhost:9999, and needs an LLM provider: an API key, a local model such as Ollama, or an existing Claude, ChatGPT, Cursor or Copilot subscription. Also pip install hindsight-api. MCP is http://localhost:8888/mcp/{bank_id}/. Coding agents: npx @vectorize-io/hindsight-coding-agents install all. CLI installer is curl -fsSL https://hindsight.vectorize.io/get-cli | bash. Read the script before running it. Optional hosted cloud is a paid product. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/vectorize-io/hindsight). [Gearlist page](https://gearlist.build/tools/hindsight/).

### [Unsloth](https://unsloth.ai/docs)

A local app to run and train models, and to point coding agents at those models with one command.

**For:** People who want Claude Code, Codex or OpenCode to use a model on their own machine.

**Access and use:** Desktop builds are on GitHub Releases. Studio installer is curl -fsSL https://unsloth.ai/install.sh | sh. Read the script before running it. Also brew install --cask unsloth. Point an agent with unsloth start claude (or codex, opencode, dsh, openclaw). Default studio is local; --secure or a non-loopback bind asks for an admin password. Core package is Apache-2.0; Unsloth Studio UI is AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/unslothai/unsloth). [Gearlist page](https://gearlist.build/tools/unsloth/).

### [llmfit](https://github.com/AlexsJones/llmfit)

A terminal tool that scores which local LLMs will fit your RAM, CPU and GPU, with a TUI and an optional web API.

**For:** People choosing a local model for a coding agent or a laptop they already have.

**Access and use:** Installer is curl -fsSL https://llmfit.axjns.dev/install.sh | sh. Read the script before running it. Also brew install AlexsJones/llmfit/llmfit, winget install --exact --id AlexsJones.llmfit, or uvx llmfit. Default llmfit opens the TUI. llmfit serve --host 0.0.0.0 --port 8787 binds the API on every interface. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/AlexsJones/llmfit). [Gearlist page](https://gearlist.build/tools/llmfit/).

### [Beads](https://beads.gascity.com/)

A graph issue tracker for coding agents, with a CLI that stores tasks in a Dolt database so agents can claim ready work.

**For:** Teams whose coding agents need a shared, dependency-aware task list across machines.

**Access and use:** Installer is curl -fsSL https://raw.githubusercontent.com/gastownhall/beads/main/scripts/install.sh | bash. Read the script before running it. Also brew install beads or npm install -g @beads/bd. Then bd init in your project, which writes AGENTS.md and installs Claude Code, Codex and Cursor integrations unless you pass --skip-agents or --stealth. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/gastownhall/beads). [Gearlist page](https://gearlist.build/tools/beads/).

### [PicoClaw](https://picoclaw.io)

A small Go assistant that runs on a laptop or a cheap Linux board, with a local Web UI and chat-app channels.

**For:** People who want a local assistant on modest hardware, using their own model keys.

**Access and use:** Download from picoclaw.io or GitHub Releases. picoclaw-launcher opens http://localhost:18800. The -public flag listens on every interface. Needs an LLM API key or a local model such as Ollama. Tools can read files and run commands on the host. Treat inbound messages as untrusted. Do not deploy to production before v1.0. PicoClaw has issued no official token; listings on token sites are scams. Official site is picoclaw.io. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/sipeed/picoclaw). [Gearlist page](https://gearlist.build/tools/picoclaw/).

### [changedetection.io](https://changedetection.io)

A self-hosted watcher that checks web pages and notifies you when the content changes.

**For:** People who want price, restock or page-content alerts from sites they choose to monitor.

**Access and use:** Self-host: docker run -d -p 127.0.0.1:5000:5000 -v datastore-volume:/datastore --name changedetection.io dgtlmoon/changedetection.io then open http://127.0.0.1:5000. Also pip3 install changedetection.io. Hosted cloud is a paid product. Optional AI rules send page diffs to the LLM provider you configure. Follow each site's terms and robots.txt. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/dgtlmoon/changedetection.io). [Gearlist page](https://gearlist.build/tools/changedetection/).

### [CodexBar](https://codexbar.app)

A macOS menu bar app, Linux desktop app and CLI that shows remaining usage windows across AI coding providers.

**For:** People who need to see when Codex, Claude and other coding-plan quotas reset.

**Access and use:** macOS 14 or later: brew install --cask codexbar, or download from GitHub Releases. Linux: Qt desktop plus CLI via brew install steipete/tap/codexbar. Reuses existing provider sessions, cookies and API keys, and stores no passwords. Full Disk Access is optional for Safari cookies. Optional CLI serve defaults to 127.0.0.1:8080; a non-loopback bind needs a dashboard token and --allow-plain-http. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/steipete/CodexBar). [Gearlist page](https://gearlist.build/tools/codexbar/).

### [ScrapeGraphAI](https://github.com/ScrapeGraphAI/Scrapegraph-ai)

A Python library that uses an LLM and graph pipelines to extract structured data from pages and local documents.

**For:** People who want a self-hosted scraper driven by a prompt.

**Access and use:** pip install scrapegraphai then playwright install. Needs an LLM API key or a local model such as Ollama. The library sends anonymous usage metrics by default; set SCRAPEGRAPHAI_TELEMETRY_ENABLED=false to turn it off. This entry covers the MIT Python library. The managed cloud API is a paid product with a separate SDK. Follow each site's terms and robots.txt. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/ScrapeGraphAI/Scrapegraph-ai). [Gearlist page](https://gearlist.build/tools/scrapegraph-ai/).

### [ego lite](https://lite.ego.app)

A desktop browser that gives coding agents their own Spaces while they share your real logins and cookies through ego-browser.

**For:** People who want an agent to use signed-in sites in a separate Space.

**Access and use:** macOS and Windows. npx skills add citrolabs/ego-lite, or download the app from lite.ego.app. On first launch it can migrate Chrome logins, cookies, extensions and bookmarks, and agents then use those sessions. Browsing data stays on the device. The app collects simple product signals such as whether it is the default browser. This entry covers the MIT skill repo. The browser is a separate free download. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/citrolabs/ego-lite). [Gearlist page](https://gearlist.build/tools/ego-lite/).

### [Eigent](https://www.eigent.ai)

An open-source desktop app that runs a single agent or a multi-agent workforce with browser, terminal, files and MCP on your machine.

**For:** People who want a local Cowork-style desktop that can operate files, a browser and a terminal.

**Access and use:** Download from eigent.ai/download. Local deployment is docker compose in server/ plus npm run dev with VITE_USE_LOCAL_PROXY=true pointing at localhost:3001. Needs Node 18 to 22. Quick start git clone then npm install && npm run dev uses Eigent cloud and needs an account. Built-in browser and terminal toolkits can operate the desktop and signed-in sites. Cloud model providers receive the text you send them. Developer uvicorn --host 0.0.0.0 binds every interface. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/eigent-ai/eigent). [Gearlist page](https://gearlist.build/tools/eigent/).

### [OpenDataLoader PDF](https://opendataloader.org)

A local PDF parser that turns documents into Markdown, JSON with bounding boxes, HTML or a Tagged PDF.

**For:** People feeding PDFs to an agent or auto-tagging untagged files for accessibility.

**Access and use:** pip install -U opendataloader-pdf. Needs Java 11 or later and Python 3.11 or later. Also npm @opendataloader/pdf and Java Maven. Default conversion runs locally. Hybrid mode (pip install "opendataloader-pdf[hybrid]") starts a backend on port 5002 and sends complex pages to that AI backend. Auto-tagging to Tagged PDF is Apache-2.0. PDF/UA export is an enterprise add-on. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/opendataloader-project/opendataloader-pdf). [Gearlist page](https://gearlist.build/tools/opendataloader-pdf/).

### [Scrapling](https://github.com/D4Vinci/Scrapling)

A Python scraping library with HTTP fetchers, stealth browsers, spiders and an MCP server for agents.

**For:** People who want a coding agent or a script to fetch pages, render JavaScript and export Markdown or JSON.

**Access and use:** pip install scrapling. Browser fetchers need pip install "scrapling[fetchers]" then scrapling install. MCP extra is pip install "scrapling[ai]". StealthyFetcher can drive a browser, keep login sessions and solve Cloudflare challenges. robots_txt_obey is optional on spiders. Follow each site's terms and robots.txt. BSD-3-Clause.

**Source checked:** 2026-10-28. [Official source](https://github.com/D4Vinci/Scrapling). [Gearlist page](https://gearlist.build/tools/scrapling/).

### [Maxun](https://www.maxun.dev)

An open-source web data platform. Record a browser workflow once and it becomes a reusable extraction robot, with scraping, crawling, an API, SDK, CLI and MCP server.

**For:** People who want repeatable structured extraction from websites, self-hosted or on the maker's cloud.

**Access and use:** Hosted at app.maxun.dev with an account, or self-hosted with Docker Compose or a local install that needs Node.js, PostgreSQL, MinIO and Redis. The Agent that finds the data on a site by itself is a Maxun Cloud feature. The self-hosted AI Mode extracts from a page you give it. Self-hosted MCP needs a built worker and a backend API key. The example environment turns telemetry on (MAXUN_TELEMETRY=true), and the source at commit 99c6bd0 passes the login email and user ID to it, so set it to false for private use. The default Compose file publishes the database, storage, app and browser ports and runs Chromium with its sandbox off, so harden it before use on a shared network. Follow each site's terms and robots.txt. AGPL-3.0: if you change it and offer it to users over a network, you must offer those users the source.

**Source checked:** 2026-11-14. [Official source](https://github.com/getmaxun/maxun). [Gearlist page](https://gearlist.build/tools/maxun/).

### [REM (Reverse Engineer Marketing)](https://github.com/dansugc/reverse-engineer-marketing)

A CLI, local web app and MCP server that collects a company's public marketing evidence from one link (ads, tracking pixels, sitemaps, social accounts, app stores) and drafts a cited report.

**For:** Marketers and founders who want a competitor's public marketing gathered in one place as a starting point for their own research.

**Access and use:** npx reverse-engineer-marketing followed by a domain. Website, pixel, sitemap, Wayback, app store and Hacker News checks need no key. Ad libraries, social stats, founders and Reddit need a paid Scrape Creators key; the README puts a run at about 25 to 50 credits. The written report uses an Anthropic API key or your installed Claude Code or Codex CLI. The tool checks that the CLI is installed and does not check which account or billing it uses. Those CLI writers run with most of your environment variables, so start it from a shell that holds no other secrets. The web app runs on localhost:4321. The built-in report validation checks citation IDs and headings and does not check that the evidence supports a claim, and a source that failed to collect can show as none. Treat long-running ads and installed pixels as leads to investigate. MIT.

**Source checked:** 2026-11-14. [Official source](https://github.com/dansugc/reverse-engineer-marketing). [Gearlist page](https://gearlist.build/tools/reverse-engineer-marketing/).

### [Plannotator](https://plannotator.ai)

A local browser app where you annotate a coding agent's plans, Markdown or HTML and review code diffs, then send your comments back to the agent as structured feedback.

**For:** Developers who use Claude Code, Codex or another supported coding agent and want to mark up its plans and changes and send it feedback.

**Access and use:** Install with curl -fsSL https://plannotator.ai/install.sh | bash (a PowerShell script on Windows), which downloads the binary from GitHub Releases and sets up hooks, skills and slash commands for each agent it finds. Read the script first, or pass --minimal for the binary only. Some agents, Claude Code among them, also need a plugin step. Plans, annotations and settings stay local by default and the README says there is no usage telemetry, but each review page checks GitHub for a newer release when it loads, and this cannot be turned off yet. Local code review can query your Git remote (--no-git-remote-check stops it), and annotating a URL fetches the page through Jina Reader by default (PLANNOTATOR_JINA=0 stops it). Ask AI and review agents send your question and the relevant plan, document or diff to the AI provider you configure. Small Markdown share links hold the content compressed in the link without encryption, so anyone or any service with the full link can read it. Larger shares are encrypted before upload, and anyone with the full link can decrypt them. PLANNOTATOR_SHARE=disabled turns sharing off, and open-source link sharing is moving to deprecated support. Workspaces, the hosted team product, is a separate service outside the local storage model. In remote or SSH mode the server listens on every network interface with no login, so keep its port closed to networks you do not trust. An agent can still misread or ignore feedback, so check what it does next. Apache-2.0 or MIT, at your option.

**Source checked:** 2026-11-14. [Official source](https://github.com/backnotprop/plannotator). [Gearlist page](https://gearlist.build/tools/plannotator/).

### [Zellij](https://zellij.dev)

A terminal workspace that arranges programs in panes and tabs, with floating panes, layouts, sessions, multiplayer collaboration, WebAssembly plugins and a built-in web client. Programs like it are sometimes called terminal multiplexers.

**For:** Developers and operations staff who keep several terminal programs, coding agents among them, running in one workspace.

**Access and use:** Install from your operating system's package manager, a prebuilt binary from GitHub Releases, or cargo install --locked zellij. The command to try it without installing runs a script downloaded from zellij.dev with bash; read the script first. Version 0.46.0 adds a desktop terminal, started with zellij terminal, for Linux, macOS and Windows; the Linux musl builds leave it out. The web server stays off until you start it, serves sessions from the same Zellij version on the same machine, and listens on 127.0.0.1:8082 by default. Signing in needs a token, which is shown only once. A read-only token lets someone watch a session without changing it. HTTPS is required before you share sessions beyond the local machine. Zellij does not sandbox agents or other programs in its panes. Zellij.online is a separate paid hosted sharing service in beta, run by the maintainers; self-hosting does not need it. MIT.

**Source checked:** 2026-11-14. [Official source](https://github.com/zellij-org/zellij). [Gearlist page](https://gearlist.build/tools/zellij/).

### [Claude Code](https://code.claude.com/docs/en/overview)

Anthropic's coding agent that reads a project, edits files, runs commands and works with your development tools, in a terminal and other development surfaces.

**For:** Developers who want an agent from Anthropic to read, change and run code in their own projects.

**Access and use:** A commercial product from Anthropic. Depending on the surface and how it is deployed, it needs a Claude subscription, an Anthropic Console account or access through a supported provider, so check what your plan or account covers before you rely on a surface. It reads and edits files, runs commands and uses connected tools within the permissions you configure. The CLI runs on your machine, but it is not an offline model. Anthropic's data-use page treats consumer accounts, where you set your own privacy choices, separately from commercial arrangements, and covers feedback, usage and conversation information; read the part that applies to your account. The GitHub repository is under Anthropic's proprietary terms, not an open-source licence.

**Source checked:** 2026-11-14. [Official source](https://github.com/anthropics/claude-code). [Gearlist page](https://gearlist.build/tools/claude-code/).

### [Codex CLI](https://learn.chatgpt.com/docs/codex/cli)

OpenAI's coding agent that runs in your terminal to inspect code, change files, run commands and automate repeatable development work.

**For:** Developers who want OpenAI's coding agent to work on their code from the terminal.

**Access and use:** Sign in with a ChatGPT subscription, or use an API key with usage-based billing. The choice decides which workspace and data controls apply, and what you pay depends on that plan or usage; enterprise data terms depend on your own workspace or API agreement. Credentials are cached in a local file or the OS credential store, depending on configuration. It changes files and runs commands on your machine within the permissions you allow. It runs locally, but code and prompts can go to the model provider you configure, so local execution does not mean local-only processing. Apache-2.0.

**Source checked:** 2026-11-14. [Official source](https://github.com/openai/codex). [Gearlist page](https://gearlist.build/tools/codex-cli/).

### [Cognee](https://github.com/topoteretes/cognee)

Agent memory that uses graph and vector retrieval over documents, conversations and code, with memory operations and integrations for coding agents and MCP.

**For:** Developers who want long-term memory for a coding agent or for an agent they build.

**Access and use:** A keyless setup with local models is documented. Usage telemetry is on by default and covers operations, settings, identifiers and a one-way hash of your API key, but not the content of documents or queries; setting TELEMETRY_DISABLED to any non-empty value turns it off. Connector ingestion has separate telemetry considerations from dlt, so check those too. If you choose remote models or embeddings, your material goes to those providers, and each connector needs its own credentials. The API requires authentication by default, and changing deployment settings can change that. A hosted cloud service and a licensed production Postgres graph store are separate offerings. Apache-2.0.

**Source checked:** 2026-11-14. [Official source](https://github.com/topoteretes/cognee). [Gearlist page](https://gearlist.build/tools/cognee/).

### [Antigravity CLI](https://antigravity.google/product/antigravity-cli)

The terminal client for Google Antigravity's coding agents, which understand a project, make edits across several files, use tools, run commands and work in parallel sessions.

**For:** Developers who want Google's Antigravity coding agents in a terminal.

**Access and use:** A commercial product from Google, not open source: no open-source licence file was found in the repository, use is governed by the Google Antigravity terms, and business contracts carry their own terms. The README documents Google sign-in with credentials in your keyring, and browser authorisation when you use it over SSH. Official onboarding also covers personal and business or provider sign-in routes; access, quotas and billing depend on the route you choose. Under the personal-service terms, your interactions can be used to improve Google's products and machine learning, including human review, unless you opt out in settings; data is still used to run and secure the service when that setting is off. The terms prohibit giving third-party services access through it, and name OpenClaw with Antigravity OAuth as an example, so do not use its sign-in as a backend for other agent harnesses. Account eligibility, regional availability, plan quotas and enterprise contract coverage were not fully verified; check them with Google.

**Source checked:** 2026-11-14. [Official source](https://github.com/google-antigravity/antigravity-cli). [Gearlist page](https://gearlist.build/tools/antigravity-cli/).

### [e2e](https://github.com/e2e-inc/e2e)

An open-source end-to-end testing framework for web and mobile apps that mixes deterministic steps with agent-assisted steps, and replays previously verified agent actions from a cache.

**For:** Developers and testers who want an agent to help run end-to-end tests of web or mobile apps.

**Access and use:** It runs on your own infrastructure and calls the model or agent engine you configure, with your credentials, and adaptive agent work can add model costs. CLI telemetry is on by default and collects command, engine, version and error metadata; the documentation says it excludes test and app content and credentials. Set E2E_TELEMETRY_DISABLED=1, or use the documented CLI controls, to turn it off. This entry covers the open-source framework only: terms for any hosted service at e2e.com are unknown. Formerly TesterArmy. Apache-2.0.

**Source checked:** 2026-11-14. [Official source](https://github.com/e2e-inc/e2e). [Gearlist page](https://gearlist.build/tools/e2e/).

### [vphone-cli](https://github.com/Lakr233/vphone-cli)

A tool that runs a virtual iPhone on an Apple Silicon Mac for research, reverse engineering and debugging.

**For:** People who need a local iOS guest on a Mac they already have.

**Access and use:** Needs a physical Apple Silicon Mac on macOS 15 or later. Download the notarized vphone-launchpad zip from GitHub Releases. Host setup uses Recovery commands csrutil enable --without debug and csrutil allow-research-guests enable. Optional API is --api-listen 127.0.0.1:8765 with a printed token. The project issues no token; listings on token sites are scams. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/Lakr233/vphone-cli). [Gearlist page](https://gearlist.build/tools/vphone-cli/).

### [Data Formulator](https://data-formulator.ai)

A local workspace where an agent explores data, branches questions and draws charts from files, databases and warehouses you connect.

**For:** Analysts who want an agent to load data, keep a visual thread of questions and share a report.

**Access and use:** uvx data_formulator, or pip install data_formulator then python -m data_formulator. Opens http://localhost:5567. Needs an LLM API key or a local model via LiteLLM. Desktop preview builds from GitHub Actions are unsigned. Connectors can reach files, databases and warehouses you configure. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/microsoft/data-formulator). [Gearlist page](https://gearlist.build/tools/data-formulator/).

### [Rowboat](https://www.rowboatlabs.com)

A local desktop assistant that indexes email, meetings and notes into a Markdown knowledge graph, with optional shared Spaces.

**For:** People who want an assistant that keeps its vault on the machine and can still join a team room.

**Access and use:** Download from rowboatlabs.com/downloads or GitHub Releases. Indexes email, meetings, Slack and assistant chats into a local Markdown vault. Meeting notes tap the mic and speaker. The built-in browser is isolated from your main browser. Optional keys live in ~/.rowboat/config. Hosted Spaces sign in with Google or Microsoft. Self-host Harbor with pnpm in apps/harbor; default port 4272. Without AUTH_ISSUER Harbor uses dev tokens that must stay off the public internet. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/rowboatlabs/rowboat). [Gearlist page](https://gearlist.build/tools/rowboat/).

### [Orchestrator.inc](https://orchestrator.inc)

A local desktop workspace that runs a fleet of coding agents, each on its own branch and worktree, through plan, CI, review and merge.

**For:** People who want several coding agents on one repo, each on its own branch.

**Access and use:** Download from orchestrator.inc/download or GitHub Releases. Local workers keep code on your machine. Clone to the cloud runs workers in hosted GitHub workspaces. Pair a phone from Settings, Connect Mobile. Product telemetry records an installation ID and GitHub username (and AO Cloud email if you sign in); turn it off in Settings, General, Privacy, Share usage analytics. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/OrchestratorInc/agent-orchestrator). [Gearlist page](https://gearlist.build/tools/orchestrator/).

### [OpenWhispr](https://openwhispr.com)

A desktop dictation app with local or cloud speech-to-text, a voice assistant, meeting transcription and notes.

**For:** People who want a hotkey that turns speech into text in any app, with the option to keep audio on the machine.

**Access and use:** Download from GitHub Releases, or brew install --cask openwhispr. macOS, Windows and Linux. Dictation, note recording and audio upload each pick their own engine. Local keeps audio on the device. OpenWhispr Cloud sends audio to their servers, keeps the transcript text and discards the recording. Bring-your-own-key sends audio to the provider you configured. Microphone is required. Accessibility pastes at the cursor. Screen Recording is needed for meeting system audio, and for Share screen context, which is off unless you turn it on and then sends one screenshot of the display under your cursor with that voice-agent request. Cloud backup is off by default. Shared notes and team-space notes always sync to the cloud. Usage analytics is off by default. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/OpenWhispr/openwhispr). [Gearlist page](https://gearlist.build/tools/openwhispr/).

### [Skill Recorder](https://github.com/microsoft/skill-recorder)

A desktop app that records a work session on your screen and turns it into a reusable agent skill or scheduled automation.

**For:** People who want an agent to repeat a task they can demonstrate once.

**Access and use:** Copy the commit-pinned install command from the latest GitHub Release. It pipes a script; read the script before running it. macOS is the primary target; Windows 11 x64 and ARM64 are supported. Needs Screen Recording. Recording stays on the machine. Analyze sends the event timeline, screen images, narration text and requested terminal excerpts to GitHub Copilot in the cloud. Needs a GitHub account with Copilot access. Keep secrets out of recordings. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/microsoft/skill-recorder). [Gearlist page](https://gearlist.build/tools/skill-recorder/).

### [Cloudflare Agents](https://developers.cloudflare.com/agents/)

An SDK for persistent, stateful agents on Cloudflare Durable Objects, with MCP, scheduling, workflows and sandboxed code.

**For:** Developers who want agents that keep state on Cloudflare and wake only when they have work.

**Access and use:** npm install agents, or npm create cloudflare@latest -- --template cloudflare/agents-starter. Needs a Durable Object binding and a SQLite migration in wrangler.jsonc. Agents hibernate when idle. MCP can act as a server or a client. Sandboxed execution runs generated code in an isolated Worker. x402 pay-per-call is optional. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/cloudflare/agents). [Gearlist page](https://gearlist.build/tools/cloudflare-agents/).

### [pxpipe](https://github.com/teamchong/pxpipe)

A local proxy that rewrites bulky coding-agent request context into PNG pages so the model reads them as images.

**For:** People who want a local proxy in front of Claude Code, Codex or Gemini CLI to cut request tokens.

**Access and use:** npx pxpipe-proxy listens on 127.0.0.1:47821. pxpipe warp wraps a client such as claude, agy or opencode. The dashboard is http://127.0.0.1:47821/. Requests still go to the provider after imaging. Events log to ~/.pxpipe/events.jsonl. Exact strings in imaged history can be misread; keep recent turns as text. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/teamchong/pxpipe). [Gearlist page](https://gearlist.build/tools/pxpipe/).

### [Codex ChatGPT Web](https://github.com/miuuyy/codex-chatgpt-web)

A local launcher that signs into ChatGPT in an embedded browser so Codex can pick those web models, including a full harness that connects ChatGPT tools back to the current Codex task.

**For:** People who already use Codex and a ChatGPT account and want those web models in the Codex picker.

**Access and use:** Download from GitHub Releases, or pipe the published install-launcher.sh or install-launcher.ps1. Read the script before running it. Unofficial browser automation. Sign in to ChatGPT in the embedded browser. Browser state is a login artifact; the loopback listener is reachable by other processes as the same local user. Builds are unsigned, so Gatekeeper or SmartScreen may warn. Full harness uses an outbound OpenAI tunnel-client and ChatGPT Developer Mode with a connector named Codex Native2, Authentication None and Allow all actions. --auto-approve-tool-calls clicks Allow once. Conversations stay in ChatGPT history. Follow OpenAI's terms. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/miuuyy/codex-chatgpt-web). [Gearlist page](https://gearlist.build/tools/codex-chatgpt-web/).

### [PortKiller](https://github.com/productdevbook/port-killer)

A menu-bar and system-tray app that lists listening TCP ports and can terminate the process behind one click.

**For:** Developers who need to free a local port, or keep kubectl port-forwards and Cloudflare tunnels in view.

**Access and use:** macOS 15+: brew install --cask productdevbook/tap/portkiller, or a .dmg from GitHub Releases. Windows 10+: extract the zip from Releases. Killing a process is immediate. Kubernetes port-forwards use your kubectl context. Cloudflare Tunnels lists active tunnels. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/productdevbook/port-killer). [Gearlist page](https://gearlist.build/tools/portkiller/).

### [ClawRouter](https://github.com/BlockRunAI/ClawRouter)

A local LLM router that picks a model per request and can pay the gateway with a wallet signature over x402, or with a BlockRun API key.

**For:** People running agents that need a local OpenAI-compatible proxy with per-call billing.

**Access and use:** npx @blockrun/clawrouter listens on localhost:8402. It picks the model locally, then sends each request through BlockRun's gateway, which bills it. First run generates a wallet locally. Paid models spend USDC from that wallet per call, or sign up at user.blockrun.ai and run clawrouter login with a brk_live_ key. Free models need no wallet. The OpenClaw plugin path is curl -fsSL https://blockrun.ai/ClawRouter-update | bash; read the script before running it. Outbound voice and phone tools bill the wallet automatically. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/BlockRunAI/ClawRouter). [Gearlist page](https://gearlist.build/tools/clawrouter/).

### [OpenCreator](https://github.com/krillinai/OpenCreator)

A local creator workspace around Codex CLI for video, images, voice, translation and agent conversations.

**For:** People who want Codex-backed creative tools on the machine, with data and attachments local by default.

**Access and use:** Download the desktop installer from GitHub Releases (macOS Apple Silicon, macOS Intel, Windows x64). First launch can reuse a local Codex ChatGPT sign-in or API key. Web from source is pnpm web:dev at http://127.0.0.1:19861/. The daemon listens on loopback only. Video downloads from some platforms need cookies. Follow each site's terms. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/krillinai/OpenCreator). [Gearlist page](https://gearlist.build/tools/opencreator/).

### [claude-devtools](https://github.com/matt1398/claude-devtools)

A desktop app that reads Claude Code session logs already on the machine and reconstructs tool calls, thinking, tokens and subagent trees.

**For:** People who want to inspect Claude Code sessions stored in ~/.claude/.

**Access and use:** brew install --cask claude-devtools, or a GitHub Release for macOS, Linux or Windows. Docker compose up serves http://localhost:3456 with ~/.claude mounted read-only. The standalone server defaults HOST to 0.0.0.0 and has no outbound network calls. SSH remote sessions read ~/.ssh/config. File reads stay in the project root and ~/.claude. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/matt1398/claude-devtools). [Gearlist page](https://gearlist.build/tools/claude-devtools/).

### [phone-harness](https://github.com/phone-harness/phone-harness)

A CLI and skill that lets a coding agent tap, type and read a real iPhone or Android, or a Phone Harness Cloud device.

**For:** People who want an agent to operate a physical phone they already have, or a hosted cloud phone.

**Access and use:** uv tool install --python 3.12 --upgrade --force phone-harness, then phone-harness skill. iPhone: macOS 15+, iPhone Mirroring paired to an iOS 18+ iPhone, Accessibility and Screen Recording. Android: adb with USB or wireless debugging. Cloud: phone-harness cloud login, then cloud start; a session lasts 15 minutes unless you pass --for. A remote MCP server at https://mcp.phone-harness.com/mcp works with cloud phones only. A cloud Android bills 5 cents a minute from account credit, and new accounts get $5 of credit. A cloud iPhone is a flat subscription from $80 a month. The harness never types a PIN. PHONE_HARNESS_NO_UPDATE_CHECK=1 skips the daily update check. The repository moved from ShawnPana/phone-harness. MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/phone-harness/phone-harness/blob/main/install.md). [Gearlist page](https://gearlist.build/tools/phone-harness/).

### [OpenHuman](https://github.com/tinyhumansai/openhuman)

A desktop app, terminal app and Rust library for running agent fleets with MCP, skills, memory and computer control.

**For:** People who want a desktop agent harness, or a Rust library that runs many agents on one machine.

**Access and use:** Download the desktop app from GitHub Releases (macOS dmg, Windows msi or exe, Linux deb or AppImage), or brew install --cask openhuman. The curl install script is curl -fsSL https://raw.githubusercontent.com/tinyhumansai/openhuman/main/scripts/install.sh | bash; read the script before running it. The agent can drive a Chrome browser and desktop apps, and it asks before actions it cannot undo. Memory items go to CortexDB: TinyHumans hosted memory needs sign-in, or you point it at your own endpoint; with neither, memory is off. The OpenHuman backend brokers LLM calls, OAuth tokens and some search. Privacy Mode keeps a run local. GPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/tinyhumansai/openhuman). [Gearlist page](https://gearlist.build/tools/openhuman/).

### [Pixel Agents](https://github.com/pixel-agents-hq/pixel-agents)

A VS Code extension and CLI that shows Claude Code sessions as pixel characters in a shared office view.

**For:** People who want to watch Claude Code terminals as characters in a pixel office.

**Access and use:** Install the VS Code extension from the Marketplace or Open VSX, or run npx pixel-agents. The CLI defaults to 127.0.0.1. Binding 0.0.0.0 exposes the UI and WebSocket on the local network. The printed URL carries a token that can install hooks and launch agents; treat it as a secret. Hooks write into ~/.claude/settings.json. Settings, Skip Permissions turns on Claude Code --dangerously-skip-permissions for every agent from that host. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/pixel-agents-hq/pixel-agents). [Gearlist page](https://gearlist.build/tools/pixel-agents/).

### [BrowserOS neo](https://github.com/browseros-ai/BrowserOS)

A second browser for coding agents. It can import Chrome logins and run each agent in its own tab, with session replay on disk.

**For:** People who want Claude Code, Codex or another MCP agent to drive a logged-in browser on the machine.

**Access and use:** brew tap browseros-ai/tap then brew install --cask browseros-neo, or a download from cdn.browseros.com for macOS, Windows or Linux. One click imports Chrome logins, bookmarks and extensions. Agents then use those accounts. Sessions and screenshots live under ~/.browserclaw/. It runs on 127.0.0.1. Anonymous product events (connect, disconnect, version, OS) go to PostHog until you turn them off in Settings. Prompts go to the AI vendor you already use. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/browseros-ai/BrowserOS). [Gearlist page](https://gearlist.build/tools/browseros-neo/).

### [Agent Relay](https://agentrelay.com)

Messaging, MCP and workflow infrastructure so coding agents on one machine, or across machines, can share channels and history.

**For:** People who want Claude Code, Codex or other local agents to talk through shared channels.

**Access and use:** npm install -g agent-relay, or curl -fsSL https://raw.githubusercontent.com/AgentWorkforce/relay/main/install.sh | bash; read the script before running it. Needs Node.js 22 or 24. relay init defaults to this machine at http://127.0.0.1:8787. Hosted mode creates a workspace on Agent Relay Cloud so agents on other machines can join; treat the workspace key as a secret. It adds an MCP server to Claude Code, Codex, OpenCode, Grok CLI, Pi or Devin (project files or global configs). Local data lives under ~/.agentworkforce/relay/local. The project workspace key is kept out of git via .git/info/exclude. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/AgentWorkforce/relay). [Gearlist page](https://gearlist.build/tools/agent-relay/).

### [Chums](https://chums.club)

Watch and iPhone apps that talk to Claude Code and Codex sessions running on your Mac, with a local hub.

**For:** People who want Claude Code or Codex on an Apple silicon Mac to take voice and approvals from an Apple Watch and iPhone.

**Access and use:** git clone https://github.com/lcoutodemos/chums then bin/chums-setup, bin/chums-hub, bin/chums-tunnel, bin/chums-install and bin/chums-agents install. Needs macOS 15.6, watchOS 26, iOS 26, Xcode 26, Node.js 20.11, Tailscale Funnel and Claude Code or Codex. The hub listens on 127.0.0.1:7717 and 127.0.0.1:7718. Funnel publishes the watch API at a public https://chums-hub.<tailnet>.ts.net URL; treat the watch token in ~/.chums/config.json as a secret, keep the file mode 0600, and do not share a built app. Funnel hostnames appear in certificate transparency logs. Default agents can use the home folder. Optional openai TTS in config sends reply text to OpenAI. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/lcoutodemos/chums). [Gearlist page](https://gearlist.build/tools/chums/).

### [OpenBrowser](https://docs.openbrowser.me)

A CodeAgent and MCP server that drives a Chromium browser over CDP, with a CLI daemon and an optional hosted dashboard.

**For:** People who want Claude Code, Codex or another MCP client to browse, scrape and fill forms on their machine.

**Access and use:** pip install openbrowser-ai, brew install openbrowser-ai, or curl -fsSL https://raw.githubusercontent.com/billy-enrizky/openbrowser-ai/main/install.sh | sh; read the script before running it. Needs Python 3.12+. uvx openbrowser-ai --mcp is the stdio MCP server. Default MCP profiles live under ~/.config/openbrowser/profiles/. The CLI daemon uses a Unix socket and ~/.config/openbrowser/profiles/daemon. Agent mode needs an LLM API key. The hosted dashboard at openbrowser.me stores cookies and scheduled tasks. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/billy-enrizky/openbrowser-ai). [Gearlist page](https://gearlist.build/tools/openbrowser/).

### [Clui CC](https://github.com/lcoutodemos/clui-cc)

A macOS overlay for Claude Code with multi-tab sessions, a permission UI, voice input and a skills marketplace.

**For:** People who run Claude Code on a Mac and want a floating desktop UI for approvals, tabs and voice.

**Access and use:** git clone https://github.com/lcoutodemos/clui-cc.git then double-click install-app.command; read the script before running it. Needs macOS 13+, Node 18+ (20 or 22 recommended), Xcode Command Line Tools, Python setuptools, and an authenticated Claude Code CLI. The packaged app is unsigned. Opening it is your call (System Settings, Privacy and Security, Open Anyway). Whisper is required and the installer installs it. Permission hooks listen on 127.0.0.1:19836. Marketplace catalog fetches anthropics GitHub repos; skill auto-install writes ~/.claude/skills/. Prompts go through your local Claude Code CLI. The README says there is no telemetry. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/lcoutodemos/clui-cc). [Gearlist page](https://gearlist.build/tools/clui-cc/).

### [Autonomous Company](https://github.com/MaxMiksa/Autonomous-Company)

A local loop of 14 expert-persona agents that research, decide and write code on a Mac or Windows WSL host, with a Product Center dashboard.

**For:** People who want Claude Code or Codex CLI to keep a continuous company loop under goals, permissions and budgets they set.

**Access and use:** git clone then make start (Claude Code default) or ENGINE=codex make start. Needs Python 3.10+, Git, make, and an authenticated Claude Code or Codex CLI. Product Center is http://127.0.0.1:8810/center (make center). Daemon mode uses launchd on macOS and systemd --user on WSL. CLAUDE_PERMISSION_MODE=bypassPermissions is the documented way to stop permission prompts; the README says prompt rules are not a sandbox and each cycle spends model quota. Optional Cursor and OpenAI-compatible adapters need explicit config. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/MaxMiksa/Autonomous-Company). [Gearlist page](https://gearlist.build/tools/autonomous-company/).

### [gallery-dl](https://github.com/mikf/gallery-dl)

A command-line downloader for image galleries and collections from hundreds of hosts, with JSON config, cookies and OAuth for logged-in sites.

**For:** People pulling galleries, manga or artist collections onto their own disk from supported hosts.

**Access and use:** Needs Python 3.8+ and Requests. python -m pip install -U gallery-dl. macOS: brew install gallery-dl. Run gallery-dl URL. Config is ~/.config/gallery-dl/config.json (Linux/macOS) or %APPDATA%\gallery-dl\config.json (Windows). Login cookies, passwords and OAuth tokens are sent to the host you download from. Active development is on Codeberg: https://codeberg.org/mikf/gallery-dl. GPL-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/mikf/gallery-dl). [Gearlist page](https://gearlist.build/tools/gallery-dl/).

### [OpenAlice](https://openalice.ai)

A local AI trading workspace that connects Claude Code, Codex, OpenCode and similar agents to market data, research folders and broker accounts.

**For:** People who want agents to research markets on their machine, with optional paper or live trading they approve.

**Access and use:** Desktop app for macOS and Windows from GitHub Releases; a broker account is optional for research. Source: git clone https://github.com/TraderAlice/OpenAlice.git && pnpm install && pnpm dev. State is ~/.openalice; workspaces are local Git directories. Broker credentials are sealed at rest. Agents and market-data providers still send prompts and quotes to their own services. Trading execution is beta: start with simulator, paper, demo or testnet; you review and approve live orders. AGPL-3.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/TraderAlice/OpenAlice). [Gearlist page](https://gearlist.build/tools/openalice/).

### [thinking-orbs](https://libraries.dev/orbs)

A React canvas library of nine dotted thought-orb animations for agent status, in two sizes, with automatic light and dark themes.

**For:** People building agent chat UIs who want a status glyph instead of a spinner.

**Access and use:** npm install thinking-orbs. Needs React 18 or newer. Import ThinkingOrb and set a state such as searching, working or solving, with size 64 or 20. The package is a canvas component; it does not call a model. Demo is https://libraries.dev/orbs. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/Jakubantalik/thinking-orbs). [Gearlist page](https://gearlist.build/tools/thinking-orbs/).

### [seekdb](https://www.seekdb.ai)

An Apache-licensed OceanBase search database that unifies vector, text and structured data for hybrid search and in-database AI functions.

**For:** Teams who want agent memory and RAG on a local file or a MySQL-compatible server.

**Access and use:** pip install -U pyseekdb. Needs Python 3.11 or later. Embedded mode on Linux and macOS: import pyseekdb then client = pyseekdb.Client() writes a local database (for example ./seekdb.db). Windows uses server mode only. AI_EMBED, AI_COMPLETE and similar SQL functions send text to the embedding or LLM service you register. Data stays in that local file or on the seekdb or OceanBase server you connect to. Apache-2.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/oceanbase/seekdb). [Gearlist page](https://gearlist.build/tools/seekdb/).

### [CashClaw](https://moltlaunch.com)

An MIT Node agent that quotes, does and gets paid for marketplace tasks, then stores what it learned for the next job.

**For:** Operators who want a local process that takes Moltlaunch tasks, or a fork they can point at their own clients.

**Access and use:** npm install -g cashclaw-agent moltlaunch then cashclaw. Setup is http://localhost:3777. Needs a Moltlaunch wallet (mltl) and an Anthropic, OpenAI or OpenRouter key. Quotes and payouts are in ETH on Base through that wallet. Optional AgentCash calls charge USDC from ~/.agentcash/wallet.json. State is ~/.cashclaw. Auto-quote and auto-work are on by default, so it quotes and submits work without asking; turn them off in Settings to approve each job. When idle it runs study sessions every 30 minutes by default, which call your LLM. Prompts go to the LLM you set. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/moltlaunch/cashclaw). [Gearlist page](https://gearlist.build/tools/cashclaw/).

### [Codag](https://codag.ai)

An MIT VS Code extension that graphs LLM calls and agent frameworks in a checkout, with a local Gemini backend for workflow labels.

**For:** Engineers who want a map of which files call which models, beside the source.

**Access and use:** Run the backend first: git clone https://github.com/michaelzixizhou/codag.git, copy backend/.env.example to backend/.env, set GEMINI_API_KEY, then make setup and docker compose up -d. Backend is http://localhost:52104. Then install Codag from the VS Code Marketplace. On activation it writes .mcp.json (or .cursor/mcp.json) into the workspace. Selected files go to Gemini 2.5 Flash for workflow labels. Live edits stay on the machine (tree-sitter). MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/michaelzixizhou/codag). [Gearlist page](https://gearlist.build/tools/codag/).

### [DeepInnovator](https://huggingface.co/T1anyu/DeepInnovator)

An MIT training recipe and Apache-2.0 14B Qwen2.5-Instruct model that proposes research ideas from scientific literature.

**For:** Researchers who want a local 14B model that drafts next research ideas, or who want to rerun the paper's RL recipe.

**Access and use:** Inference: pip install transformers torch, then load T1anyu/DeepInnovator with AutoModelForCausalLM.from_pretrained. The weights are about 15 billion parameters in BF16; Hugging Face documents GPU load. Training: git clone https://github.com/HKUDS/DeepInnovator.git, pip install openai omegaconf python-dotenv feedparser requests PyPDF2 tqdm python-dateutil datasets numpy torch transformers, set OPENAI_API_KEY and OPENAI_API_BASE in .env, then cd recipe/DeepInnovator/data_preparation and bash run.sh 100 ./data/arxiv_data. train_rl.sh needs a CUDA GPU. Data preparation sends paper text to the OpenAI-compatible API you set. GitHub recipe MIT. Hugging Face weights Apache-2.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/HKUDS/DeepInnovator). [Gearlist page](https://gearlist.build/tools/deepinnovator/).

### [Chatpack](https://docs.chatpack.dev)

An MIT chat backend you mount in your app for 1:1 and group messages, permissions, read-state and SSE delivery.

**For:** Developers who need conversations in an existing app and already have auth and a database.

**Access and use:** npm install @chatpack/core @chatpack/adapter-memory. Create chatpack({ storage, auth }) where auth returns { id } from your session cookie or null. Mount chat.handler() on a catch-all under /api/chat (Next.js app/api/chat/[...chatpack]/route.ts). Live events are GET /api/chat/stream as EventSource; cookie sessions work for SSE. Production: @chatpack/adapter-drizzle with DATABASE_URL Postgres, or @chatpack/adapter-prisma on PostgreSQL 16. Messages live in the database you attach. Optional npm install @chatpack/client react with credentials include. Agent skill: npx skills add chddaniel/chatpack. Docs MCP: npx -y @chatpack/mcp (stdio, bundled docs, no network). Docs https://docs.chatpack.dev. API is 0.x. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/chddaniel/chatpack). [Gearlist page](https://gearlist.build/tools/chatpack/).

### [CodeMap AI](https://code-map-ai-mu.vercel.app)

An MIT repo map: paste a GitHub URL and get file-dependency and function-call graphs plus issue mapping, parsed with ts-morph and tree-sitter.

**For:** Developers, especially first-time open source contributors, who need a starting map of a large GitHub repository.

**Access and use:** Hosted: https://code-map-ai-mu.vercel.app, the GitHub homepage of Ayansh0209/CodeMap-Ai (LICENSE Copyright 2026 Aayansh Singh). Paste a GitHub repo URL; that host downloads the tarball. Self-host: Node.js 20+, Redis and a GitHub token. cd backend && npm install, copy backend/.env.example to backend/.env, set REDIS_URL, GITHUB_TOKEN and PORT=5000. cd frontend && npm install. Terminal 1: cd backend && npm run dev at http://localhost:5000. Terminal 2: cd backend && npm run worker. Terminal 3: cd frontend && npm run dev at http://localhost:3000. The backend downloads the GitHub tarball and extracts it locally. BullMQ plus Redis runs the parse. ts-morph covers JS, TS, JSX and TSX; web-tree-sitter WASM covers Python, Go, C and C++. Graph artifacts go to S3-compatible storage (Backblaze B2, Cloudflare R2, Supabase) when R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME and R2_ENDPOINT or R2_ACCOUNT_ID are set; otherwise gzipped Redis. GEMINI_API_KEY enables issue mapping and chat on the parsed graph; selected file content goes to Gemini or Vertex AI. Without FIREBASE_SERVICE_ACCOUNT_BASE64 every request is anonymous trial; set it, or drop backend/firebase.json for local, for GitHub sign-in. README says the project is evolving and issue mapping can be wrong. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/Ayansh0209/CodeMap-Ai). [Gearlist page](https://gearlist.build/tools/codemap-ai/).

### [ai-phone](https://github.com/oxnw/ai-phone)

A local SIP phone daemon that lets an agent receive and place calls through a CLI on an Apple Silicon Mac.

**For:** Developers evaluating local voice agents and a phone interface for an existing agent.

**Access and use:** macOS on Apple Silicon, Python 3.11 to 3.13, Homebrew and uv. Source install builds a native PJSIP binding and setup downloads several GB of model files. The README recommends 16 GB RAM for the default 4B model, with a 2B option for 8 GB. English and one call at a time. Local SIP testing needs no paid carrier; telephone numbers and calls need a SIP trunk or carrier account and incur charges. Local speech stays on the Mac, but audio travels over SIP/RTP; remote language models and external cloud agents receive any call text passed to them. AGPL-3.0-or-later; bundled PJSIP interface files are GPLv2-or-later. The README says local call tests have run, and live carrier and end-to-end agent tests are still pending.

**Source checked:** 2026-10-30. [Official source](https://github.com/oxnw/ai-phone/blob/dfa54f4744658740054e823008a3be0a7f904f8a/README.md). [Gearlist page](https://gearlist.build/tools/ai-phone/).

### [Beacon](https://github.com/Asymptote-Labs/agent-beacon)

A local-first memory layer that captures session history from Claude Code, Cursor, Codex, OpenCode and other harnesses, then turns reviewed workflows and corrections into knowledge later agents retrieve through MCP or Agent Skills.

**For:** Developers who switch between coding agents and want what one session learned to carry into the next.

**Access and use:** Install with Homebrew (asymptote-labs/tap), a Linux .deb or .rpm installer script, or a Windows MSI; read the script or verify the package checksum first. Beacon records prompts, responses, tool calls, commands, file activity, approvals, MCP activity and token usage to ~/.beacon/endpoint/logs/runtime.jsonl. Interactive setup signs in through beacon.sh and preselects Beacon Cloud; confirming it forwards session history to Asymptote Labs, so choose Local to keep it on the machine. Unless turned off, the wizard installs Beacon Skills into ~/.agents/skills and ~/.claude/skills, and the Cloud option registers an MCP server in your harnesses. Optional forwarding to Splunk, Datadog, S3 and other destinations. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/Asymptote-Labs/agent-beacon). [Gearlist page](https://gearlist.build/tools/agent-beacon/).

### [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)

A Python app with a WebUI, API, CLI and agent skill that turns a topic or keyword into a short video, writing the script and adding stock or generated footage, voiceover, subtitles and music.

**For:** People producing short portrait, landscape or square videos from a topic on their own machine.

**Access and use:** Install with pip, the Windows one-click package, uv from source, or Docker (ghcr.io/harry0703/moneyprinterturbo:latest). The WebUI serves 127.0.0.1:8501 and API docs 127.0.0.1:8080/docs. Python 3.11 or later; a GPU is optional. API keys for the chosen LLM, footage, voice and video services are saved in config.toml; Edge TTS needs no key. An optional ChatGPT sign-in uses OpenAI's Sign in with ChatGPT flow. Publishing to TikTok, Instagram and YouTube Shorts goes through an Upload-Post API key. The README's agent quick start has a coding agent fetch a remote SKILL.md and install everything, so read it first. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/README-en.md). [Gearlist page](https://gearlist.build/tools/moneyprinterturbo/).

### [OpenMontage](https://github.com/calesthio/OpenMontage)

A video production system your coding assistant runs through pipelines, stage skills and tools for research, scripting, asset generation, editing and rendering with Remotion, HyperFrames and FFmpeg.

**For:** People who want a coding agent to plan and render explainers, documentaries or promos from a prompt or a reference video.

**Access and use:** Needs Python 3.10+, FFmpeg, Node.js 18+ and a coding assistant such as Claude Code, Cursor, Copilot, Windsurf or Codex; run make setup after cloning. With no keys it uses Piper TTS, open archives and free stock sources. Optional keys for fal.ai, Kling, ElevenLabs, OpenAI, Google, xAI, Runway, HeyGen, Suno and others go in .env and incur provider charges. Budget controls default to a $10 total cap, with per-action approval above $0.50. Local video generation needs a GPU. AGPL-3.0, which requires offering source for modified versions run as a network service.

**Source checked:** 2026-11-03. [Official source](https://github.com/calesthio/OpenMontage). [Gearlist page](https://gearlist.build/tools/openmontage/).

### [OpenSEO](https://github.com/every-app/open-seo)

An open-source SEO tool for keyword research, rank tracking, backlinks and site audits that people and agents such as Claude Code can use, positioned as a pay-as-you-go alternative to Semrush and Ahrefs.

**For:** Marketers and agencies who want SEO data inside their own agent workflows.

**Access and use:** Self-host with Docker or EveryApp, bringing your own DataForSEO API key and paying for what you use, or use the hosted version, free to try, with plans from US$10 a month that include usage credit. MCP clients connect with an account on your instance. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/every-app/open-seo). [Gearlist page](https://gearlist.build/tools/openseo/).

### [DispatchSEO](https://github.com/NeoZi12/dispatchseo)

Turns a coding agent into an SEO manager that mines keywords from Search Console, proposes topics for approval and ships content as pull requests, with daily rank checks.

**For:** Teams who run their site from a repository and already use Claude Code, Codex or Cursor.

**Access and use:** Connects to Google Search Console and your repository. The README says no extra API keys are needed and self-hosting has no feature limits; a hosted version also exists. AGPL-3.0, so changes to a hosted copy must be published.

**Source checked:** 2026-11-03. [Official source](https://github.com/NeoZi12/dispatchseo). [Gearlist page](https://gearlist.build/tools/dispatchseo/).

### [yt-dlp](https://github.com/yt-dlp/yt-dlp)

A command line tool that downloads video, audio, subtitles and metadata from YouTube and many other sites.

**For:** Agents and people who need a video's files or metadata on their own machine.

**Access and use:** Runs locally with no account. Downloads must respect each site's terms and copyright. Unlicense.

**Source checked:** 2026-11-05. [Official source](https://github.com/yt-dlp/yt-dlp). [Gearlist page](https://gearlist.build/tools/yt-dlp/).

### [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)

A Python library that fetches a YouTube video's transcript or subtitles, including auto-generated ones, without an API key.

**For:** Developers who need video text for analysis or summaries.

**Access and use:** Runs locally with no account or key. It reads YouTube's caption data, which can change or be rate limited. MIT licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/jdepoix/youtube-transcript-api). [Gearlist page](https://gearlist.build/tools/youtube-transcript-api/).

### [youtube-comment-downloader](https://github.com/egbertbouman/youtube-comment-downloader)

A Python command line tool and library that downloads a YouTube video's comments to JSON or CSV without the YouTube API.

**For:** Analysts reading audience reaction on specific videos.

**Access and use:** Runs locally with no account or API key and writes comments, including commenter names, to a local file. It reads YouTube's web pages rather than the official API, and YouTube's Terms of Service bar automated access without YouTube's written permission. MIT licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/egbertbouman/youtube-comment-downloader). [Gearlist page](https://gearlist.build/tools/youtube-comment-downloader/).

### [NewPipe Extractor](https://github.com/TeamNewPipe/NewPipeExtractor)

The Java library behind the NewPipe app that reads YouTube videos, channels, comments, playlists, search and trending lists, and also supports SoundCloud, PeerTube and Bandcamp.

**For:** Java and Android developers who want YouTube data without the official API.

**Access and use:** Runs inside your app with no account or API key, added as a dependency from JitPack or Maven Central. It scrapes YouTube's pages, which YouTube's Terms of Service bar without permission, and changes on YouTube's side can break it. GPL-3.0 licence, so software that ships it must meet the GPL's terms.

**Source checked:** 2026-11-05. [Official source](https://github.com/TeamNewPipe/NewPipeExtractor). [Gearlist page](https://gearlist.build/tools/newpipe-extractor/).

### [pytubefix](https://github.com/JuanBindez/pytubefix)

A Python library that reads YouTube video details, captions, channels, playlists and search results, and downloads streams.

**For:** Python developers who need captions or a channel's video list without an API key.

**Access and use:** Runs locally with no API key; an optional OAuth sign-in caches a Google token on the machine, and downloads are written to disk. It reads YouTube's web player rather than the official API, YouTube's Terms of Service bar automated access and downloads without permission, and changes on YouTube's side can break it. MIT licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/JuanBindez/pytubefix). [Gearlist page](https://gearlist.build/tools/pytubefix/).

### [YouTube.js](https://github.com/LuanRT/YouTube.js)

A JavaScript client for YouTube's internal InnerTube API that reads video details, channels, comments, playlists and search results.

**For:** Node.js, Deno and browser developers building YouTube research into agents.

**Access and use:** Runs locally with no API key; it caches session data by default and can use your account cookies for signed-in requests, which gives it that account's access. InnerTube is undocumented and YouTube's Terms of Service bar automated access without permission, so expect breakage and check your use. MIT licence.

**Source checked:** 2026-11-05. [Official source](https://ytjs.dev/guide/getting-started.html). [Gearlist page](https://gearlist.build/tools/youtube-js/).

### [Whisper](https://github.com/openai/whisper)

OpenAI's open speech recognition model and command line tool, which transcribes audio in many languages and can translate it into English.

**For:** People who need a transcript for a video that has no captions.

**Access and use:** Runs locally with no account; it needs Python, PyTorch and ffmpeg, downloads model weights on first use, and models need from about 1 GB to about 10 GB of GPU memory. You need the right to download and transcribe the audio you give it. MIT licence for the code and model weights.

**Source checked:** 2026-11-05. [Official source](https://github.com/openai/whisper). [Gearlist page](https://gearlist.build/tools/whisper/).

### [faster-whisper](https://github.com/SYSTRAN/faster-whisper)

A reimplementation of Whisper on the CTranslate2 inference engine, with 8-bit quantisation on CPU and GPU.

**For:** Developers running Whisper transcription in their own pipelines.

**Access and use:** Runs locally with no account and downloads converted models from the Hugging Face Hub on first use. It decodes audio with PyAV, so a system ffmpeg is not needed, while GPU use needs NVIDIA's CUDA libraries. MIT licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/SYSTRAN/faster-whisper). [Gearlist page](https://gearlist.build/tools/faster-whisper/).

### [whisper.cpp](https://github.com/ggml-org/whisper.cpp)

A C and C++ port of Whisper that runs on CPUs, Apple Silicon and a range of GPUs, with a command line tool and bindings for other languages.

**For:** People transcribing on a Mac or on a machine without a large GPU.

**Access and use:** Runs locally with no account; you build it from source and download ggml model files with the included script. The command line tool reads only 16-bit WAV files, so convert other audio with ffmpeg first. MIT licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/ggml-org/whisper.cpp). [Gearlist page](https://gearlist.build/tools/whisper-cpp/).

### [WhisperX](https://github.com/m-bain/whisperX)

A transcription tool built on faster-whisper that adds word-level timestamps and speaker labels.

**For:** Analysts transcribing interviews, podcasts or panel videos where who said what matters.

**Access and use:** Runs locally with no account for transcription, and GPU use needs NVIDIA's CUDA toolkit. Speaker labels need a Hugging Face read token and acceptance of the user agreement for the pyannote speaker-diarization-community-1 model, and alignment models are downloaded per language. BSD-2-Clause licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/m-bain/whisperX). [Gearlist page](https://gearlist.build/tools/whisperx/).

### [ThoughtLeaders CLI](https://github.com/ThoughtLeaders-io/thoughtleaders-cli)

A command line client for ThoughtLeaders' YouTube sponsorship data, covering which brands sponsor which channels, lookalike channels, transcripts, view curves and audience profiles.

**For:** Brand and agency teams using an agent to research sponsorship history before a pitch.

**Access and use:** Needs a ThoughtLeaders account, signed in by browser OAuth, device code or API key, and every query spends credits, with recommender tools on the Intelligence plan at 25 credits a call. It can add comments to records, signing out ends every session, and tl setup writes skill files into your agent's folders. Needs Python 3.12 or later with jq, ripgrep, duckdb and yt-dlp; MIT licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/ThoughtLeaders-io/thoughtleaders-cli). [Gearlist page](https://gearlist.build/tools/thoughtleaders-cli/).

### [Paseo](https://paseo.sh)

A desktop, mobile, web and CLI app that runs Claude Code, Codex, Copilot, OpenCode and other coding agents side by side, each in its own worktree.

**For:** People who want to run and steer several coding agent CLIs from one desktop app and their phone.

**Access and use:** Download the desktop app from paseo.sh/download or GitHub Releases, or on a server run npm install -g @getpaseo/cli then paseo. Needs at least one agent CLI already signed in; Paseo uses that login and stores no provider keys. The daemon listens on 127.0.0.1:6767 with no password by default, so anything that can reach that port can control your agents. Set one with paseo daemon set-password before exposing it, or pair a phone through the end-to-end encrypted relay. New Claude agents default to Auto mode, where a model classifier answers permission prompts (Always Ask on Bedrock or Vertex). Plugins run with access to the daemon machine. The README says there is no telemetry. The LICENSE file grants Apache-2.0 for Paseo and leaves third-party components under their own licences; GitHub shows NOASSERTION.

**Source checked:** 2026-11-06. [Official source](https://github.com/getpaseo/paseo). [Gearlist page](https://gearlist.build/tools/paseo/).

### [Happy](https://happy.engineering/)

A desktop and phone app that runs Claude, Codex, Grok and other coding agents on your own machine, with end-to-end encrypted sync and sessions you can share.

**For:** People who want to use the Claude, Codex or Grok subscriptions they already pay for and follow or steer the agent from a phone or with a colleague.

**Access and use:** Desktop app from happy.engineering; phone apps on the App Store and Google Play. The original CLI is npm install -g happy, then happy claude or happy codex, which shows a QR code to pair a phone. Agents sign in with your own Claude, Codex and Grok subscriptions. Sessions sync end-to-end encrypted through Happy's server (api.cluster-fluster.com by default); message IDs, timestamps and device IDs are not encrypted. npm install -g happy-server-self-host then happy server runs your own sync server. The app sends PostHog usage analytics until you turn them off in Settings. Optional voice sends microphone audio and session context to ElevenLabs outside the encryption. Anyone you invite into a session can steer its agent. MIT.

**Source checked:** 2026-11-06. [Official source](https://github.com/slopus/happy). [Gearlist page](https://gearlist.build/tools/happy/).

### [Claude Squad](https://smtg-ai.github.io/claude-squad/)

A terminal app that manages several Claude Code, Codex, Gemini or Aider sessions at once, each in its own tmux session and git worktree.

**For:** Developers who want parallel coding agents on one repository from a single terminal window.

**Access and use:** brew install claude-squad, or curl -fsSL https://raw.githubusercontent.com/smtg-ai/claude-squad/main/install.sh | bash, which puts cs in ~/.local/bin. Read the script before running it. Needs tmux and the GitHub CLI (gh). The default program is claude; start others with cs -p "codex", and the README sets OPENAI_API_KEY for Codex. The s key commits and pushes the session's branch to GitHub. The experimental -y (--autoyes) flag accepts every prompt for Claude Code and Aider without asking. Config is in ~/.claude-squad/config.json. AGPL-3.0.

**Source checked:** 2026-11-06. [Official source](https://github.com/smtg-ai/claude-squad). [Gearlist page](https://gearlist.build/tools/claude-squad/).

### [audio.cpp](https://github.com/0xShug0/audio.cpp)

A C++ inference engine built on ggml that runs local audio models for speech synthesis and recognition, voice cloning and conversion, voice activity detection and music.

**For:** Developers running speech, voice or music models on their own Windows, Linux or Mac machine from a CLI, server or web UI.

**Access and use:** Prebuilt binaries for Windows, Ubuntu and macOS are on GitHub Releases. On macOS, brew tap 0xShug0/audio-cpp, brew trust 0xShug0/audio-cpp, then brew install audio-cpp. Or build from source with CMake. Runs locally with no account. Model packages download from Hugging Face or ModelScope, and Hugging Face requests can carry your HF_TOKEN. audiocpp_server --ui --ui-management serves a web UI at http://127.0.0.1:8080 that can download models and take uploads. Model weights keep their own licences and some bar commercial use; docs/model_licenses.md lists them. The LICENSE file is Apache-2.0 (copyright ShugoAI LLC); GitHub shows NOASSERTION.

**Source checked:** 2026-11-06. [Official source](https://github.com/0xShug0/audio.cpp). [Gearlist page](https://gearlist.build/tools/audio-cpp/).

### [DS Bot](https://github.com/Fei2411/DS-Bot)

A community plugin and desktop app for DeepSeek Harness that runs a team of long-lived bots with memory, bot-to-bot handoffs and group chats.

**For:** DeepSeek Harness users who want several persistent agents to share work in group chats, on their own computer, a NAS or another always-on machine.

**Access and use:** Download the desktop app from GitHub Releases for Windows, macOS or Linux (it bundles DSH), add the ds-bot plugin in DSH Desktop, or for DSH Web run npx @deepseek-ai/dsh@0.2.2-rc.1 plugin --profile web add ds-bot then npx @deepseek-ai/dsh@0.2.2-rc.1 web, which needs Node.js 22.19 or later and pnpm. A Docker image suits a NAS or server; bots get full access to whatever you mount into the container. You need a DeepSeek account or API key, and DeepSeek bills by usage; group chats cost more, and coding-agent CLIs such as Claude Code or Codex can run a bot on their own sign-in and plan. Bot data stays in bot/ and sessions/ under ~/.dsh and is not deleted when you uninstall the plugin, but bots use your model quota, and the default auto web search falls back to the public result pages of Bing and DuckDuckGo. The Windows installer is not signed yet, so check its SHA-256 against SHA256SUMS.txt; the Windows app and Linux AppImage update themselves. The main bot has very high rights over other bots and group chats, and bots read and write files and run commands when asked. A local MCP command a bot adds needs your approval, emails wait for you to send them by default, and computer use is set per bot with a level and an app list. This is a community project, not an official DeepSeek product. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/Fei2411/DS-Bot). [Gearlist page](https://gearlist.build/tools/ds-bot/).

### [OpenWorker](https://openworker.com)

An open-source desktop AI coworker that runs on your computer, works across your files, terminal and more than 25 connected apps such as GitHub, Slack and Gmail, and asks for approval before writes, sends and shell commands.

**For:** Developers, security teams and office workers who want an agent on their own machine, using their own model keys, to review code and cloud configuration or produce documents, briefs and reports.

**Access and use:** Download the signed macOS app (Apple Silicon, macOS 12 or later) or the Windows 10/11 x64 build from openworker.com; the Windows build is not yet code-signed, so SmartScreen warns. Running from source needs Python 3.10 or later, Node 20 or later and the Rust toolchain. Add an API key for OpenAI, Anthropic, Google or another listed provider, or point it at Ollama to run fully local. Conversations, connector tokens and model keys stay in the app's local secret store, and data leaves only through the model and connectors you choose. The one cloud piece brokers OAuth sign-ins for connectors; it is used with an optional free account for one-click connections such as Slack, and everything works signed out with your own keys. Actions are approval-gated by default; an optional auto-approve mode lets a reviewer model pass routine actions, and commands can run in an NVIDIA OpenShell container, the macOS sandbox or a hidden Windows account. The app is in open beta and updates itself. The app is free and you pay your model provider directly. MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/andrewyng/openworker). [Gearlist page](https://gearlist.build/tools/openworker/).

### [Cactus](https://github.com/cactus-compute/cactus)

A Python package that runs small text, speech and vision models locally, with tool calling, structured extraction, transcription, image description and fine-tuning.

**For:** Developers who want an agent to call tools, extract structured data or transcribe speech on a laptop or consumer device, with inference running locally.

**Access and use:** Install with pip install -U cactus-compute; it needs Python 3.9 or later. On first use it downloads and caches the engine and the requested model weights from Hugging Face, then inference runs locally. agent.run() executes your Python functions as soon as the model picks them; use complete() to inspect proposed calls before running them. The package sends anonymous usage counts (function name, package version, OS and a random install ID, which the docs say never include prompts, outputs or data). The README says CACTUS_TELEMETRY=0 turns this off, and the repo's llms.txt names NEEDLE_TELEMETRY=0 or DO_NOT_TRACK=1. Fine-tuning needs pip install "cactus-compute[train]", and the documented synthetic data step is set up with an OPENROUTER_API_KEY. The hosted Cactus Platform for fine-tuning needs a CACTUS_API_KEY, and each finetune or generate job spends account allowance at submission. The Needle 3, Whistle and Mirage weights are tagged apache-2.0 on Hugging Face. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/cactus-compute/cactus). [Gearlist page](https://gearlist.build/tools/cactus/).

### [Kanzo](https://github.com/emanuele-em/kanzo)

A self-hosted kanban board and MCP server in one program, where coding agents take tasks, move cards and comment on the same board you use in the browser.

**For:** Developers running Claude Code, Codex or another MCP client who want one task board shared between themselves and their agents.

**Access and use:** Install on macOS or Linux with curl -LsSf https://github.com/emanuele-em/kanzo/releases/latest/download/kanzo-installer.sh | sh. Read the script before running it. Windows uses a PowerShell installer that also pipes a downloaded script, and cargo install kanzo works too; releases can be checked with gh attestation verify <file> --repo emanuele-em/kanzo. Run kanzo to open the board at http://localhost:4242, then connect an agent with claude mcp add kanzo --scope user -- kanzo mcp (Claude Code) or codex mcp add kanzo -- kanzo mcp (Codex). No account is needed, and the board and its settings live in ~/kanzo. The board has no logins: it listens on 127.0.0.1 by default, but sharing it (kanzo share on) or setting listen = "0.0.0.0" lets anyone who can reach the port read and change the board and use its MCP endpoint, so share only on a network you trust. Optional sync commits the board and pushes it to a private git repo you own. The board checks GitHub releases for a new version, caching the result for 24 hours, and offers a one-click update. AGPL-3.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/emanuele-em/kanzo/blob/main/README.md). [Gearlist page](https://gearlist.build/tools/kanzo/).

### [Cindy](https://cindy.app)

An open-source AI agent app for desktop and mobile that runs Claude Code, Codex or the Pi agent behind one interface, works with your files, browser and apps, and lets you pick up a session from another of your devices.

**For:** People who already pay for Claude Code or Codex, or hold model API keys, and want one agent app across their computers and phone with automations, Skills, plugins and MCP.

**Access and use:** Download for macOS, Windows, Linux, iOS or Android from cindy.app/download; Linux has its own install guide. Building from source needs Node.js 22, pnpm 10 and Git LFS, and pnpm install downloads the claude-code, codex and ripgrep binaries. Authorise a Claude Code or Codex plan you already pay for, add your own API keys, or use a local model. The client connects to Cindy's cloud services by default and updates from Cindy's CDN; when signed in, cloud companions sync conversations, memory, skills and shared attachments through Cindy's services, while Skip Sign-In runs local agents with no account but without server features. Official builds send TapDB usage analytics (device identifiers, app version and activity events, linked to your account ID after sign-in, but not chat or file content), on by default and switchable off under Settings, About, Usage statistics. The phone's built-in remote desktop can operate a connected computer once you grant it permissions. The client is free; Cindy's managed model service is optional, with top-ups from $10 and plans from $16 a month (currency not stated). The backend is not in this repository. Apache-2.0 for the client.

**Source checked:** 2026-11-07. [Official source](https://github.com/makecindy/cindy). [Gearlist page](https://gearlist.build/tools/cindy/).

### [Fara1.5](https://github.com/microsoft/fara)

A family of Microsoft computer use agent models in 4B, 9B and 27B sizes that read a screenshot of a browser and act with mouse and keyboard input or web searches, with a command-line tool to run them.

**For:** Researchers and developers building browser agents who want an open-weight computer use model they can host on Microsoft Foundry or on their own GPUs.

**Access and use:** Clone the repository, create a Python virtual environment, then run pip install -e . and playwright install (use pip install -e .[vllm] to self-host). The easiest path is to deploy a model on Microsoft Foundry and point fara-cli at its endpoint URL and API key, with no GPU or model download; otherwise download the weights from Hugging Face and serve them with vLLM on your own GPUs, with a context length of at least 15000 tokens. On Windows, Microsoft recommends WSL2. Each step gives the model a screenshot of the browser and the conversation history, so those go to whichever endpoint hosts it, and runs save per-step screenshots and a data_point.json to the output folder. Microsoft calls it a research preview and recommends running it in a sandbox, monitoring it, and avoiding sensitive data and high-risk sites; Magentic-UI adds a sandboxed browser with action logs and prompts at critical points. MIT for the code and the model weights.

**Source checked:** 2026-11-07. [Official source](https://github.com/microsoft/fara). [Gearlist page](https://gearlist.build/tools/fara/).

## MCP and integrations

### [Are you found by AI? MCP server](https://github.com/techhorizonlabs/foundbyai-mcp)

Connect an MCP client to saved AI visibility measurements and evidence. Tech Horizon Labs project.

**For:** Businesses and agencies using their own AI to inspect visibility data.

**Access and use:** Account access is scoped by the connection. Review the rescan action separately from read tools.

**Source checked:** 2026-10-25. [Official source](https://github.com/techhorizonlabs/foundbyai-mcp). [Gearlist page](https://gearlist.build/tools/found-by-ai-mcp/).

### [gogcli](https://gogcli.sh/)

A command line interface for Google Workspace services with structured output.

**For:** People and agents automating Workspace tasks.

**Access and use:** OAuth scopes can allow reads and writes. Choose the account and access needed for the task.

**Source checked:** 2026-10-25. [Official source](https://gogcli.sh/). [Gearlist page](https://gearlist.build/tools/gogcli/).

### [GitHub MCP Server](https://github.com/github/github-mcp-server)

GitHub's official MCP server for repositories, issues, pull requests and Actions.

**For:** Agents and developers working on GitHub data they are allowed to access.

**Access and use:** Needs a GitHub OAuth login or personal access token. Scopes can read and write repositories. Use a read-only token unless a write is required.

**Source checked:** 2026-10-26. [Official source](https://github.com/github/github-mcp-server). [Gearlist page](https://gearlist.build/tools/github-mcp-server/).

### [GitMCP](https://gitmcp.io/)

A remote MCP server that turns a public GitHub project into documentation an agent can query.

**For:** People pointing an agent at a public repository without cloning it.

**Access and use:** Works on public GitHub content. Last upstream push observed 2026-05-08. Confirm the target repo is public before connecting.

**Source checked:** 2026-10-26. [Official source](https://github.com/idosal/git-mcp). [Gearlist page](https://gearlist.build/tools/gitmcp/).

### [XERJ](https://xerj.org)

A local-first search engine and MCP server that indexes code, docs, logs and PDFs for agents.

**For:** People who want cited local search and agent memory without a hosted search cluster.

**Access and use:** Installer is curl -fsSL https://xerj.org/get | sh. Read the script before running it. The binary indexes local paths and can serve an Elasticsearch-compatible API on localhost. Apache-2.0.

**Source checked:** 2026-10-27. [Official source](https://github.com/xerj-org/xerj). [Gearlist page](https://gearlist.build/tools/xerj/).

### [Supabase MCP](https://supabase.com/docs/guides/ai-tools/mcp)

Supabase's official remote MCP server for docs, account, database, functions and related project tools.

**For:** Developers whose agents need to work on a Supabase project they control.

**Access and use:** Remote URL https://mcp.supabase.com/mcp with OAuth. Can list, query and change project data. Read Supabase's MCP security notes and restrict feature groups before connecting production.

**Source checked:** 2026-10-27. [Official source](https://supabase.com/docs/guides/ai-tools/mcp). [Gearlist page](https://gearlist.build/tools/supabase-mcp/).

### [Notion MCP](https://developers.notion.com/guides/mcp/overview)

Notion's hosted MCP server for searching, reading, creating and updating pages and databases in a workspace the user can access.

**For:** People whose agents need live Notion context they already have permission to see.

**Access and use:** Remote URL https://mcp.notion.com/mcp with OAuth. On Business and Enterprise plans a workspace owner can also create an MCP token, which a client sends as a bearer token with no browser sign-in, and Enterprise workspaces with SAML SSO can use enterprise-managed authorization. Only workspace members can connect; guests cannot. Can read and write workspace content. Workspace owners can manage which clients connect. Prefer the hosted server over the unmaintained self-hosted repo.

**Source checked:** 2026-11-07. [Official source](https://developers.notion.com/guides/mcp/get-started-with-mcp). [Gearlist page](https://gearlist.build/tools/notion-mcp/).

### [Cloudflare MCP](https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/)

Cloudflare's hosted API MCP server covering DNS, Workers, R2, Zero Trust and the rest of the Cloudflare API, plus docs search.

**For:** People whose agents work on a Cloudflare account they control.

**Access and use:** Remote URL https://mcp.cloudflare.com/mcp with OAuth, or a scoped API token as a bearer. Can change account configuration. Grant the smallest permission set. Other product-specific Cloudflare MCP URLs exist; this is the main API server.

**Source checked:** 2026-10-27. [Official source](https://developers.cloudflare.com/agents/model-context-protocol/cloudflare/servers-for-cloudflare/). [Gearlist page](https://gearlist.build/tools/cloudflare-mcp/).

### [OmniSeek](https://github.com/Battam1111/omniseek)

A local MCP add-on that searches places web search often misses, including Bilibili, Zhihu and scholarly papers.

**For:** People whose agents need those sources in Claude Code, Cursor or Codex.

**Access and use:** Install with uv tool install omniseek, then claude mcp add omniseek -- omniseek. Runs on your computer. Apache-2.0. Python 3.11 or later.

**Source checked:** 2026-10-28. [Official source](https://github.com/Battam1111/omniseek). [Gearlist page](https://gearlist.build/tools/omniseek/).

### [Context Mode](https://github.com/mksglu/context-mode)

An MCP server and hooks layer that sandboxes large tool output, keeps a local session index, and can run analysis scripts so agents do not dump whole files into context.

**For:** People running Claude Code or other supported clients whose context windows fill with tool output.

**Access and use:** In Claude Code: /plugin marketplace add mksglu/context-mode then /plugin install context-mode@context-mode. MCP-only: claude mcp add context-mode -- npx -y context-mode. ctx_execute can run code on your machine. Elastic License 2.0: you may not offer it as a hosted service that exposes its features.

**Source checked:** 2026-10-28. [Official source](https://github.com/mksglu/context-mode). [Gearlist page](https://gearlist.build/tools/context-mode/).

### [jCodeMunch MCP](https://github.com/jgravelle/jcodemunch-mcp)

A local MCP server that indexes a codebase with tree-sitter and returns the function or class an agent asked for, instead of whole files.

**For:** People whose coding agents spend context reading large files in Claude Code, Cursor, Codex or other MCP clients.

**Access and use:** Install with uv tool install jcodemunch-mcp, then jcodemunch-mcp init. Indexes live at ~/.code-index/. Free for personal use. Commercial use needs a paid licence. Default install sends an anonymous savings counter; set share_savings false to opt out.

**Source checked:** 2026-10-28. [Official source](https://github.com/jgravelle/jcodemunch-mcp). [Gearlist page](https://gearlist.build/tools/jcodemunch-mcp/).

### [Monid](https://monid.ai/)

A hosted MCP, CLI and skill for discovering, inspecting and running third-party data endpoints against one Monid balance. The public repo is the MIT Deno connector framework those endpoints are written in.

**For:** Teams who want one billed catalog of agent tools, or to add a connector as a pull request.

**Access and use:** Hosted MCP is https://mcp.monid.ai/v1 and signs in with a Monid account. Skill setup is the public file https://monid.ai/SKILL.md plus an API key from app.monid.ai. CLI is npm install -g @monid-ai/cli, then monid keys add. Hosted runs spend a prepaid balance or x402 USDC (a stablecoin payment), priced per call or per result on each endpoint. Local clone needs Deno 2.x; deno task check and deno task test run offline, and engine:run needs that provider's vendor key. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/monid-ai/monid). [Gearlist page](https://gearlist.build/tools/monid/).

### [anymd](https://sylphxai.github.io/anymd/)

A local Rust MCP server and CLI that turns PDFs, Office files, HTML, images, audio and video into Markdown for agents.

**For:** People whose coding agents need to read local documents as Markdown.

**Access and use:** npx -y @sylphx/anymd setup. Needs Node 18 or later. Also brew install sylphxai/tap/anymd, pip, Docker or cargo. Local MIT binary needs no API key. OCR and ASR model downloads need explicit opt-in. Confine the MCP server with --allow-dir. Hosted Sylphx AI parse is a paid metered service that uses the same crates. anymd Pro is an optional one-time purchase for cite-check and video timelines. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/SylphxAI/anymd). [Gearlist page](https://gearlist.build/tools/anymd/).

### [Chrome DevTools for agents](https://developer.chrome.com/docs/devtools/agents)

Browser debugging for coding agents from the Chrome DevTools team: an MCP server, chrome-devtools-mcp, that lets an agent inspect and control Chrome, record performance traces, debug console and network activity, take screenshots and automate pages with Puppeteer.

**For:** Developers who want a coding agent to debug, test or measure web pages in Chrome.

**Access and use:** The connected MCP client can inspect and change browser and DevTools data. A normal browser profile can hold signed-in sessions and other sensitive data, and this is neither a sandbox nor a read-only debugger. Usage statistics are on by default; --no-usage-statistics turns them off, and Chrome's own metrics setting is separate. Performance tools may send trace URLs to CrUX, the Chrome UX Report; --no-performance-crux turns that off. npm update checks are a further outside request. Officially supports Chrome and Chrome for Testing. Apache-2.0.

**Source checked:** 2026-11-14. [Official source](https://github.com/ChromeDevTools/chrome-devtools-mcp). [Gearlist page](https://gearlist.build/tools/chrome-devtools-mcp/).

### [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)

Tools for inspecting and testing MCP servers, from the Model Context Protocol project, with browser, command line and terminal interfaces for connecting to a server.

**For:** Developers building, debugging or testing MCP servers.

**Access and use:** It can start local stdio servers, which runs their code on your machine, and connect to remote servers using their authentication and the OAuth grants you give; the scopes depend on each server. It can save tokens, client secrets and configured environment values. Secrets go to the OS credential store when one is available; on headless or keychain-less systems they can fall back to a file that is not encrypted unless you configure a key. Some connection tooling is experimental. The current version 2 documentation differs from the legacy version 1. The licence is in transition: new code is Apache-2.0, older contributions without relicensing consent remain MIT, and documentation other than the specification is CC BY 4.0.

**Source checked:** 2026-11-14. [Official source](https://github.com/modelcontextprotocol/inspector). [Gearlist page](https://gearlist.build/tools/mcp-inspector/).

### [OpenAI MCP Extensions](https://github.com/openai/mcp-extensions)

An SDK and spec that add ChatGPT-specific MCP capabilities so plugins can open from the sidebar, handle files and take composer mentions.

**For:** People building ChatGPT plugins that need more than a plain MCP server.

**Access and use:** npm install @openai/mcp-extensions, or pip install openai-mcp-extensions. For ChatGPT plugin developers. Try Bits & Bolts Remote from ChatGPT's plugin list. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/openai/mcp-extensions). [Gearlist page](https://gearlist.build/tools/openai-mcp-extensions/).

### [MCPProxy](https://mcpproxy.app)

A local proxy that sits in front of many MCP servers, holds new tools until you approve them, and gives agents a small discovery set.

**For:** People who want many MCP servers behind one localhost endpoint, with a review gate before agents can call new tools.

**Access and use:** brew install --cask smart-mcp-proxy/mcpproxy/mcpproxy, or brew install smart-mcp-proxy/mcpproxy/mcpproxy for the CLI, or a GitHub Release for macOS, Windows or Linux. mcpproxy serve listens on 127.0.0.1:8080. Config and data live under ~/.mcpproxy/. New servers stay quarantined until you review and approve them. Update checks query GitHub Releases on startup and every 4 hours until you set update_check.enabled to false or MCPPROXY_DISABLE_AUTO_UPDATE=true. JavaScript code execution is on by default. The tray Unix socket is trusted without the API key until you set enable_socket to false. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/smart-mcp-proxy/mcpproxy-go). [Gearlist page](https://gearlist.build/tools/mcpproxy/).

### [PLUR](https://plur.ai)

Local-first shared memory for coding agents, stored as plain YAML engrams under ~/.plur/.

**For:** People who want corrections and conventions to persist across Claude Code, Codex, Cursor, OpenCode and similar tools.

**Access and use:** npm install -g @plur-ai/cli@latest @plur-ai/mcp@latest, then plur init and plur doctor. Needs Node.js 20+. For Claude Code, init writes the MCP server into ~/.claude.json and hooks into ~/.claude/settings.json. plur doctor downloads a local search model when downloads are allowed; without it, search uses keywords. An optional openai-3-large embedder sends text to OpenAI. plur dashboard is loopback-only. plur sync to a personal git remote pushes private engrams; use a private repo. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/plur-ai/plur). [Gearlist page](https://gearlist.build/tools/plur/).

### [Plausible MCP](https://plausible-mcp.sentry.dev)

An MCP server that queries Plausible Analytics for traffic, conversions and period comparisons.

**For:** People who want a coding agent to read Plausible stats with a Plausible API key.

**Access and use:** Hosted: claude mcp add --transport http plausible https://plausible-mcp.sentry.dev/mcp --header "Authorization: Bearer YOUR_PLAUSIBLE_API_KEY". Queries go to that Sentry-hosted server with your key. Tools are read-only. Local: Node.js 20+, git clone, pnpm install and pnpm build, then node dist/index.js with PLAUSIBLE_API_KEY. PLAUSIBLE_BASE_URL points at a self-hosted Plausible. The hosted /internal path is for Sentry staff. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/getsentry/plausible-mcp). [Gearlist page](https://gearlist.build/tools/plausible-mcp/).

### [Short Video Maker](https://github.com/gyoridavid/short-video-maker)

A local MCP and REST server that turns English narration scenes into captioned short videos with Kokoro speech, Whisper captions, Pexels B-roll and Remotion.

**For:** People generating English short-form videos on their own machine or Docker host.

**Access and use:** Needs a free Pexels API key, about 4 GB RAM, 2 vCPU and 5 GB disk. Docker tiny image: docker run -it --rm --name short-video-maker -p 3123:3123 -e PEXELS_API_KEY= gyoridavid/short-video-maker:latest-tiny. Web UI and REST at http://localhost:3123. MCP SSE at /mcp/sse. Videos land in ~/.ai-agents-az-video-generator with npm, or /app/data in Docker. English voiceover only. Windows is unsupported. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/gyoridavid/short-video-maker). [Gearlist page](https://gearlist.build/tools/short-video-maker/).

### [AnythingMCP](https://github.com/HelpCode-ai/anythingmcp)

A self-hosted MCP gateway that turns REST, OpenAPI, SOAP, GraphQL, OData or SQL systems into MCP tools, with a catalog of ready connectors.

**For:** Teams who want Claude, ChatGPT or Copilot to call existing APIs and ERPs through one MCP URL they host.

**Access and use:** Needs Docker 24+ and openssl. mkdir anythingmcp && cd anythingmcp, then curl the official docker-compose.quickstart.yml, write JWT_SECRET and ENCRYPTION_KEY with openssl rand -hex 32, then docker compose up -d. UI is http://localhost:3000; the first registered account is admin. MCP is http://localhost:4000/mcp. Keep the generated .env: ENCRYPTION_KEY decrypts stored connector credentials. Quickstart binds 127.0.0.1. Connector keys are stored encrypted and forwarded to the APIs you attach (SAP, shops, databases). SQL tools are read-only by default. The optional hosted trial at https://cloud.anythingmcp.com runs on the maintainers' servers in Frankfurt, Germany, and holds your connector credentials there. AGPL-3.0 for the open tree; ee/ directories use a separate commercial licence.

**Source checked:** 2026-10-28. [Official source](https://github.com/HelpCode-ai/anythingmcp). [Gearlist page](https://gearlist.build/tools/anythingmcp/).

### [Alumnium](https://alumnium.ai)

An MIT AI test harness over Appium, Maestro, Playwright or Selenium, as a library and as MCP.

**For:** Testers who want an agent to drive a browser or a phone with do, get and check.

**Access and use:** MCP: curl -LsSf https://alumnium.ai/install.sh | sh (read the script before running it), then claude mcp add alumnium --env OPENAI_API_KEY=... -- alumnium mcp. Libraries: pip install alumnium, npm install alumnium, or the Java artifact. Agentic mode (default) sends page text, accessibility trees and screenshots to the model you set. Direct mode skips the model and lets your coding agent call driver actions. Browser profiles live in ~/.alumnium/profiles. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/alumnium-hq/alumnium). [Gearlist page](https://gearlist.build/tools/alumnium/).

### [ACI.dev](https://github.com/aipotheosis-labs/aci)

An open-source tool-calling platform that gives agents over 600 pre-built app integrations, with managed OAuth and secrets, natural-language permission boundaries and tool discovery, through a unified MCP server or Python and TypeScript SDKs.

**For:** Developers giving an agent or agentic IDE authenticated access to many SaaS tools, for themselves or for their own end users.

**Access and use:** Use the managed service at aci.dev with an account and API key, or run the platform locally: Python 3.12+, Docker Compose, PostgreSQL with pgvector and an OpenAI API key, with PropelAuth for the dev portal. Each linked app needs OAuth consent or API credentials from the account the agent will act on, held in ACI's secrets management. The unified MCP server is a separate repository, aipotheosis-labs/aci-mcp. Apache-2.0.

**Source checked:** 2026-11-03. [Official source](https://github.com/aipotheosis-labs/aci). [Gearlist page](https://gearlist.build/tools/aci-dev/).

### [Xero MCP Server](https://github.com/XeroAPI/xero-mcp-server)

Xero's MCP server for reading and writing accounting and payroll data, including contacts, invoices, quotes, payments, bank transactions, manual journals, reports and timesheets.

**For:** Businesses and bookkeepers who want an agent to query or update a Xero organisation.

**Access and use:** Runs locally with Node.js 18 or later through npx -y @xeroapi/xero-mcp-server@latest. Authenticate with a Xero Custom Connection (XERO_CLIENT_ID and XERO_CLIENT_SECRET) or a bearer token from your own OAuth flow (XERO_CLIENT_BEARER_TOKEN). Xero's developer docs say Custom Connections are only for organisations in Australia, New Zealand, the UK and the US and need an additional monthly subscription, but connect to the Demo Company free for development. The tools can create invoices, payments, bank transactions and manual journals and approve timesheets, so narrow XERO_SCOPES and start on the Demo Company. Payroll queries need an NZ or UK organisation. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/XeroAPI/xero-mcp-server). [Gearlist page](https://gearlist.build/tools/xero-mcp-server/).

### [World Intelligence MCP Server](https://github.com/marc-shade/world-intel-mcp)

A Python MCP server, CLI and local dashboard that pulls markets, SEC filings, economic data, conflict, disaster, aviation, cyber and news feeds from public APIs, keeps a dated history, and can index results in Qdrant for semantic search.

**For:** Analysts and research agents that need a broad, cited view of world events and markets.

**Access and use:** Clone, pip install -e ., then run world-intel-mcp over stdio and add it to ~/.claude.json. The dashboard serves http://localhost:8501 and binds 127.0.0.1 by default. Most sources need no key; ACLED, UCDP, NASA FIRMS, EIA, FRED, Cloudflare, OpenSky, TomTom and Windy tools use optional credentials. The optional collector daemon fetches every source on a 5-minute default interval and stores history in ~/.cache/world-intel-mcp/cache.db. Qdrant runs separately in Docker, and AI briefs use a local Ollama. Each upstream source keeps its own terms of use, so check them before business use. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/marc-shade/world-intel-mcp). [Gearlist page](https://gearlist.build/tools/world-intel-mcp/).

### [Influencers Club MCP server](https://github.com/Influencers-Club/influencers-club-mcp)

Search creators on Instagram, TikTok, YouTube and other platforms from an MCP client, with profile, audience and lookalike data.

**For:** Marketers looking for creators whose audience matches their buyers.

**Access and use:** Needs an Influencers Club account with API credits, and each call spends them. A local install reads an API key from the environment, and its batch tools read and write local files. MIT licence.

**Source checked:** 2026-11-05. [Official source](https://docs.influencers.club/guides/mcp-server). [Gearlist page](https://gearlist.build/tools/influencers-club-mcp/).

### [vidIQ MCP server](https://github.com/vid-io/vidiq-mcp)

Gives an AI client vidIQ's YouTube data: video and channel stats, outlier videos, keyword research, comments, transcripts and earnings estimates.

**For:** Marketers and creators researching YouTube channels and content.

**Access and use:** Needs a vidIQ account, and hosted tools may use credits. It reads data for the channels you authorise, and some tools can make approved edits to videos you own. Apache 2.0 licence for the plugin.

**Source checked:** 2026-11-05. [Official source](https://github.com/vid-io/vidiq-mcp). [Gearlist page](https://gearlist.build/tools/vidiq-mcp/).

### [YouTube Data API](https://developers.google.com/youtube/v3)

Google's official API for public channel, video and playlist data, such as subscriber, view and comment counts.

**For:** Developers building channel analysis into agents.

**Access and use:** Needs a Google Cloud project and an API key. The default quota is 10,000 units a day, and most reads cost 1 unit. Changes to a channel need its owner's OAuth consent.

**Source checked:** 2026-11-05. [Official source](https://developers.google.com/youtube/v3/getting-started). [Gearlist page](https://gearlist.build/tools/youtube-data-api/).

### [yutu](https://github.com/eat-pray-ai/yutu)

A CLI, MCP server and agent mode that work through the official YouTube Data API, with optional Analytics and Reporting API access.

**For:** Channel teams who want an agent to read and manage their own YouTube channel.

**Access and use:** Needs your own Google Cloud project and OAuth client, and it saves client_secret.json and youtube.token.json in the working folder unless you set its environment variables. The OAuth grant lets it create, update and delete videos, playlists and comments on that channel, and agent mode sends prompts to the Gemini or OpenAI key you supply. Data API quota applies; Apache 2.0 licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/eat-pray-ai/yutu). [Gearlist page](https://gearlist.build/tools/yutu/).

### [YouTube MCP Server (ZubeidHendricks)](https://github.com/ZubeidHendricks/youtube-mcp-server)

An MCP server with read-only tools for YouTube video, channel, playlist and transcript lookups, plus creator search filtered by subscriber count and recent uploads.

**For:** Marketers using an MCP client to shortlist creators by size and activity.

**Access and use:** Needs a YouTube Data API key in the environment, and each search spends that key's daily quota. It can fall back to a second and third key when one runs out, but the YouTube API Services Terms forbid getting round quota limits, so configure one key. Channel results can include emails found in public metadata, which are personal information; MIT licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/ZubeidHendricks/youtube-mcp-server). [Gearlist page](https://gearlist.build/tools/youtube-mcp-server-zubeid/).

### [YouTube Transcript MCP server](https://github.com/kimtaeyoon83/mcp-server-youtube-transcript)

An MCP server that fetches a YouTube video's captions, with optional timestamps, and by default strips sponsor and promotional sections marked by chapters.

**For:** People who want an agent to read or summarise what a video says.

**Access and use:** Runs through npx with no account or key for transcripts. It reads YouTube's caption data outside the official API, which YouTube's Terms of Service restrict, and the optional video analysis tool sends a direct video URL to TwelveLabs under your own TwelveLabs key. MIT licence.

**Source checked:** 2026-11-05. [Official source](https://github.com/kimtaeyoon83/mcp-server-youtube-transcript). [Gearlist page](https://gearlist.build/tools/youtube-transcript-mcp/).

### [HypeAuditor MCP server](https://mcp.hypeauditor.com/)

HypeAuditor's hosted MCP server for YouTube, Instagram and TikTok creator analytics, including subscriber demographics, authenticity scores, growth and price estimates.

**For:** Brands and agencies vetting creators before paying for a campaign.

**Access and use:** Sign in with a HypeAuditor Pro or higher account; creator analytics spend AI credits at US$0.005 each, about 10 for a search and 100 for an analysed account, and the assistant asks before any paid unlock. It can also create media plans and move creators between campaigns in your account. HypeAuditor's terms bar bots and scraping outside its API, which is a separate product sold through its sales team.

**Source checked:** 2026-11-05. [Official source](https://mcp.hypeauditor.com/). [Gearlist page](https://gearlist.build/tools/hypeauditor-mcp/).

### [Arcmira](https://arcmira.com/)

A hosted transcript search service and MCP server for YouTube and podcasts that finds quotes, mentions, media appearances, ad reads and recurring channel sponsors.

**For:** Researchers tracking what is said about a brand and which brands sponsor which channels.

**Access and use:** Sign in through your MCP client or use an arc_sk_ account key; the free plan has 1,000 credits a month and withholds the newest 30 days, and sponsor and ad-read data needs the Pro+ plan. Reads cost credits per row, and the write tool can create and pause monitors but not delete them. Speaker and sponsor labels can be incomplete, and the MCP server's repository, arcmira/mcp, has a proprietary licence that only permits running the published server; the Claude Code plugin and its skills, in its plugins/arcmira folder, are Apache-2.0.

**Source checked:** 2026-11-08. [Official source](https://arcmira.com/docs/mcp-server). [Gearlist page](https://gearlist.build/tools/arcmira/).

### [1of10 MCP](https://1of10.com/mcp)

Connects Claude or ChatGPT to 1of10's database of YouTube outlier videos, which beat their channel's usual views, and to its title and thumbnail tracking.

**For:** Creators and strategists looking for video ideas that already work in a niche.

**Access and use:** Needs a 1of10 Pro (US$89 a month) or Ultra plan, and you connect by signing in from its Claude and ChatGPT page; the server link for other clients appears only after sign-in. Research does not use credits but generating titles, ideas or thumbnails does, and it can save videos, create trackers and link your channel without deleting anything. There is no public API reference beyond the product page.

**Source checked:** 2026-11-05. [Official source](https://1of10.com/mcp). [Gearlist page](https://gearlist.build/tools/1of10-mcp/).

### [Are you found by AI? DNS-AID checker](https://areyoufoundbyai.com/tools/dns-aid-checker)

Check a domain's DNS-AID index record against DNS-AID draft-02, an IETF Internet-Draft that is still a work in progress. It checks DNS only, and a DNS-AID record does not change your Are you found by AI? score. It looks for an SVCB record (type 64) at _index._agents.yourdomain.com and does not test the endpoint the record points to, its TLS connection or whether an AI engine uses it. Tech Horizon Labs project.

**For:** People who operate an agent index and want to see whether their domain publishes its DNS-AID record.

**Access and use:** Free web form that asks only for a domain, with no sign-in. The page sends that domain to areyoufoundbyai.com, which looks up the record and shows the queried name, the target and whether the resolver reports an authenticated answer. The page says no DNS-AID setup is needed unless you operate an agent index, and to read its setup requirements at areyoufoundbyai.com/guides/dns-aid before changing DNS.

**Source checked:** 2026-11-06. [Official source](https://areyoufoundbyai.com/tools/dns-aid-checker). [Gearlist page](https://gearlist.build/tools/dns-aid-checker/).

### [Playwright MCP](https://github.com/microsoft/playwright-mcp)

Microsoft's MCP server that lets an agent drive a real browser with Playwright, reading each page as an accessibility snapshot so it needs no screenshots or vision model.

**For:** Developers who want an agent to browse sites, fill in forms or test a web app from Claude Code, Codex, VS Code, Cursor or another MCP client.

**Access and use:** Runs locally with npx @playwright/mcp@latest, for example claude mcp add playwright npx @playwright/mcp@latest. Needs Node.js 18 or later. By default the browser keeps a persistent profile on disk (ms-playwright/mcp-* in your user cache folder), so sites you sign in to stay signed in; --isolated keeps the profile in memory instead. --extension connects to your running Chrome or Edge and its signed-in tabs. The README says the server is not a security boundary, and neither are --allowed-origins and --blocked-origins. --port serves it over HTTP on localhost; --host 0.0.0.0 opens it to the network. The README suggests coding agents may do better with the Playwright CLI and skills, which use fewer tokens. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/microsoft/playwright-mcp). [Gearlist page](https://gearlist.build/tools/playwright-mcp/).

### [Sentry MCP](https://mcp.sentry.dev)

Sentry's hosted MCP server that lets a coding agent look up Sentry issues, errors, traces and logs, and ask Sentry's Seer to analyse an issue, while you debug.

**For:** Developers whose apps report to Sentry and who want Cursor, Claude Code or another coding agent to pull in production errors while they fix them.

**Access and use:** Remote URL https://mcp.sentry.dev/mcp, for example claude mcp add --transport http sentry https://mcp.sentry.dev/mcp, which opens an OAuth sign-in to your Sentry account. Adding an organisation slug, or an organisation and project slug, to the URL path limits the session to that scope. Clients that send custom headers can pass a Sentry user token as Authorization: Sentry-Bearer instead. For self-hosted Sentry, run npx @sentry/mcp-server@latest over stdio with SENTRY_AUTH_TOKEN and SENTRY_HOST; the README's token scopes include project:write, team:write and event:write. When you run it yourself, the natural-language search tools need your own OpenAI, Azure OpenAI, Anthropic or OpenRouter key. The source moved from getsentry/sentry-mcp to getsentry/toolkit. The LICENSE.md file is FSL-1.1-Apache-2.0; GitHub shows NOASSERTION.

**Source checked:** 2026-11-07. [Official source](https://github.com/getsentry/toolkit). [Gearlist page](https://gearlist.build/tools/sentry-mcp/).

### [Atlassian MCP Server](https://github.com/atlassian/atlassian-mcp-server)

Atlassian's official hosted MCP server, which lets an agent search, summarise, create and update work in Jira, Confluence, Jira Service Management, Bitbucket, Compass and Loom.

**For:** Teams on Atlassian Cloud who want Claude, ChatGPT, Cursor, VS Code or a coding agent to work with their Jira issues and Confluence pages.

**Access and use:** Remote URL https://mcp.atlassian.com/v2/mcp (v2 is the recommended version), for example claude mcp add --transport http atlassian https://mcp.atlassian.com/v2/mcp, then /mcp to sign in. Needs an Atlassian Cloud site. Sign in with OAuth 2.1 or an API token; actions run with your existing Atlassian permissions. Jira Service Management tools work only with API tokens that an organisation admin has turned on, and the Jira delete and manage tools stay off until an admin enables them. Admins can choose which AI tools and domains may connect, and each tool call is recorded in the organisation's audit log. IP allowlists apply to MCP requests, so a hosted AI client calling from its provider's addresses may be refused. The repository's plugin files and skills are Apache-2.0; the server itself runs on Atlassian Cloud.

**Source checked:** 2026-11-07. [Official source](https://github.com/atlassian/atlassian-mcp-server). [Gearlist page](https://gearlist.build/tools/atlassian-mcp-server/).

### [Stripe MCP](https://docs.stripe.com/mcp)

Stripe's hosted MCP server, in public preview, that lets an agent search Stripe's documentation and read or write account data through the Stripe API.

**For:** Developers and Stripe account owners who want an agent to build a Stripe integration, look up Stripe data or analyse subscriptions and billing.

**Access and use:** Remote URL https://mcp.stripe.com. npm install -g @stripe/cli@latest then stripe agent setup configures it, with Stripe's skills, for the agents it detects. Sign in with OAuth, choosing which live accounts or sandboxes the client may use, or pass an agent API key as a bearer token. From December 2026 it stops accepting full-access secret keys and restricted keys without the Agent tag. The stripe_api_write tool can call any Stripe API POST, PATCH, PUT or DELETE method. Some actions, such as refunds, wait for you to approve them in the Dashboard, and Stripe asks you to turn on tool approval in your client as well. Admins can turn MCP access on or off for live mode and for sandboxes. The older @stripe/agent-toolkit and @stripe/mcp packages are deprecated and get no security fixes. Stripe's plugin and skills repository, github.com/stripe/ai, is MIT.

**Source checked:** 2026-11-07. [Official source](https://docs.stripe.com/mcp). [Gearlist page](https://gearlist.build/tools/stripe-mcp/).

### [Linear MCP server](https://linear.app/docs/mcp)

Linear's hosted MCP server, with tools to find, create and update issues, projects and comments in a Linear workspace.

**For:** Teams on Linear who want Claude, Cursor, Codex or another agent to read and update their issues and projects.

**Access and use:** Remote URL https://mcp.linear.app/mcp over Streamable HTTP, for example claude mcp add --transport http linear-server https://mcp.linear.app/mcp, then /mcp to sign in with OAuth 2.1. That endpoint can read and write. For read-only access, connect to https://mcp.linear.app/mcp/readonly or request only the read OAuth scope. A Linear API key or OAuth token can go in an Authorization: Bearer header instead; a key with only the Read permission keeps it read-only. Each workspace needs its own sign-in. Clients without remote MCP support can use npx -y mcp-remote https://mcp.linear.app/mcp. The /sse endpoint is deprecated.

**Source checked:** 2026-11-07. [Official source](https://linear.app/docs/mcp). [Gearlist page](https://gearlist.build/tools/linear-mcp/).

### [Figma MCP server](https://developers.figma.com/docs/figma-mcp-server/)

Figma's MCP server, which gives coding agents the design context in Figma files, such as variables, components and layout, for generating code, and lets agents write native content back to the canvas.

**For:** Designers and developers who turn Figma designs into code with Claude Code, Codex, Cursor, VS Code or another MCP client.

**Access and use:** Remote server at https://mcp.figma.com/mcp, for example claude mcp add --transport http figma https://mcp.figma.com/mcp, or Figma's plugin with claude plugin install figma@claude-plugins-official. You sign in with your Figma account and can reach only files you already have access to. Starter plans and View or Collab seats get up to 20 read tool calls a month; Full and Dev seats on paid plans get 200 to 600 a day. Writing outside your drafts needs a Full seat. Writing to the canvas is free during the beta and will become a usage-based paid feature. generate_image and send_prompt use Figma AI credits. A desktop server that runs through the Figma desktop app needs a Dev or Full seat. Use falls under the Figma Developer Terms.

**Source checked:** 2026-11-07. [Official source](https://developers.figma.com/docs/figma-mcp-server/rate-limits-access/). [Gearlist page](https://gearlist.build/tools/figma-mcp-server/).

### [Slack MCP server](https://docs.slack.dev/ai/slack-mcp-server/)

Slack's hosted MCP server, with tools to search a workspace, read channels and threads, send and schedule messages, and manage canvases, lists and files.

**For:** Slack workspaces that want Claude, Cursor or Perplexity to use their Slack history, and developers building an MCP client on a Slack app.

**Access and use:** Ready to use in Claude.ai, Claude Code, Perplexity and Cursor. A client you build must be backed by a registered Slack app, either internal or published in the Slack Marketplace, and connects to https://mcp.slack.com/mcp over Streamable HTTP with confidential OAuth (the app's client ID and secret, or PKCE for desktop clients). SSE and dynamic client registration are not supported. Workspace admins approve and manage MCP client apps. User token scopes follow the tools, for example search:read.public to search, chat:write to send and channels:history to read. MCP activity appears in Slack's audit logs, the app's IP allowlist applies, and standard Slack API rate limits apply per tool.

**Source checked:** 2026-11-07. [Official source](https://docs.slack.dev/ai/slack-mcp-server/). [Gearlist page](https://gearlist.build/tools/slack-mcp-server/).

### [Zapier MCP](https://docs.zapier.com/mcp/home)

Zapier's hosted MCP server that lets an AI client run actions in the 9,000 or more apps Zapier connects to, such as sending a Slack message or creating a task, through your Zapier account.

**For:** Zapier users who want Claude, ChatGPT, Cursor, VS Code or another MCP client to act in their other apps without an integration for each one.

**Access and use:** Clients connect to https://mcp.zapier.com/api/v1/connect, and most sign in with OAuth. Plugins for Claude Code, Codex, Cursor and Gemini CLI come from github.com/zapier/zapier-mcp (MIT). Actions run through the same app connections as your Zaps, so the agent acts with those accounts. In agentic mode the AI adds the actions it needs during a conversation; managed mode limits it to a fixed set you pick. Each successful tool call uses two tasks from your Zapier plan. Sharing a server needs a Team or Enterprise plan. Clients must support Streamable HTTP; SSE is not supported.

**Source checked:** 2026-11-07. [Official source](https://docs.zapier.com/mcp/home). [Gearlist page](https://gearlist.build/tools/zapier-mcp/).

### [Gemini Docs MCP](https://aistudio.google.com/docs/coding-agents)

Google's public MCP server that lets a coding agent search and read the full Gemini API documentation.

**For:** Developers whose coding agents write Gemini API code and need current model names, request schemas and limits.

**Access and use:** Remote URL https://gemini-api-docs-mcp.dev. Claude Code: claude mcp add --transport http geminiDocs https://gemini-api-docs-mcp.dev, or npx add-mcp https://gemini-api-docs-mcp.dev for the agents it detects. Two tools, gemini_search_docs and gemini_get_doc, both over Google's public Gemini API documentation. Google's setup page uses no key or sign-in for it and names no price. The same documentation is also listed for agents at https://aistudio.google.com/llms.txt.

**Source checked:** 2026-11-07. [Official source](https://aistudio.google.com/docs/coding-agents). [Gearlist page](https://gearlist.build/tools/gemini-docs-mcp/).

### [Google Developer Knowledge MCP](https://developers.google.com/knowledge/mcp)

Google's MCP server for searching and reading its official developer documentation, including Firebase, Google Cloud, Android and Google Maps Platform.

**For:** Developers whose coding agents build on Google products and need current documentation.

**Access and use:** Remote URL https://developerknowledge.googleapis.com/mcp. Enable the Developer Knowledge API in a Google Cloud project, then send an API key in the X-Goog-Api-Key header, or use OAuth or Application Default Credentials. Tools: search_documents, get_documents and answer_query, which writes an answer from the documentation. Default quotas per project are 100 searches and 100 document reads a minute, and 50 generated answers a day. The setup and quota pages name no price.

**Source checked:** 2026-11-07. [Official source](https://developers.google.com/knowledge/mcp). [Gearlist page](https://gearlist.build/tools/google-developer-knowledge-mcp/).

### [Maps Experience agent tools](https://developers.google.com/maps/ai/maps-experience-agent-tools)

Google Maps Platform's MCP server, formerly Maps Grounding Lite, that lets an agent search places, look up weather, compute routes and turn place names or Maps links into place IDs.

**For:** Teams building agents that answer questions about places, routes, travel times or local weather.

**Access and use:** Remote URL https://mapstools.googleapis.com/mcp with a Google Maps Platform API key in the X-Goog-Api-Key header, or OAuth. Five tools: search_places, lookup_weather, compute_routes, resolve_names and resolve_maps_urls. Essentials requests are free for the first 10,000 a month, then US$7.00 per 1,000. Pro options cost US$14.00 per 1,000 after 5,000 free a month, and for now work only on allowlisted projects. Search, weather and routes each allow 300 queries a minute per project. Answers must show the Google Maps sources each response returns, and the model you use must not cache, store or train on Google Maps content. The Maps Demo Key covers it for prototyping.

**Source checked:** 2026-11-07. [Official source](https://developers.google.com/maps/ai/maps-experience-agent-tools). [Gearlist page](https://gearlist.build/tools/maps-experience-agent-tools/).

### [Microsoft MCP Server for Enterprise](https://learn.microsoft.com/en-us/graph/mcp-server/overview)

Microsoft's MCP server, in preview, that turns plain questions about a Microsoft Entra tenant's users, groups, apps and devices into read-only Microsoft Graph calls.

**For:** IT admins and helpdesk staff who want an agent to answer identity and directory questions about their own tenant.

**Access and use:** Remote URL https://mcp.svc.cloud.microsoft/enterprise, in preview under the Microsoft APIs Terms of Use. An Application Administrator or Cloud Application Administrator registers it once per tenant with the Microsoft.Entra.Beta PowerShell module and grants MCP scopes to each client; Claude and other non-Microsoft clients need their own app registration. Its Graph tool, microsoft_graph_get, is read-only and honours the signed-in user's roles and the scopes granted. The server has no extra cost or licence, but you need licences for the data you read. Limit: 100 calls a minute per user, plus Graph throttling. Global cloud only. Turn on Microsoft Graph activity logs to record every call.

**Source checked:** 2026-11-07. [Official source](https://learn.microsoft.com/en-us/graph/mcp-server/overview). [Gearlist page](https://gearlist.build/tools/microsoft-mcp-server-for-enterprise/).

### [OpenRouter MCP](https://openrouter.ai/docs/guides/overview/mcp-server)

OpenRouter's hosted MCP server that lets a coding agent look up live models, prices, benchmarks, providers and your credit balance, and send test messages to any model.

**For:** Developers choosing or testing models on OpenRouter from inside their coding agent.

**Access and use:** Remote URL https://mcp.openrouter.ai/mcp. Claude Code: claude mcp add --transport http openrouter https://mcp.openrouter.ai/mcp, then claude mcp login openrouter. Signing in with OAuth creates a separate key for this connection that expires within 7 days and starts with a US$10 spend cap, which you can change on the approval screen. Most of its 17 tools are read-only lookups; send-message and generate-image spend credits, and send-feedback sends a report on one of your generations to OpenRouter. OpenRouter suggests it for building and testing, and the API for running models in your app.

**Source checked:** 2026-11-07. [Official source](https://openrouter.ai/docs/guides/overview/mcp-server). [Gearlist page](https://gearlist.build/tools/openrouter-mcp/).

## Security and governance

### [CISO AI](https://cisoai.au/)

Security briefings, analysis and governance resources.

**For:** Teams following security developments and governance topics.

**Access and use:** Read the linked primary sources and check dates before using advice in an operational decision.

**Source checked:** 2026-10-25. [Official source](https://cisoai.au/). [Gearlist page](https://gearlist.build/tools/ciso-ai/).

### [node9](https://node9.ai/)

Access control for AI agents. It decides what Claude Code, Codex, Gemini, Cursor and MCP servers may do, and can block or review risky actions.

**For:** People running coding agents against Slack, GitHub, email, files or databases.

**Access and use:** Install with brew tap node9-ai/node9 && brew install node9, or npm install -g node9-ai. Needs Node.js 22 or later. Local protection needs no account. Optional dashboard login. Apache-2.0.

**Source checked:** 2026-10-27. [Official source](https://github.com/node9-ai/node9-proxy). [Gearlist page](https://gearlist.build/tools/node9/).

### [ClawSecCheck](https://github.com/gl0di/clawseccheck)

A local, read-only security audit for an OpenClaw agent. It looks for config, prompt-injection and supply-chain risks and can vet a skill before install.

**For:** People running OpenClaw who want a local A to F grade without sending config off the machine.

**Access and use:** Python 3.10 or later. Install with pipx from the GitHub repo. The scanner reports and does not change OpenClaw config. Official docs say the scanner makes no network calls. MIT.

**Source checked:** 2026-10-27. [Official source](https://github.com/gl0di/clawseccheck). [Gearlist page](https://gearlist.build/tools/clawseccheck/).

### [GuardStein](https://guardstein.com/)

A document and deal room service that describes browser encryption and controlled sharing.

**For:** Teams evaluating document sharing for deals and reviews.

**Access and use:** Encryption claims are the provider's. Review its security model and recovery process before uploading sensitive documents.

**Source checked:** 2026-10-25. [Official source](https://guardstein.com/). [Gearlist page](https://gearlist.build/tools/guardstein/).

### [Codex Security](https://learn.chatgpt.com/docs/security/cli)

OpenAI's tool that looks for vulnerabilities in a codebase, investigates them and proposes fixes, through a Codex plugin, a CLI, a TypeScript SDK or a GitHub Action, with threat-model and report workflows.

**For:** Developers and security teams checking code they own or are authorised to test.

**Access and use:** It reads your repository and uses an authenticated model service, so it needs a login or API key, and the provider bills for the usage. Amazon Bedrock and other documented providers are supported alternatives. Cloud publishing and issue integrations add destinations outside your machine. The example GitHub Action uses an estimated US$5 limit per scan and warns that requests already in flight can go past it, so treat that limit as an estimate, not a hard cap. Some requests need additional cyber access. Use it only on code you own or are authorised to test. Its findings and patches are candidates for you to review, not a certified audit or proof that the code is safe. Apache-2.0.

**Source checked:** 2026-11-14. [Official source](https://github.com/openai/codex-security). [Gearlist page](https://gearlist.build/tools/codex-security/).

### [promptfoo](https://www.promptfoo.dev)

A tool for evaluating and red-teaming LLM applications, from the command line or as a library, with test cases written as configuration and CI integration.

**For:** Developers and security teams testing LLM applications they own or are authorised to assess.

**Access and use:** Promptfoo is now part of OpenAI, its README says. Usage telemetry is on by default and, when you are logged in, can include account identifiers; the documentation says it excludes prompts, outputs and keys. Set PROMPTFOO_DISABLE_TELEMETRY=1 to turn it off. That does not stop requests to model providers or to optional hosted features, which are separate data paths with their own costs, and the CLI also checks for updates. Test only applications you own or are authorised to assess, and do not read passing tests as proof that an application is secure. MIT.

**Source checked:** 2026-11-14. [Official source](https://github.com/promptfoo/promptfoo). [Gearlist page](https://gearlist.build/tools/promptfoo/).

### [Cisco AI Defense Skill Scanner](https://cisco-ai-defense.github.io/docs/skill-scanner)

A best-effort security check for agent skills, using deterministic rules, code and dataflow analysis and optional model or cloud analysers, with CI, SARIF and pre-commit integration.

**For:** Developers and security teams who want to check agent skills in CI or before a commit.

**Access and use:** Core scans need no model account. The optional analysers send data elsewhere: the LLM analyser sends a skill's instructions and scripts, or bounded excerpts, to the model you configure, and setups with a local provider differ; the AI Defense analyser sends extracted instructions, metadata, Markdown and code to Cisco's API; and VirusTotal checks binaries by reputation, with optional upload flags that can send unknown binaries to it. These need API access and can carry provider costs. An optional interactive wizard recommends an LLM, which a core-only command line scan does not need. No findings does not mean no risk, and it is not a certification or complete detection of malicious skills. The LICENSE file is Apache-2.0; GitHub shows NOASSERTION.

**Source checked:** 2026-11-14. [Official source](https://github.com/cisco-ai-defense/skill-scanner). [Gearlist page](https://gearlist.build/tools/cisco-skill-scanner/).

### [Skylos](https://skylos.dev)

A code and pull request checker for dead code, security issues, secrets, dependency risks and changes written by coding agents, with completion checks, agent hooks and CI gates.

**For:** Developers and teams who review changes from coding agents and want checks on the branch and in CI.

**Access and use:** Language coverage varies. Local static analysis is different from its model-assisted checks: AI options send relevant source code to the provider you choose, and a configured Jev review can send bounded first-party source to that service. Cloud upload can include findings, file paths, code snippets and commit and author metadata. The CI workflow it generates uses a different upload default when the machine is logged in, so read the workflow before you commit it; cloud and app setup are separate steps. Setup commands can change agent hooks and CI files. SKYLOS_NO_TELEMETRY=1 turns off a PyPI update lookup. Scan coverage and the benchmark results it reports are not an independent security audit. Apache-2.0.

**Source checked:** 2026-11-14. [Official source](https://github.com/duriantaco/skylos). [Gearlist page](https://gearlist.build/tools/skylos/).

### [Quicksand](https://microsoft.github.io/quicksand/)

An async Python API that boots QEMU Linux VMs so agents can run commands, mounts and a desktop without root or Docker.

**For:** People who want coding agents to work inside a local virtual machine.

**Access and use:** pip install 'quick-sandbox[qemu,alpine]', or pip install quick-sandbox then quicksand install qemu alpine. Desktop images: quicksand install ubuntu-desktop or alpine-desktop. Sandboxes are network-isolated by default; NetworkMode.FULL gives internet. Host directories can be mounted into the guest. Bidirectional port forwards map host and guest TCP ports. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/microsoft/quicksand). [Gearlist page](https://gearlist.build/tools/quicksand/).

### [Snyk Agent Scan](https://github.com/snyk/agent-scan)

A command line scanner that finds the agents, MCP servers and skills installed on a machine and checks them for prompt injection, tool poisoning, malware hidden in text and other risks.

**For:** Developers and security teams who want to check the MCP servers and skills used by Claude Code, Cursor, Gemini CLI, Windsurf or VS Code before trusting them.

**Access and use:** uvx snyk-agent-scan@latest scans the whole machine; pass a path such as ~/.claude/skills or an mcp.json file to scan one target. Standalone binaries with an SBOM and signed checksums are on GitHub Releases. Needs a Snyk account and a SNYK_TOKEN. To read tool descriptions it starts the stdio MCP servers in your configs and connects to remote ones, so the README advises scanning untrusted configs inside a sandbox; interactive runs ask before contacting each server. It sends component details, tool descriptions and skill content to Snyk's analysis API, with secrets redacted, under Snyk's Agent Scan terms. The README says CLI output is experimental and may change. The repository moved from invariantlabs-ai/mcp-scan. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/snyk/agent-scan). [Gearlist page](https://gearlist.build/tools/snyk-agent-scan/).

### [ToolHive](https://github.com/stacklok/toolhive)

Stacklok's platform that runs each MCP server in an isolated container and adds encrypted secrets, access policy, a server registry and audit logging.

**For:** Developers who want to run MCP servers locally with fewer permissions, and platform teams who run approved MCP servers for an organisation on Kubernetes.

**Access and use:** brew tap stacklok/tap then brew install thv, winget install stacklok.thv, a binary from GitHub Releases, or the ToolHive desktop app. Needs Docker, Podman, Colima or Rancher Desktop. Each server gets a container with a minimal permission file and no local credentials. Secrets are stored encrypted, with the encryption password kept in your OS keyring. Per-request access policy needs an identity provider to be configured. The CLI checks for updates and sends anonymous usage metrics (tool call counts) until you run thv config usage-metrics disable. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/stacklok/toolhive). [Gearlist page](https://gearlist.build/tools/toolhive/).

### [NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails)

NVIDIA's Python library for adding programmable guardrails to LLM apps, with rails that check user input, model output, retrieved chunks and tool calls, including jailbreak and injection detection.

**For:** Developers building chat assistants, RAG apps or agents in Python who want configurable checks between their code and the model.

**Access and use:** pip install nemoguardrails. Needs Python 3.11 to 3.13. Rails are set in a config.yml file and Colang flows, and call the LLM provider set there, such as OpenAI, with your own key. nemoguardrails server runs it as an HTTP API. The library sends anonymous telemetry to NVIDIA (versions, OS, provider names and rail counts; the README says no prompts, completions or keys) until you set NEMO_GUARDRAILS_NO_USAGE_STATS=1 before it starts. The README says NVIDIA Build endpoints are for evaluation only. The LICENSE file is Apache-2.0; GitHub shows NOASSERTION.

**Source checked:** 2026-11-07. [Official source](https://github.com/NVIDIA-NeMo/Guardrails). [Gearlist page](https://gearlist.build/tools/nemo-guardrails/).

### [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)

The OWASP GenAI Security Project's list of the ten most critical security risks for AI agents, from agent goal hijack and tool misuse to memory poisoning and rogue agents, with attack scenarios and mitigations for each.

**For:** Teams that build, deploy or review AI agents and want a shared list of risks to check designs and controls against.

**Access and use:** A free PDF from the OWASP GenAI Security Project page, downloadable without signing in. The 2026 edition was published on 9 December 2025. Risks are numbered ASI01 to ASI10 and mapped to OWASP's Agentic AI Threats and Mitigations guide. CC BY-SA 4.0.

**Source checked:** 2026-11-07. [Official source](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/). [Gearlist page](https://gearlist.build/tools/owasp-agentic-top-10/).

### [Cloudflare security-audit skill](https://github.com/cloudflare/security-audit-skill)

Cloudflare's coding-agent skill for a six-phase security audit of a codebase, in which separate agents find each issue, try to disprove it and check the final record.

**For:** Developers and security teams who want a coding agent to review code they own for vulnerabilities.

**Access and use:** npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit. Needs a model with tool use and parallel sub-agents, and Node.js for its two validators. It reads the code and writes its reports, by default under ~/security-audit-skill/. Before it runs any of the target's own code it asks for an OS-enforced sandbox with outside networking turned off; without one, those leads stay marked needs_validation. Cloudflare says one run found about half of what repeated runs found. Audit only code you are allowed to test. MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/cloudflare/security-audit-skill). [Gearlist page](https://gearlist.build/tools/cloudflare-security-audit-skill/).

### [SkillSpector](https://github.com/NVIDIA/SkillSpector)

A scanner from NVIDIA that checks AI agent skills and MCP servers for prompt injection, data exfiltration, supply-chain and other risks before you install them, and gives each a risk score from 0 to 100.

**For:** Developers and security teams who install third-party skills into Claude Code, Codex, Gemini CLI or similar agents and want to know whether a skill is safe first.

**Access and use:** Install with uv tool install git+https://github.com/NVIDIA/skillspector.git, or with uv tool install 'skillspector[mcp] @ git+https://github.com/NVIDIA/skillspector.git' to also run it as an MCP server (claude mcp add skillspector -- skillspector mcp). A Dockerfile is included if you would rather not install Python. Needs Python 3.12 to 3.15. LLM analysis is on by default and sends the scanned files' contents to the configured provider, which defaults to NVIDIA's build.nvidia.com with an NVIDIA_INFERENCE_KEY; OpenAI, Anthropic, Bedrock, Gemini, Azure OpenAI, local Ollama and the Claude, Gemini and OpenCode CLIs also work, and --no-llm keeps file contents local. The dependency check sends package names and versions to OSV.dev even with --no-llm. The MCP HTTP transport has no authentication and only binds to loopback addresses, and the README notes a known initialise hang on the stdio transport (issue #199). It never runs the scanned skill and does not sandbox a skill you install anyway. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/NVIDIA/SkillSpector). [Gearlist page](https://gearlist.build/tools/skillspector/).

### [BLA (Blind LLM Agents)](https://github.com/qybaihe/bla)

A Node.js CLI, MCP server and agent skill that alters the software you ship so AI reverse-engineering agents hit resource limits and follow decoys, while runtime behaviour is meant to stay the same.

**For:** Developers who ship binaries, Electron apps, JavaScript bundles, Python or WebAssembly and want automated AI reverse engineering of their own releases to cost more.

**Access and use:** Run npx bla-agents setup to register the bla MCP server and blind-llm-agents skill with your coding agents, then npx bla-agents harden . to audit, protect and verify build outputs; it needs Node.js ^22.23.4 or >=24.0.0. Setup auto-discovers installed coding agents and writes to their global config files, such as ~/.claude.json and ~/.cursor/mcp.json; use --client to limit it and npx bla-agents uninstall to remove it. Protection adds decoy metadata, honey tables and canary credentials to your artifacts and can make them much larger (the README lists an Electron ASAR going from 607 B to 16.9 MiB), and it adds inspector and Frida detection that returns synthetic telemetry, so run bla verify against the original in staging before shipping. Risky LLM-facing bait, including fake COPPA or medical notices, is off unless you pass --llm-directives. The MCP tools refuse to overwrite an existing output file unless confirm_overwrite: true is set. The README's token and cost multipliers are the project's own internal estimates. Only run it on software you own or are authorised to modify. The npm package is published from this repo with npm provenance. MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/qybaihe/bla). [Gearlist page](https://gearlist.build/tools/bla-blind-llm-agents/).

## Platforms

### [Raft](https://github.com/botiverse/raft-source)

A shared workspace where people and persistent AI agents collaborate in messages and tasks.

**For:** Teams working with agents across projects and machines.

**Access and use:** Source available under FSL, not an unrestricted open source licence. Agents need explicit access to their tools and data.

**Source checked:** 2026-10-25. [Official source](https://github.com/botiverse/raft-source). [Gearlist page](https://gearlist.build/tools/raft/).

### [Official MCP Registry](https://registry.modelcontextprotocol.io)

The official hosted registry of publicly available Model Context Protocol servers, with a REST API and server.json metadata.

**For:** MCP clients, aggregators and people looking up a server by name.

**Access and use:** The registry is in preview. Breaking changes or data resets may occur before general availability. Listing a server is not a security audit. Installing a listed server still needs its own credentials and terms.

**Source checked:** 2026-10-26. [Official source](https://modelcontextprotocol.io/registry/about). [Gearlist page](https://gearlist.build/tools/mcp-registry/).

### [OmniRoute](https://github.com/cheaper-inference/OmniRoute)

A local AI gateway that routes coding tools to many provider accounts through one OpenAI-compatible endpoint.

**For:** People who already have provider accounts and want one local endpoint with fallback.

**Access and use:** Install with npm install -g omniroute. It runs locally (default http://localhost:20128). Bring your own provider credentials. OmniRoute does not grant tokens. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/cheaper-inference/OmniRoute). [Gearlist page](https://gearlist.build/tools/omniroute/).

### [Overmind](https://www.overmindlab.ai/)

A hosted or self-hosted platform that turns production traces into evals, prompt experiments and fine-tuned models for an agent you already run.

**For:** Teams who want to train and score a specialised agent from their own traces.

**Access and use:** SDK and CLI: pip install overmind, then overmind init and overmind sync. Hosted console is console.overmindlab.ai with a project API key. MCP is https://api.overmindlab.ai/api/mcp/ with X-Api-Key. Self-host is docker compose; the API needs OpenRouter, Modal, AWS and Hugging Face keys before it boots. SDK and CLI are MIT. The platform is AGPL-3.0. SDK and CLI send anonymous usage to PostHog; opt out with OVERMIND_ANALYTICS_ENABLED=false or DO_NOT_TRACK=1.

**Source checked:** 2026-10-28. [Official source](https://github.com/overmind-core/overmind). [Gearlist page](https://gearlist.build/tools/overmind/).

### [OpenBot](https://www.copilotkit.ai/openbot)

A self-hosted AG-UI coworker app. Each bot gets its own computer, browser logins and files, and every action is decided and recorded before it runs.

**For:** Teams that want a clone-and-own agent workspace on their own infrastructure, with their own model keys.

**Access and use:** Clone https://github.com/CopilotKit/OpenBot. Needs Docker, Bun 1.3 or later, a CopilotKit Intelligence project, and a model key. Default OPENBOT_SINGLE_USER admits every request as one administrator until you turn sign-in on. Credentials are encrypted at rest. Published image ghcr.io/copilotkit/openbot. MIT. Marked beta.

**Source checked:** 2026-10-28. [Official source](https://github.com/CopilotKit/OpenBot). [Gearlist page](https://gearlist.build/tools/openbot/).

### [Orca](https://onorca.dev)

A desktop app that runs coding agents side by side, each in its own git worktree, with a phone companion to watch and steer them.

**For:** People who want several CLI coding agents working in parallel on one machine, with a phone app to follow them.

**Access and use:** Download from https://onorca.dev/download or GitHub Releases. macOS Homebrew is brew install --cask stablyai/orca/orca; a bare brew install --cask orca is a different Plotly app. Mobile companion is on the App Store and as an Android APK. The README points to privacy and telemetry docs for usage data and how to opt out. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/stablyai/orca). [Gearlist page](https://gearlist.build/tools/orca/).

### [serviette](https://github.com/pathwaycom/serviette)

A RAG server that watches a folder of documents, keeps a vector index live, and serves a chat UI plus REST API with cited answers.

**For:** People who want answers from their own files that stay current as those files change, on a machine they control.

**Access and use:** pip 23.1 or later. pip install serviette. Needs a free Pathway licence in PATHWAY_LICENSE_KEY from pathway.com/framework/get-license (GitHub or LinkedIn sign-in). Default server binds localhost:8989 with no built-in auth. Local embeddings extra is serviette[local]. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/pathwaycom/serviette). [Gearlist page](https://gearlist.build/tools/serviette/).

### [DeerFlow](https://deerflow.tech)

A self-hosted agent harness that runs sub-agents, skills, memory and sandboxes for long research and coding jobs.

**For:** People who want a local super-agent stack they can configure with their own model keys.

**Access and use:** Clone https://github.com/bytedance/deer-flow then make setup. Docker is make docker-init and make docker-start. Python 3.12 or later and Node 22 or later for a local run. The Docker stack and local start bind to 127.0.0.1. Treat Gateway admin as code execution on the host. Set BIND_HOST only after you have put auth in place. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/bytedance/deer-flow). [Gearlist page](https://gearlist.build/tools/deerflow/).

### [OpenClaw](https://openclaw.ai)

A self-hosted assistant gateway that meets you in the chat apps you already use, with native apps for macOS, iOS, Android, Windows and Linux.

**For:** People who want one local assistant that can talk on WhatsApp, Slack, Telegram and other channels, using their own model keys.

**Access and use:** Installer is curl -fsSL https://openclaw.ai/install.sh | bash. Read the script before running it. Also npm install -g openclaw@latest --allow-scripts=openclaw. Needs Node 24.22.1 or later, or Node 26.12.1 or later. After npm, run openclaw onboard --install-daemon. Daily version check is on by default; anonymous feature statistics are opt-in; update.checkOnStart: false turns both off. Tools run on the host unless you configure sandboxing. Treat inbound messages as untrusted. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/openclaw/openclaw). [Gearlist page](https://gearlist.build/tools/openclaw/).

### [DeepSeek Harness](https://deepseek-harness.github.io/deepseek-harness/)

An open-source agent harness from DeepSeek where every capability is a plugin, with a local web UI.

**For:** People who want to run DeepSeek's plugin-based agent stack on their own machine.

**Access and use:** npx @deepseek-ai/dsh web. Default web UI is http://127.0.0.1:3080. Marked developer preview with expected breaking changes. The SAFETY notice says it can execute model-generated code, load plugins, and has not been security audited. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/deepseek-ai/deepseek-harness). [Gearlist page](https://gearlist.build/tools/deepseek-harness/).

### [Huginn](https://github.com/huginn/huginn)

A self-hosted agent system that watches the web, mail and feeds, then takes actions you define.

**For:** People who want IFTTT-style automations on a server they control, with their data staying there.

**Access and use:** Quick try: docker run -it -p 3000:3000 ghcr.io/huginn/huginn then open http://localhost:3000 and log in as admin with the password printed once in the container log. Production needs MySQL or PostgreSQL and a web process plus a worker. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/huginn/huginn). [Gearlist page](https://gearlist.build/tools/huginn/).

### [Agent TARS](https://github.com/bytedance/UI-TARS-desktop)

A multimodal agent stack with a CLI and web UI, plus a desktop GUI agent that can operate a local or remote computer and browser.

**For:** People who want a vision-capable agent that can drive a browser or desktop, using their own model keys.

**Access and use:** Needs Node 22 or later. npx @agent-tars/cli@latest, or npm install @agent-tars/cli@latest -g, then agent-tars --provider anthropic --model MODEL --apiKey KEY. The same repository ships UI-TARS Desktop. Treat computer and browser operators as full desktop control. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/bytedance/UI-TARS-desktop). [Gearlist page](https://gearlist.build/tools/agent-tars/).

### [CopilotKit](https://docs.copilotkit.ai)

An SDK that puts an agent into a web, mobile or chat UI, with shared state, generative UI and human-in-the-loop pauses.

**For:** Teams adding an agent to an app they already ship, or connecting one agent to Slack, Teams and similar channels.

**Access and use:** From the app root: npx --yes copilotkit@latest onboard start. New project: npx copilotkit@latest create. Optional skills: npx copilotkit@latest skills install. CopilotKit Intelligence is a separate hosted or self-hosted product. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/CopilotKit/CopilotKit). [Gearlist page](https://gearlist.build/tools/copilotkit/).

### [Sim](https://www.sim.ai)

A workspace to build, deploy and monitor agents and workflows, with a visual builder, tables, files and a knowledge base.

**For:** Teams that want a self-hosted or hosted agent workspace with MCP access from Claude Code and Codex.

**Access and use:** Cloud at sim.ai. Self-host: npx sim-setup. Read the script before running it. Then open http://localhost:3000. Needs Node 20 or later and Docker. Chat on a self-hosted install uses a Chat API key from sim.ai. Cloud MCP is https://mcp.sim.ai/mcp. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/simstudioai/sim). [Gearlist page](https://gearlist.build/tools/sim/).

### [ArchiveBox](https://archivebox.io)

A self-hosted archiver that saves pages you give it as HTML, PDF, PNG, WARC and other ordinary files.

**For:** People who want a local copy of bookmarks, research pages or public web content they choose to keep.

**Access and use:** Installer is curl -fsSL https://get.archivebox.io | bash. Read the script before running it. Also docker compose from docker-compose.archivebox.io, or uv tool install archivebox. Docker -p 5797:5797 and archivebox server 0.0.0.0:5797 bind every interface. Pages are submitted to archive.org by default. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/ArchiveBox/ArchiveBox). [Gearlist page](https://gearlist.build/tools/archivebox/).

### [oMLX](https://omlx.ai)

A local LLM inference server for Apple Silicon, with a menu bar app, OpenAI-compatible API and SSD-backed KV cache.

**For:** People who want coding agents and chat apps to call models that run on a Mac they already have.

**Access and use:** Needs macOS 15 or later and Apple Silicon. Download the .dmg from GitHub Releases, or brew tap jundot/omlx then brew install jundot/omlx/omlx. Default server is http://localhost:8000/v1. A non-loopback bind (--host 0.0.0.0) needs a main API key. Optional MCP via pip install mcp then omlx restart. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/jundot/omlx). [Gearlist page](https://gearlist.build/tools/omlx/).

### [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)

Python and TypeScript libraries from Anthropic that expose Claude Code's agent loop, tools and context management, and run the Claude Code binary underneath.

**For:** Developers building their own agents on Claude Code's agent loop in Python or TypeScript.

**Access and use:** The quickstart authenticates with an API key or a supported cloud provider, and that account is billed for usage. Agents can read and write files and run commands, as you configure them. SDK and product use is governed by Anthropic's Commercial Terms, apart from separately licensed components. Unless Anthropic approves, third-party developers may not offer claude.ai login or its rate limits in their products, including agents built on this SDK, so it is not a way to run a customer product on a personal Claude subscription. Licences differ by language: the Python source is MIT, and the TypeScript package is under Anthropic's proprietary Commercial Terms. The MIT Python wrapper does not make the Claude Code runtime or Anthropic's service open source.

**Source checked:** 2026-11-14. [Official source](https://code.claude.com/docs/en/agent-sdk/overview). [Gearlist page](https://gearlist.build/tools/claude-agent-sdk/).

### [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)

A framework for tool-using agents with handoffs, guardrails, sessions and tracing, in Python and JavaScript or TypeScript, with integrations for several model providers.

**For:** Developers building agents in Python or JavaScript who want handoffs, guardrails and tracing in their own code.

**Access and use:** Model provider authentication and usage charges apply. Tracing is on by default and can include model and tool inputs and outputs, which are sent to OpenAI; choosing another provider's model does not keep traces with that provider. Set OPENAI_AGENTS_DISABLE_TRACING=1 to turn tracing off everywhere, or use the documented per-run and data controls. Tracing is unavailable under OpenAI's documented Zero Data Retention policy. Connected tools decide what else an agent can reach. Guardrails are controls you program, not a full safety guarantee. The JavaScript and TypeScript SDK is at github.com/openai/openai-agents-js. Both are MIT.

**Source checked:** 2026-11-14. [Official source](https://developers.openai.com/api/docs/guides/agents/integrations-observability). [Gearlist page](https://gearlist.build/tools/openai-agents-sdk/).

### [Buzz](https://github.com/block/buzz)

A self-hosted workspace where humans and agents share signed events on a relay you run.

**For:** Teams who want agents in the same rooms as people, with their own keys and an audit trail.

**Access and use:** Download the desktop app from GitHub Releases, or git clone then just setup && just dev. Needs Docker. Default relay is ws://localhost:3000. Agents use buzz-cli with BUZZ_PRIVATE_KEY; they can open repos, send patches and run workflows on that relay. The Windows installer is unsigned. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/block/buzz). [Gearlist page](https://gearlist.build/tools/buzz/).

### [OpenSandbox](https://open-sandbox.ai)

A sandbox runtime that gives agents isolated Docker or Kubernetes environments for commands, files, browsers and desktops.

**For:** People who want coding agents to run sandboxes on their own infrastructure.

**Access and use:** uvx opensandbox-server init-config ~/.sandbox.toml --example docker then uvx opensandbox-server. Needs Docker and Python 3.10 or later. SDK: pip install opensandbox. CLI: pip install opensandbox-cli. MCP: pip install opensandbox-mcp then opensandbox-mcp --domain localhost:8080 --protocol http. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/opensandbox-group/OpenSandbox). [Gearlist page](https://gearlist.build/tools/opensandbox/).

### [Experiential](https://platform.experientiallabs.ai)

An OpenAI-compatible gateway that routes hosted, BYOK and local models, with spend limits and traffic-based routing.

**For:** Teams who want one API in front of several model providers, with a budget per identity.

**Access and use:** pip install experiential then exp. Local gateway is http://127.0.0.1:8000/v1. Hosted API is api.experientiallabs.ai. Anonymous PostHog product telemetry is on by default; exp config telemetry disable turns it off. exp capture (experimental, macOS) installs an extension and certificate to read your Codex and Claude Code desktop traffic, and sends those traces to your Experiential account. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/experientiallabs/experiential). [Gearlist page](https://gearlist.build/tools/experiential/).

### [QM](https://github.com/yc-software/qm)

A multiplayer agent harness for Slack and the web, with a personal sandbox per person and shared rooms.

**For:** Startups who want each person to have their own agent workspace, plus shared rooms on Slack and the web.

**Access and use:** npm exec --yes --package=@yc-software/qm@latest -- qm init . --org <slug> --target <fly-or-aws>. Needs Node 24.15 or later. The agent acts with that person's credentials. Default security posture is Auto, which blocks private-network access. Strict pauses every harness tool call. Dangerous drops those gates. Sessions need DATABASE_URL and SESSION_STORE=postgres to survive restart. A third-party hosted version runs at agent37.com/qm. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/yc-software/qm). [Gearlist page](https://gearlist.build/tools/qm/).

### [Cloudflare OS](https://os.cloudflare.app)

An early-access workspace where agents build sandboxed apps (Gadgets) behind Gatekeepers that log and queue side-effect approvals.

**For:** Companies who want an internal agent workspace with sandboxed apps and a security layer they can copy.

**Access and use:** pnpm run-local then visit http://localhost:8787. Needs pnpm. Early-access v2. Deploy to a Cloudflare account at os.cloudflare.app/deploy. Gadgets are sandboxed. Gatekeepers log actions and can queue side-effect approvals. Agents get only the resources you introduce. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/cloudflare/cloudflare-os). [Gearlist page](https://gearlist.build/tools/cloudflare-os/).

### [moltworker](https://github.com/cloudflare/moltworker)

An experimental Cloudflare Worker that runs OpenClaw inside a Cloudflare Sandbox container.

**For:** People who want OpenClaw hosted on Cloudflare Workers, with pairing and Access in front.

**Access and use:** Experimental proof of concept. Needs a Workers Paid plan for Sandbox containers. npm install, then npx wrangler secret put ANTHROPIC_API_KEY (or the AI Gateway secrets) and MOLTBOT_GATEWAY_TOKEN, then npm run deploy. Open the Control UI with ?token=YOUR_GATEWAY_TOKEN. Cloudflare Access plus device pairing at /_admin/ are required before the Control UI works. Optional R2 keeps pairing and history across container restarts. SANDBOX_SLEEP_AFTER defaults to never; a timeout such as 10m sleeps the container to cut cost. DEV_MODE=true is local only and skips Access and pairing. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/cloudflare/moltworker). [Gearlist page](https://gearlist.build/tools/moltworker/).

### [agentOS](https://rivet.dev/agentos)

A WebAssembly sandbox that gives each agent files, processes, a shell and networking inside one compact runtime.

**For:** People who want agent code isolated from the host process, with explicit mounts and network rules.

**Access and use:** Library: npm install @rivet-dev/agentos-core, then AgentOs.create() in your backend. The sidecar is a separate Rust process. Guest code reaches host files, environment or the network only through mounts, host functions or network allow rules you add. Hosted: npm install @rivet-dev/agentos, set RIVET_NAMESPACE and RIVET_TOKEN from the Rivet dashboard, and keep the token on the backend. Browser clients need a JWT scoped to that VM. Preview URLs expire. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/rivet-dev/agentos). [Gearlist page](https://gearlist.build/tools/agentos/).

### [Solo Agent](https://soloagent.team)

A local-first workspace where humans and coding agents share channels, tasks, teams and memory.

**For:** People who run Claude Code, Codex, OpenCode, Hermes or OpenClaw and want them in one workspace.

**Access and use:** git clone then make dev. Needs Go 1.25+, Node.js 20+, Docker and at least one supported agent CLI on PATH. make dev starts PostgreSQL in Docker on port 5432, a Go API on 8080, a daemon on 8081 and the UI on 3000. Register at http://localhost:3000. Signup stays on until you set ALLOW_SIGNUP=false. LLM_PROVIDER defaults to local, so agents are your installed CLIs. Workspace data lives in PostgreSQL. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/solo-agent/solo). [Gearlist page](https://gearlist.build/tools/solo-agent/).

### [HybridClaw](https://hybridclaw.io)

A self-hosted assistant runtime with a local gateway, sandbox, web chat and TUI, plus HybridAI Cloud as a hosted path.

**For:** People who want a local assistant on Node 22 with their own model keys, or the HybridAI Cloud workspace.

**Access and use:** npm install -g @hybridaione/hybridclaw, or curl -fsSL https://raw.githubusercontent.com/HybridAIOne/hybridclaw/main/scripts/install.sh | bash; read the script before running it. Needs Node.js 22.23.4 or later, below 23. hybridclaw onboarding then hybridclaw gateway. Default bind is 127.0.0.1:9090; web chat is http://127.0.0.1:9090/chat. Config is ~/.hybridclaw/config.json. Provider keys live in the encrypted store under ~/.hybridclaw/credentials.json. Docker is the default sandbox. Hosted path is hybridclaw.io. Set ops.webApiToken before exposing the gateway beyond loopback. Treat inbound channel messages as untrusted. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/HybridAIOne/hybridclaw). [Gearlist page](https://gearlist.build/tools/hybridclaw/).

### [HarnessRouter](https://harnessrouter.ai)

A self-hosted gateway that runs Codex, Claude Code and other harnesses through one OpenAI Responses-compatible API.

**For:** People who want one local console and API in front of several coding-agent harnesses, using their own model keys.

**Access and use:** docker run -d --name harnessrouter -p 127.0.0.1:3000:3000 -v harnessrouter:/data harnessrouter/harnessrouter. Needs Docker and about 4 GB of disk. Console is http://127.0.0.1:3000. Default Console login is harnessrouter / harnessrouter; change it before exposing the instance. First launch installs harness CLIs into the volume. Provider keys go under Bring your own key. Product API keys are created in the Console and belong in a backend, not a browser. Gateway :8080 and Runner :8081 stay on loopback inside the container. Hosted path is harnessrouter.ai. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/HarnessRouter/harnessrouter). [Gearlist page](https://gearlist.build/tools/harnessrouter/).

### [GOD](https://xiaoluolyg.github.io/GOD/)

A local control room for language-agent societies: pause a run, ask a resident, inject the next step, and export a replay pack.

**For:** People who want to inspect and steer a town of LLM agents from one browser on their machine.

**Access and use:** git clone https://github.com/XiaoLuoLYG/GOD.git then ./scripts/god.sh start (Windows: .\scripts\god.cmd start). The first run installs dependencies and opens a browser wizard. Paste an OpenAI-compatible API key, base URL and model name. The control room prints a URL such as http://127.0.0.1:5174/pixel-replay/god_town/1. .env stores local model and port settings. The model endpoint is the external service. Curated browser replays on the public site need no install or API key. Apache-2.0. Bundled AgentSociety and JiuwenClaw checkouts keep their own licences.

**Source checked:** 2026-10-28. [Official source](https://github.com/XiaoLuoLYG/GOD). [Gearlist page](https://gearlist.build/tools/god/).

### [EdgeEver](https://edgeever.org)

An open-source notes and knowledge workspace with three-pane editing, multi-device sync, and a native remote MCP so agents can create and edit notes in the same account.

**For:** People who want a self-hosted or Cloudflare-hosted notebook that coding agents can read and write through MCP.

**Access and use:** Cloudflare: fork the repo, create D1 edgeever and R2 edgeever-resources, then a Worker from main. Set the runtime Secret EDGE_EVER_AUTH_PASSWORD; upstream recommends 32 characters or longer. Username defaults to admin via EDGE_EVER_AUTH_USERNAME. Notes and attachments then live in that Cloudflare account. Docker: curl -fsSL https://edgeever.org/install.sh | bash (read the script before running it). The installer writes ~/edgeever, pulls ghcr.io/tianma-if/edgeever, generates an administrator password, and serves http://localhost:8787. Daily auto-update is crontab 04:17 unless EDGE_EVER_AUTO_UPDATE=false. Profile -> API / MCP issues a token with full CRUD on notes, notebooks, tags, attachments, history, templates and AI instructions. BYOK sends note text to the model endpoint you configure. The public demo at https://demo.edgeever.org resets daily; keep private notes off it. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/tianma-if/edgeever). [Gearlist page](https://gearlist.build/tools/edgeever/).

### [MiroFish](https://github.com/666ghj/MiroFish)

A multi-agent simulation engine that builds a digital world from seed documents and runs thousands of persona agents so you can rehearse what-if outcomes.

**For:** People who want to simulate public opinion, policy or story trajectories with an LLM swarm on their own machine.

**Access and use:** Needs Node.js 18+, Python 3.11 or 3.12, and uv. Copy .env.example to .env. Set LLM_API_KEY, LLM_BASE_URL and LLM_MODEL_NAME for any OpenAI-compatible endpoint, plus ZEP_API_KEY from https://app.getzep.com/. Your seed documents and agent memory are sent to Zep Cloud, and prompts go to the LLM endpoint you set. npm run setup:all then npm run dev. Frontend is http://localhost:3000; backend is http://localhost:5001. Docker: docker compose up -d with the same .env. Upstream says LLM use is high; try fewer than 40 rounds first. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/666ghj/MiroFish). [Gearlist page](https://gearlist.build/tools/mirofish/).

### [Plane](https://github.com/makeplane/plane)

An AGPL project-management app for work items, cycles, modules, views, pages and analytics, as a self-hosted or cloud Linear-style workspace.

**For:** Teams who want issues, sprints and docs on a stack they can host.

**Access and use:** Cloud sign-up is https://app.plane.so. Community self-host: mkdir plane-selfhost && cd plane-selfhost, curl -fsSL -o setup.sh https://github.com/makeplane/plane/releases/latest/download/setup.sh, chmod +x setup.sh, then ./setup.sh action 1. Edit plane.env WEB_URL and CORS_ALLOWED_ORIGINS (defaults http://localhost on ports 80 and 443), then ./setup.sh action 2 to start. Commercial installer: curl -fsSL https://prime.plane.so/install/ | sh - (read the script before running it); that edition starts on a free plan with 12 seats. Needs 2 CPU cores and 4 GB RAM. Instance admins configure the host in God mode. Self-hosted Plane sends telemetry to Plane by default: the admin's name and email, the instance ID, anonymised usage counts and performance data including stack traces. Turn it off in God mode under General Settings, Telemetry. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/makeplane/plane). [Gearlist page](https://gearlist.build/tools/plane/).

### [SearXNG](https://docs.searxng.org/)

A self-hosted metasearch engine that queries the search services you enable and returns aggregated results without a SearXNG user account.

**For:** People who want a private search front-end they can host, or who will use a public instance they trust.

**Access and use:** Self-host with Docker or Podman: mkdir -p ./searxng/core-config && cd ./searxng, curl -fsSL -O https://raw.githubusercontent.com/searxng/searxng/master/container/docker-compose.yml -O https://raw.githubusercontent.com/searxng/searxng/master/container/.env.example, cp .env.example .env, then docker compose up -d. Compose publishes 0.0.0.0:8080. Edit core-config/settings.yml. Manual run: docker run --name searxng -d -p 8888:8080 -v ./config/:/etc/searxng/ -v ./data/:/var/cache/searxng/ docker.io/searxng/searxng:latest then http://localhost:8888. Each query is sent to the engines you enable. A public instance operator sees the queries you type. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/searxng/searxng). [Gearlist page](https://gearlist.build/tools/searxng/).

### [Invidious](https://invidious.io/)

An AGPL YouTube front-end for videos, subscriptions and comments, as a self-hosted instance or a public one.

**For:** People who want a lighter YouTube player they can host, or who will pick a public instance they trust.

**Access and use:** Public instances are listed at https://instances.invidious.io; that operator holds your subscriptions, history and watch requests, and the instance fetches video from YouTube. Self-host: git clone https://github.com/iv-org/invidious.git && cd invidious. Generate two 16-character keys with pwgen 16 1, put them in docker-compose.yml as hmac_key and invidious_companion_key (companion SERVER_SECRET_KEY must match). Default compose binds 127.0.0.1:3000. Needs about 20 GB disk and 2 GB RAM; restart at least daily. Playback needs Invidious companion. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/iv-org/invidious). [Gearlist page](https://gearlist.build/tools/invidious/).

### [SimpleX Chat](https://simplex.chat/)

An AGPL messenger that connects people with one-off invitation links or QR codes, using SMP relays instead of user accounts.

**For:** People who want encrypted chat on iOS, Android or a terminal, with relays they can pick or host.

**Access and use:** Mobile: App Store, Google Play, F-Droid (https://app.simplex.chat) or the APK from GitHub Releases. Terminal: curl -o- https://raw.githubusercontent.com/simplex-chat/simplex-chat/stable/install.sh | bash (read the script before running it). Connect by scanning a QR code or opening an smp invitation link. Encrypted messages travel through the SMP relays you choose; the default public relays are operated by SimpleX Chat Ltd. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/simplex-chat/simplex-chat). [Gearlist page](https://gearlist.build/tools/simplex-chat/).

### [ConvertX](https://github.com/C4illin/ConvertX)

A self-hosted file converter that wraps Inkscape, Calibre, LibreOffice, FFmpeg, ImageMagick and other engines behind a web UI.

**For:** People converting documents, images, e-books or video on a machine they control.

**Access and use:** Docker: map port 3000 and volume ./data:/app/data, set PUID to your host user id, then open http://localhost:3000 and create the first account. Anyone who can reach that URL can register that first account. Set JWT_SECRET. HTTP_ALLOWED=true only on a non-HTTPS local connection. Files land in ./data on the host; AUTO_DELETE_EVERY_N_HOURS defaults to 24. ALLOW_UNAUTHENTICATED and ACCOUNT_REGISTRATION stay off on a public host. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/C4illin/ConvertX). [Gearlist page](https://gearlist.build/tools/convertx/).

### [DocuSeal](https://www.docuseal.com/)

An AGPL platform for building PDF forms, collecting signatures and storing completed documents, self-hosted or on DocuSeal Cloud.

**For:** Teams who want fill-and-sign workflows on a host they run, or on DocuSeal's cloud.

**Access and use:** Cloud sign-up is https://docuseal.com/sign_up; completed documents then live on DocuSeal LLC servers. Self-host: docker run --name docuseal -p 3000:3000 -v.:/data docuseal/docuseal then http://localhost:3000. Compose: curl https://raw.githubusercontent.com/docusealco/docuseal/master/docker-compose.yml > docker-compose.yml then sudo HOST=your-domain-name.com docker compose up. SQLite is the default; set DATABASE_URL for PostgreSQL or MySQL. Disk or S3/GCS/Azure for files. AGPL-3.0 with Section 7(b) additional terms: keep DocuSeal attribution in interactive UIs.

**Source checked:** 2026-10-28. [Official source](https://github.com/docusealco/docuseal). [Gearlist page](https://gearlist.build/tools/docuseal/).

### [Midday](https://midday.ai)

An AGPL business workspace for invoicing, time tracking, inbox matching, file vault and an assistant, for freelancers and solo operators.

**For:** Freelancers and contractors who want invoices, time and bank feeds in one product they can host or run on Midday Cloud.

**Access and use:** Cloud is https://app.midday.ai, run by Midday Labs AB; your invoices, transactions and files are then processed in Sweden. Bank connections go through GoCardless (EU), Plaid (Canada and US) or Teller (US). Hosted analytics use OpenPanel. Local: git clone https://github.com/midday-ai/midday.git then bun i; you need a Supabase account, which holds the database, files and sign-in, and an Upstash account for its key-value store (https://docs.midday.ai/local-development). AGPL-3.0 for non-commercial use. For commercial use, Midday Labs AB asks for a commercial licence at engineer@midday.ai.

**Source checked:** 2026-10-28. [Official source](https://github.com/midday-ai/midday). [Gearlist page](https://gearlist.build/tools/midday/).

### [Logto](https://logto.io/)

Open-source OIDC and OAuth 2.1 identity infrastructure with multi-tenancy, SSO, RBAC and SDKs for 30-plus frameworks.

**For:** Teams adding sign-in, organisations and MCP-ready auth to a SaaS or agent product.

**Access and use:** Cloud is https://cloud.logto.io; identity data then lives on Logto Cloud. Local Docker Compose: curl -fsSL https://raw.githubusercontent.com/logto-io/logto/HEAD/docker-compose.yml | docker compose -p logto -f - up. That compose bundles Postgres and drops data if you run it again. npm init @logto@latest needs Node.js 26+ and PostgreSQL 14+. Core is http://localhost:3001; Admin Console is http://localhost:3002. The welcome page creates one admin account with username and password. Recommended host: 2 vCPU, 8 GiB RAM, 256 GiB disk. MPL-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/logto-io/logto). [Gearlist page](https://gearlist.build/tools/logto/).

### [Leantime](https://leantime.io)

An AGPL project-management system for goals, tasks, timesheets, wikis and canvases, designed for neurodivergent teams.

**For:** Small teams who want kanban, gantt, goals and docs on a host they run.

**Access and use:** Cloud is https://leantime.io; project data then lives on Leantime's hosted service. Self-host needs PHP 8.2+ and MySQL 8.0+ or MariaDB 10.6+. Docker: docker run -d --restart unless-stopped -p 8080:8080 with LEAN_DB_HOST, LEAN_DB_USER, LEAN_DB_PASSWORD, LEAN_DB_DATABASE and LEAN_EMAIL_RETURN, then open http://localhost:8080/install. Files can go to local disk or S3. Plugins need the plugins volume mounted and writable by www-data. Self-hosted Leantime sends a daily anonymous usage summary (counts and versions) to telemetry.leantime.io by default; set LEAN_ALLOW_TELEMETRY=false to stop it. AGPL-3.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/Leantime/leantime). [Gearlist page](https://gearlist.build/tools/leantime/).

### [Fluxer](https://fluxer.com/)

An AGPL instant-messaging and VoIP app for friends, groups and communities, with desktop, mobile and a browser client.

**For:** People who want chat and calls on Fluxer's hosted service or on an instance they run.

**Access and use:** Hosted: https://web.fluxer.app or the desktop and mobile apps; messages then live on Fluxer's servers. Self-host: curl -fsSL https://fluxer.dev/install.sh | sh (read the script before running it). Windows: irm https://fluxer.dev/install.ps1 | iex (read the script before running it). Needs 2 CPU cores, 4 GB RAM, 20 GB disk, a domain A record, TCP 80, 443 and 7881, and UDP 443 and 7882. rexctl creates one admin account in the terminal or with a setup token. AGPL-3.0-or-later for the source; artwork is CC BY-SA 4.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/fluxerapp/fluxer). [Gearlist page](https://gearlist.build/tools/fluxer/).

### [Suwayomi Server](https://github.com/Suwayomi/Suwayomi-Server)

A Java manga reader server that runs Mihon (Tachiyomi) extensions, with a bundled web UI, library, downloads and OPDS.

**For:** People who want a self-hosted manga library that talks to the same sources as Mihon.

**Access and use:** OS bundles (Windows, macOS, Linux) ship JRE, Electron and a launcher from GitHub Releases. Docker: ghcr.io/suwayomi/tachidesk, default http://localhost:4567. Jar needs JRE 21+: java -jar Suwayomi-Server-vX.Y.Z-rxxxx.jar. Library, backups and downloads live on the host. Installed extensions fetch chapters from the manga sites you enable; optional FlareSolverr and trackers (MyAnimeList, AniList, MangaUpdates) send data to those services. MPL-2.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/Suwayomi/Suwayomi-Server). [Gearlist page](https://gearlist.build/tools/suwayomi-server/).

### [Open Executive](https://github.com/SenteLabsAI/OpenExecutive)

An Apache-licensed FastAPI and Next.js executive persona backed by nine specialist agents, with local RAG, episodic memory and optional chat and mail connectors.

**For:** Teams who want a self-hosted executive assistant that drafts in one voice and leaves messages on approval cards unless Handle it for me is on.

**Access and use:** git clone https://github.com/SenteLabsAI/OpenExecutive.git && make install, copy .env.example to .env, set ANTHROPIC_API_KEY, then make dev. UI is http://localhost:3000; API is http://localhost:8000. Needs Python 3.11+ and Node 22.6+. First boot downloads an embedding model of about 90 MB. Local make dev with blank AUTH_GOOGLE_ID accepts connections from this computer only. Company documents and memory are stored on the host (ChromaDB and SQLite); prompts, retrieved document chunks and memory go to the Anthropic API. Slack, mail, Telegram, Google Chat and similar connectors send messages through those services when you set their tokens. Apache-2.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/SenteLabsAI/OpenExecutive). [Gearlist page](https://gearlist.build/tools/openexecutive/).

### [Mailflare](https://mailflare.co)

An AGPL custom-domain inbox with calendar, booking, Drive and an MCP mail assistant, running on Cloudflare Workers or Docker.

**For:** People who want mailboxes on their own domain, on a Cloudflare account or a Docker host they run.

**Access and use:** Cloudflare: Deploy to Cloudflare with Worker name mailflare, then open /setup to create the first admin account. CF_TOKEN is a scoped API token that can edit DNS and Email Routing on the zones you connect, and Email Sending if you send through Cloudflare. Docker: git clone https://github.com/hieunc229/mailflare.git && cd mailflare && cp .env.docker.example .env.docker && docker compose up -d --build. Setup is http://localhost:3000/setup. On Cloudflare, mailbox records live in D1 and files live in R2 (or B2 or S3) in that account. Docker stores SQLite, mail and backups in the mailflare-data volume. Send and receive through Cloudflare Email, Resend, Amazon SES or SMTP. The assistant sends mailbox content to the AI provider you set under Admin, Agent. MCP is Streamable HTTP at /mcp on your origin with a Bearer key; request_send still needs confirmation in Mailflare. Optional Pro and Team licence keys are checked with Paymug. AGPL-3.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/hieunc229/mailflare). [Gearlist page](https://gearlist.build/tools/mailflare/).

### [OpenScience](https://openscience.sh)

An Apache-licensed research workbench that plans, searches literature, runs code and experiments, and writes up results with a visible trace.

**For:** Researchers who want a local workbench that keeps project files on the machine and sends model calls to a provider they choose.

**Access and use:** Desktop app for macOS, Windows and Linux from https://openscience.sh/download. CLI: npm install -g @synsci/openscience then openscience. Or npx synsci. Or curl -fsSL https://openscience.sh/install | bash (read the script before running it). First launch of the GUI asks you to sign in to a Synthetic Sciences account. Project files stay in the connected folder. Prompts go to the model provider you connect, a local endpoint, or Ace Wallet pay as you go. Ace auto reload is a separate opt-in that charges a saved card. Search, database connectors and remote compute send queries and selected files to those services. While signed in, session traces are shared by default, including sessions that use your own keys or a local model; turn that off under Customize, Permissions, Data and privacy. Apache-2.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/synthetic-sciences/openscience). [Gearlist page](https://gearlist.build/tools/openscience/).

### [Piik](https://piik.tv)

An MIT screen-sharing app for one host and up to 20 viewers, with browser watch, optional remote control, voice and a self-hosted server.

**For:** Friends who want a private watch-together room they can run themselves.

**Access and use:** Hosted demo is https://demo.piik.tv, P2P only; video and audio travel between participants. App: download Piik App from https://piik.tv, then choose Public invite or Local room. Self-host: extract the Server archive from GitHub Releases and run ./piik-server (Linux) or ./piik-server.exe (Windows). Local UI is http://localhost:8787. Room records stay in SQLite. Docker: download compose.yaml and .env.example from the repo, set your domain, then docker compose up -d. Default is P2P with STUN on UDP 3478; optional SFU on UDP 7882 forwards video and audio through the server. Remote control, once you approve it, lets viewers use the host keyboard, mouse or a supported gamepad. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/TNTcraftHIM/Piik). [Gearlist page](https://gearlist.build/tools/piik/).

### [Whiteboard](https://dev.fast)

An MIT desktop canvas where humans and coding agents draw software maps, traces and semantic diffs against a local checkout.

**For:** Developers who want an agent to diagram a change beside the local repository.

**Access and use:** macOS, Windows and Linux installers from https://dev.fast/install. On macOS: brew install --cask devdotfast/tap/whiteboard. Connect Claude Code, Codex or another coding agent from the welcome screen. Whiteboards stay in ~/.dev/review-api.db. Anonymous telemetry is on by default and goes to PostHog as feature counts, durations and versions under a random installation ID; it omits source code, diffs, paths, prompts and model output. Turn it off in Settings under Share anonymous usage data, or set DO_NOT_TRACK=1. After a crash, the next launch uploads the dump to bug.dev.fast, and it can contain process memory including open source text; with telemetry off, dumps are deleted without upload. whiteboard share uploads a copy of that whiteboard, traces and referenced source to the /dev/fast share service. Trace capture is off until you allow a repository. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/devdotfast/whiteboard). [Gearlist page](https://gearlist.build/tools/whiteboard/).

### [It's a Plan](https://itsaplan.dev)

An AGPL self-hosted issue tracker where people and agents share the same board, with REST, webhooks and MCP.

**For:** Teams who want Linear-style tracking on their own Postgres, with agents as assignees.

**Access and use:** git clone https://github.com/croffasia/itsaplan.git && bun install && bun run setup, then answer Try it. UI is http://localhost:3001; API is http://localhost:3000. Production: copy .env.example to .env, set the secrets and public URLs, then docker compose up -d behind TLS. The first account is instance admin. Issues live in Postgres; files live in RustFS. Agent prompts go to the model or CLI you configure. A daily telemetry snapshot goes to https://telemetry.itsaplan.dev by default (counts as ranges, plus which features and integrations are on); set TELEMETRY_DISABLED=1 or DO_NOT_TRACK=1 to stop it. MCP is on the API origin. AGPL-3.0; the runner package is Apache-2.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/croffasia/itsaplan). [Gearlist page](https://gearlist.build/tools/itsaplan/).

### [openwork](https://github.com/langchain-ai/openwork)

A LangChain desktop UI for deepagentsjs, with filesystem tools, planning and subagent delegation.

**For:** People who want a desktop harness that can read the workspace and run shell commands after you approve the tool call.

**Access and use:** npx openwork, or npm install -g openwork then openwork. Needs Node.js 18 or later. From source: git clone https://github.com/langchain-ai/openwork.git && npm install && npm run dev. Set Anthropic, OpenAI or Google keys in the settings panel. Agents can read the filesystem and run shell commands; review each tool call and only open workspaces you trust. Prompts go to the model provider you choose. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/langchain-ai/openwork). [Gearlist page](https://gearlist.build/tools/openwork/).

### [ZTM](https://github.com/flomesh-io/ztm)

An Apache-licensed zero-trust mesh of HTTP/2 tunnels, with a hub, agents, TLS certificates and apps for tunnel, proxy, script and terminal.

**For:** People who want a small private mesh across home, work and a cloud box, without a SaaS overlay.

**Access and use:** Download the CLI or desktop app from GitHub Releases. Hub: ztm start hub --listen 0.0.0.0:8888 --names YOUR_PUBLIC_IP:8888 --permit root.json. Agent: ztm start agent, then ztm join MESH --as NAME --permit root.json. GUI is http://localhost:7777 after the agent starts. Hub state is ~/.ztm/ztm-hub.db; agent state is ~/.ztm/ztm.db. Traffic is TLS. The permit file is the join key. Apache-2.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/flomesh-io/ztm). [Gearlist page](https://gearlist.build/tools/ztm/).

### [CodeVibes](https://github.com/danish296/codevibes)

An MIT GitHub-repo auditor that scores security, bugs and quality with DeepSeek and a 0 to 100 Vibe Score.

**For:** Developers who want an AI pass over a GitHub repo for secrets, injection and quality.

**Access and use:** Self-host: git clone https://github.com/danish296/codevibes.git, npm install, then cd codevibes-backend && npm install, copy .env.example to .env, set DEEPSEEK_API_KEY, JWT_SECRET and a 32-character ENCRYPTION_KEY. Backend: npm run dev at http://localhost:3001. Frontend: npm run dev at http://localhost:8080. History is SQLite at codevibes-backend/data/codevibes.db. Repo files go to DeepSeek. Private repos need a GitHub token or GitHub OAuth (GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET). MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/danish296/codevibes). [Gearlist page](https://gearlist.build/tools/codevibes/).

### [Hands](https://hands.build)

An MIT Cloudflare-native release platform for draft-first app builds, staged rollouts, share pages, crash reports and in-app feedback.

**For:** Teams shipping Android, iOS, HarmonyOS or Electron builds who want agents and CI to publish through one API.

**Access and use:** Hosted dashboard https://app.hands.build and API https://hands.build, run by Oranix on Cloudflare Workers, D1 and R2. Login with Raft. CLI: npm install -g @botiverse/hands-cli, then hands login (browser JWT saved at $XDG_CONFIG_HOME/quiver/auth.json) or CI HANDS_API=https://hands.build with HANDS_AUTH_TOKEN or HANDS_BEARER_TOKEN. Builds, crash reports, feedback and installable artifacts go to that Cloudflare account. Self-host: git clone https://github.com/botiverse/hands.git, pnpm install, pnpm --filter @botiverse/hands-worker dev at http://127.0.0.1:8787, pnpm --filter @botiverse/hands-admin dev at http://localhost:5173 (proxies /api to 8787). Docker is needed for the APK parser container. Set RAFT_CLIENT_ID in worker config and wrangler secret put RAFT_CLIENT_SECRET. The production Worker config turns Cloudflare observability traces on (5 percent head sample, persist). MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/botiverse/hands). [Gearlist page](https://gearlist.build/tools/hands/).

### [Antiproton](https://antiproton.ai)

An Apache-2.0 Cloudflare-native multi-tenant runtime for autonomous agents, with Durable Object SQLite per tenant, V8 isolates and on-demand Run9 containers.

**For:** Teams who want agents to call real APIs and sandboxes while keeping credentials out of the model context.

**Access and use:** Hosted UI https://antiproton.ai and admin https://admin.antiproton.ai, run by botiverse on Cloudflare Workers, Durable Objects, D1 and R2. Custom domain antiproton.botiverse.dev sits behind Cloudflare Access. GitHub sign-in; UI_ALLOW_ANONYMOUS is 0; GITHUB_OPEN_SIGNUP is 1 so a GitHub account registers on first sign-in. Self-host: git clone https://github.com/botiverse/antiproton.git, npm install, Node.js 24+. cd cf && npx wrangler dev. npx wrangler secret put ANTHROPIC_API_KEY, or OPENROUTER_API_KEY or DEEPSEEK_API_KEY. Production deploy: cf/scripts/deploy-pinned.sh from origin/master. Default HARNESS_MODEL is deepseek-flash. USER_MODELS are deepseek-flash and gpt-5.6-luna through Cloudflare AI Gateway once AI_GATEWAY_TOKEN is set. Credentials stay behind the tool gateway and never enter model context prompts, tool outputs or execution logs. Three tiers: Durable Object plus SQLite per tenant and agent; V8 Dynamic Worker with globalOutbound null; Run9 containers with a 30 minute idle lease and a 5 minute warning. TRACE_INGEST_URL and TRACE_INGEST_TOKEN are unset so trace forwarding is off. Cloudflare observability is enabled. Raft provision APIs can create hosted agents. Daily spend limits apply on the operator model accounts. Docs: docs/agents-api.md, docs/agent-surface.md, docs/plugins.md, docs/runbook.md. Default branch is master. Apache-2.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/botiverse/antiproton). [Gearlist page](https://gearlist.build/tools/antiproton/).

### [BillionMail](https://github.com/Billionmail/BillionMail)

A self-hosted mail server and email campaign platform with contact groups, templates, tracking and a sending API.

**For:** Teams evaluating a Linux mail and newsletter stack they operate themselves.

**Access and use:** Linux amd64 or arm64 with Docker and Docker Compose. The stack includes PostgreSQL, Redis, Postfix, Dovecot, Rspamd and Roundcube; the management container has a Docker socket mount and network capabilities. Requires domain and DNS configuration. Self-hosting, maintenance and any external SMTP relay or AI provider have their own costs. SMTP relay is configurable per sending domain. AI features can call configured model providers, and an image-upload path uses the BillionMail CDN. AGPL-3.0. CVE-2026-111367 affects releases through 4.9; the reviewed dev source still has deterministic fallback generation for subscription signing secrets. A fixed deployment image has not been verified. Separate contact groups or domains do not by themselves keep one client's data apart from another's. We list it for its documentation and source only.

**Source checked:** 2026-10-30. [Official source](https://github.com/Billionmail/BillionMail/blob/fc36c76c050c3775c5e899faf7403cf0262d2744/README.md). [Gearlist page](https://gearlist.build/tools/billionmail/).

### [n8n](https://github.com/n8n-io/n8n)

A visual workflow platform that combines integrations, AI models, code and approval steps.

**For:** Teams who want to connect existing services in workflows they can host or run in n8n Cloud.

**Access and use:** Self-host with Docker using docker.n8n.io/n8nio/n8n; the editor runs on port 5678 and the n8n_data volume persists data under /home/node/.n8n. Workflows use the credentials and data access of the connected services; model and service charges still apply. n8n Cloud has its own account and plan. Source-available under the Sustainable Use License for internal business, personal or non-commercial use, with separate enterprise terms for designated code. Check the licence before embedding it in a customer product or offering hosted access.

**Source checked:** 2026-10-30. [Official source](https://github.com/n8n-io/n8n/blob/21e9955261c5a97b3620f6ecabecc53944b70318/README.md). [Gearlist page](https://gearlist.build/tools/n8n/).

### [Dify](https://github.com/langgenius/dify)

A visual platform for AI applications, agents, document retrieval and model workflows, with APIs for applications.

**For:** Teams building AI applications with a visual workflow and document knowledge base.

**Access and use:** Self-host with Docker Compose 2.24 or later. The README specifies at least 2 CPU cores and 4 GiB RAM. From the docker directory, configure .env and start Compose; initialise through /install. Dify Cloud needs an account and has its own plan. Documents and conversation data are processed by the deployment and whichever models, tools or observability services you configure. Model-provider charges still apply. The modified Apache-2.0 licence restricts operating a multi-tenant environment without written authorisation or a commercial licence, and removing frontend logos or copyright notices. A workspace is a tenant under these terms.

**Source checked:** 2026-10-30. [Official source](https://github.com/langgenius/dify/blob/7e15fac03242a9e6a3a1e5010b06956c7aa101a2/README.md). [Gearlist page](https://gearlist.build/tools/dify/).

### [Langflow](https://github.com/langflow-ai/langflow)

A visual builder for AI agents and workflows that can expose flows through APIs and MCP.

**For:** Developers who want to design and serve AI workflows visually.

**Access and use:** The README supports a desktop app for Windows and macOS, a Python package, or Docker. Python 3.10 to 3.14; install with uv pip install langflow -U, then uv run langflow run. Local UI is http://127.0.0.1:7860. Set LANGFLOW_SUPERUSER_PASSWORD before startup. Official release packages and Docker images require authentication by default; development branches retain automatic login. Flow components can use connected files, models, databases and service credentials, with provider charges where applicable. MIT.

**Source checked:** 2026-10-30. [Official source](https://github.com/langflow-ai/langflow/blob/b5c54a64e685b7e50fd3bc76e965ad718fc2dea3/README.md). [Gearlist page](https://gearlist.build/tools/langflow/).

### [CrewAI](https://github.com/crewAIInc/crewAI)

A Python framework for composing agent teams and controlled workflows with tools, memory and model integrations.

**For:** Python developers building agent workflows in their own application.

**Access and use:** Requires Python 3.10 to 3.13 and uv. Install the CLI with uv tool install crewai. Models and tool integrations need their own configuration, credentials and any provider fees. The framework can run tools with the access the host gives them. Its README describes usage telemetry, disabled with OTEL_SDK_DISABLED=true. Enabling share_crew additionally shares detailed agent and task execution data. MIT.

**Source checked:** 2026-10-30. [Official source](https://github.com/crewAIInc/crewAI/blob/97bbfb64811775a965304bda45c8ec0e8e4ef3a2/README.md). [Gearlist page](https://gearlist.build/tools/crewai/).

### [RAGFlow](https://github.com/infiniflow/ragflow)

A document retrieval and agent platform that parses documents and supplies retrieved context to language models.

**For:** Teams evaluating searchable document collections and retrieval workflows they operate.

**Access and use:** Self-host through Docker and Docker Compose; the reviewed README quickstart selects release candidate v1.0.0-rc2. Recommended starting host: 4 CPU cores, 16 GB RAM and 50 GB disk, with more resources for local models or higher load. Docker 24 or later and Compose 2.26.1 or later. Configure an LLM, embedding model and reranker, including endpoint and API key as needed. Uploaded documents are processed and stored by the deployment, and configured model services may receive document or query content. Provider and hosting costs apply. Apache-2.0.

**Source checked:** 2026-10-30. [Official source](https://github.com/infiniflow/ragflow/blob/6f571fda64cb4eb712aa6c06b3209a4b0553a27c/README.md). [Gearlist page](https://gearlist.build/tools/ragflow/).

### [Open WebUI](https://github.com/open-webui/open-webui)

A self-hosted chat interface for local and remote models, including Ollama and OpenAI-compatible services.

**For:** Teams who want a web interface for model access and document chat on infrastructure they operate.

**Access and use:** Use the official Docker image ghcr.io/open-webui/open-webui, or install the Python package with Python 3.12. The Docker quickstart serves the UI on localhost:3000 and persists the database and uploads in the open-webui volume at /app/backend/data. Local or remote model endpoints determine where prompts and documents go and whether provider charges apply. Offline use needs local models and assets prepared first. The current Open WebUI License includes branding-preservation requirements, with exceptions including deployments of at most 50 end users in a rolling 30-day period or written permission. Earlier components retain their original terms. Check the licence before rebranding.

**Source checked:** 2026-10-30. [Official source](https://github.com/open-webui/open-webui/blob/f7ac7ee10962ddec0017f5c29b6740d9b9c5faca/README.md). [Gearlist page](https://gearlist.build/tools/open-webui/).

### [ToolJet](https://github.com/ToolJet/ToolJet)

A visual builder for internal tools, admin panels and dashboards that run on existing databases, APIs and SaaS systems, with an MCP server that lets coding agents build and edit ToolJet apps.

**For:** Teams building internal apps over their own data who want people and coding agents working in the same app builder.

**Access and use:** Use ToolJet Cloud with an account, or self-host on Docker, Kubernetes, AWS, GCP, Azure and the other documented targets. The README's quick-try image is tooljet/try:ee-lts-latest on port 80. Each data source needs its own credentials, which apps use to run queries. The MCP server is marked beta and runs agent operations on your own model subscription. AI app generation, workflows and the agent builder are listed under the Enterprise edition, whose code sits in non-public submodules (frontend/ee, server/ee). The repository is AGPL-3.0, which requires offering source for modified versions run as a network service.

**Source checked:** 2026-11-03. [Official source](https://github.com/ToolJet/ToolJet). [Gearlist page](https://gearlist.build/tools/tooljet/).

### [Future AGI](https://github.com/future-agi/future-agi)

A self-hostable platform for tracing, evaluating, simulating and guarding LLM and agent applications, with an OpenAI-compatible gateway and prompt optimisation.

**For:** Teams running agents in production who want traces, evals and guardrails in one system they can host themselves.

**Access and use:** Future AGI Cloud needs an account. Self-host clones the repository and runs ./bin/install, which writes secrets to .env and pulls about 800 MB of images. The default Standalone setup needs Docker Compose v2.24 or newer with 2 vCPUs and 4 GB of memory; a Helm chart is also published. Apps send traces with an API key and secret key; add LLM provider keys when you need them. Self-hosted installs send telemetry by default, including the email addresses of owner, admin and staff accounts. Opting out with --no-telemetry or FUTURE_AGI_TELEMETRY_DISABLED=true still sends one registration without email addresses; block api.futureagi.com to send nothing. The core is Apache-2.0, but code in ee/ directories is under the Future AGI Enterprise License and needs a paid subscription for production use.

**Source checked:** 2026-11-03. [Official source](https://github.com/future-agi/future-agi). [Gearlist page](https://gearlist.build/tools/future-agi/).

### [OpenMuse](https://github.com/CopilotKit/openmuse)

An alpha personal agent app for iOS, Android and web, built on CopilotKit and AG-UI, with a persistent Chromium browser, an optional Linux workspace, task plans with approvals, and Gmail and Calendar adapters.

**For:** Developers who want a self-hosted personal agent template to fork and extend.

**Access and use:** Needs Node 24, pnpm 11.19.0 and a CopilotKit Intelligence project key in every mode; Intelligence is a separate service outside the MIT licence. A model needs an OpenAI, Anthropic or Google key. Gmail and Calendar need your own Google OAuth client plus live mode with an access key and token encryption key, and each send or calendar change waits for review. Web search is on by default and sends model-generated queries and context to Parallel's Search MCP; set WEB_SEARCH_ENABLED=false to turn it off. The CopilotKit SDK sends runtime telemetry to PostHog. The optional Linux computer needs Docker. The Render blueprint runs the API and browser on Standard instances. One owner behind a shared access key; not multi-tenant. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/CopilotKit/openmuse). [Gearlist page](https://gearlist.build/tools/openmuse/).

### [Agent Lightning](https://github.com/microsoft/agent-lightning)

Microsoft's reinforcement learning framework for training the model behind an agent while the agent keeps running in its real harness, through a gateway that captures interactions as training data.

**For:** Machine learning teams who want to train an open-weight model on their own agent's tasks.

**Access and use:** Needs a CUDA GPU machine. The README example runs uv sync and a verl setup script for CUDA 13.0, and the trainer uses verl and vLLM. Agents run locally or as Kubernetes Jobs. The Calc-X example needs one GPU. Releases before v1.0 live on the v0.x branch. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/microsoft/agent-lightning). [Gearlist page](https://gearlist.build/tools/agent-lightning/).

### [Social Blade](https://socialblade.com/)

Public statistics, growth history and estimated earnings for YouTube, Instagram, TikTok and Twitch accounts.

**For:** Anyone sizing a creator's reach and growth from public data.

**Access and use:** Public pages are free to read. Reports and an API are for business customers. Earnings figures are estimates from public view counts.

**Source checked:** 2026-11-05. [Official source](https://socialblade.com/info). [Gearlist page](https://gearlist.build/tools/social-blade/).

### [Floci](https://floci.io/floci/)

A local AWS emulator for development, tests and CI that serves AWS-shaped services at localhost:4566 and can replace LocalStack Community.

**For:** Developers who test AWS SDK, CLI, Terraform or CDK code on their machine or in CI without an AWS account.

**Access and use:** docker compose up with the floci/floci image on port 4566, or floci start with the Floci CLI; a standalone binary is on GitHub Releases. Needs no AWS account or auth token, and any non-empty credentials work unless you turn on service auth checks. Lambda, RDS, ECS, EC2, EKS and other services run real containers and need the Docker socket mounted, which gives Floci control of Docker on the host. The web console at localhost:4566/_floci/ui starts a sidecar on port 4500, published on every interface unless you set FLOCI_SERVICES_UI_BIND_ADDRESS. Data stays in memory by default. MIT.

**Source checked:** 2026-11-06. [Official source](https://github.com/floci-io/floci). [Gearlist page](https://gearlist.build/tools/floci/).

### [Ansvisor](https://github.com/ansvisor/ansvisor)

An open-source AI search visibility platform that tracks how a brand appears in ChatGPT, Gemini, Claude, Google AI Overviews and other engines, and uses agents to draft content fixes, with an MCP server and Claude skills.

**For:** Agencies, brands, SaaS companies and developers who want to track and improve how AI answer engines present them, including from Claude, Cursor or another MCP client.

**Access and use:** Self-host: clone the repo, copy the web and server .env example files, run the migration SQL in a Supabase project (the free tier works), then install the web app with Yarn and the server with npm, or run docker compose up --build. Needs Node.js 20 or later, a key for at least one AI provider (OpenAI, Google Gemini or Anthropic) and a Cloro key for collecting answers from AI platforms; Site Audit also needs Scrape.do, and DataForSEO, Tavily, OpenRouter and Composio are optional. Tracked prompts go to the AI providers you configure and to Cloro on a nightly cycle, and each run uses credits at those services. Connect Claude Code, Cursor or another MCP client to /api/mcp with an ans_ API key sent as a bearer header; app.ansvisor.com/api/mcp is the hosted endpoint on Ansvisor's servers. Docker Compose publishes the web app on port 3000 and the API on port 80, and the first user to sign up becomes the admin, so register first and put a firewall in front. Send to CMS sends WordPress pages as drafts for you to publish. Agents that publish on their own are off by default and need server flags, an Admin switch and per-agent permission. Telemetry is off on self-host unless you set a PostHog key. A managed Ansvisor Cloud is also offered. MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/ansvisor/ansvisor/blob/main/README.md). [Gearlist page](https://gearlist.build/tools/ansvisor/).

## Protocols

### [x402](https://x402.org/)

An open protocol for payments over HTTP using the 402 response.

**For:** Developers building services that charge per request.

**Access and use:** Connecting a payment client can spend funds. Set explicit transaction limits.

**Source checked:** 2026-10-25. [Official source](https://x402.org/). [Gearlist page](https://gearlist.build/tools/x402/).

### [Model Context Protocol](https://modelcontextprotocol.io)

An open protocol that connects LLM applications to tools, resources and data sources.

**For:** People building hosts, clients or servers that speak MCP.

**Access and use:** Spec and docs at modelcontextprotocol.io. Official org is github.com/modelcontextprotocol. Python SDK (MIT): uv add "mcp[cli]" or pip install "mcp[cli]", Python 3.11 or later. TypeScript SDK at github.com/modelcontextprotocol/typescript-sdk. Public servers are listed in the Official MCP Registry already in this catalog. The servers repo keeps only steering-group reference servers. New spec and code contributions are Apache-2.0; some older MIT remains; docs excluding the spec are CC BY 4.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/modelcontextprotocol/modelcontextprotocol). [Gearlist page](https://gearlist.build/tools/mcp/).

### [Agent2Agent (A2A)](https://a2a-protocol.org)

An open protocol for independent agents to discover each other and collaborate on tasks without exposing internal state.

**For:** People connecting agents built on different frameworks.

**Access and use:** pip install a2a-sdk. Also official Go, JavaScript, Java, .NET and Rust SDKs. Spec v1.0 at a2a-protocol.org. Linux Foundation project, donated by Google. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/a2aproject/A2A). [Gearlist page](https://gearlist.build/tools/a2a/).

### [Agent Client Protocol](https://agentclientprotocol.com)

An open protocol that connects a code editor to a coding agent so they can share files, tools and a session.

**For:** People wiring an editor such as Zed or JetBrains to a coding agent, or shipping either side of that pair.

**Access and use:** Spec at agentclientprotocol.com. Current stable protocol version is 1. TypeScript: npm install @agentclientprotocol/sdk. Rust: cargo add agent-client-protocol. Also official Python, Java and Kotlin SDKs. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/agentclientprotocol/agent-client-protocol). [Gearlist page](https://gearlist.build/tools/agent-client-protocol/).

### [Agent Skills specification](https://agentskills.io/specification)

The SKILL.md folder format for agent skills, in which a skill's instructions and associated resources sit in one directory that compatible agents can discover and load when relevant.

**For:** People who write agent skills, and developers whose agents load them.

**Access and use:** A file format, not a hosted service, so reading or adopting it needs no account. It is not an agent, a safety scanner or a permission boundary. A skill written to the format can still hold scripts, instructions and access to resources; what it may do and where its data goes depend on the agent that loads it and on the skill itself, so read a skill before you install it. Following the format does not make a skill trustworthy. Originally developed by Anthropic, with contributions from the wider ecosystem. A living specification with no versioned releases. Code is Apache-2.0 and documentation is CC BY 4.0.

**Source checked:** 2026-11-14. [Official source](https://github.com/agentskills/agentskills). [Gearlist page](https://gearlist.build/tools/agent-skills-specification/).

### [AG-UI](https://docs.ag-ui.com)

An event-based protocol for connecting agents to user-facing applications, carrying streamed messages, tool activity and shared state.

**For:** Developers connecting an agent backend to the interface of an application people use.

**Access and use:** The protocol has no account or model bill of its own. The server, client, model and hosting you choose decide authentication, what content is sent and the cost, and adopting the protocol does not supply authentication, hosting or enterprise governance. The project is led by CopilotKit, with other contributors. Repository releases are dated groups of implementations, not one SDK version. MIT.

**Source checked:** 2026-11-14. [Official source](https://github.com/ag-ui-protocol/ag-ui). [Gearlist page](https://gearlist.build/tools/ag-ui/).

### [llms.txt](https://llmstxt.org)

A proposed Markdown file at /llms.txt, or at any path on a site, that gives agents a short summary of the site and links to clean Markdown versions of its pages.

**For:** Site owners and documentation teams who want coding agents and assistants to find the right pages, and people writing tools that read those files.

**Access and use:** A plain file you publish. It grants no access, and agents read it on demand while they help a user. Format: an H1 name, an optional blockquote summary, then H2 sections of Markdown link lists, with an Optional section for links an agent can skip. Version 2 also proposes .md copies of pages, linked with rel="alternate" type="text/markdown" and rel="describedby". Written by Jeremy Howard and open for community input at github.com/AnswerDotAI/llms-txt, which is Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://llmstxt.org/). [Gearlist page](https://gearlist.build/tools/llms-txt/).

### [Universal Commerce Protocol (UCP)](https://ucp.dev)

An open standard for AI agents, apps, businesses and payment providers to handle product search, carts, checkout, identity linking and orders without a custom integration for each connection.

**For:** Retailers, commerce platforms, payment providers and AI platforms that want agents to buy from businesses through one interface.

**Access and use:** Spec and docs at ucp.dev; schemas, SDKs, samples and conformance tests at github.com/Universal-Commerce-Protocol. Businesses declare the capabilities they support in a profile and offer them over REST, MCP or A2A. Identity linking uses OAuth 2.0, and payments can use AP2 mandates. Businesses stay the merchant of record. Co-developed by Google, Shopify, Etsy, Wayfair, Target, Walmart and others. The latest dated release is v2026-08-25; the lodging spec is a draft. An agent that completes a checkout can spend money, so set limits. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/Universal-Commerce-Protocol/ucp). [Gearlist page](https://gearlist.build/tools/universal-commerce-protocol/).

### [Agentic Commerce Protocol (ACP)](https://www.agenticcommerce.dev)

An open standard from OpenAI and Stripe for checkout between buyers, their AI agents and businesses, including passing payment credentials through the agent without exposing them.

**For:** Businesses that want their checkout to work with ChatGPT and other agents, AI platforms that add purchasing, and payment providers.

**Access and use:** The spec is in beta, with dated versions; the latest stable one is 2026-04-17, published as RFCs, OpenAPI and JSON Schema files on GitHub. It works over REST or MCP. ChatGPT was the first platform to implement it, and businesses apply to sell there. Stripe was the first compatible payment provider, through its Shared Payment Token. Businesses stay the merchant of record and can accept or decline each agent transaction. An agent that completes a checkout can spend money, so set limits. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol). [Gearlist page](https://gearlist.build/tools/agentic-commerce-protocol/).

## Skills and learning

### [THL Open](https://github.com/techhorizonlabs/thl-open)

Agent skills and reporting tools for AI readiness audits and fix plans. Tech Horizon Labs project.

**For:** Agencies, consultants and teams evaluating their own or authorised client sites.

**Access and use:** Skills may use external services or scan a site. Obtain target permission and review dependencies before running them.

**Source checked:** 2026-10-25. [Official source](https://github.com/techhorizonlabs/thl-open). [Gearlist page](https://gearlist.build/tools/thl-open/).

### [AGENTS.md](https://agents.md)

An open markdown format at the root of a repository that tells coding agents how the project works.

**For:** Repository maintainers and coding agents.

**Access and use:** A file in a clone. It does not grant credentials. Agents that read it will follow those instructions, so keep secrets out of it.

**Source checked:** 2026-10-26. [Official source](https://github.com/agentsmd/agents.md). [Gearlist page](https://gearlist.build/tools/agents-md/).

### [npx skills](https://github.com/vercel-labs/skills)

A command line installer that copies Agent Skills (SKILL.md folders) into the skill directories of local coding agents.

**For:** People installing portable skills into Claude Code, Codex, Cursor and similar agents.

**Access and use:** Writes files onto the machine. Treat a skill as untrusted code and instructions until you have read it. Example: npx skills add techhorizonlabs/thl-open.

**Source checked:** 2026-10-26. [Official source](https://github.com/vercel-labs/skills). [Gearlist page](https://gearlist.build/tools/npx-skills/).

### [Anthropic skills](https://github.com/anthropics/skills)

Public Agent Skills from Anthropic for coding agents that read SKILL.md.

**For:** People installing first-party examples of the Agent Skills format.

**Access and use:** Public git clone or npx skills add. GitHub licence field was empty on 26 October 2026. Read the repository licence files before reuse.

**Source checked:** 2026-10-26. [Official source](https://github.com/anthropics/skills). [Gearlist page](https://gearlist.build/tools/anthropic-skills/).

### [Hyperresearch](https://github.com/jordan-gibbs/hyperresearch)

A deep research skill and CLI that collects web and scholarly sources into a persistent vault and writes a cited report.

**For:** People running long research jobs in Claude Code or Codex, or using the hosted site.

**Access and use:** pip install writes skills, hooks and project files. Runs need network and write access. Hosted product at hyperresearch.ai is a separate account. MIT. Check what the vault stores before pointing it at private material.

**Source checked:** 2026-10-27. [Official source](https://github.com/jordan-gibbs/hyperresearch). [Gearlist page](https://gearlist.build/tools/hyperresearch/).

### [Tech Horizon Academy](https://academy.techhorizonlabs.com/)

A free academy of Claude skills, prompts and AI tools for Australian small businesses. Tech Horizon Labs project.

**For:** Australian operators and the agents they run.

**Access and use:** Public site. Skills and prompts are instructions; tools in the directory may need their own accounts. Indexes on 27 Oct 2026: 67 skills, 206 tools, 1217 prompt titles. Indexes are names and notes, not skill bodies or prompt text. Some academy tool pages carry partner flags; Gearlist omits referral parameters.

**Source checked:** 2026-10-27. [Official source](https://academy.techhorizonlabs.com/skills). [Gearlist page](https://gearlist.build/tools/tech-horizon-academy/).

### [Claude Academy](https://academy.claude.com/)

Anthropic's official courses on Claude, Claude Code, MCP, skills and the Claude API.

**For:** People learning Claude products and MCP.

**Access and use:** Free courses at academy.claude.com. Some lessons need a Claude account.

**Source checked:** 2026-10-27. [Official source](https://academy.claude.com/courses). [Gearlist page](https://gearlist.build/tools/claude-academy/).

### [Claude plugins official](https://github.com/anthropics/claude-plugins-official)

Anthropic's official Claude Code plugin marketplace. 315 plugins counted on 27 Oct 2026, mostly partner connectors.

**For:** Claude Code users installing plugins with /plugin.

**Access and use:** Claude Code adds this marketplace on first interactive session. A plugin can install MCP servers and write config. Review a plugin before enabling it. Names and homepages are in indexes/claude-plugins-official.json. Not a security audit of each plugin.

**Source checked:** 2026-10-27. [Official source](https://code.claude.com/docs/en/plugins/anthropic-marketplaces). [Gearlist page](https://gearlist.build/tools/claude-plugins-official/).

### [SkillsMP](https://skillsmp.com/)

A community index of Agent Skills scraped from GitHub. Not run by Anthropic.

**For:** People searching for community skills at their own risk.

**Access and use:** Unvetted. Individual skills keep their upstream licences. Anonymous API is rate limited. Treat a listed skill as untrusted code until you have read it. Optional paid API plans.

**Source checked:** 2026-10-27. [Official source](https://skillsmp.com/). [Gearlist page](https://gearlist.build/tools/skillsmp/).

### [Anthropic Cybersecurity Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills)

An independent community library of 818 cybersecurity skills in the agentskills.io format, mapped to MITRE ATT&CK, NIST CSF 2.0 and related frameworks. Not affiliated with Anthropic.

**For:** Security practitioners whose agents need structured playbooks for authorised testing, defence and education.

**Access and use:** Install with npx skills add mukul975/Anthropic-Cybersecurity-Skills. Apache-2.0. Includes offensive and dual-use techniques. Use only on systems you own or have written permission to test. A listed skill is not a security audit of your environment.

**Source checked:** 2026-10-28. [Official source](https://github.com/mukul975/Anthropic-Cybersecurity-Skills). [Gearlist page](https://gearlist.build/tools/anthropic-cybersecurity-skills/).

### [OrchestKit](https://orchestkit.dev)

A free Claude Code plugin of skills, agents and hooks for review, testing, security and memory, with a smaller pack for Cursor and Codex.

**For:** People who want those playbooks and quality gates on Claude Code or a compatible host.

**Access and use:** Claude Code: claude plugin marketplace add yonatangross/orchestkit && claude plugin install ork@orchestkit, then /ork:setup. Hooks read tool events and write local metrics under ~/.local/state/orchestkit/. Prompt text is not recorded. Network telemetry is off unless you set a destination. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/yonatangross/orchestkit). [Gearlist page](https://gearlist.build/tools/orchestkit/).

### [UX/UI Agent Skills](https://plugin87.github.io/ux-ui-agent-skills/)

A design-system kit for coding agents (also called XIAS): tokens, 26 skills, 52 objective gates, and a library of design-system specs.

**For:** People whose agents design or review UI in Claude Code, Codex, Cursor, Gemini CLI or an MCP client.

**Access and use:** Claude Code: /plugin marketplace add plugin87/ux-ui-agent-skills then /plugin install ux-ui-agent-skills@ux-ui-agent-skills. Other hosts: npx ux-ui-agent-skills init, or Homebrew plugin87/tap/ux-ui-agent-skills. MCP is claude mcp add ux-ui-gates -- npx -y --package=ux-ui-agent-skills ux-ui-mcp. 34 of the 52 gates open a real browser using Chrome on the machine or npx playwright install chrome. Live demo needs no install. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/plugin87/ux-ui-agent-skills). [Gearlist page](https://gearlist.build/tools/ux-ui-agent-skills/).

### [AI Marketing Skills](https://github.com/ericosiu/ai-marketing-skills)

Open-source Claude Code skills for growth experiments, sales pipeline, content ops, outbound, SEO, finance and related marketing workflows, published by Single Grain.

**For:** Marketing and sales teams whose coding agent should run those playbooks.

**Access and use:** Clone the repo, then copy each skill directory (SKILL.md plus any scripts, references or agents) into your agent's skills folder. Categories also ship Python scripts; pip install -r requirements.txt and fill .env with the API keys that category needs. Local usage logs live at ~/.ai-marketing-skills/analytics/. Remote telemetry stays off until you opt in. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/ericosiu/ai-marketing-skills). [Gearlist page](https://gearlist.build/tools/ai-marketing-skills/).

### [Solid Glass](https://deeplethe.github.io/solid-glass)

A shadcn/ui stylesheet and component registry for agent workspaces: status, composer, tool steps, diffs and related screens.

**For:** People building agent UIs on React 19, Tailwind CSS 4 and shadcn/ui.

**Access and use:** Start from a shadcn/ui project, then npx shadcn@latest add deeplethe/solid-glass/solid-glass and import the stylesheet after Tailwind and shadcn. Extra components such as status-glyph install the same way. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/deeplethe/solid-glass). [Gearlist page](https://gearlist.build/tools/solid-glass/).

### [Product Launch Motion](https://github.com/AbubakrChan/product-launch-motion)

A Claude Code skill that reads a website URL and renders a local launch film with Playwright, FFmpeg and music-timed springs.

**For:** People who want a product launch video directed from their site inside Claude Code.

**Access and use:** npx skills add AbubakrChan/product-launch-motion. Needs Claude Code, Node 20 or later, Playwright, FFmpeg, and Python with numpy. Renders on the local machine. MIT on the skill and references. The sample films belong to Cheerful, and the MIT licence doesn't cover them.

**Source checked:** 2026-10-28. [Official source](https://github.com/AbubakrChan/product-launch-motion). [Gearlist page](https://gearlist.build/tools/product-launch-motion/).

### [jev-seo](https://github.com/AgriciDaniel/jev-seo)

A local Python CLI and Claude Code skill that crawls a site, scores technical rules, optionally has the Jev model from TypeSafe judge each page, and writes a PDF, Excel tracker and Markdown from one audit record.

**For:** People who want a live site audit with ranked, evidence-linked fixes from a homepage URL.

**Access and use:** Python 3.10 or later. git clone, then python3 -m venv and pip install -r requirements.txt. WeasyPrint needs Pango. Set TYPESAFE_API_KEY in .env for Jev judgments; without it the audit still runs as a partial audit. Optional PAGESPEED_API_KEY, and for --full DATAFORSEO_USERNAME and DATAFORSEO_PASSWORD. Optional Playwright Chromium for JavaScript-only pages. Reports land under jev-seo-reports/. Claude Code: ln -s the clone into ~/.claude/skills/jev-seo. MIT. Bundled fonts are SIL. Jev citability answers are model judgments of a page.

**Source checked:** 2026-10-28. [Official source](https://github.com/AgriciDaniel/jev-seo). [Gearlist page](https://gearlist.build/tools/jev-seo/).

### [SEOmator SEO Audit](https://github.com/seo-skills/seo-audit-skill)

A local CLI, Electron app and Claude Code skill that crawls a site, scores technical, content and AI-crawler checks, and writes console, JSON, HTML, Markdown or LLM XML reports.

**For:** People who want a local site audit they can run from a terminal, a desktop window or Claude Code.

**Access and use:** Node.js 20.3 or later. npm install -g @seomator/seo-audit, then seomator audit URL. For Core Web Vitals, npx playwright install chromium. Audits land in ~/.seomator by default; seomator serve binds loopback with a per-launch token. Claude Code: npx skills add seo-skills/seo-audit-skill. MIT. This entry covers the open-source audit engine only.

**Source checked:** 2026-10-28. [Official source](https://github.com/seo-skills/seo-audit-skill). [Gearlist page](https://gearlist.build/tools/seomator-seo-audit/).

### [Hallmark](https://www.usehallmark.com/)

A design skill that picks a theme, builds a self-contained HTML page from your brief, and lints it in a browser for contrast, layout and common machine-made tells.

**For:** People who want a coding agent to design a page with a named theme and a local lint pass.

**Access and use:** npx skills add nutlope/hallmark -g. Needs Node 18 or later. Browser checks need puppeteer-core and Chrome; static checks still run without them. MIT. Bundled photo index points at Wikimedia Commons; each photograph keeps its own licence and is credited on the page.

**Source checked:** 2026-10-28. [Official source](https://github.com/Nutlope/hallmark). [Gearlist page](https://gearlist.build/tools/hallmark/).

### [Superpowers](https://github.com/obra/superpowers)

A skills pack that makes a coding agent specify, plan, test and review before it writes code.

**For:** People who want a spec-plan-TDD workflow in Claude Code, Codex, Cursor and other coding agents.

**Access and use:** Claude Code: /plugin install superpowers@claude-plugins-official. Other harnesses have their own plugin install in the README. Optional visual companion loads a logo from primeradiant.com with the Superpowers version; set SUPERPOWERS_DISABLE_TELEMETRY to turn that off. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/obra/superpowers). [Gearlist page](https://gearlist.build/tools/superpowers/).

### [Spec Kit](https://github.github.io/spec-kit/)

A GitHub toolkit that gives a coding agent spec-driven build, bug-fix and idea-assessment processes, plus templates you can replace with your own.

**For:** People who want a coding agent to work from a written spec, a bug report, or an idea assessment rather than jumping straight to code.

**Access and use:** Python 3.11 or later and uv. uv tool install specify-cli, then specify init my-project --integration copilot (or another listed agent). Bug-fix and assessment extensions are specify extension add bug and specify extension add assess. Community catalog listings are unvetted. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/github/spec-kit). [Gearlist page](https://gearlist.build/tools/spec-kit/).

### [Marketing Skills](https://marketing-skills.com)

A pack of marketing skills for coding agents covering conversion, copy, SEO, ads, analytics and growth.

**For:** Technical marketers and founders who want a coding agent to help with CRO, copy, SEO and measurement.

**Access and use:** npx skills add coreyhaines31/marketingskills. From inside Claude Code, pass -a claude-code so it lands in .claude/skills. Claude Code plugin: /plugin marketplace add coreyhaines31/marketingskills then /plugin install marketing-skills. MIT. Verified partners fund the library and sit beside the integrations; the README says they do not change what the core skills recommend.

**Source checked:** 2026-10-28. [Official source](https://github.com/coreyhaines31/marketingskills). [Gearlist page](https://gearlist.build/tools/marketing-skills/).

### [Archify](https://archify.si)

A skill that turns a description or a repository into a self-contained interactive HTML diagram you can open in a browser.

**For:** People who want a coding agent to draw an architecture, sequence or explainer page they can share as one file.

**Access and use:** npx skills add tt-a1i/archify -g. Optional preview binds a random port on 127.0.0.1. Archify may GET a stable-release manifest to show an update reminder; set ARCHIFY_UPDATE_CHECK_DISABLED=1 to turn that off. Third-party paid services listed in the README are run by those providers. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/tt-a1i/archify). [Gearlist page](https://gearlist.build/tools/archify/).

### [last30days](https://github.com/mvanhorn/last30days-skill)

A research skill that searches Reddit, Hacker News, GitHub, Polymarket and optional social APIs, then writes a cited brief from the last 30 days.

**For:** People who want a coding agent to brief them on a person, product or topic from recent public conversation.

**Access and use:** Claude Code: /plugin marketplace add mvanhorn/last30days-skill then /plugin install last30days. Other hosts: npx skills add mvanhorn/last30days-skill -g. Reddit, HN, Polymarket and GitHub work with no keys. Extra sources need API keys or a logged-in browser. Needs Python 3.12 or later. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/mvanhorn/last30days-skill). [Gearlist page](https://gearlist.build/tools/last30days/).

### [Matt Pocock Skills](https://github.com/mattpocock/skills)

A pack of engineering skills for coding agents covering grilling, specs, TDD, architecture and pull-request shape.

**For:** People who want a coding agent to interview them, write a spec, then implement with tests and a review.

**Access and use:** Claude Code: claude plugin install mattpocock-skills@claude-plugins-official. Other hosts: npx skills@latest add mattpocock/skills. Pick the plugin or the copied files for each agent; installing both puts every skill in twice. Run /setup-matt-pocock-skills once per repo. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/mattpocock/skills). [Gearlist page](https://gearlist.build/tools/mattpocock-skills/).

### [career-ops](https://career-ops.org)

A local job-search skill that scores a listing against your CV, drafts the application, and leaves Submit to you.

**For:** People who want a coding agent to filter and prepare applications on their own machine.

**Access and use:** npx @santifer/career-ops init, then open your coding agent in that folder. Claude Code plugin: /plugin marketplace add career-ops-hq/career-ops then /plugin install career-ops@career-ops. Data stays in the workspace (plugin installs use ~/career-ops-data). It drafts CVs, cover letters and emails; it never POSTs an application or sends mail. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/career-ops-hq/career-ops). [Gearlist page](https://gearlist.build/tools/career-ops/).

### [gstack](https://github.com/garrytan/gstack)

A skills pack that turns a coding agent into a sprint team: office hours, architecture, review, browser QA and a ship command.

**For:** People who want named specialist skills on Claude Code, Codex, OpenCode and other hosts.

**Access and use:** Needs Git, Bun 1.4.2 or later, and Node on Windows. git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup. Other hosts: ./setup --host auto. Team mode runs a silent hourly update check. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/garrytan/gstack). [Gearlist page](https://gearlist.build/tools/gstack/).

### [The Agency](https://github.com/msitarzewski/agency-agents)

A large roster of specialist agent files for coding tools, covering engineering, design, sales, marketing and operations.

**For:** People who want to drop named specialist agents into Claude Code, Cursor, Codex and other hosts.

**Access and use:** Native app at https://agencyagents.app, or brew install --cask msitarzewski/agency-agents/agency-agents. From a clone: ./scripts/install.sh --tool claude-code, or --tool with another listed host. Install a subset with --division or --agent. OpenCode currently registers about 119 agents and drops the rest. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/msitarzewski/agency-agents). [Gearlist page](https://gearlist.build/tools/agency-agents/).

### [Claude for Financial Services](https://github.com/anthropics/financial-services)

Reference agents and skills for investment banking, equity research, private equity and fund ops, drafted for a human to sign off.

**For:** Firms that want Claude to draft models, memos and reconciliations under a qualified reviewer's control.

**Access and use:** Claude Code: claude plugin marketplace add anthropics/financial-services, then claude plugin install financial-analysis@claude-for-financial-services and the named agents you need. Cowork: Settings, Plugins, Add plugin, paste the repo URL. The README says nothing here is investment, legal, tax or accounting advice, and agents do not execute trades or post to a ledger. MCP data connectors may need a provider subscription. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/anthropics/financial-services). [Gearlist page](https://gearlist.build/tools/claude-for-financial-services/).

### [Claude Code Templates](https://aitmpl.com)

A catalog of Claude Code agents, commands, hooks, settings and MCP installs you can browse and add with one npx command.

**For:** People who want a ready-made Claude Code stack of agents, commands and MCP installs.

**Access and use:** npx claude-code-templates@latest, then pick components, or pass --agent, --command, --mcp, --hook or --setting with --yes. The CLI sends anonymous usage tracking to aitmpl.com by default; set CCT_NO_TRACKING=true to turn it off. Analytics, chats and health-check are extra flags on the same CLI. Bundled third-party skills keep their original licences. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/davila7/claude-code-templates). [Gearlist page](https://gearlist.build/tools/claude-code-templates/).

### [book-to-skill](https://github.com/virgiliojr94/book-to-skill)

A converter that turns a book, folder or set of documents you already have into a structured agent skill with on-demand chapters.

**For:** People who want a coding agent to answer from a book or internal docs they own.

**Access and use:** npx skills add virgiliojr94/book-to-skill. Then /book-to-skill ./my-book.pdf. Extraction runs on your machine and the tool uploads nothing, but if your agent uses a cloud model, the text goes to that provider like any prompt. The MIT licence covers the converter. Books you process keep their own copyright. Keep generated skills of copyrighted books private. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/virgiliojr94/book-to-skill). [Gearlist page](https://gearlist.build/tools/book-to-skill/).

### [video-use](https://github.com/browser-use/video-use)

A coding-agent skill that transcribes a folder of takes and cuts a video from them.

**For:** People who want Claude Code or Codex to edit talking-head or launch videos from local files.

**Access and use:** git clone https://github.com/browser-use/video-use then symlink the repo into your agent's skills directory. Needs ffmpeg and an ElevenLabs API key for transcription. uv sync or pip install -e . Hosted product is on a waitlist at video-use.com. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/browser-use/video-use). [Gearlist page](https://gearlist.build/tools/video-use/).

### [/brag](https://github.com/latent-spaces/brag)

An agent skill that turns the project you just built into a short launch video with music and share copy.

**For:** Builders who want a coding agent to produce a shareable launch clip from the current repo.

**Access and use:** npx skills add https://github.com/latent-spaces/brag --skill brag. Claude Code: /plugin marketplace add latent-spaces/brag then /plugin install brag@brag. Needs Node 22 or later and ffmpeg. Hyperframes via npx hyperframes. Hosted shortcut is letsbrag.app. Bundled music is CC BY 4.0 from ende.app. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/latent-spaces/brag). [Gearlist page](https://gearlist.build/tools/brag/).

### [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin)

A plugin of skills that runs a brainstorm, plan, build, review and capture-what-you-learned loop on a coding agent.

**For:** Teams who want each change to leave notes the next agent can read.

**Access and use:** Claude Code: /plugin marketplace add EveryInc/compound-engineering-plugin then /plugin install compound-engineering. Cursor: /add-plugin compound-engineering. Codex CLI: codex plugin marketplace add EveryInc/compound-engineering-plugin then codex plugin add compound-engineering@compound-engineering-plugin. Existing installs must refresh the marketplace before /plugin update. /lfg can push, open a PR and watch CI; it merges only if you grant that. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/EveryInc/compound-engineering-plugin). [Gearlist page](https://gearlist.build/tools/compound-engineering/).

### [/watch](https://github.com/bradautomates/claude-video)

An agent skill that turns a video URL or local file into timestamped frames and a transcript.

**For:** People who want a coding agent to inspect a video as evidence.

**Access and use:** Claude Code: /plugin marketplace add bradautomates/claude-video then /plugin install watch@claude-video. Also npx skills add bradautomates/claude-video -g --skill watch. Needs Python 3.10 or later, ffmpeg and yt-dlp. Default Gemini engine uploads videos to Google; --engine local keeps extraction on the machine. Cookie files and --cookies-from-browser are opt-in. Claude Chat and Cowork are unsupported. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/bradautomates/claude-video). [Gearlist page](https://gearlist.build/tools/watch/).

### [OpenWiki](https://github.com/langchain-ai/openwiki)

A CLI that turns a repository into a linked Markdown wiki your coding agent can search, with facts tracked back to source lines.

**For:** Teams who want agents to search a living wiki of the code.

**Access and use:** npm install -g openwiki. Needs Node 22.22.0 or later. Then openwiki integrations install claude (or codex, cursor, opencode). Uses the coding agent's existing model session. openwiki visualize serves 127.0.0.1 only; the graph page still loads libraries from a public CDN. Native CLI init writes provider keys to ~/.openwiki/.env. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/langchain-ai/openwiki). [Gearlist page](https://gearlist.build/tools/openwiki/).

### [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian)

A Claude Code plugin and Agent Skills pack that turns inbox sources into a linked Markdown wiki you can open in Obsidian.

**For:** People who keep research in an Obsidian vault and want Claude to file, cite and query it.

**Access and use:** claude plugin marketplace add AgriciDaniel/claude-obsidian then claude plugin install claude-obsidian@agricidaniel-claude-obsidian. Needs Python 3.11 or later. Notes Claude reads are sent to Claude like any other prompt. Web research and remote models stay off until you allow them for a task. The vault stays as local Markdown. The plugin has no telemetry. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/AgriciDaniel/claude-obsidian). [Gearlist page](https://gearlist.build/tools/claude-obsidian/).

### [antislop](https://github.com/miqdadbadjuber/anti-slop)

Agent skills that filter generic AI UI, copy and comments, with a delivery gate before you ship.

**For:** People who want a coding agent to reject generic output before it lands in the repo.

**Access and use:** npx antislop-ai. The npm name antislop is a different package. Also npx skills add miqdadbadjuber/anti-slop. Optional mode preference is ~/.config/antislop/settings.json. There is no antislop coin, token or fundraise. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/miqdadbadjuber/anti-slop). [Gearlist page](https://gearlist.build/tools/anti-slop/).

### [GEO-SEO Claude](https://github.com/zubair-trabzada/geo-seo-claude)

A Claude Code skill pack that audits a URL for AI-search citability, crawler access, schema and llms.txt.

**For:** People who want Claude Code to score a site for AI citation and crawler access.

**Access and use:** curl -fsSL https://raw.githubusercontent.com/zubair-trabzada/geo-seo-claude/main/install.sh | bash; read the script before running it. Needs Python 3.10+ and Claude Code. Dependencies go into ~/.claude/skills/geo/.venv/. /geo audit fetches the target URL. Optional Playwright takes screenshots. Prospect files live in ~/.geo-prospects/ and stay after uninstall. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/zubair-trabzada/geo-seo-claude). [Gearlist page](https://gearlist.build/tools/geo-seo-claude/).

### [Maestro](https://maestroskills.dev)

A workflow skill pack with 25 commands, seven domain references, a memory layer and an MCP server for coding agents.

**For:** People who want Cursor, Claude Code, Codex, OpenCode or similar tools to follow a shared workflow skill.

**Access and use:** npx skills add sharpdeveye/maestro copies skills into the provider folders in the project. For a live MCP server, add npx -y maestro-workflow-mcp to the client config (stdio). npx maestro-workflow-mcp --http --port 3001 serves /mcp on that port on every interface. /capture writes .maestro/ with context.md, decisions.jsonl, audit.jsonl and session files; session data is gitignored by default. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/sharpdeveye/maestro). [Gearlist page](https://gearlist.build/tools/maestro/).

### [ClosedLoop Claude Plugins](https://www.closedloop.ai/docs)

Open-source Claude Code plugins for plan-first coding, review and self-learning, grounded in the repo.

**For:** People who want Claude Code or Codex plugins for planning, implementation and pull-request review.

**Access and use:** curl -fsSL https://raw.githubusercontent.com/closedloop-ai/claude-plugins/main/install.sh | bash; read the script before running it. Needs Claude Code, Python 3.11+ and jq. It registers the closedloop-ai marketplace and installs code, code-review, platform and self-learning at user scope under ~/.claude/plugins, with auto-update on. claude /plugin marketplace install closedloop is the interactive path. Codex: codex plugin marketplace add https://github.com/closedloop-ai/claude-plugins then add closedloop-core@closedloop-ai. /code-review:start writes inline GitHub pull-request comments. self-learning writes under .learnings/; org share uses CLAUDE_ORG_ID. bootstrap writes .claude/agents and .closedloop-ai/. The README calls this an engineering preview for trusted environments. Apache-2.0.

**Source checked:** 2026-10-28. [Official source](https://github.com/closedloop-ai/claude-plugins). [Gearlist page](https://gearlist.build/tools/closedloop-claude-plugins/).

### [Skills Manager](https://github.com/yibie/skills-manager)

A native macOS app that discovers, installs and mounts agent skills across Claude Code, Cursor, Codex and dozens of other coding agents.

**For:** People who keep skills in several coding agents on a Mac and want one local library they can mount on demand.

**Access and use:** macOS 14 or later. Download Skills Manager 2.0.0 from GitHub Releases and drag it to Applications. The zip is Developer ID signed and Apple-notarized; SHA-256 8da1f38838119864e593e9e591355dd53b5d407e4a7383aac68f095efdac1ad5. There is no Skills Manager backend. Discover refreshes from skills.sh and caches under ~/.skills-manager/. Installing from Discover downloads the GitHub skill package into the Library and links it into agents. Try sends the skill to your own Claude, OpenAI, OpenRouter, Ollama or LM Studio endpoint. Local Ollama and LM Studio endpoints are rewritten to 127.0.0.1. The TUI is npm exec skills-manager from tui/. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/yibie/skills-manager). [Gearlist page](https://gearlist.build/tools/skills-manager/).

### [Screenwriting Skills](https://github.com/jtydhr88/screenwriting-skills)

Twenty-six agent skills for screenwriting, television writing and dramaturgy, following the agentskills.io format for Claude Code and Codex.

**For:** Writers and agents drafting features, series or stage work who want craft checklists beside the script.

**Access and use:** Claude Code: /plugin marketplace add jtydhr88/screenwriting-skills then /plugin install screenwriting@screenwriting-skills. Skills run as /screenwriting:<skill>. Codex: codex plugin marketplace add jtydhr88/screenwriting-skills then install Screenwriting Skills from Plugins. Manual copy writes plugins/screenwriting/skills/* into ~/.claude/skills/ or ~/.agents/skills/ (or the project .claude/skills / .agents/skills). Skill bodies are Chinese; the agent answers in the language you asked. sw-workflow keeps project state in story-bible.md. MIT covers the skill architecture; quotations from the listed books and scripts stay with their rights holders (NOTICE).

**Source checked:** 2026-10-28. [Official source](https://github.com/jtydhr88/screenwriting-skills). [Gearlist page](https://gearlist.build/tools/screenwriting-skills/).

### [Cookiy User Research](https://github.com/cookiy-ai/user-research-skill)

An MIT agent skill that plans user research, synthesises interview transcripts, and can run interviews and surveys through Cookiy AI.

**For:** Product and research people who want an agent to plan studies or launch them on Cookiy.

**Access and use:** Claude Code: /plugin marketplace add cookiy-ai/user-research-skill then /plugin install user-research@cookiy-ai then /reload-plugins. Invoke /user-research-cookiy. Cowork and Claude Desktop need network egress; allow s-api.cookiy.ai. Other agents: npx cookiy-ai or npm install -g @cookiyai/cookiy-cli (Node.js 18+). Planning and local transcript synthesis run in the agent. Running interviews or surveys needs a Cookiy login: the CLI prints a login URL, the human pastes an access token into cookiy save-token. On Cookiy, recruiting, synthetic interviews, report generation and discussion guide generation cost money from a wallet that charges your saved card when the balance is short; run cookiy user info for limits. MIT for the skill.

**Source checked:** 2026-10-28. [Official source](https://github.com/cookiy-ai/user-research-skill). [Gearlist page](https://gearlist.build/tools/cookiy-user-research/).

### [Shader Skills](https://github.com/gokayfem/shader-skills)

An agent skill plus a 186-function GLSL library, bundler and checker for Shadertoy and WebGL2 procedural shaders.

**For:** People writing SDF raymarching, terrain, water, clouds or generative GLSL with a coding agent.

**Access and use:** Claude Code: claude plugin marketplace add gokayfem/shader-skills then claude plugin install shader-skills@shader-skills. Other agents: npx skills add gokayfem/shader-skills (Node.js 22.20 or later; -g for a global install). Manual copy writes skills/shader-art-coding into ~/.claude/skills/ or ~/.agents/skills/. Python 3 glsl_tools.py search, bundle and check use the standard library; check compiles when glslangValidator is installed. Local harness: python3 tests/build_harness.py && python3 tests/serve.py then http://127.0.0.1:8765/build/harness.html. Targets Shadertoy, WebGL2 and GLSL ES 3.00. MIT.

**Source checked:** 2026-10-28. [Official source](https://github.com/gokayfem/shader-skills). [Gearlist page](https://gearlist.build/tools/shader-skills/).

### [SEO Machine](https://github.com/TheCraigHewitt/seomachine)

A Claude Code workspace of slash commands, agents and 26 marketing skills for researching, writing and optimising long-form blog posts.

**For:** People drafting SEO articles in Claude Code who will fill in brand, keyword and competitor context files.

**Access and use:** git clone https://github.com/TheCraigHewitt/seomachine.git && cd seomachine && pip install -r data_sources/requirements.txt then claude. Needs Claude Code (Claude Pro, Max, Team, Enterprise, or Anthropic Console API billing) and a DataForSEO account. Optional Google Analytics 4 and Search Console credentials. Keyword and SERP calls go to DataForSEO. Fill context/brand-voice.md and the other context templates before writing. Docker: docker-compose build && docker-compose run seomachine bash. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/TheCraigHewitt/seomachine). [Gearlist page](https://gearlist.build/tools/seo-machine/).

### [Legal Templates](https://github.com/General-Legal/legal-templates)

CC0 attorney-drafted startup templates in LLM-oriented markdown and original Word files, covering NDAs, DPAs, privacy policies, MSAs and related forms.

**For:** Founders and agents who need a starting draft of common technology-company contracts.

**Access and use:** git clone https://github.com/General-Legal/legal-templates.git and open the markdown under templates/ or the files in docx-originals/. Fill the marked fields before you use a document. General Legal says the templates are for general reference only, are not legal advice, and that it does not review your changes. The templates are CC0 1.0; the authors ask you to keep the General Legal footnote. CC0-1.0.

**Source checked:** 2026-10-29. [Official source](https://github.com/General-Legal/legal-templates). [Gearlist page](https://gearlist.build/tools/legal-templates/).

### [page-mascot](https://koboyo.com/page-mascot)

An MIT React mascot that tracks the pointer, with a skill that draws the two sprite sheets and drops the component on a page.

**For:** People who want a small character on a site, or an agent that can draw one from a prompt.

**Access and use:** npm i page-mascot. Put two sprite sheets on the page and pass them as directions and reactions. Skill: npx skills add nilbuild/page-mascot --skill page-mascot --global --yes, then /page-mascot. Drawing a new character needs an image tool; Claude Code uses OPENAI_API_KEY for the OpenAI images API, and a photo you attach is sent there. MIT.

**Source checked:** 2026-10-29. [Official source](https://github.com/nilbuild/page-mascot). [Gearlist page](https://gearlist.build/tools/page-mascot/).

### [fun-isometric](https://github.com/kelvinkn17/skills)

An agent skill and canvas kit for drawing animated isometric stickers, with a React component and video export.

**For:** Designers and developers who want animated icons they can adapt to a project palette.

**Access and use:** Install with npx skills add kelvinkn17/skills@fun-isometric, then start a new agent session. Needs Node.js 22 or later. Rendering and checks use Bun and Playwright Chromium, which downloads on first use into ~/.cache/fun-isometric. Video export also needs ffmpeg. The output is a canvas icon module or alpha video with a still poster. The skill adds instructions and runnable rendering tools to the agents you select. MIT.

**Source checked:** 2026-10-30. [Official source](https://github.com/kelvinkn17/skills/blob/7c8a7526306e09855c0d4f66130cbaa87422cb8d/README.md). [Gearlist page](https://gearlist.build/tools/fun-isometric/).

### [Awesome AI Apps](https://github.com/Arindam200/awesome-ai-apps)

A collection of 138 runnable LLM apps and agents, from framework starters to multi-agent systems, with tutorials.

**For:** Builders who want working examples of agents, RAG apps and MCP tools.

**Access and use:** Each project brings its own dependencies and model provider keys; review a project before running it.

**Source checked:** 2026-11-03. [Official source](https://github.com/Arindam200/awesome-ai-apps). [Gearlist page](https://gearlist.build/tools/awesome-ai-apps/).

### [Awesome OpenClaw Use Cases](https://github.com/hesamsheikh/awesome-openclaw-usecases)

A community collection of real-life OpenClaw use cases, grouped by area such as social media and productivity.

**For:** OpenClaw users looking for ideas on what to automate.

**Access and use:** The list links to community skills and plugins; its own README warns some may have security vulnerabilities, so review each before installing.

**Source checked:** 2026-11-03. [Official source](https://github.com/hesamsheikh/awesome-openclaw-usecases). [Gearlist page](https://gearlist.build/tools/awesome-openclaw-usecases/).

### [Claude Code Best Practice](https://github.com/shanraisshan/claude-code-best-practice)

A reference repository that maps Claude Code features such as subagents, commands, skills, hooks, MCP, settings and memory to written practice notes and working examples, with a list of 83 tips from the Claude Code team and community.

**For:** Claude Code users who want worked examples of agents, commands, skills and hooks to adapt for their own setup.

**Access and use:** Reading needs nothing beyond a public clone. Running the /weather-orchestrator example needs Claude Code and a Claude account. The clone's .claude/settings.json allows Bash(*), Edit(*), Write(*) and WebFetch for any domain, and its .mcp.json declares Playwright, Context7 and DeepWiki servers run through npx. Review both before opening the folder in Claude Code. The README carries sponsor links. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/shanraisshan/claude-code-best-practice). [Gearlist page](https://gearlist.build/tools/claude-code-best-practice/).

### [awesome-seo](https://github.com/i365dev/awesome-seo)

A curated reading list of SEO guides and tools, with a section on AI search, crawler controls and agent accessibility that points to Google, OpenAI, Anthropic and Cloudflare documentation.

**For:** People who run websites and want sourced starting points for search and AI crawler questions.

**Access and use:** Reading needs nothing. Linked tools and services carry their own accounts and terms. The list says it is not an advertising channel and does not accept unsolicited vendor or self-promotional listings. Maintained by i365, a digital product studio. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/i365dev/awesome-seo). [Gearlist page](https://gearlist.build/tools/awesome-seo/).

### [Claude Code Training](https://github.com/kousen/claude-code-training)

Ken Kousen's Claude Code course: a Slidev deck, progressive hands-on labs, an instructor guide, copyable skills and hook examples, and sample projects in Python, TypeScript and Java.

**For:** Developers and trainers learning or teaching Claude Code workflows.

**Access and use:** Slides are published at https://kousen.github.io/claude-code-training/ with a PDF on GitHub Releases; running the deck locally needs pnpm. The labs need Claude Code signed in with a Claude subscription or an ANTHROPIC_API_KEY, plus Python, JavaScript or TypeScript, and Java toolchains. Docker is optional. The clone's .claude/settings.json runs bun hook scripts on agent events and a status line command, so review it before opening the folder in Claude Code. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/kousen/claude-code-training). [Gearlist page](https://gearlist.build/tools/claude-code-training/).

### [Oz Skills](https://github.com/warpdotdev/oz-skills)

Warp's set of 15 Agent Skills for Warp agents and Oz, covering CI fixes, pull requests, docs updates, GitHub issue triage, MCP server building, Terraform style, web accessibility and performance audits, Playwright testing and BigQuery analysis.

**For:** Warp users, or anyone running agents that read SKILL.md folders, who want ready-made engineering skills.

**Access and use:** Copy a skill folder from .agents/skills/ into a project's .agents/skills/ or into ~/.agents/skills/. Skills act through tools you already have: the gh CLI for pull requests and CI fixes, BigQuery and dbt for the data skills, Chrome DevTools MCP for performance audits and Playwright for web app tests. The ci-fix skill pushes to a fix branch. Most skills are MIT; mcp-builder and webapp-testing carry their own Apache-2.0 LICENSE.txt.

**Source checked:** 2026-11-03. [Official source](https://github.com/warpdotdev/oz-skills). [Gearlist page](https://gearlist.build/tools/oz-skills/).

### [Cloudflare Skills](https://github.com/cloudflare/skills)

Cloudflare's 22 Agent Skills for building on Workers, Durable Objects, the Agents SDK, Wrangler, Sandbox, Cloudflare One and the rest of its developer platform.

**For:** Developers whose coding agents build, deploy or debug apps on Cloudflare.

**Access and use:** Claude Code: /plugin marketplace add cloudflare/skills, then /plugin install cloudflare@cloudflare. Codex, VS Code and Cursor installs are in the README, and npx skills add https://github.com/cloudflare/skills installs the skills on their own. The plugin also adds Cloudflare's main MCP server, https://mcp.cloudflare.com/mcp, which signs in with OAuth or an API token and can change account settings, so grant it the smallest permissions. The turnstile-spin skill ships shell scripts that use CLOUDFLARE_API_TOKEN to create Turnstile widgets. Cloudflare usage follows your account's plan. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/cloudflare/skills). [Gearlist page](https://gearlist.build/tools/cloudflare-skills/).

### [Gemini API skills](https://github.com/google-gemini/gemini-skills)

Four Agent Skills from Google's Gemini team for writing Gemini API code, calling the API from the shell, building Live API streaming apps and generating video with Gemini Omni Flash.

**For:** Developers whose coding agents write apps on the Gemini API.

**Access and use:** npx skills add google-gemini/gemini-skills --skill gemini-api-dev installs one skill. Claude Code: /plugin marketplace add google-gemini/gemini-skills, then /plugin install gemini-skills@gemini-skills. Codex and Cursor installs are in the README. In Antigravity the repository installs as the Gemini API plugin, which Google says also adds the Gemini Docs MCP server and API key tools. The gemini-omni-flash-api skill ships Python scripts that use GEMINI_API_KEY to upload files and generate video, which uses that key's quota and billing. The README says it is not an officially supported Google product. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/google-gemini/gemini-skills). [Gearlist page](https://gearlist.build/tools/gemini-skills/).

### [Google Agent Skills](https://github.com/google/skills)

Google's Agent Skills for its developer products, mostly Google Cloud (GKE, BigQuery, Cloud Storage, Agent Platform, Gemini on Cloud and the gcloud CLI), plus Google Ads, Analytics, sign-in and documentation lookup.

**For:** Developers and platform engineers whose coding agents build on or run Google Cloud.

**Access and use:** npx skills add google/skills asks which skills to install and where. Claude Code: claude plugin marketplace add google/skills, then install a plugin such as google-cloud-developer@google-plugins. The plugins bundle skills with MCP servers; google-cloud-developer adds Google's Developer Knowledge MCP server with a key from DEVELOPERKNOWLEDGE_API_KEY. Skills that run the gcloud CLI act as whatever account gcloud is signed in to, and Google Cloud bills the project they use. 192 SKILL.md files on 7 November 2026. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/google/skills). [Gearlist page](https://gearlist.build/tools/google-skills/).

### [Google Maps Platform agent skills](https://github.com/googlemaps/agent-skills)

Google Maps Platform's Agent Skills for writing map, places, routes, geocoding and environment features across web, Android, iOS and web service APIs, plus a Navigation SDK migration skill.

**For:** Developers whose coding agents add Google Maps features to an app.

**Access and use:** npx skills add googlemaps/agent-skills. Installing it as a Gemini CLI extension also adds the Maps Code Assist MCP server, https://mapscodeassist.googleapis.com/mcp. The main skill tells the agent to fetch a skills index and sub-skills from www.gstatic.com on each request, with a client parameter naming the agent, and to send documentation questions to Google's Code Assist service. It also asks for a Google usage attribution ID, gmp_git_agentskills_v1, in the code it writes. For prototyping it points to the Maps Demo Key, which needs no billing account; production keys bill to a Google Cloud project. The README says it is not an officially supported Google product. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/googlemaps/agent-skills). [Gearlist page](https://gearlist.build/tools/google-maps-agent-skills/).

### [Microsoft Graph Developer Skills](https://github.com/microsoftgraph/dev-skills)

A GitHub Copilot CLI plugin from Microsoft Graph with five skills that find the Graph endpoints and least-privilege permissions for a use case, generate a small API client with Kiota or AI, and write the app code.

**For:** Developers building or slimming down C#, Python or TypeScript apps that call Microsoft Graph.

**Access and use:** Built for GitHub Copilot CLI: start a session and run /plugin install with the path to a clone. Needs a Copilot plan, a Microsoft Entra tenant where you can create or use an app registration, and the .NET SDK with Kiota for the default workflow. The skills work from Microsoft's docs and the public Graph OpenAPI file. Apps they generate can ask for access to organisational Microsoft 365 data, so check each permission before you grant it. Last commit 4 August 2026. The README says MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/microsoftgraph/dev-skills). [Gearlist page](https://gearlist.build/tools/microsoft-graph-dev-skills/).

### [Microsoft Agent Skills](https://github.com/microsoft/skills)

Microsoft's Agent Skills, custom agents and MCP configurations for coding agents that build with Azure SDKs and Microsoft Foundry in Python, .NET, TypeScript, Java and Rust.

**For:** Developers whose coding agents build on Azure services or Microsoft Foundry.

**Access and use:** npx skills add microsoft/skills opens a picker, and the README asks you to install only the skills a project needs. In Copilot CLI, /plugin marketplace add microsoft/skills offers plugins such as azure, which uses the azure and foundry-mcp MCP servers to manage, monitor and deploy Azure resources. Azure usage bills to your subscription. The README calls the repository a work in progress. MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/microsoft/skills). [Gearlist page](https://gearlist.build/tools/microsoft-skills/).

### [Notion Skills](https://github.com/makenotion/skills)

Notion's two Agent Skills: one for its ntn command line tool, which calls the Notion API, deploys workers and uploads files, and one for building Notion Apps such as workflows and database syncs.

**For:** Developers whose agents script Notion or build Notion Apps.

**Access and use:** npx skills add makenotion/skills, or add --skill notion-cli for one skill. The notion-cli skill installs ntn with curl -fsSL https://ntn.dev | bash, so read that script first. ntn uses NOTION_API_TOKEN when it is set, or ntn login in a browser, and can read and write whatever that token reaches. Last commit 22 September 2026. MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/makenotion/skills). [Gearlist page](https://gearlist.build/tools/notion-skills/).

### [Notion plugin for Claude Code](https://github.com/makenotion/claude-code-notion-plugin)

Notion's Claude Code plugin, which installs 12 workspace skills, slash commands and the hosted Notion MCP server together.

**For:** Claude Code users who want to search, plan and write in their Notion workspace from the terminal.

**Access and use:** /plugin marketplace add makenotion/claude-code-notion-plugin, then /plugin install notion-workspace-plugin@notion-plugin-marketplace, then restart Claude Code. It connects to https://mcp.notion.com/mcp and signs in with OAuth, so it can search, read, create and update pages and add database rows anywhere your Notion account can. The skills are mirrored from the Notion Cookbook. Its plugin.json says MIT, but the repository had no licence file on 7 November 2026.

**Source checked:** 2026-11-07. [Official source](https://github.com/makenotion/claude-code-notion-plugin). [Gearlist page](https://gearlist.build/tools/notion-claude-code-plugin/).

### [OpenRouter Skills](https://github.com/OpenRouterTeam/skills)

OpenRouter's 19 Agent Skills for its API, covering model lookup, benchmarks, usage analytics, image, speech, transcription and video generation, OAuth sign-in, its TypeScript SDK and agent scaffolds.

**For:** Developers whose coding agents build on OpenRouter or answer questions about their OpenRouter usage.

**Access and use:** Claude Code: /plugin marketplace add OpenRouterTeam/skills, then /plugin install openrouter@openrouter. Other agents: gh skill install OpenRouterTeam/skills, with GitHub CLI 2.90.0 or later. The scripts read OPENROUTER_API_KEY. The image, speech, transcription and video skills spend credits on that key, and the analytics and generations skills read its spend, usage and stored prompts. install-ori-harness pipes an install script from openrouter.ai into bash. The repository had no licence file on 7 November 2026.

**Source checked:** 2026-11-07. [Official source](https://github.com/OpenRouterTeam/skills). [Gearlist page](https://gearlist.build/tools/openrouter-skills/).

### [NVIDIA Agent Skills](https://github.com/NVIDIA/skills)

NVIDIA's catalogue of Agent Skills for its software, covering Physical AI and robotics, simulation, CUDA-X libraries such as cuDF and cuOpt, NeMo and Nemotron, Jetson, Run:ai and RAG blueprints, copied daily from each product's own repository.

**For:** Developers whose coding agents work with NVIDIA's GPU libraries, robotics, simulation or AI platform tools.

**Access and use:** npx skills add nvidia/skills --skill nvidia-skill-finder --yes installs a finder skill that searches the catalogue and can install other skills itself. 438 SKILL.md files on 7 November 2026. Each skill ships a detached signature you can check against NVIDIA's root certificate. Some skills act on outside services, such as the Run:ai skills through the Run:ai MCP server, and the README warns that the software fetches outside material under separate terms. Apache-2.0 for code and CC-BY-4.0 for skills and docs.

**Source checked:** 2026-11-07. [Official source](https://github.com/NVIDIA/skills). [Gearlist page](https://gearlist.build/tools/nvidia-skills/).

### [motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing)

An agent skill that plans, renders and checks motion graphics films such as launch films and product promos, using measured timing rules and scripted quality gates.

**For:** People who use Claude Code or another agent that reads a SKILL.md folder to make launch films, product promos or kinetic-type videos from HTML.

**Access and use:** Install for Claude Code with git clone https://github.com/Tejashmakwana/motionmaxxing ~/.claude/skills/motionmaxxing, then bash ~/.claude/skills/motionmaxxing/install.sh, which checks requirements and installs nothing system-wide. Other agents can be pointed at the folder and need shell access. Requires Node 22 or newer, Python 3, ffmpeg and Google Chrome. Films render locally from HTML, but the brand step captures the website you give it and the logo script fetches marks from SVGL, Simple Icons or that site. Voice, sound effects and music are optional and go through ElevenLabs, which needs an ELEVENLABS_API_KEY; generated surface plates optionally use the Codex CLI. The author describes it as an early release that has not had a wide test. The bundled GSAP is under the GreenSock Standard License, which is not open source, and other bundled components keep their own licences. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/Tejashmakwana/motionmaxxing/blob/main/README.md). [Gearlist page](https://gearlist.build/tools/motionmaxxing/).

### [Teardown](https://github.com/elvarofficial/teardown)

A Claude Code skill that builds an interactive 3D simulator of a real machine as one offline HTML page and can record its tour to a 60 fps video.

**For:** Claude Code users who want to show how a machine or mechanism works as an interactive 3D model rather than describe it in text.

**Access and use:** Install with npx skills add elvarofficial/teardown -g -a claude-code, then run npm install && npx playwright install chromium once in the installed folder. Requires Node.js 20 or newer; recording video also needs ffmpeg, and the sound needs Python 3. Builds and renders are written to ./teardown-out in the folder you run from, and the finished pages run offline. The runtime, frame capture and sound engine come from whaleyxbt/claude-motion (MIT). MIT.

**Source checked:** 2026-11-07. [Official source](https://github.com/elvarofficial/teardown/blob/main/README.md). [Gearlist page](https://gearlist.build/tools/teardown/).

### [Elephant-Goldfish Model (EGM)](https://github.com/google/elephant-goldfish-model)

A plugin of agent skills from Google in which your coding agent drafts a software design specification with full project context, then fresh subagents that have not seen the conversation review it for missing assumptions and risks.

**For:** Developers using Claude Code, Codex, Antigravity or ChatGPT who want a design reviewed by fresh agents before they implement it.

**Access and use:** Claude Code: claude plugin marketplace add google/elephant-goldfish-model, then claude plugin install egm@egm. Codex CLI: codex plugin marketplace add google/elephant-goldfish-model, then codex plugin add egm@egm. Antigravity CLI: agy plugin install https://github.com/google/elephant-goldfish-model. ChatGPT and Codex desktop install the published plugin listing, and the setup guide covers Claude Cowork, ChatGPT Work, omp and Muse. Install the whole plugin, because installers that copy only the skills folder break it. Brainstorm and review need a host that can start fresh subagents, and the review stops if it cannot; standalone Antigravity IDE is not supported. A recorded Muse run used 15 fresh-context reviewers across one brainstorm and one review. The skills write briefs, drafts and reports into your working directory. The setup guide notes that Codex CLI and Antigravity CLI were reported passing project AGENTS.md or GEMINI.md files into reviewer context. Not an officially supported Google product. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/google/elephant-goldfish-model). [Gearlist page](https://gearlist.build/tools/elephant-goldfish-model/).

## APIs and data

### [ABN Lookup web services](https://abr.business.gov.au/Tools/WebServices)

The Australian Business Register's free API for searching ABNs and business names and validating ABN details.

**For:** Agents and apps that verify or pre-fill Australian business details.

**Access and use:** Free. Requires registering and accepting the web services agreement to receive an authentication GUID by email; keep the GUID out of code and chats. Its JSON service covers ABN, ACN and name searches.

**Source checked:** 2026-11-07. [Official source](https://abr.business.gov.au/Tools/WebServices). [Gearlist page](https://gearlist.build/tools/abn-lookup-web-services/).

### [data.gov.au API](https://data.gov.au/data/api/3/action/status_show)

The CKAN API behind data.gov.au, for searching and downloading Australian government datasets, including ASIC's business names dataset.

**For:** Agents and analysts working with Australian public data.

**Access and use:** No key needed to search and read public datasets. Each dataset carries its own licence; check it before reuse.

**Source checked:** 2026-11-03. [Official source](https://data.gov.au/data/dataset/asic-business-names). [Gearlist page](https://gearlist.build/tools/data-gov-au-api/).

### [ABS Data API](https://www.abs.gov.au/about/data-services/application-programming-interfaces-apis/data-api-user-guide)

The Australian Bureau of Statistics API for population, economic and industry statistics in SDMX formats.

**For:** Agents and apps that need Australian statistics by region or industry.

**Access and use:** Free and open without an API key since 29 November 2024; responses are SDMX, so set the Accept header for JSON or CSV.

**Source checked:** 2026-11-03. [Official source](https://www.abs.gov.au/about/data-services/application-programming-interfaces-apis/data-api-user-guide). [Gearlist page](https://gearlist.build/tools/abs-data-api/).

### [Domain API](https://developer.domain.com.au/)

Domain Group's API packages for Australian property data: address suggestions, agents and listings, listing management, price and rental estimates, auction results, suburb statistics and schools.

**For:** Agencies, property apps, brokers and fintechs building on Australian real estate data.

**Access and use:** Sign up with a corporate email, build in the sandbox, then go live per package. Pricing and limits depend on the package, so check the plan before building. Listing Management can create and update live listings.

**Source checked:** 2026-11-03. [Official source](https://developer.domain.com.au/). [Gearlist page](https://gearlist.build/tools/domain-api/).

### [NSW bulk property sales information](https://www.valuergeneral.nsw.gov.au/design/bulk_psi_content/bulk_psi)

The NSW Valuer General's free download of property sales records from 1990 onwards, updated weekly by local government area.

**For:** Analysts and agents who need NSW sales history.

**Access and use:** Free download in .DAT files. Licensed under Creative Commons BY-NC-ND 4.0, which rules out commercial use and modified versions without permission.

**Source checked:** 2026-11-03. [Official source](https://www.valuergeneral.nsw.gov.au/design/bulk_psi_content/bulk_psi). [Gearlist page](https://gearlist.build/tools/nsw-property-sales-information/).

### [Companies House public data API](https://developer.company-information.service.gov.uk/)

The UK Companies House REST API for searching the register and reading company profiles, filing history, officers and charges.

**For:** Agents and apps that check or pre-fill UK company details.

**Access and use:** Free. Needs a Companies House account and an API key sent by HTTP Basic auth; keep the key out of code and chats. Up to 600 requests in 5 minutes. Officer and PSC records are about people.

**Source checked:** 2026-11-07. [Official source](https://developer-specs.company-information.service.gov.uk/guides/rateLimiting). [Gearlist page](https://gearlist.build/tools/companies-house-api/).

### [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)

The US SEC's JSON APIs on data.sec.gov for each filer's submission history and XBRL financial data.

**For:** Agents and analysts researching US public companies and their filings.

**Access and use:** No key. The SEC asks automated requests to declare a name and contact email in the User-Agent header and to stay under 10 requests a second. Covers SEC filers, mostly public companies.

**Source checked:** 2026-11-07. [Official source](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data). [Gearlist page](https://gearlist.build/tools/sec-edgar-apis/).

### [NZBN API](https://portal.api.business.govt.nz/api/nzbn)

MBIE's API for searching the New Zealand Business Number Register and reading business details, including companies from the Companies Office registers.

**For:** Agents and apps that check or pre-fill New Zealand business details.

**Access and use:** No fee. Needs a signed MBIE API Access Agreement, an approved subscription and a subscription key sent in a header. Passed-on data must carry the search time and "Data sourced from the [Register name]".

**Source checked:** 2026-11-07. [Official source](https://portal.api.business.govt.nz/api/nzbn). [Gearlist page](https://gearlist.build/tools/nzbn-api/).

### [Public APIs](https://github.com/public-apis/public-apis)

A large community list of free APIs grouped by topic, most marked with their auth type, HTTPS and CORS support.

**For:** Builders looking for a free API for a specific job.

**Access and use:** A list only; each API has its own terms, keys and limits, so check the provider before relying on one. MIT.

**Source checked:** 2026-11-03. [Official source](https://github.com/public-apis/public-apis). [Gearlist page](https://gearlist.build/tools/public-apis/).

### [Cloudflare API](https://developers.cloudflare.com/fundamentals/api/get-started/)

Cloudflare's API for managing accounts, DNS, zones, Workers and the rest of its products.

**For:** Agents and scripts that deploy or manage sites and Workers on Cloudflare.

**Access and use:** Use a permission-scoped API token rather than the legacy global key, and give it only the zones and products the job needs. The published limit is 1,200 requests per five minutes per user or account token, and 200 per second per IP, with extra limits on some endpoints. Free plans exist, but metered products bill separately. Permission to manage an account is not permission to share its customers' data.

**Source checked:** 2026-11-04. [Official source](https://developers.cloudflare.com/fundamentals/api/reference/limits/). [Gearlist page](https://gearlist.build/tools/cloudflare-api/).

### [Claude API](https://platform.claude.com/docs/en/api/overview)

Anthropic's API for Claude models, with batches, token counting and managed agents.

**For:** Teams building agents or apps on Claude.

**Access and use:** Authenticate with a Console API key or workload identity federation. Billing is per token, and some Max, Ultra and Team subscriptions include monthly API credits that have to be claimed. Rate limits depend on the organisation's usage tier and the model class. Commercial API inputs and outputs aren't used for training by default, with opt-in and feedback exceptions.

**Source checked:** 2026-11-04. [Official source](https://platform.claude.com/docs/en/api/rate-limits). [Gearlist page](https://gearlist.build/tools/claude-api/).

### [OpenAI API](https://developers.openai.com/api/reference/overview)

OpenAI's API for model inference, realtime audio, images, tools and organisation administration.

**For:** Teams building agents or apps on OpenAI models.

**Access and use:** Authenticate with an API key or a short-lived workload identity token; admin keys cover a separate administrative surface. Billing is per use, and API billing is separate from a ChatGPT plan. Limits are set per organisation and project and vary by model. API data isn't used for training by default, but abuse-monitoring logs can be kept for up to 30 days unless approved retention controls apply.

**Source checked:** 2026-11-04. [Official source](https://developers.openai.com/api/docs/guides/your-data). [Gearlist page](https://gearlist.build/tools/openai-api/).

### [Gemini Developer API](https://aistudio.google.com/docs/api-key)

Google's API for Gemini models, with grounding, multimodal input and tool use.

**For:** Teams building agents or apps on Gemini models.

**Access and use:** Keys belong to a Google Cloud project, and limits (requests per minute, tokens per minute and requests per day) apply per project, with daily limits resetting on Pacific time. There is an unpaid tier for eligible models. Under the unpaid terms, Google may use what you send to improve its products and people may review it, so don't send confidential or client data on that tier. Paid use has different terms. In the European Economic Area, Switzerland and the UK, the paid data terms apply to unpaid use too. These terms took effect on 23 March 2026.

**Source checked:** 2026-11-07. [Official source](https://aistudio.google.com/docs/terms). [Gearlist page](https://gearlist.build/tools/gemini-api/).

### [Google Search Console API](https://developers.google.com/webmaster-tools)

Google's API for search performance data, verified sites and sitemaps, with URL inspection as a separate service.

**For:** Agents and dashboards that report on a site's Google search traffic.

**Access and use:** Private site data needs OAuth from a user with access to that property; request the read-only scope when you only read. Search Analytics allows 1,200 queries per minute per site and user, and URL inspection allows 2,000 a day per site. The data belongs to the property, so access follows whoever the owner has granted.

**Source checked:** 2026-11-04. [Official source](https://developers.google.com/webmaster-tools/limits). [Gearlist page](https://gearlist.build/tools/search-console-api/).

### [Google Places API](https://developers.google.com/maps/documentation/places/web-service/get-api-key)

Google's API for searching places and reading business and location details.

**For:** Agents and apps that look up local businesses, addresses or opening hours.

**Access and use:** For production, needs a Google Cloud project with billing and a restricted API key. For prototyping, the Maps Demo Key needs no billing account or credit card; it has a daily limit per API and covers a set list of APIs, including Text Search, Nearby Search and Autocomplete. Pricing is per SKU, and the fields you request can move a call to a dearer SKU, so ask only for the fields you need. Storing or caching results is restricted, except place IDs, and results come with display and attribution rules.

**Source checked:** 2026-11-07. [Official source](https://developers.google.com/maps/documentation/places/web-service/policies). [Gearlist page](https://gearlist.build/tools/google-places-api/).

### [Microsoft Graph](https://learn.microsoft.com/en-us/graph/auth/auth-concepts)

Microsoft's API for Microsoft 365 and identity data, including mail, files, calendars and users.

**For:** Agents that work inside a business's Microsoft 365 tenant.

**Access and use:** Uses Microsoft identity platform tokens with delegated or application permissions, and some permissions need an admin to consent for the tenant. Many calls come with the user's licence, but some APIs are metered. Throttling varies by service, so honour 429 responses and their Retry-After header. A token reaches only the tenant and data its permissions allow.

**Source checked:** 2026-11-04. [Official source](https://learn.microsoft.com/en-us/graph/throttling). [Gearlist page](https://gearlist.build/tools/microsoft-graph/).

### [OpenRouter](https://openrouter.ai/docs/api_reference/authentication)

One API for many model providers, with routing between them.

**For:** Teams that want to try or switch between models from several providers through one key.

**Access and use:** Authenticate with an API key, or use the documented OAuth flow for users. Some models have free variants, limited to 20 requests a minute with a daily ceiling that depends on credits bought; paid models use credits. Each provider has its own data policy. OpenRouter offers privacy settings and zero-retention routing, but legal and safety exceptions still apply.

**Source checked:** 2026-11-07. [Official source](https://openrouter.ai/docs/api_reference/limits). [Gearlist page](https://gearlist.build/tools/openrouter/).

### [DataForSEO](https://docs.dataforseo.com/v3/auth/)

APIs for search results, keywords, backlinks, market data and AI visibility, priced per call.

**For:** Agents and SEO tools that need search and keyword data on demand.

**Access and use:** Uses HTTP Basic authentication with your API login and a generated API password, which differs from the dashboard password. Pay as you go, with trial credit for new accounts and a sandbox of sample responses. The default limit rose to 10,000 requests a minute, though some endpoints have their own limits. Label which data is measured and which is modelled, and check the terms before passing data on.

**Source checked:** 2026-11-04. [Official source](https://dataforseo.com/update/api-rate-limit-10000-requests-per-minute). [Gearlist page](https://gearlist.build/tools/dataforseo/).

### [Stripe API](https://docs.stripe.com/api/authentication)

Stripe's API for payments, subscriptions, invoices and the events behind them.

**For:** Agents and apps that read or manage billing.

**Access and use:** Use a restricted API key with only the permissions the job needs, and test in a sandbox before using live keys. A restricted key for an autonomous agent can be tagged as an agent key; agent-tagged keys need a designated reviewer to approve sensitive actions, and from December 2026 Stripe's MCP server stops accepting full-access secret keys and restricted keys without the Agent tag. The published limits are 100 requests a second in live mode and 25 in a sandbox, with a 25-a-second limit on most endpoints and further exceptions. Read requests must also average no more than 500 per transaction over a rolling 30 days, with a minimum allowance of 10,000 a month. A key that can read invoices shouldn't be able to refund or pay out, so scope it accordingly.

**Source checked:** 2026-11-07. [Official source](https://docs.stripe.com/rate-limits). [Gearlist page](https://gearlist.build/tools/stripe-api/).

### [Resend API](https://resend.com/docs/api-reference/introduction)

An email API for transactional and marketing email, with inbound handling.

**For:** Agents and apps that send email from a verified domain.

**Access and use:** Authenticate with an API key that can be limited by permission and domain. The free plan covers 3,000 emails a month, up to 100 a day. The default API limit is 10 requests a second per team, separate from sending quotas. Recipients' details and email content are customer data, and API access doesn't give consent to email anyone.

**Source checked:** 2026-11-04. [Official source](https://resend.com/docs/api-reference/rate-limit). [Gearlist page](https://gearlist.build/tools/resend-api/).

### [Notion API](https://developers.notion.com/guides/authorization/overview)

Notion's API for pages, databases, comments and files in a workspace.

**For:** Agents that read or update a team's Notion workspace.

**Access and use:** Connect with an internal connection token, a personal access token or OAuth; each reaches only the pages shared with it. A personal token acts as its user. Limits are 600 requests a minute per connection on Business and Enterprise plans and 180 on other plans, plus workspace limits, so honour Retry-After. Querying a data source has its own limit of about 3 requests a second per connection.

**Source checked:** 2026-11-07. [Official source](https://developers.notion.com/reference/request-limits). [Gearlist page](https://gearlist.build/tools/notion-api/).

### [HeyGen API](https://developers.heygen.com/docs/quick-start)

HeyGen's API for avatar video, images, voice and translation.

**For:** Teams producing video with AI avatars or translated voice.

**Access and use:** The API uses an API key with scopes and bills against an API plan. The MCP server and CLI sign in as your web account and use its subscription credits instead, so a web plan isn't API credit. Limits vary by endpoint and plan. Using a person's likeness or voice needs their consent.

**Source checked:** 2026-11-04. [Official source](https://developers.heygen.com/docs/api-key). [Gearlist page](https://gearlist.build/tools/heygen-api/).

### [NVIDIA NIM API catalog](https://docs.api.nvidia.com/nim/docs/api-quickstart)

Hosted model endpoints from NVIDIA for prototyping, with some models also available to run yourself.

**For:** Developers trying open models before choosing where to run them.

**Access and use:** Needs an NVIDIA developer account and API key. Developer Program access is for prototyping, research, development and testing only; production, which NVIDIA defines to include anything serving real end users, needs an NVIDIA AI Enterprise licence. The API trial terms bar confidential information and, unless a service allows it, personal data, and say NVIDIA sets use limits; the docs give no rate limit figure. The model list at https://integrate.api.nvidia.com/v1/models answers without a key, and a retired model's id returns HTTP 410 with its end-of-life date. Each model's licence and terms apply separately.

**Source checked:** 2026-11-07. [Official source](https://docs.api.nvidia.com/nim/docs/product). [Gearlist page](https://gearlist.build/tools/nvidia-nim-api/).

### [GitHub REST API](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api)

GitHub's API for repositories, issues, pull requests, releases and users.

**For:** Agents that read or manage code and project work on GitHub.

**Access and use:** Use a fine-grained personal access token, a GitHub App or OAuth; workflows get a built-in token. Unauthenticated calls to public endpoints allow 60 an hour, and an authenticated user gets 5,000 an hour, with separate limits for search and apps. A public repository still has its own licence, so check it before reusing code.

**Source checked:** 2026-11-04. [Official source](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api). [Gearlist page](https://gearlist.build/tools/github-rest-api/).

### [Supabase APIs](https://supabase.com/docs/reference/api/introduction)

The Supabase Management API for projects, alongside each project's own database, auth and storage APIs.

**For:** Agents that set up or manage Supabase projects.

**Access and use:** The Management API uses a scoped personal access token or OAuth. Each project's data APIs use their own keys and row-level security, which is a separate layer. The free plan covers two active projects, and inactive ones pause. Never expose a management or service key in a client app.

**Source checked:** 2026-11-04. [Official source](https://supabase.com/pricing). [Gearlist page](https://gearlist.build/tools/supabase-api/).

### [YouTube Analytics API](https://developers.google.com/youtube/analytics)

Google's official API for targeted queries on a channel's own analytics, such as views, ratings, audience age, gender and country, and estimated revenue.

**For:** Channel owners, agencies and the agents they authorise to report on a channel's performance.

**Access and use:** Needs OAuth consent from the channel or content owner, so it cannot read another creator's private analytics unless they grant access. The yt-analytics.readonly scope covers activity metrics, revenue needs the separate yt-analytics-monetary.readonly scope, and Google sets a quota cost for each query. The YouTube API Services Terms and Developer Policies apply, including limits on storing data and on combining data from different content owners.

**Source checked:** 2026-11-05. [Official source](https://developers.google.com/youtube/analytics/reference/reports/query). [Gearlist page](https://gearlist.build/tools/youtube-analytics-api/).

### [YouTube Reporting API](https://developers.google.com/youtube/reporting)

Google's official API for scheduled bulk reports of a channel's or content owner's analytics, delivered as daily CSV files.

**For:** Analysts who want a channel's full daily history in their own database.

**Access and use:** Needs OAuth consent from the channel or content owner, with the same read-only and monetary scopes as the Analytics API. A new reporting job backfills 30 days, the first files can take 48 hours, and reports stay downloadable for 60 days, or 30 days for backfilled history. The YouTube API Services Terms and Developer Policies limit how long stored data can be kept without a refresh.

**Source checked:** 2026-11-05. [Official source](https://developers.google.com/youtube/reporting/v1/reports). [Gearlist page](https://gearlist.build/tools/youtube-reporting-api/).

### [Supadata](https://supadata.ai/)

An API and MCP server for transcripts and metadata from YouTube and other video platforms, with AI-generated transcripts billed by the minute.

**For:** Developers who want transcripts through a paid API instead of running their own scraper.

**Access and use:** Needs a Supadata account and API key, or OAuth sign-in for the hosted MCP server at api.supadata.ai/mcp; the local server reads SUPADATA_API_KEY. The free plan gives 100 credits a month at one request a second, a transcript costs 1 credit, and a generated transcript costs 2 credits a minute. The MCP server code is MIT licensed.

**Source checked:** 2026-11-05. [Official source](https://docs.supadata.ai/integrations/mcp). [Gearlist page](https://gearlist.build/tools/supadata/).

### [SponsorBlock API](https://wiki.sponsor.ajay.app/w/API_Docs)

The public API and database behind SponsorBlock, with crowdsourced timestamps for sponsor reads, self-promotion, intros and other segments in YouTube videos.

**For:** Analysts measuring how often and how long channels run sponsor segments.

**Access and use:** Reading segments needs no account or key, and the full database can be downloaded. The API and database are under CC BY-NC-SA 4.0 unless the maintainer gives permission, so commercial use needs that permission and reuse needs attribution. Automated submissions are not allowed, and segments are community votes rather than verified facts.

**Source checked:** 2026-11-05. [Official source](https://wiki.sponsor.ajay.app/w/API_Docs). [Gearlist page](https://gearlist.build/tools/sponsorblock-api/).

### [Return YouTube Dislike API](https://returnyoutubedislike.com/docs)

A public API that returns like counts and estimated dislike counts for YouTube videos, built from archived dislike data and estimates extrapolated from its extension's users.

**For:** Analysts who want a rough measure of negative reaction to a video.

**Access and use:** No account or key is needed, and each client is limited to 100 requests a minute and 10,000 a day. Third-party use must credit the project with a link to its repository or returnyoutubedislike.com. Dislike figures for the period since YouTube hid them are estimates, so label them as such.

**Source checked:** 2026-11-05. [Official source](https://returnyoutubedislike.com/docs/usage-rights). [Gearlist page](https://gearlist.build/tools/return-youtube-dislike-api/).

### [SerpApi YouTube Search API](https://serpapi.com/youtube-search-api)

A paid API that returns YouTube search results as JSON, including videos, channels, Shorts, view counts and subscriber counts.

**For:** Agents that need to see what ranks in YouTube search for a keyword.

**Access and use:** Needs a SerpApi account and private API key; the free plan covers 250 searches a month at 50 an hour, and the Starter plan is US$25 a month for 1,000. Cached searches are free, and an output option returns Markdown for agents. SerpApi's U.S. Legal Shield, its cover for scraping and parsing search data, starts on the Production plan.

**Source checked:** 2026-11-05. [Official source](https://serpapi.com/pricing.md). [Gearlist page](https://gearlist.build/tools/serpapi-youtube-search/).

### [NoxInfluencer API](https://www.noxinfluencer.com/api-service)

NoxInfluencer's API for YouTube, TikTok and Instagram creator profiles, videos, comments, search and contact details.

**For:** Agencies building creator search or vetting into their own tools.

**Access and use:** A free trial gives 80 one-time credits, and ongoing access uses a Nox Key set up through an account manager with quoted pricing; each key is limited to 60 requests a minute. The site's terms forbid crawling NoxInfluencer data, so use the API rather than automating the web app. Contact details it returns are personal information.

**Source checked:** 2026-11-05. [Official source](https://www.noxinfluencer.com/api-docs/docs/rest/api). [Gearlist page](https://gearlist.build/tools/noxinfluencer-api/).

### [Modash API](https://www.modash.io/influencer-marketing-api)

Modash's Discovery and Raw APIs for searching and analysing YouTube, Instagram and TikTok creators, with audience demographics, lookalikes, audience overlap and recent posts.

**For:** Platforms and agencies building creator discovery into their own products.

**Access and use:** Needs an access token under a Modash API agreement; each call spends credits, published pricing starts at US$16,200 a year for Discovery and US$10,000 a year for Raw, and trial credits are offered after a call with the team. Modash also offers an MCP server for the same data. The API terms bar standalone resale of raw results and require a lawful basis for processing creator data.

**Source checked:** 2026-11-05. [Official source](https://www.modash.io/influencer-marketing-api). [Gearlist page](https://gearlist.build/tools/modash-api/).

### [Phyllo](https://www.getphyllo.com/)

A social data API that returns creators' public data and, with each creator's sign-in and consent, private data such as audience demographics and income from supported platforms, including YouTube.

**For:** Agencies and creator platforms that need data a creator has agreed to share.

**Access and use:** Sign up for a free sandbox, then talk to sales for production access and pricing. Consented data needs each creator to connect their account through Phyllo and approve the fields shared. Its developer documentation is published under the InsightIQ name at docs.insightiq.ai.

**Source checked:** 2026-11-05. [Official source](https://www.getphyllo.com/). [Gearlist page](https://gearlist.build/tools/phyllo/).

### [ChannelCrawler](https://channelcrawler.com/api)

A YouTube channel database whose API searches over 35 million channels by niche, location, size and engagement and returns video lists and subscriber history, with sponsorship tracking in the web app.

**For:** Brands and agencies finding channels to sponsor and checking which creators competitors sponsor.

**Access and use:** The API uses a bearer key and prepaid credits, from 100 credits for US$24, charged per result, with free search previews and email lookups billed only when an email is found. Sponsorship tracking is part of the web app's Power and Enterprise plans, not the API. Business emails it returns are personal information, so outreach must follow spam and privacy law.

**Source checked:** 2026-11-05. [Official source](https://channelcrawler.com/api). [Gearlist page](https://gearlist.build/tools/channelcrawler/).

### [Apify YouTube Scraper](https://apify.com/streamers/youtube-scraper)

An Apify actor that collects public YouTube video and channel data, such as titles, views, likes, subscriber counts and upload dates, with optional subtitles.

**For:** Analysts who need bulk YouTube data without writing a scraper.

**Access and use:** Needs an Apify account and API token; it bills per video, about US$2.40 to US$4 per 1,000 depending on plan, and results are stored in your Apify datasets. The free plan's US$5 monthly credit covers a small run. It scrapes YouTube outside the official API, which YouTube's Terms of Service bar without permission, and Apify says not to collect personal data without a legitimate reason.

**Source checked:** 2026-11-05. [Official source](https://apify.com/streamers/youtube-scraper). [Gearlist page](https://gearlist.build/tools/apify-youtube-scraper/).

### [NVIDIA Auto Ontology](https://github.com/NVIDIA/auto-ontology)

An open library from NVIDIA that builds an ontology from database metadata and serves it to agents through MCP, CLI and API, so they answer data questions with SQL that is checked against the database.

**For:** Data and platform teams who want agents to answer analytics questions over SQL sources such as PostgreSQL, Snowflake and Databricks using shared, certified definitions.

**Access and use:** Runs as a self-hosted stack: clone the repo, copy .env.example to .env, then docker compose up -d --build; a Helm chart covers Kubernetes. Requires Docker with Compose v2, uv and an NVIDIA API key (nvapi-...) from build.nvidia.com, or any OpenAI-compatible endpoint set per model role. By default the models that build the ontology and write each answer's SQL run on NVIDIA's hosted API catalog (integrate.api.nvidia.com); point the endpoints at self-hosted NIM to keep inference in house. Connect agents through the MCP query tools with uvx --from "git+https://github.com/NVIDIA/auto-ontology.git#subdirectory=mcp" auto-ontology-mcp; each user signs in, and every call runs with that user's application permissions. Generated SQL runs with the connected database account's rights, so use a dedicated read-only account limited to the tables and views you intend to expose. Compose publishes Postgres, pgAdmin and the web app on the host, so replace every default password first, and keep ports 3001 and 3002 on a private network because the ingestion endpoints have no authentication of their own. Setting KUMO_RFM_API_KEY makes the agent upload connected tables to the hosted KumoRFM service for predictive questions. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://github.com/NVIDIA/auto-ontology/blob/main/README.md). [Gearlist page](https://gearlist.build/tools/nvidia-auto-ontology/).

### [MiniCPM-OCR](https://github.com/OpenBMB/MiniCPM-OCR)

An open-weight OCR model family that parses Chinese and English PDFs and images into Markdown or JSON, with a second model that scores how reliable each recognised region is.

**For:** Teams building document agents or extraction pipelines who want OCR they can run on their own GPU, with a score that flags regions for human review.

**Access and use:** Install the SDK with python -m pip install --upgrade "minicpm-ocr[all]" (Python 3.10 or later) plus the PaddlePaddle GPU packages for layout detection, then serve the recognition model with vLLM, SGLang, llama.cpp, Ollama or FlagOS. The tutorial's vLLM route needs Linux x86_64, an NVIDIA GPU with driver 580 or later and at least 40 GB of disk, and it builds vLLM from source; the Docker image needs Linux x86-64, an NVIDIA GPU, a CUDA 12.9 compatible driver and the NVIDIA Container Toolkit. Deployed locally, document processing and inference stay on your machine, and the tutorial starts vLLM on 127.0.0.1; the first install and model downloads need internet. The free hosted API and online demo run at platform.modelbest.ai, so documents sent there leave your machine. The README suggests telling a coding agent to "Read and execute" a remote SKILL.md that sets up environments and downloads models: read it yourself before handing it over. Apache-2.0, covering code and model weights.

**Source checked:** 2026-11-07. [Official source](https://github.com/OpenBMB/MiniCPM-OCR). [Gearlist page](https://gearlist.build/tools/minicpm-ocr/).

## Hardware

### [AMD Radeon AI PRO R9700](https://www.amd.com/en/products/graphics/workstations/radeon-ai-pro/ai-9000-series/amd-radeon-ai-pro-r9700.html)

A workstation graphics card from AMD with 32 GB of GDDR6 memory on the RDNA 4 architecture, made for local AI inference and development.

**For:** People building a Linux or Windows desktop or home server that runs local models and needs 32 GB of graphics memory on one card.

**Access and use:** For local AI inference and development on a desktop PC or workstation. It has 32 GB of dedicated GDDR6 memory on a 256-bit bus with 640 GB/s peak bandwidth, and ECC memory support on Linux only. AMD lists Windows 10, Windows 11 and Linux x86 64-bit support, and the ROCm 10.1.0 compatibility matrix (dated 26 August 2026) lists the R9700 for Ubuntu 26.04.1, 24.04.5 and 22.04.5, RHEL 10.2 and 9.8, and Windows 11 25H2. It needs a PCIe 5.0 x16 slot and two slots of space, takes a 12V-2x6 power connector and has a total board power of 300 W; AMD recommends at least a 750 W power supply. Cards come from board partners and AMD says configuration varies by partner design: XFX, for example, sells its version as model RX-97XPROAIY and specifies a 1000 W minimum power supply for it. Caveats: it is not a CUDA card, and AMD's HIPIFY documentation says HIP is not a complete replacement for CUDA and cannot translate all code, so confirm your software supports ROCm. AMD says these cards are not designed or validated for data centre use. XFX states a 2 year warranty on its card.

**Source checked:** 2026-11-07. [Official source](https://www.amd.com/en/products/graphics/workstations/radeon-ai-pro/ai-9000-series/amd-radeon-ai-pro-r9700.html). [Gearlist page](https://gearlist.build/tools/amd-radeon-ai-pro-r9700/).

### [Apple Mac mini](https://www.apple.com/mac-mini/)

A small Apple desktop computer with an M6 or M5 Pro chip and up to 64 GB of unified memory, used to run coding agents and local models on macOS.

**For:** People who want a compact, always-on Mac to run coding agents and smaller local models, or several units as a cluster.

**Access and use:** For running coding agents, local models and agent workflows on macOS. The M6 model has a 12-core CPU and 12-core GPU with 16 GB of unified memory as standard, configurable to 24 GB or 32 GB, and 153 GB/s of memory bandwidth (170 GB/s with the larger memory). The M5 Pro model has up to an 18-core CPU and 20-core GPU, 24 GB of unified memory configurable to 48 GB or 64 GB, and 307 GB/s of memory bandwidth. Memory is chosen when you order. Apple's MLX framework is built for machine learning on Apple silicon and installs on macOS with pip install mlx; Apple's page also names Claude Code and Codex for coding, and exo and LM Studio Bionic for running agents across a cluster of Mac mini units, with Thunderbolt 5 on the M5 Pro model (up to 120 Gb/s) as the clustering link. Maximum continuous power is 155 W, and a power cord is in the box. It has 2.5 Gb Ethernet, configurable to 10 Gb, and runs macOS. Apple's US store listed it from $899 (M6) and from $1,699 (M5 Pro) on 7 November 2026. Caveat: the M6 model tops out at 32 GB of unified memory; the M5 Pro goes to 64 GB.

**Source checked:** 2026-11-07. [Official source](https://www.apple.com/mac-mini/specs/). [Gearlist page](https://gearlist.build/tools/apple-mac-mini/).

### [Apple Mac Studio](https://www.apple.com/mac-studio/)

An Apple desktop workstation with an M5 Max or M5 Ultra chip and up to 512 GB of unified memory, used to run large language models locally.

**For:** People who want to run large open-weight models and local agent workflows on one desktop Mac, or across several clustered over Thunderbolt 5.

**Access and use:** For running large language models and agent workflows locally. The M5 Max model has an 18-core CPU and 32-core GPU with 36 GB of unified memory at 460 GB/s; with the 40-core GPU it takes 48 GB, 64 GB or 128 GB at 614 GB/s. The M5 Ultra model has a 30-core CPU and 64-core GPU with 96 GB at 1.2 TB/s, configurable to 256 GB, or to 512 GB with the 36-core CPU and 80-core GPU version. Memory is chosen when you order. Apple's page names LM Studio Bionic for running LLMs locally and exo for clustering machines, and says Thunderbolt 5 (up to 120 Gb/s) handles clustered compute. Apple's MLX framework is built for machine learning on Apple silicon and installs on macOS with pip install mlx. Maximum continuous power is 480 W. It runs macOS. Apple's US store listed it from $2,499 (M5 Max) and from $5,499 (M5 Ultra) on 7 November 2026. Caveat: the 512 GB option is only offered on the top M5 Ultra configuration.

**Source checked:** 2026-11-07. [Official source](https://www.apple.com/mac-studio/specs/). [Gearlist page](https://gearlist.build/tools/apple-mac-studio/).

### [Framework Desktop (AMD Ryzen AI Max+ 395)](https://frame.work/desktop)

A 4.5 litre mini-ITX desktop from Framework with an AMD Ryzen AI Max+ 395, Radeon 8060S graphics and up to 128 GB of soldered LPDDR5x memory, sold for running large AI models on hardware you own.

**For:** People who want a small x86 desktop running Linux or Windows that can hold large quantised open-weight models in memory and run agents locally.

**Access and use:** For running large open-weight models and local agents on an x86 desktop. The Ryzen AI Max+ 395 versions have a 16-core, 32-thread CPU, Radeon 8060S graphics with 40 graphics cores, and 64 GB or 128 GB of soldered, non-upgradeable LPDDR5x-8000 memory on a 256-bit bus. Framework's own table shows DeepSeek V4 Flash at UD-IQ2_XXS quantisation using 90.9 GB on the 128 GB model, and notes that results vary with quantisation, context length and runtime. A newer version with the Ryzen AI Max+ PRO 495 and 192 GB is also sold. AMD's ROCm 10.1.0 matrix lists the Ryzen AI Max+ 395 (Radeon 8060S) for Ubuntu 26.04.1 and 24.04.5 and for Windows 11 25H2. Framework publishes its own list of supported Linux distributions, with Linux kernel 6.11 as the minimum and 6.15 or later recommended. The Max+ 395 is sold as a DIY Edition: you bring your own operating system (Windows 11 is an optional extra) and can bring your own M.2 2280 NVMe drives for its two PCIe 4.0 slots. It has an included 400 W FlexATX power supply, and the processor runs at 120 W sustained and 140 W boost. USB4 and a PCIe x4 slot are offered for clustering several units. Caveat: check that your Linux distribution is on both Framework's supported list and AMD's ROCm matrix before relying on GPU compute. A 1 year limited warranty is included, extendable to 3 years.

**Source checked:** 2026-11-07. [Official source](https://frame.work/products/desktop-diy-amd-aimax300). [Gearlist page](https://gearlist.build/tools/framework-desktop/).

### [NVIDIA DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/)

A small desktop AI computer from NVIDIA built on the GB10 Grace Blackwell superchip, with 128 GB of unified memory for running and fine-tuning large models and agents locally.

**For:** Developers who want a CUDA machine on their desk to run, test and fine-tune models of up to about 200 billion parameters and to host always-on agents.

**Access and use:** For running, testing and fine-tuning large models and always-on agents locally. It has 128 GB of LPDDR5x unified memory at 273 GB/s, a 20-core Arm CPU and a Blackwell GPU, and NVIDIA says it supports models up to 200 billion parameters, or 405 billion with two units. A 64 GB configuration is sold only through participating OEM partners. It ships with NVIDIA DGX OS, which is based on Ubuntu, with CUDA, cuDNN, Docker and the NVIDIA Container Runtime preinstalled; use of the preinstalled CUDA Toolkit is subject to NVIDIA's CUDA Toolkit End User License Agreement. Power comes from the included 240 W external supply (the GB10 chip is rated at 140 W), and NVIDIA warns that a different or lower-rated supply can cause reduced performance, failure to boot or unexpected shutdowns. Networking is 10 GbE, two ConnectX-7 QSFP ports and Wi-Fi 7, and up to four units can be clustered. You can use it with a monitor and keyboard or over the local network with SSH, NVIDIA Sync or remote desktop tools. NVIDIA's US marketplace listed the 4 TB model at $6,950.00, marked out of stock, on 7 November 2026; NVIDIA also sells it through authorised channel and retail partners. Caveats: the processor is ARM64-based; GPU passthrough to virtual machines is not supported; major DGX OS updates come about twice a year for the first two years after initial release, with security patches between releases.

**Source checked:** 2026-11-07. [Official source](https://www.nvidia.com/en-us/products/workstations/dgx-spark/). [Gearlist page](https://gearlist.build/tools/nvidia-dgx-spark/).

### [NVIDIA GeForce RTX 5090](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/)

A desktop graphics card from NVIDIA with 32 GB of GDDR7 memory on the Blackwell architecture, used to run local AI models with CUDA on Windows or Linux PCs.

**For:** People building a Windows or Linux PC or home server who need CUDA software support and 32 GB of graphics memory on one card.

**Access and use:** For local inference and AI development on a desktop PC. It has 32 GB of GDDR7 memory on a 512-bit bus with 1,792 GB/s of bandwidth, 21,760 CUDA cores, fifth-generation Tensor Cores and CUDA compute capability 12.0. NVIDIA's CUDA Toolkit supports Windows 11 and major Linux distributions including Ubuntu, RHEL, SUSE, Debian and Fedora, and NVIDIA names LM Studio and AnythingLLM as tools for running models on RTX PCs. Total graphics power is 575 W. NVIDIA lists 1000 W required system power, based on a PC with a Ryzen 9 9950X, and recommends a PCIe CEM 5.1 compliant power supply. Power comes from one 600 W PCIe Gen 5 cable or four PCIe 8-pin cables with the adapter in the box. The Founders Edition is a 2-slot, 304 mm long PCIe Gen 5 card; partner cards differ, and NVIDIA notes that small form factor readiness varies by manufacturer. NVIDIA's US page showed "Starting at $1999" on 7 November 2026 and points to regional NVIDIA sites for local pricing and partner retailers. Caveat: NVIDIA says power requirements differ by system configuration, so size the power supply for the whole build.

**Source checked:** 2026-11-07. [Official source](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/). [Gearlist page](https://gearlist.build/tools/nvidia-geforce-rtx-5090/).

### [Synology DiskStation DS925+](https://www.synology.com/en-global/products/DS925+)

A four-bay network storage box (NAS) from Synology running DSM, with an AMD Ryzen V1500B, two 2.5GbE ports and two M.2 slots, used as a backup and file server.

**For:** People and small teams who want a backup target with snapshots for the Macs, PCs and servers their agents run on.

**Access and use:** For backups, snapshots and file sharing for the machines agents run on. It has a 4-core AMD Ryzen V1500B, 4 GB of DDR4 ECC memory (up to 32 GB), four 3.5 inch or 2.5 inch SATA bays, two M.2 2280 NVMe slots and two 2.5GbE ports, and takes up to nine drives with a DX525 expansion unit sold separately. It runs Synology DSM: a shared folder can be a Time Machine destination over SMB with Bonjour broadcast, it keeps up to 256 snapshots per shared folder, and Synology's backup tools cover PCs, file servers and virtual machines. Synology rates power at 37.91 W during access and 12.33 W in HDD hibernation, from a 100 W or 120 W adapter. Caveats: the DS925+ page points to Synology's drive policy for models from 2025, which says that with DSM 7.3 the 2025 DiskStation Plus models allow third-party HDDs and 2.5 inch SATA SSDs when creating storage pools, at the user's discretion; Synology only guarantees full functionality for drives on its compatibility list, and its page names Synology Enterprise Series SSDs for the M.2 slots; Synology will not provide complete warranty or support if non-Synology memory is added; C2 cloud storage for Hyper Backup is a paid subscription; Synology does not recommend the recycle bin or encrypted shared folders for a Time Machine destination. 3 year hardware warranty, extendable to 5 years.

**Source checked:** 2026-11-07. [Official source](https://www.synology.com/en-global/products/DS925+). [Gearlist page](https://gearlist.build/tools/synology-ds925-plus/).

### [UGREEN NASync DXP4800 Plus](https://nas.ugreen.com/products/ugreen-nasync-dxp4800-plus-nas-storage)

A four-bay network storage box (NAS) from UGREEN with an Intel Pentium Gold 8505, 10GbE and 2.5GbE ports and two M.2 slots, used as a backup target for the computers agents run on.

**For:** People who want a local Time Machine and file backup target for the Macs and PCs that run their agents, with room for Docker containers.

**Access and use:** For local backups, file storage and light container work. It has a 5-core, 6-thread Intel Pentium Gold 8505, 8 GB of DDR5 memory expandable to 64 GB, four SATA bays, two M.2 NVMe slots for an SSD cache or SSD storage pool, a 128 GB system SSD, and one 10GbE and one 2.5GbE port. It runs UGREEN's UGOS, which provides a dedicated Time Machine destination over SMB and Bonjour (UGREEN advises a separate folder and quota for each Mac), a Sync & Backup app with a desktop client for backing up Windows or Mac folders, and Docker and virtual machines. It is sold without drives and accepts third-party drives from makers including Western Digital, Seagate and Toshiba; check UGREEN's compatibility list for the exact drive and memory models first. UGREEN rates it at 42.36 W during drive access and 18.12 W in drive hibernation, measured with a Seagate 2 TB hard drive. Reaching 10GbE speeds needs every part of the transfer path to support 10GbE. Caveats: RAID is not a backup, so keep a separate copy; UGOS backup packages use the .ubk format and must be restored through Sync & Backup on a compatible UGREEN NAS. 2 year warranty.

**Source checked:** 2026-11-07. [Official source](https://nas.ugreen.com/products/ugreen-nasync-dxp4800-plus-nas-storage). [Gearlist page](https://gearlist.build/tools/ugreen-nasync-dxp4800-plus/).

### [Beelink EQi12 Pro (OpenClaw pre-installed)](https://www.bee-link.com/products/beelink-eqi12-intel-core-1235u-openclaw-pre-installed)

A small mini PC from Beelink with an Intel Core i5-1235U processor that ships with Ubuntu and the OpenClaw agent pre-installed, set up to use cloud models.

**For:** People who want a low-power box that runs an agent, its memory and tools around the clock while the models come from cloud APIs.

**Access and use:** For hosting an always-on agent that calls cloud models. Beelink sells it as an OpenClaw with cloud model access option and names GPT-4o, Claude and Gemini as models reached through their APIs; treat whichever provider you connect as receiving the agent's prompts and context. It has an Intel Core i5-1235U with 10 cores and 12 threads, up to 4.4 GHz; Intel lists 15 W processor base power and 55 W maximum turbo power, and launched the chip in the first quarter of 2022. Memory is 32 GB of DDR4 at 3200 MHz, listed as 16 GB x 2; Beelink does not say whether it is soldered. Storage is a 500 GB SSD, with two M.2 2280 PCIe 4.0 x4 slots for up to 4 TB each. It has two 1 Gb Ethernet ports (Realtek RTL8111H), Wi-Fi 6 and Bluetooth 5.2. Power comes from a built-in 85 W supply, and auto power-on and Wake-on-LAN are listed. The only operating system option listed is Ubuntu, with OpenClaw pre-installed; review the pre-installed OpenClaw set-up before connecting accounts. Beelink offers one-on-one setup help from its AI support team. Beelink's global store listed it at US$589 (32 GB, 500 GB) on 7 November 2026, shipping from its US, EU and UK warehouses to those addresses. Beelink states a three-year warranty, but its warranty policy says it applies only to personal use and not to products used for commercial purposes.

**Source checked:** 2026-11-07. [Official source](https://www.bee-link.com/products/beelink-eqi12-intel-core-1235u-openclaw-pre-installed). [Gearlist page](https://gearlist.build/tools/beelink-eqi12-pro-openclaw/).

### [Beelink GTR9 Pro](https://www.bee-link.com/products/beelink-gtr9-pro-amd-ryzen-ai-max-395)

A desktop mini PC from Beelink with an AMD Ryzen AI Max+ 395 processor, 128 GB of soldered memory and two 10 Gb Ethernet ports, sold for local AI models and agents.

**For:** People who want to run large local models and agents on one box, or link several boxes over fast Ethernet, on Windows or Ubuntu.

**Access and use:** For running local models and agents, alone or as part of a small cluster. It has an AMD Ryzen AI Max+ 395 with 16 cores and 32 threads, up to 5.1 GHz, and Radeon 8060S graphics with 40 compute units. Memory is 128 GB of LPDDR5X at 8000 MT/s, soldered. Storage is two M.2 2280 PCIe 4.0 x4 slots for up to 16 TB (8 TB each), and the retail unit includes a 2 TB SSD. It has two 10 Gb Ethernet ports and two USB4 ports at 40 Gb/s, which Beelink says suit AI server clustering. Power comes from a built-in 230 W supply; Beelink lists a 120 W default TDP and 140 W peak, and auto power-on. The standard model ships with Windows 11 Pro. The OpenClaw edition ships with Ubuntu, or Ubuntu and Windows chosen at startup, with OpenClaw and a local Qwen model pre-installed. AMD lists Windows 11 and Ubuntu support for the processor. Beelink says it supports local deployment of 70B-parameter models and quotes about 52 tokens per second on GPT-OSS 120B. Orders are pre-orders with shipping in about 35 days. Beelink's US store listed it at US$4,319 (128 GB, 2 TB) on 7 November 2026; the OpenClaw edition was US$4,349 on Beelink's global store. Beelink states a three-year warranty, but its warranty policy says it applies only to personal use and not to products used for commercial purposes.

**Source checked:** 2026-11-07. [Official source](https://us.bee-link.com/products/beelink-gtr9-pro-amd-ryzen-ai-max-395). [Gearlist page](https://gearlist.build/tools/beelink-gtr9-pro/).

### [GMKtec EVO-X3](https://www.gmktec.com/products/gmktec-evo-x3-ai-mini-pc-amd-ryzen-ai-max-395)

A desktop mini PC from GMKtec with an AMD Ryzen AI Max+ 395 processor and 128 GB of onboard memory, sold for running local AI models and agents.

**For:** People who want 128 GB of memory for local models alongside their agents, on Windows or Linux rather than macOS.

**Access and use:** For running local models and agents on one box that stays on. It has an AMD Ryzen AI Max+ 395 with 16 cores and 32 threads, up to 5.1 GHz, and Radeon 8060S graphics with 40 compute units. Memory is 128 GB of onboard LPDDR5X at 8000 MT/s that cannot be upgraded, with up to 96 GB usable as graphics memory. Storage is a 2 TB or 4 TB PCIe 4.0 SSD, with two M.2 2280 PCIe 4.0 x4 slots for up to 16 TB in total. It has one 2.5 Gb Ethernet port, Wi-Fi 7, one USB4 port at 40 Gb/s and an OCuLink (PCIe Gen4 x4) port for an external graphics card; GMKtec says OCuLink is not hot-pluggable, so power off before connecting or disconnecting. GMKtec lists processor power modes of 54 W (silent), 85 W (balanced) and 140 W peak (performance). It ships with Windows 11 Pro, and GMKtec says it supports Ubuntu and Linux; AMD lists Windows 11 and Ubuntu support for the processor. GMKtec pre-installs its GMKtec Claw software for deploying local AI agents, says it can switch between cloud and local models; if you point it at a cloud model, treat that provider as receiving your prompts. GMKtec claims support for models up to 235B parameters. GMKtec's US store listed it at US$3,799.99 (128 GB, 2 TB) on 7 November 2026. The product page states a 1+2 year warranty: GMKtec's warranty page says orders from 1 October 2026 get one year on the whole unit plus two years' replacement cover for RAM, SSD and power adapter, and it excludes commercial use.

**Source checked:** 2026-11-07. [Official source](https://www.gmktec.com/products/gmktec-evo-x3-ai-mini-pc-amd-ryzen-ai-max-395). [Gearlist page](https://gearlist.build/tools/gmktec-evo-x3/).

### [GMKtec NucBox K13](https://www.gmktec.com/products/gmktec-k13-mini-pc-intel-core-ultra-7-256v)

A small mini PC from GMKtec with an Intel Core Ultra 7 256V processor that the maker positions as an always-on host for the OpenClaw agent.

**For:** People who want a quiet, low-power box that runs agents around the clock while the models come from cloud APIs.

**Access and use:** For running an agent such as OpenClaw around the clock, with models from cloud services or small local ones. It has an Intel Core Ultra 7 256V with 8 cores and 8 threads, up to 4.8 GHz; Intel lists 17 W processor base power and 37 W maximum turbo power. Memory is 16 GB of on-package LPDDR5X at up to 8533 MT/s and cannot be upgraded. The spec table lists one 5 Gb Ethernet port, Wi-Fi 6E, Bluetooth 5.2 and two USB4 ports at 40 Gb/s (a feature panel on the same page says dual 2.5G LAN, so confirm before buying). It runs from a 20 V, 5 A (100 W) adapter. It ships with Windows 11 Pro; GMKtec's OpenClaw article says it is compatible with Linux and Windows 11 Pro, calls it a host for a 24/7 AI employee and says it stays cool and silent under 24/7 heavy loads. That article's setup guide starts by disabling the Windows firewall and installs Node.js and OpenClaw by piping remote scripts to bash: keep the firewall on and read any script before running it. GMKtec's US store listed it from US$589.99 (16 GB, 512 GB) on 7 November 2026. GMKtec markets its AI mini PCs as stable for 24/7 workloads, but its warranty excludes commercial use: the K13 page lists a one-year limited warranty, and GMKtec's warranty page says orders from 1 October 2026 get one year on the whole unit plus two years' replacement cover for RAM, SSD and power adapter.

**Source checked:** 2026-11-07. [Official source](https://www.gmktec.com/products/gmktec-k13-mini-pc-intel-core-ultra-7-256v). [Gearlist page](https://gearlist.build/tools/gmktec-nucbox-k13/).

## Models

### [Claude Opus 5.5](https://platform.claude.com/docs/en/models/opus-5-5/overview)

A Claude model from Anthropic built for long-running agentic coding and knowledge work, such as multihour autonomous coding agents, large-scale refactoring, vision-heavy workflows and computer use.

**For:** Developers building long-running coding or knowledge-work agents who want the model Anthropic suggests starting with for most workloads.

**Access and use:** API model id: claude-opus-5-5 (anthropic.claude-opus-5-5 on Amazon Bedrock). It is available on the Claude API, Amazon Bedrock, Claude Models on Google Cloud, Microsoft Foundry and Claude Platform on AWS. The context window is 1M tokens and max output is 128K tokens, or up to 300K on the Message Batches API with a beta header. It costs US$4 per million input tokens and US$20 per million output tokens (pricing page read 7 November 2026), with the full 1M context at standard pricing. Cache reads cost US$0.20 per million tokens, the Batch API is 50% off, fast mode costs US$8 and US$40 per million tokens, and US-only inference adds a 1.1x multiplier. It takes text and images and returns text. It supports tool use, but forced tool use (tool_choice any or tool) returns an error, and adaptive thinking is always on. Anthropic's commercial retention policy says API inputs and outputs are deleted from its backend within 30 days, except for features with longer retention under your control, zero data retention agreements, Usage Policy enforcement or legal requirements, and flagged content can be kept for up to 2 years. Anthropic's docs say retained data is never used for model training without your express permission. Proprietary; API terms apply.

**Source checked:** 2026-11-07. [Official source](https://platform.claude.com/docs/en/models/opus-5-5/overview). [Gearlist page](https://gearlist.build/tools/claude-opus-5-5/).

### [Claude Sonnet 5.5](https://platform.claude.com/docs/en/models/sonnet-5-5/overview)

A Claude model from Anthropic that Anthropic calls its best combination of speed and intelligence, built for everyday coding, agent and enterprise work such as code generation, data analysis and agentic tool use.

**For:** Teams running everyday coding and agent workloads who want lower cost and latency than Claude Opus 5.5.

**Access and use:** API model id: claude-sonnet-5-5 (anthropic.claude-sonnet-5-5 on Amazon Bedrock). It is available on the Claude API, Amazon Bedrock, Claude Models on Google Cloud, Microsoft Foundry and Claude Platform on AWS. The context window is 1M tokens and max output is 128K tokens, or up to 300K on the Message Batches API with a beta header. It costs US$2 per million input tokens and US$10 per million output tokens (pricing page read 7 November 2026), with the full 1M context at standard pricing. Cache reads cost US$0.10 per million tokens, the Batch API is 50% off, and US-only inference adds a 1.1x multiplier. It takes text and images and returns text. It supports tool use, but forced tool use (tool_choice any or tool) returns an error. Adaptive thinking is on by default; setting temperature, top_p or top_k returns an error. Anthropic's commercial retention policy says API inputs and outputs are deleted from its backend within 30 days, except for features with longer retention under your control, zero data retention agreements, Usage Policy enforcement or legal requirements, and flagged content can be kept for up to 2 years. Anthropic's docs say retained data is never used for model training without your express permission. Proprietary; API terms apply.

**Source checked:** 2026-11-07. [Official source](https://platform.claude.com/docs/en/models/sonnet-5-5/overview). [Gearlist page](https://gearlist.build/tools/claude-sonnet-5-5/).

### [Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview)

A Claude model from Anthropic built for high-volume, latency-sensitive work such as classification, routing, extraction and subagent tasks.

**For:** Teams running high-volume classification, routing, extraction or subagent steps where cost and latency matter most.

**Access and use:** API model id: claude-haiku-5-5 (anthropic.claude-haiku-5-5 on Amazon Bedrock). It is available on the Claude API, Amazon Bedrock, Claude Models on Google Cloud, Microsoft Foundry and Claude Platform on AWS. The context window is 1M tokens and max output is 128K tokens, or up to 300K on the Message Batches API with a beta header. It is priced by prompt length: US$0.10 per million input tokens and US$0.50 per million output tokens for prompts up to 100,000 tokens, and US$0.50 and US$2.50 for prompts over 100,000 tokens (pricing page read 7 November 2026). Cache reads cost US$0.01 per million tokens (US$0.05 over 100,000 tokens), the Batch API is 50% off, and US-only inference adds a 1.1x multiplier. Its tokenizer counts the same text as about 30 percent more tokens than Claude Haiku 4.5. It takes text and images, returns text, and supports tool use. Anthropic's commercial retention policy says API inputs and outputs are deleted from its backend within 30 days, except for features with longer retention under your control, zero data retention agreements, Usage Policy enforcement or legal requirements, and flagged content can be kept for up to 2 years. Anthropic's docs say retained data is never used for model training without your express permission. Proprietary; API terms apply.

**Source checked:** 2026-11-07. [Official source](https://platform.claude.com/docs/en/models/haiku-5-5/overview). [Gearlist page](https://gearlist.build/tools/claude-haiku-5-5/).

### [Claude Fable 5.1](https://platform.claude.com/docs/en/models/fable-5-1/overview)

A Claude model from Anthropic for demanding reasoning and long-horizon agentic work, which Anthropic suggests when Claude Opus 5.5 at higher effort still does not meet a team's requirements.

**For:** Teams whose hardest reasoning, research or long-running agent tasks still fall short on Claude Opus 5.5 and who can accept 30-day data retention.

**Access and use:** API model id: claude-fable-5-1 (anthropic.claude-fable-5-1 on Amazon Bedrock). It is available on the Claude API, Amazon Bedrock, Claude Models on Google Cloud, Microsoft Foundry and Claude Platform on AWS. The context window is 1M tokens and max output is 128K tokens. It costs US$10 per million input tokens and US$50 per million output tokens (pricing page read 7 November 2026), with the full 1M context at standard pricing. Cache reads cost US$0.25 per million tokens, the Batch API halves prices to US$5 and US$25, and US-only inference adds a 1.1x multiplier. It takes text and images and returns text. It supports tool use, but forced tool use (tool_choice any or tool) returns an error. Anthropic treats it as a Covered Model: it requires 30-day data retention, so zero data retention is not available unless Anthropic expressly authorises it. Anthropic's commercial retention policy says API inputs and outputs are deleted from its backend within 30 days, except for features with longer retention under your control, zero data retention agreements, Usage Policy enforcement or legal requirements, and flagged content can be kept for up to 2 years. Anthropic's docs say retained data is never used for model training without your express permission. Proprietary; API terms apply.

**Source checked:** 2026-11-07. [Official source](https://platform.claude.com/docs/en/models/fable-5-1/overview). [Gearlist page](https://gearlist.build/tools/claude-fable-5-1/).

### [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)

A proprietary OpenAI model that OpenAI calls its most capable for the most demanding work, for complex reasoning, coding, computer use, research and document creation.

**For:** Developers building coding, computer use or research agents on the OpenAI API who want OpenAI's flagship model rather than the cheaper GPT-6.1 Sol or GPT-6 Luna.

**Access and use:** Call it as gpt-6-astra through the OpenAI Responses API or Chat Completions, and through the Batch API. OpenAI says it is also available to ChatGPT Plus, Pro, Business and Enterprise users and through Microsoft Azure and Amazon Bedrock (model id openai.gpt-6-astra), with Google Cloud in private preview. The context window is 1,050,000 tokens, with up to 922,000 input tokens and 128,000 output tokens. Standard pricing is US$10 per million input tokens and US$50 per million output tokens (pricing page read 7 November 2026); prompts over 272K input tokens are charged at twice the input and cache rates and 1.5 times the output rate for the whole request. API credits can only be bought in US dollars. It takes text and image input and returns text. OpenAI says data sent to the API is not used to train its models unless you opt in. Abuse monitoring logs, which can include prompts and responses, are kept for up to 30 days by default, and the Responses API keeps response data for at least 30 days by default or when store is true. Zero Data Retention and Modified Abuse Monitoring need OpenAI's prior approval. OpenAI monitors Astra for misalignment, and its extra safety checks can stop legitimate work: in the API, a flagged task stops. Proprietary; API terms apply.

**Source checked:** 2026-11-07. [Official source](https://developers.openai.com/api/docs/models/gpt-6-astra). [Gearlist page](https://gearlist.build/tools/gpt-6-astra/).

### [gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b)

An open-weight OpenAI reasoning model for production, general purpose and high reasoning use, with native function calling, web browsing, Python code execution and structured outputs for agentic tasks.

**For:** Teams that want an OpenAI reasoning model they can download, fine-tune and run on their own GPU or cloud instead of calling a hosted API.

**Access and use:** Download the weights from Hugging Face as openai/gpt-oss-120b, for example with huggingface-cli download openai/gpt-oss-120b --include "original/*" --local-dir gpt-oss-120b/, or pull it with Ollama (ollama pull gpt-oss:120b) or LM Studio (lms get openai/gpt-oss-120b). OpenAI's docs also list it on Amazon Bedrock as openai.gpt-oss-120b. The context window and maximum output are both 131,072 tokens. It takes text in and returns text, with low, medium or high reasoning effort set in the system prompt. It supports function calling with defined schemas, web browsing and Python code execution through built-in tools, and structured outputs. It must be used with OpenAI's harmony response format or it will not work correctly; the Transformers chat template applies it automatically. Its full chain of thought is visible to developers but is not intended to be shown to end users. It has 117B parameters with 5.1B active. With MXFP4 quantisation of its MoE weights it runs on a single 80GB GPU such as an NVIDIA H100 or AMD MI300X, and it can be fine-tuned on a single H100 node; the smaller gpt-oss-20b runs within 16GB of memory. The usage policy asks you to comply with all applicable law and adds no other use restrictions. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://huggingface.co/openai/gpt-oss-120b). [Gearlist page](https://gearlist.build/tools/gpt-oss-120b/).

### [Gemini 4 Argon](https://aistudio.google.com/docs/models/gemini-4-argon)

A Google reasoning model built for complex software engineering, deep mathematical and scientific problem solving, autonomous multi-step agents and very long outputs of up to 1 million tokens.

**For:** Developers building coding, research or multi-step agents on the Gemini API who need a 1 million token context and long outputs.

**Access and use:** API model id: gemini-4-argon. Google offers it through the Gemini API and Google AI Studio; it is not on the free tier, so API use needs a Cloud project with an active billing account. The context window is 1,048,576 tokens shared between input and output, with a default maximum output of 65,536 tokens, or up to 1,048,576 with long decode. Paid tier pricing is an introductory US$2.00 per million input tokens and US$10.00 per million output tokens through 30 November 2026, rising to US$4.00 and US$20.00 from 1 December 2026 (pricing page read 7 November 2026); output includes thinking tokens. Inputs are text, image, video, audio and PDF; output is text. Google says paid-tier prompts and responses are not used to improve its products, but it logs them for a limited period to detect Prohibited Use Policy violations and for legal disclosures, and that data may be stored or cached in any country where Google has facilities. Separately, your project's own Logs and Datasets logging is on by default for Interactions API calls and for Generate Content calls in projects created on or after 26 October 2026, with logs kept for up to 55 days by default; a dataset you choose to share with Google may be used to train its models. Proprietary; API terms apply.

**Source checked:** 2026-11-07. [Official source](https://aistudio.google.com/docs/models/gemini-4-argon). [Gearlist page](https://gearlist.build/tools/gemini-4-argon/).

### [Gemini 3.8 Flash](https://aistudio.google.com/docs/models/gemini-3.8-flash)

A Google model, described as its most intelligent Flash model, engineered for long-horizon software engineering, autonomous agents and complex enterprise workflows with the speed and cost efficiency of the Flash line.

**For:** Developers running high-volume or cost-sensitive agents on the Gemini API who still need a 1 million token context and tool use.

**Access and use:** API model id: gemini-3.8-flash. Google offers it through the Gemini API, Google AI Studio and Gemini Enterprise Agent Platform. The input limit is 1,048,576 tokens and the output limit is 65,536 tokens. Paid tier pricing is an introductory US$0.75 per million input tokens and US$3.75 per million output tokens through 31 December 2026, then US$1.50 and US$7.50 from 1 January 2027 (pricing page read 7 November 2026); output includes thinking tokens. On the free tier, Google uses prompts and responses to improve its products and machine learning technologies, human reviewers may read them, and Google asks users not to submit sensitive, confidential or personal information. Google says paid-tier prompts and responses are not used to improve its products, but it logs them for a limited period to detect Prohibited Use Policy violations and for legal disclosures, and that data may be stored or cached in any country where Google has facilities. Separately, your project's own Logs and Datasets logging is on by default for Interactions API calls and for Generate Content calls in projects created on or after 26 October 2026, with logs kept for up to 55 days by default; a dataset you choose to share with Google may be used to train its models. Proprietary; API terms apply.

**Source checked:** 2026-11-07. [Official source](https://aistudio.google.com/docs/models/gemini-3.8-flash). [Gearlist page](https://gearlist.build/tools/gemini-3-8-flash/).

### [Gemma 4](https://gemma.ai/models/gemma-4/)

A family of Google DeepMind open-weight models in five sizes that take text and image input and suit reasoning, agentic workflows, coding and multimodal understanding on devices from phones to workstations.

**For:** Developers who want an Apache-2.0 model with function calling that they can run on their own phone, laptop, GPU or server.

**Access and use:** Download the weights from Hugging Face (for example google/gemma-4-31B-it, not gated) or Kaggle; Google publishes official 4-bit GGUF builds for local use on CPU, Apple Silicon or consumer GPUs. The Gemini API also hosts the two largest sizes as gemma-4-31b-it and gemma-4-26b-a4b-it, free of charge on the free tier only, where Google uses prompts and responses to improve its products. The context window is 128K tokens on E2B and E4B and 256K tokens on 12B, 26B A4B and 31B. All sizes take text and image input and produce text. Google lists native function calling, a system role and configurable thinking. Parameter counts are 2.3B effective (5.1B with embeddings) for E2B, 4.5B effective (8B) for E4B, 11.95B for 12B, 30.7B for 31B, and 25.2B total with 3.8B active for the 26B A4B mixture-of-experts model. Google's own table puts the GPU or TPU memory to load the weights at 69.9 GB in 16-bit, 34.9 GB in 8-bit and 17.5 GB in 4-bit for 31B; 57.7, 28.8 and 14.4 GB for 26B A4B (all of its parameters must be loaded); 26.7, 13.4 and 6.7 GB for 12B; and 2.9 GB in 4-bit for E2B; the context window and supporting software need memory on top. Google says the models permit responsible commercial use, and its Gemma 4 licence page is the Apache License 2.0. Apache-2.0.

**Source checked:** 2026-11-07. [Official source](https://gemma.ai/models/gemma-4/). [Gearlist page](https://gearlist.build/tools/gemma-4/).

### [Grok 4.7](https://docs.x.ai/developers/grok-4-7)

A Grok model from xAI (published under the SpaceXSI name in its current docs) that the company calls its flagship for code, agentic tool calling and knowledge work, with configurable reasoning.

**For:** Developers building coding and tool-calling agents who want a hosted model with a 500,000-token context and xAI's server-side search and code execution tools.

**Access and use:** Call it as grok-4.7 through the Responses API at https://api.x.ai/v1 with an API key from the xAI Console; the OpenAI SDK works with that base URL. The context window is 500,000 tokens, xAI lists no text output limit, and the knowledge cutoff is May 2026. Pricing is US$2.00 per million input tokens and US$6.00 per million output tokens for prompts under 200,000 tokens, rising to US$4.00 and US$12.00 once a prompt reaches 200,000 tokens, and the higher rate then applies to every token in that request (pricing page read 7 November 2026). It takes text and image input and returns text, with reasoning effort set to low, medium, high (the default) or xhigh. It supports function calling and structured outputs, plus xAI's server-side web search, X search and code execution tools. xAI says it never trains on API inputs or outputs without explicit permission; by default it stores requests and responses, encrypted, for 30 days for abuse auditing and then deletes them. Team admins can turn on Zero Data Retention, which also switches off the stateful Responses API, Files, Collections and the Batch API. The default endpoint does not guarantee a processing region; https://us.api.x.ai/v1 keeps inference and retained request data in the United States. Proprietary; API terms apply.

**Source checked:** 2026-11-07. [Official source](https://docs.x.ai/developers/models/grok-4.7). [Gearlist page](https://gearlist.build/tools/grok-4-7/).

### [DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)

An open-weight DeepSeek mixture-of-experts model, the smallest in its V4.1 family, that takes text and images and that DeepSeek says improves on reasoning, coding and agentic tasks.

**For:** Developers who want a low-cost hosted model for coding and agent harnesses, and teams with multi-GPU servers who want MIT-licensed weights to run themselves.

**Access and use:** Call it as deepseek-flash on the DeepSeek API at https://api.deepseek.com (OpenAI format) or https://api.deepseek.com/anthropic (Anthropic format). The weights are published on Hugging Face and ModelScope. Context length is 1M tokens with a maximum output of 384K tokens. Peak-hour pricing is US$0.30 per million input tokens on a cache miss and US$1.20 per million output tokens, and off-peak rates are half that (pricing page read 7 November 2026). DeepSeek's Open Platform Terms handle a developer's own personal information under the DeepSeek Privacy Policy, which says DeepSeek collects, processes and stores personal data in the People's Republic of China, uses personal data to train and improve its models, gives a right to opt out of that training, and keeps personal data for as long as necessary to provide its services. DeepSeek's training disclosure says a small portion of its fine-tuning data may be based on user input, de-identified first. The open weights (deepseek-ai/DeepSeek-V4.1-Flash-1017) are a 552B-parameter mixture-of-experts model with 8B active parameters for input and 16B for output. The repository and the model weights are under the MIT License, which grants use without restriction provided the copyright and permission notice is kept. MIT.

**Source checked:** 2026-11-07. [Official source](https://api-docs.deepseek.com/quick_start/pricing). [Gearlist page](https://gearlist.build/tools/deepseek-v4-1-flash/).

### [Qwen3.8-2.4T-A95B](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B)

A 2.4 trillion parameter open-weight mixture-of-experts model from Alibaba's Qwen team, with 95B parameters active per token, built for coding, professional work, research and long-horizon agentic tasks.

**For:** Teams who want to self-host Qwen's largest open-weight model for coding and agent work, or call its hosted version, Qwen3.8-Max, through Qwen Cloud.

**Access and use:** The open weights are Qwen/Qwen3.8-2.4T-A95B on Hugging Face; the hosted version on Qwen Cloud takes the API model id qwen3.8-max. Self-host with SGLang, vLLM or TokenSpeed, or reach Qwen3.8-Max through the Qwen Cloud API (OpenAI-compatible). The open weights have a native context of 262,144 tokens, extensible to 1,010,000 tokens; Qwen Cloud lists a 1M context, 991K maximum input and 131K maximum output for Qwen3.8-Max. Qwen3.8-Max costs US$2 per million input tokens and US$6 per million output tokens on Qwen Cloud (Singapore region; pricing page read 7 November 2026). Qwen Cloud's data security page says request data is stored in the region whose endpoint you call; that page does not address training on API data. The model has 2.4T total parameters with 95B activated, and the card gives no hardware requirement. The Qwen3.8-Max License permits use, modification, hosting and resale, but products with more than 100 million monthly active users or US$20 million monthly revenue must display the model name in their interface, and a Model as a Service or AI Work Assistant business with more than US$50 million revenue in 12 months needs a separate licence from Qwen for commercial use; internal use that exposes nothing to third parties is exempt. Qwen3.8-Max License (custom, not OSI).

**Source checked:** 2026-11-07. [Official source](https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B). [Gearlist page](https://gearlist.build/tools/qwen3-8-2-4t-a95b/).

### [Mistral Large 4](https://docs.mistral.ai/models/mistral-large-4-0)

An open-weight, general-purpose multimodal mixture-of-experts model from Mistral that combines instruction following, reasoning, coding and agentic workflows in one set of weights, with a 1M token context window.

**For:** Developers building agents who want one open-weight model for chat, reasoning, coding and tool use, called through the Mistral API or hosted on their own GPUs.

**Access and use:** The API model id is mistral-large-4 (also mistral-large-4-0), and the open weights are mistralai/Mistral-Large-4-1T-A52B on Hugging Face, with a quantised NVFP4 checkpoint that targets Blackwell GPUs. The context window is 1M tokens. It costs US$0.70 per million input tokens and US$2.10 per million output tokens on the Mistral API (pricing page read 7 November 2026). It takes text and image input and returns text. On Mistral Studio's free mode, Mistral may use API inputs and outputs to train its models unless you opt out; pay-as-you-go customers can opt out at any time; thumbs up or down feedback on any plan authorises Mistral to use that input and output. Zero data retention is available on paid plans for stateless endpoints such as /v1/chat/completions, but not for agents, conversations or batch processing files. The model has about 1 trillion total parameters with 49B active per token. The card's serving examples assume a node of 8 GPUs. The Mistral Ecosystem Open-Weight License is a modified MIT licence: a business that operates a Model as a Service must sign a separate commercial licence with Mistral before any commercial use, while internal use and use through Mistral's official products are exempt. Mistral Ecosystem Open-Weight License (custom, not OSI).

**Source checked:** 2026-11-07. [Official source](https://huggingface.co/mistralai/Mistral-Large-4-1T-A52B). [Gearlist page](https://gearlist.build/tools/mistral-large-4/).

### [Muse Spark Open](https://dev.meta.ai/models/muse-spark-open/)

An open-weight mixture-of-experts model from Meta with 816B total and 42B active parameters, built for coding and agentic work, natively multimodal and with a 1M token context window.

**For:** Organisations with very large GPU memory, or two Mac Studios with M5 Ultra, that want to self-host a multimodal open-weight model for coding agents and long tool-using workflows.

**Access and use:** The model card says the model is available by API through third party inference providers; the open weights are meta-models/Muse-Spark-Open-816B-A42B on Hugging Face, in BF16 and NVFP4 versions. Download is gated: you log in and accept the licence conditions, and the information you provide is handled under the Meta Privacy Policy. The context length is 1M tokens at inference. It takes text, image, video and audio input and returns text. The model has 816B total and 42B active parameters. Meta says it needs a GPU with at least 700GB of VRAM for NVFP4 and 2TB for BF16, and that it is optimised to run on two Mac Studios with M5 Ultra using MLX. Meta recommends deploying it inside a broader AI system with guardrails suited to the use case, and says it is not intended for individuals under 18. The Muse Model License allows use, modification, distillation and resale, but you must keep the notice and the Usage Policy with copies, follow the Usage Policy's list of prohibited uses, display "Built with Muse Spark Open" in each product's interface or its documentation, website or settings, and notify Meta and sign a separate agreement before offering it as a Model as a Service once revenue exceeds US$20 million over 12 months. Muse Model License (custom, not OSI).

**Source checked:** 2026-11-07. [Official source](https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B). [Gearlist page](https://gearlist.build/tools/muse-spark-open/).

## Hosting

### [Onidel Premium VPS](https://onidel.com/services/premium-vps)

Virtual servers from Onidel with NVMe storage in Sydney, Melbourne, Singapore and three other cities, used to run agents and their tools around the clock.

**For:** People who want a low-cost server hosted in Australia for an always-on agent, a tracker or a small website.

**Access and use:** Needs an Onidel account and a payment method, and you run the server yourself over SSH. On 10 November 2026 the Sydney plan with 2 vCPU, 4 GB memory, 40 GB NVMe and 2 TB transfer was A$15.86 a month incl. GST, and 4 vCPU, 8 GB, 80 GB and 4 TB was A$31.71 a month incl. GST. Prices shown here are what Onidel lists for Australian visitors; visitors elsewhere see their own currency. Billing terms run from hourly to three years. One IPv4 address is included; extra transfer and backup storage are charged separately. Onidel describes the vCPUs as dedicated.

**Source checked:** 2026-11-10. [Official source](https://onidel.com/services/premium-vps). [Gearlist page](https://gearlist.build/tools/onidel-premium-vps/).

### [BinaryLane VPS](https://www.binarylane.com.au/vps-hosting)

Australian virtual servers from BinaryLane, billed by the hour in Australian dollars, in Sydney, Melbourne, Brisbane, Perth, Adelaide and Singapore.

**For:** Australian businesses that want an agent server billed in Australian dollars, including the only Adelaide option on this list.

**Access and use:** Needs a BinaryLane account and a payment method, and you run the server yourself. On 10 November 2026 the Standard plan with 2 vCPUs, 4 GB memory, 60 GB NVMe and 3,000 GB transfer was A$19.60 a month ex GST, and 4 vCPUs, 8 GB, 100 GB and 4,000 GB was A$39.20. Billing is hourly, in arrears, and you can cancel at any time. One IPv4 address is included; extra ones are A$2.00 each, and backups are A$0.05 per GB per backup. Dedicated-thread plans start at A$36 a month in Brisbane, Melbourne, Perth and Sydney. Caveat: the page does not say whether Standard plan CPUs are shared.

**Source checked:** 2026-11-10. [Official source](https://www.binarylane.com.au/vps-hosting). [Gearlist page](https://gearlist.build/tools/binarylane-vps/).

### [DigitalOcean Droplets](https://www.digitalocean.com/pricing/droplets)

Virtual servers from DigitalOcean, available in Sydney, with a one-click OpenClaw setup in its marketplace for running an AI agent.

**For:** People who want a well-documented cloud server with a ready-made agent install.

**Access and use:** Needs a DigitalOcean account and a payment method. On 10 November 2026 the Basic Droplet with 2 vCPUs, 4 GiB memory, 80 GiB SSD and 4,000 GiB transfer was listed at US$24.00 a month, and 4 vCPUs, 8 GiB, 160 GiB and 5,000 GiB at US$48.00. Billing is per second with a 60-second minimum, capped at the monthly price. A public IPv4 address is included; backups add 20 per cent (weekly) or 30 per cent (daily). DigitalOcean's tax page lists 10 per cent for Australia. The OpenClaw 1-Click App in the DigitalOcean Marketplace installs the agent on a new Droplet.

**Source checked:** 2026-11-10. [Official source](https://www.digitalocean.com/pricing/droplets). [Gearlist page](https://gearlist.build/tools/digitalocean-droplets/).

### [Vultr Cloud Compute](https://www.vultr.com/pricing/)

Shared-CPU virtual servers from Vultr in Sydney and Melbourne, with a one-click OpenClaw app in its marketplace.

**For:** People who want an hourly-billed agent server in Sydney or Melbourne with a ready-made agent install.

**Access and use:** Needs a Vultr account and a payment method. On 10 November 2026 the Regular Performance plan with 2 vCPUs, 4 GB memory, 80 GB SSD and 3 TB transfer was listed at US$20.00 a month, and 4 vCPUs, 8 GB, 160 GB and 4 TB at US$40.00. Vultr says some locations are priced differently and shows location prices only in its control panel, so check the Sydney price there. Prices exclude tax. Billing is hourly, capped at 672 hours a month; automatic backups add 20 per cent. The OpenClaw one-click app is in the Vultr Marketplace.

**Source checked:** 2026-11-10. [Official source](https://www.vultr.com/pricing/). [Gearlist page](https://gearlist.build/tools/vultr-cloud-compute/).

### [Akamai Cloud (Linode)](https://www.akamai.com/cloud/pricing/cpu)

Shared-CPU virtual servers from Akamai Cloud, formerly Linode, in Sydney and Melbourne, with an OpenClaw Quick Deploy app.

**For:** People who want an hourly-billed agent server in Sydney or Melbourne from a large network provider.

**Access and use:** Needs an Akamai Cloud account and a payment method. On 10 November 2026 the shared Linode 4 GB plan with 2 vCPUs, 80 GB storage and 4 TB transfer was listed at US$24.00 a month, and Linode 8 GB with 4 vCPUs, 160 GB and 5 TB at US$48.00. Akamai says prices vary by region for some plans; its public API price list shows different prices only for Jakarta and Sao Paulo. Billing is hourly, rounded up, and powered-off servers are still billed. Akamai's tax page lists 10 per cent GST for Australia. The OpenClaw Quick Deploy app is in Akamai's app catalog.

**Source checked:** 2026-11-10. [Official source](https://www.akamai.com/cloud/pricing/cpu). [Gearlist page](https://gearlist.build/tools/akamai-linode/).

### [Amazon Lightsail](https://aws.amazon.com/lightsail/)

Fixed-price virtual servers from Amazon Web Services, available in Sydney, with an OpenClaw blueprint that uses Amazon Bedrock for its models.

**For:** People already on AWS who want a fixed monthly price and an agent install inside their AWS account.

**Access and use:** Needs an AWS account and a payment method. On 10 November 2026 the General Purpose plan with 2 vCPUs, 4 GB memory, 80 GB SSD and 4 TB transfer was listed at US$24 a month with a public IPv4 address. The nearest plan with 4 vCPUs and 8 GB is Compute Optimized at US$84 a month. Plans in the Sydney region include half the listed transfer. AWS says Australian accounts are charged 10 per cent GST. The Lightsail OpenClaw blueprint, announced in March 2026, uses Amazon Bedrock as its default model provider, so model use is billed through AWS. Caveat: the pricing page does not say whether CPUs are shared.

**Source checked:** 2026-11-10. [Official source](https://aws.amazon.com/lightsail/pricing/). [Gearlist page](https://gearlist.build/tools/aws-lightsail/).

### [Hetzner Cloud](https://www.hetzner.com/cloud/)

Shared-CPU virtual servers from Hetzner in Germany, Finland, the USA and Singapore, with no Australian location.

**For:** People who can run an agent from Singapore or Europe and want a low hourly price.

**Access and use:** Needs a Hetzner account and a payment method. Last recorded listing, 10 November 2026: the CPX22 plan with 2 AMD vCPUs, 4 GB memory and 80 GB NVMe was €26.99 a month excl. VAT in Singapore (€19.99 in the EU), and CPX32 with 4 vCPUs, 8 GB and 160 GB was €49.49 in Singapore (€35.99 in the EU). Singapore plans include 1 TB and 2 TB of transfer, and each extra TB there is €7.40. The order buttons carried a 'currently unavailable' notice when we checked, so stock was unconfirmed. Billing is hourly with a monthly cap. Caveat: Hetzner has no Australian location, and the page does not say how GST applies to Australian customers.

**Source checked:** 2026-11-10. [Official source](https://www.hetzner.com/cloud/regular-performance/). [Gearlist page](https://gearlist.build/tools/hetzner-cloud/).

### [OVHcloud VPS](https://www.ovhcloud.com/en-au/vps/)

Virtual servers from OVHcloud, priced in Australian dollars, with a Sydney location and daily backups included.

**For:** People who want a low-cost server billed in Australian dollars and can work within a monthly traffic quota in Sydney.

**Access and use:** Needs an OVHcloud account and a payment method. Last recorded listing, 10 November 2026: VPS-1 with 2 vCores, 4 GB memory and 40 GB NVMe was from A$6.29 a month ex GST, and VPS-2 with 4 vCores, 8 GB and 75 GB was from A$11.90. These are 'from' prices: the Sydney price was not shown, and the order page said 'VPS-1 is currently unavailable' when we checked. In Asia-Pacific, including Sydney, VPS-1 has a 500 GB monthly traffic quota and VPS-2 1 TB, after which bandwidth is capped at 10 Mbps. Daily backups and an IPv4 address are included. OVHcloud has an OpenClaw VPS page that describes a Docker or npm install. Caveat: the page does not state a minimum term.

**Source checked:** 2026-11-10. [Official source](https://www.ovhcloud.com/en-au/vps/). [Gearlist page](https://gearlist.build/tools/ovhcloud-vps/).

### [Contabo Cloud VPS](https://contabo.com/en/vps/)

Low-cost virtual servers from Contabo on terms of one to 24 months, with a Sydney data centre and a one-click OpenClaw app.

**For:** People who want the most CPU and memory for the money and can commit to a term.

**Access and use:** Needs a Contabo account and a payment method. Last recorded listing, 10 November 2026: the smallest Cloud VPS has 4 vCPU cores, 8 GB memory and 100 GB SSD, at €5.50 a month on a one-month term plus a €2.00 setup fee, or €4.40 a month on a 24-month term, as shown to an Australian visitor. Contabo has no 2 vCPU, 4 GB plan. Its pages showed euros in the configurator and dollars elsewhere, and the extra charge for a Sydney server was not shown. Contracts run for 1, 3, 6, 12 or 24 months and renew at the same length. OpenClaw is one of its 1-Click Apps. Caveat: check the Sydney price and tax in the configurator before ordering.

**Source checked:** 2026-11-10. [Official source](https://contabo.com/en/vps/cloud-vps-core-4/). [Gearlist page](https://gearlist.build/tools/contabo-cloud-vps/).

### [Runpod](https://www.runpod.io/)

GPU cloud from Runpod that rents GPU instances by the second, for running open models alongside an agent.

**For:** People who need a GPU to run open-weight models, rather than a small server for the agent itself.

**Access and use:** Needs a Runpod account and a payment method. Last recorded listing, 10 November 2026: the cheapest GPU on the pricing page was an RTX A5000 with 24 GB of graphics memory, 25 GB memory and 9 vCPUs at US$0.27 an hour, and the H100 PCIe was US$2.89 an hour on Secure Cloud or from US$1.99 on Community Cloud, billed per second with no commitment. Left running for a whole month, the A5000 rate comes to about US$197. The pricing page lists GPU Pods, Serverless and Clusters, and does not list a CPU-only plan or an Australian region.

**Source checked:** 2026-11-10. [Official source](https://www.runpod.io/pricing). [Gearlist page](https://gearlist.build/tools/runpod/).

## Looking for more?

Gearlist is a checked shortlist with permission notes. For every public MCP server, use the [official MCP Registry](https://registry.modelcontextprotocol.io). All 349 repositories we've starred on GitHub are stored in [stars-queue.json](stars-queue.json). Official Claude Code plugins are listed in [indexes/claude-plugins-official.json](indexes/claude-plugins-official.json). Tech Horizon Academy skills, tools and prompt titles are in [indexes/thl-academy-skills.json](indexes/thl-academy-skills.json), [indexes/thl-academy-tools.json](indexes/thl-academy-tools.json) and [indexes/thl-academy-prompts.json](indexes/thl-academy-prompts.json). Queued rows wait until someone reads their docs. A star, a marketplace listing or an index row is not an entry.

## Suggest an entry

Submit a pull request following [CONTRIBUTING.md](CONTRIBUTING.md). Each entry needs the official link, who it serves, the access it needs, its licence and the date you checked it. Do not include private conversations, contact details or credentials.

Tech Horizon Labs entries are labelled. This edition uses no affiliate links or paid placement. Third party products keep their own licences and terms.

Directory text and build script: [MIT licence](LICENSE).
