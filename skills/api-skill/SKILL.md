---
name: api-skill
description: Turn a REST API into an agent skill instead of an MCP server. Use when asked to give an agent access to an API, to "wrap" an API, or to decide between a skill and an MCP server for one.
---

# Turn an API into a skill

Most APIs an agent needs are a few calls and one key. A skill covers that with a page of instructions. Build an MCP server only when the job outgrows the page.

## Skill or MCP server

Build a skill when:
- the agent uses a handful of endpoints;
- it signs in with one key, or none;
- each call stands alone, with no session to keep;
- one person or one team uses it.

Build an MCP server when:
- each user signs in with their own account (OAuth);
- there are many tools, or long-running and streaming calls;
- several agents or apps share it and need separate permissions.

Start with a skill. Move to an MCP server when the instructions pass about a page, or users need their own sign-in.

## Steps

1. Read the official API docs. Note the base URL, how it signs in, rate limits and terms of use.
2. Keep the key in an environment variable or the user's secret store. It never goes in the skill file, a prompt or a chat.
3. Write `SKILL.md`:
   - frontmatter with a `name` and a `description` that names the words a user would say;
   - what the API gives, in one line;
   - how it signs in and which variable holds the key;
   - the three to five calls the agent will actually make, each with an example request and the response fields to read;
   - limits, error codes and what to do on each;
   - what not to do: writes, deletes or spend without a human's yes.
4. Add a short script under `scripts/` only when requests need signing, paging or parsing.
5. Run each example once, read-only, and write the date you checked it in the skill.
6. List the API in Gearlist with its access notes.

## Example: ABS Data API (no key)

Free and open without a key since 29 November 2024. Responses are SDMX, so ask for JSON or CSV in the Accept header.

```bash
# List the datasets (dataflows) the ABS publishes
curl -s -H "Accept: application/vnd.sdmx.structure+json" \
  "https://data.api.abs.gov.au/rest/dataflow/ABS?detail=allstubs"

# The latest Consumer Price Index figures as CSV
curl -s -H "Accept: application/vnd.sdmx.data+csv" \
  "https://data.api.abs.gov.au/rest/data/ABS,CPI/all?lastNObservations=1"
```

Read `data.dataflows[].id` and `.name` from the first call to pick a dataset, then swap it in for `CPI`. Replace `all` with a key to filter by measure or region; the ABS Data API user guide explains the key format.

## Example: ABN Lookup (free key)

Register on the ABN Lookup web services page to receive a GUID by email, then keep it in `ABR_GUID`.

```bash
# One ABN's registered details
curl -s "https://abr.business.gov.au/json/AbnDetails.aspx?abn=${ABN}&guid=${ABR_GUID}&callback=c"

# Businesses matching a name
curl -s "https://abr.business.gov.au/json/MatchingNames.aspx?name=${NAME}&maxResults=10&guid=${ABR_GUID}&callback=c"
```

The JSON comes wrapped in `c(...)`, so strip the wrapper before parsing. Read `EntityName`, `AbnStatus`, `BusinessName` and `AddressState`. An empty `Abn` means not found or a bad GUID.

Checked 3 November 2026.
