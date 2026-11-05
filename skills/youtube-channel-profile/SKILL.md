---
name: youtube-channel-profile
description: Profile a YouTube channel from the official YouTube Data API v3. Covers subscribers, views, upload cadence, recent views and trend, engagement, Shorts share, top videos and an estimated ad earnings range with its formula. Use when given a YouTube channel URL, @handle or channel ID and asked how big, active, engaged or valuable the channel is.
---

# YouTube channel profile

`scripts/channel_profile.py` reads public channel data through the YouTube Data API v3 and prints a Markdown report, or JSON with `--json`. It uses the official API only. It never loads YouTube web pages, and it writes nothing to disk.

## Before you run it

1. The human needs a Google Cloud project with the YouTube Data API v3 enabled and an API key, restricted to that API.
2. The key lives in the `YOUTUBE_API_KEY` environment variable. Never put it in a prompt, file or chat, and never print it. If it is not set, stop and ask the human to set it. Do not look for keys anywhere else.
3. Install the one dependency: `pip install -r scripts/requirements.txt` (requests).

## Run

```bash
python3 scripts/channel_profile.py @handle
python3 scripts/channel_profile.py https://www.youtube.com/@handle --videos 100
python3 scripts/channel_profile.py UCxxxxxxxxxxxxxxxxxxxxxx --json
```

Options: `--videos N` (recent uploads to read, default 50, max 500), `--json`, `--no-search`, `--cpm-low` and `--cpm-high` (default 0.25 and 4.00).

## How it finds the channel

- A channel ID or a `/channel/UC...` URL: `channels.list` with `id`.
- An `@handle` or `/@handle` URL: `channels.list` with `forHandle`.
- A `/user/` URL: `forUsername`. A `/c/` URL is tried as a handle.
- If nothing matches, it falls back to `search.list` for the best match and says so in the report. Check the title and ID before you rely on it. `--no-search` turns the fallback off.
- Video links, playlist links and non-YouTube addresses are refused. Ask for the channel link.

## Quota

| Call | Cost |
| --- | --- |
| `channels.list` | 1 unit |
| `playlistItems.list` | 1 unit per 50 uploads |
| `videos.list` | 1 unit per 50 videos |
| `search.list` (fallback only) | 1 call from its own bucket |

The default run costs 3 units of the 10,000-unit daily default. Since 1 June 2026, `search.list` has its own bucket of 100 calls a day. Before that, one search cost 100 units from the main quota, so older guides will say 100. Failed calls still cost quota. Quota resets at midnight Pacific Time. Every report ends with the quota it used.

## What it reports

From YouTube, as returned:
- Subscribers, rounded down by YouTube to three significant figures. If the owner hides the count, the report says "Hidden" and gives no guess.
- Total channel views and the public video count.
- Views, likes and comments for each recent video.

Derived by the script, marked `*`:
- Cadence: median days between the last N uploads, uploads a month ((N - 1) gaps / days spanned x 30.44), and days since the last upload.
- Median and mean views of recent videos. Live and upcoming streams are left out.
- Trend: median views of the last 10 uploads against the 10 before. Newer videos have had less time to gather views.
- Engagement: per-video (likes + comments) / views, then the median. Videos with hidden likes are left out. Videos with comments off count 0 comments.
- Shorts against long-form, by duration. This is a heuristic: 180 seconds or less counts as a Short, because the API has no Shorts flag.
- Top 5 recent videos by views.
- Estimated monthly views: the sum of current views on videos published in the last 30 days. This leaves out back-catalogue views. If the sample does not reach back 30 days, the report says so and asks for a larger `--videos`. That check assumes the uploads playlist lists newest first, as it usually does.

YouTube API policy III.E.4.h allows derived figures only next to YouTube's own totals, with a clear note that they are not from YouTube. The report does both. Keep that note whenever you quote a starred figure.

## Earnings method

```
low  = estimated monthly views / 1,000 x US$0.25
high = estimated monthly views / 1,000 x US$4.00
```

US$0.25 to US$4.00 is Social Blade's published default CPM range (socialblade.com/youtube/calculator). The report prints the formula with the real numbers. It is ad revenue only. It leaves out sponsorships, memberships, shopping and affiliate income, and fan funding. Actual RPM varies by niche, audience country and format. Shorts revenue is pooled on different terms. A channel outside the YouTube Partner Program earns no ad revenue. Always call it an estimated range, never income.

## Errors

| Exit | Meaning | What to do |
| --- | --- | --- |
| 0 | Report printed | |
| 2 | Bad input, missing key, or no channel found | Fix the input, or ask the human for the key or the right link |
| 3 | Quota used up | Stop. Tell the human it resets at midnight Pacific Time. Do not retry in a loop or switch keys |
| 4 | Other API error, such as an invalid key or the API not enabled | Show the message to the human |
| 5 | Network error | Retry once, then report it |

Errors print the quota used before the failure. Every message and report is scrubbed of the key before it is printed.

## Rules

- Official API only. Do not scrape YouTube pages to fill a gap. Report the gap.
- Cache nothing beyond the run. Do not save raw API responses. If the human keeps the report, API statistics may not be stored for more than 30 days (policy III.E.4.b).
- Public data only. Audience demographics are not public: see the `creator-audience` skill.

Checked 5 November 2026 against the YouTube Data API reference, quota page, revision history and developer policies. The script's tests run offline against fixtures. It has not been run against the live API here.
