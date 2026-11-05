---
name: creator-audience
description: Get a YouTube creator's audience demographics (age, gender, country) with consent. These figures are not public, so they come from the channel owner's own YouTube Analytics or from a paid estimate. Use when asked who watches a channel, whether its audience fits a brand, or for audience age, gender or location.
---

# Creator audience

YouTube does not publish audience demographics. The Data API used by `youtube-channel-profile` has none. There are two honest sources: the channel owner's own analytics, shared with their consent, or a paid third-party estimate the human approves. Anything else is a guess. Say so.

## The consent rule

1. Owner data comes from the owner. They choose what to share, for which dates, and who sees it. Get that in writing (an email or message) before you ask for access.
2. The owner signs in with their own account. Never ask for their password or a sign-in code, and never type one for them.
3. Spend needs a yes. Ask the human before each paid lookup, and name its cost.
4. Never infer age, gender or location from names, faces, voices, comments or thumbnails.
5. Keep it only for the job. Show it only to the owner and the people they approved (YouTube policy III.E.3.b). Delete it within 7 days of a request (III.E.4.g). If you keep it, re-check the owner's consent every 30 days (III.E.4.b).

## Route 1: the owner shares from YouTube Studio (start here)

This needs no API work. It suits a one-off brief.

Option A, export: ask the owner to open YouTube Studio, go to Analytics, then the Audience tab. They pick a date range (the last 90 days is a good default), then share a screenshot or export of age, gender and top countries.

Option B, read-only access: the owner opens YouTube Studio and goes to Settings, then Permissions, then Invite. They enter the human's Google account email and choose the Viewer (Limited) role. That role can see analytics but not revenue. Invites expire after 30 days. When the job ends, the owner removes the access from the same screen. Brand Account channels must move to channel permissions first.

## Route 2: the YouTube Analytics API (repeat or larger jobs)

Use this when the owner, or their team, will run it, or for an ongoing engagement with a written consent.

1. In Google Cloud, create a project. Enable the YouTube Analytics API and the YouTube Data API v3.
2. Set up the OAuth consent screen: user type External, publishing status Testing. Add the owner's Google account as a test user.
3. Create an OAuth client ID of type Desktop app and download the client file. Treat it as a secret.
4. Request these scopes only:
   - `https://www.googleapis.com/auth/yt-analytics.readonly`
   - `https://www.googleapis.com/auth/youtube.readonly` (the `reports.query` reference now requires it as well)
   - Add `yt-analytics-monetary.readonly` only if the owner agrees to share revenue.
5. Run the sign-in on the machine where the owner signs in themselves. For example:

```python
# pip install google-auth-oauthlib requests
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly",
          "https://www.googleapis.com/auth/youtube.readonly"]
creds = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES).run_local_server(port=0)
base = "https://youtubeanalytics.googleapis.com/v2/reports"
common = {"ids": "channel==MINE", "startDate": "2026-08-01", "endDate": "2026-10-31"}
auth = {"Authorization": f"Bearer {creds.token}"}
age_gender = requests.get(base, headers=auth, params={**common,
    "metrics": "viewerPercentage", "dimensions": "ageGroup,gender"}).json()
countries = requests.get(base, headers=auth, params={**common,
    "metrics": "views,estimatedMinutesWatched", "dimensions": "country",
    "sort": "-views", "maxResults": 10}).json()
```

6. The owner picks the right channel when Google asks. `channel==MINE` means the channel they signed in as.
7. Read `columnHeaders` and `rows`. `viewerPercentage` covers only viewers who were signed in. When there is no data, YouTube leaves out `rows`. Report that as "not available", never as zero.
8. Hold the token in memory only. Afterwards, revoke it: the owner can do this at myaccount.google.com/permissions. A Testing app's refresh tokens also expire after 7 days.

## Route 3: a paid estimate (Influencers Club MCP)

Influencers Club estimates audience demographics for public YouTube channels. It is a third-party model, not YouTube data. Each lookup spends credits.

1. Run `check_credits` (free) and note the balance.
2. Tell the human the tool and its cost, then wait for a yes. Costs from the server README, checked 5 November 2026: `enrich_by_handle_analytics` is 0.8 credits and returns audience demographics. `enrich_by_handle` is 1 credit; on older servers, pass `include_audience_data` true for the audience section. `enrich_by_handle_raw` is 0.03 credits and has no audience data. Read the tool's own description first, because versions differ.
3. Make one call for the one channel, with `platform` set to `youtube` and `handle` set to the handle or channel ID.
4. If any call returns a limit or credit error, stop. Do not retry, and report how many lookups were done.
5. Do not use `get_audience_locations` or `get_audience_interests` for this. They are free lists of filter values, not the creator's audience.

Label the result "estimated by Influencers Club", give the lookup date, and never mix it with owner figures without saying which is which.

## What to write in the brief

- The source of each figure: owner's YouTube Analytics with its date range, owner's Studio export, or a third-party estimate.
- Age and gender shares for signed-in viewers, and the top countries by views.
- If there is no consent and no approved spend, write "Audience demographics: not available without the owner's analytics or a paid estimate." That is a complete answer.

Checked 5 November 2026 against the YouTube Analytics API reference, metrics and authorisation pages, YouTube Help on channel permissions, and the Influencers Club MCP README and usage limits.
