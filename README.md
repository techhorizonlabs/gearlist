# Gearlist

![Gearlist](social-preview.png)

A source-checked stack of agent tools, MCP servers and skills. Each entry says what it is, who it is for, and the access it needs, so a person can scan it and an agent can load it.

By Tech Horizon Labs. This edition contains 20 entries. Documentation checked means the source was read. It does not mean the software was installed, tested or security audited. Entries are grouped by purpose, in no particular order.

## How to use this

- Human: scan the groups below. The heading is the product. **For** is the audience. **Access and use** is the permission note.
- Agent: load [llms.txt](llms.txt) first, then [llms-full.txt](llms-full.txt) or [resources.json](resources.json). [AGENTS.md](AGENTS.md) is the house rules. Do not install from a row until a human authorises it.

Install the catalog skill with:

```bash
npx skills add techhorizonlabs/gearlist
```

## Contents

- [Agent tools](#agent-tools) (6)
- [MCP and integrations](#mcp-and-integrations) (4)
- [Security and governance](#security-and-governance) (2)
- [Platforms](#platforms) (3)
- [Skills and learning](#skills-and-learning) (5)


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

## Security and governance

### [CISO AI](https://cisoai.au/)

Security briefings, analysis and governance resources.

**For:** Teams following security developments and governance topics.

**Access and use:** Read the linked primary sources and check dates before using advice in an operational decision.

**Source checked:** 2026-10-25. [Official source](https://cisoai.au/).

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

### [x402](https://x402.org/)

A protocol for payments over HTTP using the 402 response.

**For:** Developers building services that charge per request.

**Access and use:** Connecting a payment client can spend funds. Set explicit transaction limits.

**Source checked:** 2026-10-25. [Official source](https://x402.org/).

### [Official MCP Registry](https://registry.modelcontextprotocol.io)

The official hosted registry of publicly available Model Context Protocol servers, with a REST API and server.json metadata.

**For:** MCP clients, aggregators and people looking up a server by name.

**Access and use:** The registry is in preview. Breaking changes or data resets may occur before general availability. Listing a server is not a security audit. Installing a listed server still needs its own credentials and terms.

**Source checked:** 2026-10-26. [Official source](https://modelcontextprotocol.io/registry/about).

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

## Looking for more?

Gearlist is a checked shortlist with permission notes. For every public MCP server, use the [official MCP Registry](https://registry.modelcontextprotocol.io). All 313 repositories we've starred on GitHub are stored in [stars-queue.json](stars-queue.json). Queued rows wait until someone reads their docs. A star is not an entry.

## Suggest an entry

Submit a pull request following [CONTRIBUTING.md](CONTRIBUTING.md). Each entry needs the official link, who it serves, the access it needs, its licence and the date you checked it. Do not include private conversations, contact details or credentials.

Tech Horizon Labs entries are labelled. This edition uses no affiliate links or paid placement. Third party products keep their own licences and terms.

Directory text and build script: [MIT licence](LICENSE).
