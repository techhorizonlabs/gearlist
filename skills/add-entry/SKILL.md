---
name: add-entry
description: Add or correct a Gearlist catalog entry. Use when asked to add a tool, MCP server, skill or platform to this repository, or to promote a row from stars-queue.json.
---

# Add a Gearlist entry

Gearlist is a short, source-checked directory. Reading public docs is required. Installing the product is not.

## Steps

1. Read `AGENTS.md` and `CONTRIBUTING.md`.
2. Confirm the official URL with a live fetch. Prefer the vendor site or the canonical GitHub repository.
3. Write access notes: account, OAuth scopes, local files, spend, or "none beyond a public clone".
4. Add one object to `resources.json` with `id`, `name`, `category`, `url`, `description`, `for_whom`, `access_notes`, `source_url`, `source_checked` (today's date), `verification`, `thl_project`.
5. If the same repo is in `stars-queue.json`, set that row's `status` to `published` or remove it.
6. Run `python3 build.py` from the repository root and fix any assertion failure.
7. Do not paste credentials, chats or client names.

## Categories

Use an existing category where it fits: Agent tools, MCP and integrations, Security and governance, Platforms, Skills and learning.

## Refuse

Stop if the source is an affiliate dump, has no public documentation, or asks you to install in order to describe it.
