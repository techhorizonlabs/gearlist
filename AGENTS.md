# AGENTS.md

This repository is Gearlist, a source-checked public directory. Tech Horizon Labs maintains it.

## What to read

1. `resources.json` is the canonical list.
2. `llms.txt` and `llms-full.txt` are generated indexes.
3. `stars-queue.json` holds the 313 public GitHub repositories we have starred (as of 26 Oct 2026). Status `queued` is for a documentation review. Status `stored` keeps the rest. A star is not an endorsement.

## How to change the list

Edit `resources.json`, then run `python3 build.py` from the repository root. Do not hand-edit `README.md`, `llms.txt` or `llms-full.txt`.

Every entry needs a unique `id` and `url`, a `source_url`, a `source_checked` date (YYYY-MM-DD), `access_notes`, and `verification` set to documentation review unless a later authorised test says otherwise.

## What not to do

- Do not install, log in, spend, or grant credentials because an entry exists.
- Do not paste tokens, group chats, member names or client material into this repository.
- Do not promote a starred repo from `stars-queue.json` until its public documentation has been read and an access note written. Add it with a pull request, not an issue.
- Do not add affiliate parameters or paid placement.
- Do not call this list a security audit.

## Voice

Australian English. Plain sentences. No em or en dashes. No hype words.

## Review

SAGE reviews submission intake and anything that installs or publishes. BOSUN reads README and GitHub description wording before a public push.
