#!/usr/bin/env python3
"""Profile a YouTube channel with the official YouTube Data API v3.

Reads the API key from the YOUTUBE_API_KEY environment variable and never
prints it. Writes nothing to disk. Prints a Markdown report, or JSON with
--json.

Usage:
    python3 channel_profile.py @handle
    python3 channel_profile.py https://www.youtube.com/@handle --videos 50
    python3 channel_profile.py UCxxxxxxxxxxxxxxxxxxxxxx --json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlparse

API_BASE = "https://www.googleapis.com/youtube/v3"
PAGE_SIZE = 50  # playlistItems.list and videos.list both cap at 50 per call
DAILY_UNITS = 10000  # default daily allocation for most endpoints
SEARCH_DAILY_CALLS = 100  # search.list has its own bucket since 1 June 2026
UNIT_COST = {"channels": 1, "playlistItems": 1, "videos": 1}
SHORTS_MAX_SECONDS = 180
CPM_LOW = 0.25
CPM_HIGH = 4.00
CPM_SOURCE = (
    "Social Blade's published default CPM range, US$0.25 to US$4.00 "
    "(https://socialblade.com/youtube/calculator)"
)
DAYS_PER_MONTH = 30.44
TREND_WINDOW = 10
MAX_VIDEOS = 500

CHANNEL_ID_RE = re.compile(r"^UC[0-9A-Za-z_-]{22}$")
DURATION_RE = re.compile(
    r"^P(?:(\d+)W)?(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$"
)

DISCLOSURE = (
    "Figures marked * are calculated by this script from YouTube API data. "
    "They are not from YouTube."
)

EXIT_OK = 0
EXIT_INPUT = 2
EXIT_QUOTA = 3
EXIT_API = 4
EXIT_NETWORK = 5


class ProfileError(Exception):
    exit_code = EXIT_API


class InputError(ProfileError):
    exit_code = EXIT_INPUT


class ChannelNotFound(ProfileError):
    exit_code = EXIT_INPUT


class NetworkError(ProfileError):
    exit_code = EXIT_NETWORK


class ApiError(ProfileError):
    exit_code = EXIT_API

    def __init__(self, status, reason, message):
        self.status = status
        self.reason = reason
        super().__init__(f"YouTube API error {status} ({reason}): {message}")


class QuotaExceeded(ApiError):
    exit_code = EXIT_QUOTA


QUOTA_REASONS = {"quotaExceeded", "dailyLimitExceeded"}


# ---------------------------------------------------------------- API client


class YouTubeClient:
    """Thin wrapper over the Data API that counts quota as it goes."""

    def __init__(self, api_key, session=None, timeout=20):
        if not api_key:
            raise InputError(
                "YOUTUBE_API_KEY is not set. Ask the human to set it in the "
                "environment. Do not paste it into a prompt or a file."
            )
        if session is None:
            try:
                import requests
            except ImportError as exc:
                raise InputError(
                    "The requests library is missing. Run: pip install -r requirements.txt"
                ) from exc
            session = requests.Session()
        self._key = api_key
        self.session = session
        self.timeout = timeout
        self.units = 0
        self.search_calls = 0
        self.calls = {}

    def _redact(self, text):
        return str(text).replace(self._key, "***") if self._key else str(text)

    def get(self, endpoint, **params):
        # Count before calling: Google charges quota for failed requests too.
        if endpoint == "search":
            self.search_calls += 1
        else:
            self.units += UNIT_COST.get(endpoint, 1)
        self.calls[endpoint] = self.calls.get(endpoint, 0) + 1
        query = dict(params)
        query["key"] = self._key
        try:
            resp = self.session.get(
                f"{API_BASE}/{endpoint}", params=query, timeout=self.timeout
            )
        except Exception as exc:  # requests.RequestException and friends
            raise NetworkError(
                f"Network error calling {endpoint}.list: {self._redact(exc)}"
            ) from None
        try:
            data = resp.json()
        except Exception:  # a body that is not JSON; keep its text out of messages
            data = {}
        if resp.status_code != 200:
            raise self._api_error(endpoint, resp.status_code, data)
        return data

    def _api_error(self, endpoint, status, data):
        err = data.get("error") if isinstance(data, dict) else None
        err = err or {}
        reason = "unknown"
        for item in err.get("errors") or []:
            if item.get("reason"):
                reason = item["reason"]
                break
        for detail in err.get("details") or []:
            if reason == "unknown" and detail.get("reason"):
                reason = detail["reason"]
        reason = self._redact(reason)
        message = re.sub(r"<[^>]+>", "", self._redact(err.get("message", "")))
        if reason in QUOTA_REASONS:
            bucket = (
                "the search.list bucket (default 100 calls a day)"
                if endpoint == "search"
                else "the daily Data API quota (default 10,000 units)"
            )
            return QuotaExceeded(
                status,
                reason,
                f"{message} This project has used up {bucket}. It resets at "
                "midnight Pacific Time. Do not retry in a loop or switch keys "
                "to get around it.",
            )
        return ApiError(status, reason, message or "no message")

    def quota_summary(self):
        return {
            "data_api_units": self.units,
            "data_api_daily_default": DAILY_UNITS,
            "search_calls": self.search_calls,
            "search_daily_default_calls": SEARCH_DAILY_CALLS,
            "calls": dict(self.calls),
            "note": (
                "Each channels.list, playlistItems.list and videos.list call "
                "costs 1 unit. Since 1 June 2026 search.list is charged to its "
                "own bucket (1 unit a call, default 100 calls a day); before "
                "that one search cost 100 units. Failed calls also cost quota."
            ),
        }


# ------------------------------------------------------------- input parsing


def parse_channel_input(raw):
    """Return (kind, value). kind is id, handle, username or custom."""
    text = (raw or "").strip()
    if not text:
        raise InputError("Pass a channel URL, @handle or channel ID.")
    if CHANNEL_ID_RE.match(text):
        return "id", text
    if text.startswith("@"):
        return "handle", text
    lowered = text.lower()
    if text.startswith("/") and not text.startswith("//"):
        text = "https://www.youtube.com" + text  # a bare path such as /user/name
        lowered = text.lower()
    looks_like_url = "://" in lowered or "youtube.com" in lowered or "youtu.be" in lowered
    if not looks_like_url:
        return "handle", "@" + text
    parsed = urlparse(text if "://" in text else "https://" + text.lstrip("/"))
    host = parsed.netloc.lower().split(":")[0]
    if not (host == "youtu.be" or host == "youtube.com" or host.endswith(".youtube.com")):
        raise InputError(f"{host or text!r} is not a YouTube address.")
    parts = [unquote(p) for p in parsed.path.split("/") if p]
    if host == "youtu.be" or (parts and parts[0] in {"watch", "shorts", "embed", "live", "playlist"}):
        raise InputError(
            "That looks like a video or playlist link. Pass the channel URL, "
            "@handle or channel ID instead."
        )
    if not parts:
        raise InputError(f"No channel found in {text!r}.")
    first = parts[0]
    if first.startswith("@"):
        return "handle", first
    if first == "channel" and len(parts) > 1 and CHANNEL_ID_RE.match(parts[1]):
        return "id", parts[1]
    if first == "user" and len(parts) > 1:
        return "username", parts[1]
    if first == "c" and len(parts) > 1:
        return "custom", parts[1]
    return "custom", first


def resolve_channel(client, raw, allow_search=True):
    """Return (channel resource, how it was resolved)."""
    kind, value = parse_channel_input(raw)
    part = "snippet,statistics,contentDetails"
    method = None
    items = []
    try:
        if kind == "id":
            items = client.get("channels", part=part, id=value).get("items") or []
            method = "channel ID (channels.list id)"
        elif kind == "username":
            items = client.get("channels", part=part, forUsername=value).get("items") or []
            method = "legacy username (channels.list forUsername)"
        else:
            handle = value if value.startswith("@") else "@" + value
            items = client.get("channels", part=part, forHandle=handle).get("items") or []
            method = "handle (channels.list forHandle)"
    except ApiError as exc:
        if exc.reason != "channelNotFound" or isinstance(exc, QuotaExceeded):
            raise
        items = []
    if not items and kind != "id" and allow_search:
        query = value.lstrip("@")
        found = client.get("search", part="snippet", type="channel", q=query, maxResults=1)
        ids = []
        for item in found.get("items") or []:
            cid = (item.get("id") or {}).get("channelId") or (item.get("snippet") or {}).get("channelId")
            if cid:
                ids.append(cid)
        if ids:
            items = client.get("channels", part=part, id=ids[0]).get("items") or []
            method = (
                "search.list fallback (best match only: check the title and ID "
                "are the channel you meant)"
            )
    if not items:
        raise ChannelNotFound(f"No YouTube channel matches {raw!r}.")
    return items[0], method


# ---------------------------------------------------------------- fetching


def fetch_upload_ids(client, playlist_id, limit):
    """Return (video IDs newest first, whether the playlist was exhausted)."""
    ids, seen, token = [], set(), None
    while len(ids) < limit:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": min(PAGE_SIZE, limit - len(ids)),
        }
        if token:
            params["pageToken"] = token
        try:
            data = client.get("playlistItems", **params)
        except ApiError as exc:
            if exc.reason == "playlistNotFound" and not ids:
                return [], True  # a channel with no public uploads
            raise
        for item in data.get("items") or []:
            vid = (item.get("contentDetails") or {}).get("videoId")
            if vid and vid not in seen:
                seen.add(vid)
                ids.append(vid)
        token = data.get("nextPageToken")
        if not token:
            return ids[:limit], True
    return ids[:limit], False


def fetch_videos(client, video_ids):
    videos = []
    for start in range(0, len(video_ids), PAGE_SIZE):
        batch = video_ids[start:start + PAGE_SIZE]
        data = client.get(
            "videos", part="snippet,statistics,contentDetails", id=",".join(batch),
            maxResults=len(batch),
        )
        videos.extend(normalise_video(item) for item in data.get("items") or [])
    return videos


# ---------------------------------------------------------------- parsing


def parse_time(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_duration(value):
    """ISO 8601 duration (PT1H2M3S) to seconds. Unknown formats give None."""
    match = DURATION_RE.match(value or "")
    if not match:
        return None
    weeks, days, hours, minutes, seconds = match.groups()
    total = (
        int(weeks or 0) * 604800
        + int(days or 0) * 86400
        + int(hours or 0) * 3600
        + int(minutes or 0) * 60
        + float(seconds or 0)
    )
    return int(total) if total == int(total) else total


def _int_or_none(value):
    return int(value) if value not in (None, "") else None


def normalise_video(item):
    snippet = item.get("snippet") or {}
    stats = item.get("statistics") or {}
    details = item.get("contentDetails") or {}
    duration = parse_duration(details.get("duration"))
    return {
        "id": item.get("id"),
        "title": snippet.get("title", ""),
        "url": f"https://www.youtube.com/watch?v={item.get('id')}",
        "published_at": snippet.get("publishedAt"),
        "live_status": snippet.get("liveBroadcastContent", "none"),
        "duration_seconds": duration,
        "format": classify_format(duration),
        "views": _int_or_none(stats.get("viewCount")),
        "likes": _int_or_none(stats.get("likeCount")),
        "comments": _int_or_none(stats.get("commentCount")),
    }


# ---------------------------------------------------------------- metrics


def classify_format(duration_seconds):
    """Heuristic: 180 seconds or less counts as a Short. The API has no Shorts flag.

    A missing or zero duration (live or upcoming streams report P0D) is unknown.
    """
    if duration_seconds is None or duration_seconds == 0:
        return "unknown"
    return "short" if duration_seconds <= SHORTS_MAX_SECONDS else "long"


def _median(values):
    values = [v for v in values if v is not None]
    return statistics.median(values) if values else None


def _mean(values):
    values = [v for v in values if v is not None]
    return statistics.fmean(values) if values else None


def compute_cadence(published, now):
    """published: list of datetimes. Returns gaps in days and uploads a month."""
    dates = sorted((d for d in published if d), reverse=True)
    if not dates:
        return {"uploads_in_sample": 0, "median_days_between_uploads": None,
                "uploads_per_month": None, "days_since_last_upload": None,
                "uploads_last_30_days": 0, "method": "No uploads in the sample."}
    gaps = [(dates[i] - dates[i + 1]).total_seconds() / 86400 for i in range(len(dates) - 1)]
    span_days = (dates[0] - dates[-1]).total_seconds() / 86400
    per_month = (len(dates) - 1) / span_days * DAYS_PER_MONTH if span_days > 0 else None
    cutoff = now - timedelta(days=30)
    return {
        "uploads_in_sample": len(dates),
        "median_days_between_uploads": round(_median(gaps), 2) if gaps else None,
        "uploads_per_month": round(per_month, 2) if per_month is not None else None,
        "days_since_last_upload": round((now - dates[0]).total_seconds() / 86400, 1),
        "uploads_last_30_days": sum(1 for d in dates if d >= cutoff),
        "method": (
            f"{len(gaps)} gaps between the {len(dates)} most recent uploads. "
            "Uploads per month = gaps / days spanned x 30.44."
        ),
    }


def compute_engagement(videos):
    """Median of (likes + comments) / views per video, with YouTube's raw totals."""
    rates = []
    used_likes = used_comments = used_views = 0
    hidden_likes = zero_views = comments_off = 0
    for v in videos:
        if not v.get("views"):
            zero_views += 1
            continue
        if v.get("likes") is None:
            hidden_likes += 1
            continue
        comments = v.get("comments")
        if comments is None:
            comments_off += 1
            comments = 0
        rates.append((v["likes"] + comments) / v["views"])
        used_likes += v["likes"]
        used_comments += comments
        used_views += v["views"]
    median_rate = _median(rates)
    return {
        "median_rate": round(median_rate, 5) if median_rate is not None else None,
        "videos_used": len(rates),
        "excluded_hidden_likes": hidden_likes,
        "excluded_zero_views": zero_views,
        "comments_hidden_or_off_counted_as_zero": comments_off,
        "youtube_totals_for_videos_used": {
            "likes": used_likes, "comments": used_comments, "views": used_views,
        },
        "method": "Per video (likes + comments) / views, then the median.",
    }


def compute_format_split(videos):
    groups = {"short": [], "long": [], "unknown": []}
    for v in videos:
        groups[v["format"]].append(v)
    known = len(groups["short"]) + len(groups["long"])
    out = {}
    for name, items in groups.items():
        out[name] = {
            "count": len(items),
            "share": round(len(items) / known, 3) if known and name != "unknown" else None,
            "median_views": _median([v["views"] for v in items]),
        }
    out["method"] = (
        f"Heuristic: a video of {SHORTS_MAX_SECONDS} seconds or less is counted "
        "as a Short. The API does not say which videos are Shorts, so a short "
        "long-form video is miscounted as a Short."
    )
    return out


def compute_trend(videos_newest_first, window=TREND_WINDOW):
    views = [v["views"] for v in videos_newest_first if v.get("views") is not None]
    if len(views) < window * 2:
        return {"available": False,
                "reason": f"Needs {window * 2} published videos; the sample has {len(views)}."}
    recent = _median(views[:window])
    previous = _median(views[window:window * 2])
    change = (recent - previous) / previous * 100 if previous else None
    return {
        "available": True,
        "last_10_median_views": recent,
        "previous_10_median_views": previous,
        "change_pct": round(change, 1) if change is not None else None,
        "caveat": "Newer videos have had less time to gather views, so a fall can be age, not decline.",
    }


def estimate_monthly_views(videos, now, sample_reaches_back):
    cutoff = now - timedelta(days=30)
    recent = [v for v in videos if v["published"] and v["published"] >= cutoff]
    total = sum(v["views"] or 0 for v in recent)
    return {
        "views": total,
        "videos_counted": len(recent),
        "complete": sample_reaches_back,
        "method": (
            "Sum of the current view counts of videos published in the last 30 "
            "days. It leaves out views on older videos, so it understates a "
            "channel with a strong back catalogue, and a channel that did not "
            "upload in the last 30 days shows 0. It counts as complete when the "
            "sample reaches past 30 days, which assumes the uploads playlist lists "
            "newest first, as it usually does."
        ),
    }


def estimate_earnings(monthly_views, cpm_low=CPM_LOW, cpm_high=CPM_HIGH):
    low = monthly_views / 1000 * cpm_low
    high = monthly_views / 1000 * cpm_high
    return {
        "monthly_low_usd": round(low, 2),
        "monthly_high_usd": round(high, 2),
        "yearly_low_usd": round(low * 12, 2),
        "yearly_high_usd": round(high * 12, 2),
        "cpm_low_usd": cpm_low,
        "cpm_high_usd": cpm_high,
        "formula": (
            f"{monthly_views:,} estimated monthly views / 1,000 x US${cpm_low:.2f} "
            f"= US${low:,.2f}; / 1,000 x US${cpm_high:.2f} = US${high:,.2f}. "
            "Yearly = monthly x 12."
        ),
        "cpm_source": CPM_SOURCE,
        "excludes": [
            "sponsorships", "channel memberships", "shopping and affiliate income",
            "Super Chat, Super Thanks and other fan funding",
        ],
        "caveats": [
            "Actual RPM varies by niche, audience country, season and format.",
            "Shorts ad revenue is pooled and shared on different terms, so the range is weaker for a Shorts-heavy channel.",
            "If the channel is not in the YouTube Partner Program, ad earnings are zero.",
            "Since August 2026 YouTube counts a public view when a video starts to play, which can lift views above monetised playbacks.",
        ],
    }


def lifetime_monthly_average(channel_views, created, now):
    if not channel_views or not created:
        return None
    months = (now - created).total_seconds() / 86400 / DAYS_PER_MONTH
    return round(channel_views / months) if months >= 1 else None


# ---------------------------------------------------------------- assemble


def build_profile(client, raw, video_limit=50, allow_search=True, now=None,
                  cpm_low=CPM_LOW, cpm_high=CPM_HIGH):
    now = now or datetime.now(timezone.utc)
    channel, method = resolve_channel(client, raw, allow_search=allow_search)
    snippet = channel.get("snippet") or {}
    stats = channel.get("statistics") or {}
    uploads = ((channel.get("contentDetails") or {}).get("relatedPlaylists") or {}).get("uploads")

    hidden = bool(stats.get("hiddenSubscriberCount")) or "subscriberCount" not in stats
    subscribers = None if hidden else _int_or_none(stats.get("subscriberCount"))

    ids, exhausted = fetch_upload_ids(client, uploads, video_limit) if uploads else ([], True)
    videos = fetch_videos(client, ids)
    missing = len(ids) - len(videos)
    for v in videos:
        v["published"] = parse_time(v["published_at"])
    videos.sort(key=lambda v: v["published"] or now, reverse=True)
    published = [v for v in videos if v["live_status"] == "none"]
    excluded_live = len(videos) - len(published)

    oldest = published[-1]["published"] if published else None
    reaches_back = exhausted or (oldest is not None and oldest < now - timedelta(days=30))
    monthly = estimate_monthly_views(published, now, reaches_back)
    created = parse_time(snippet.get("publishedAt"))
    total_views = _int_or_none(stats.get("viewCount"))

    top = sorted(published, key=lambda v: v["views"] or 0, reverse=True)[:5]
    notes = []
    if hidden:
        notes.append("The channel owner hides the subscriber count, so it is not shown or estimated.")
    else:
        notes.append("YouTube rounds subscriber counts down to three significant figures.")
    if excluded_live:
        notes.append(f"{excluded_live} live or upcoming video(s) left out of the view metrics.")
    if missing > 0:
        notes.append(f"{missing} upload(s) in the playlist were not returned by videos.list "
                     "(private, deleted or blocked). They are left out.")
    if not reaches_back:
        notes.append("The sample does not reach back 30 days. Rerun with a larger --videos for a complete monthly figure.")
    if method and method.startswith("search"):
        notes.append("The channel was found by search. Check it is the right one.")

    def public(v):
        return {k: v[k] for k in ("id", "title", "url", "published_at", "live_status",
                                  "duration_seconds", "format", "views", "likes", "comments")}

    return {
        "source": "YouTube Data API v3",
        "disclosure": DISCLOSURE,
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "input": raw,
        "resolved_by": method,
        "channel": {
            "id": channel.get("id"),
            "title": snippet.get("title"),
            "custom_url": snippet.get("customUrl"),
            "url": f"https://www.youtube.com/channel/{channel.get('id')}",
            "country": snippet.get("country"),
            "created_at": snippet.get("publishedAt"),
            "subscribers": subscribers,
            "subscribers_hidden": hidden,
            "total_views": total_views,
            "public_videos": _int_or_none(stats.get("videoCount")),
        },
        "sample": {
            "requested": video_limit,
            "fetched": len(videos),
            "published_used": len(published),
            "live_or_upcoming_excluded": excluded_live,
            "newest": published[0]["published_at"] if published else None,
            "oldest": published[-1]["published_at"] if published else None,
        },
        "derived": {
            "cadence": compute_cadence([v["published"] for v in published], now),
            "median_views": _median([v["views"] for v in published]),
            "mean_views": round(_mean([v["views"] for v in published]) or 0) if published else None,
            "views_trend": compute_trend(published),
            "engagement": compute_engagement(published),
            "formats": compute_format_split(published),
            "estimated_monthly_views": monthly,
            "lifetime_monthly_average_views": lifetime_monthly_average(total_views, created, now),
            "estimated_earnings": estimate_earnings(monthly["views"], cpm_low, cpm_high),
        },
        "top_videos": [public(v) for v in top],
        "videos": [public(v) for v in videos],
        "quota": client.quota_summary(),
        "notes": notes,
    }


# ---------------------------------------------------------------- output


def _n(value):
    return "n/a" if value is None else f"{value:,.0f}"


_MD_SPECIAL = set("\\`*_[]<>#|")


def _cell(text):
    """Make third-party text (titles, handles) safe inline in Markdown: one line, markup escaped."""
    text = " ".join(str(text if text is not None else "").split())
    return "".join("\\" + ch if ch in _MD_SPECIAL else ch for ch in text)


def _duration(seconds):
    if not seconds:
        return "n/a"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def render_markdown(p):
    c, d, s = p["channel"], p["derived"], p["sample"]
    cad, eng, fmt = d["cadence"], d["engagement"], d["formats"]
    trend, mv, earn = d["views_trend"], d["estimated_monthly_views"], d["estimated_earnings"]
    subs = "Hidden by the channel owner" if c["subscribers_hidden"] else (
        f"{_n(c['subscribers'])} (YouTube rounds this down to three significant figures)")
    lines = [
        f"# YouTube channel profile: {_cell(c['title'])}",
        "",
        f"Source: YouTube Data API v3, fetched {p['generated_at']}. {p['disclosure']}",
        "",
        f"- Channel: {_cell(c['title'])} ({_cell(c['custom_url']) if c['custom_url'] else 'no handle'}), ID `{c['id']}`, {c['url']}",
        f"- Found by: {p['resolved_by']}",
        f"- Country on profile: {c['country'] or 'not set'}. Created: {(c['created_at'] or 'n/a')[:10]}",
        "",
        "## Channel totals (from YouTube)",
        "",
        "| Measure | Value |",
        "| --- | --- |",
        f"| Subscribers | {subs} |",
        f"| Total views | {_n(c['total_views'])} |",
        f"| Public videos | {_n(c['public_videos'])} |",
        "",
        f"## Recent uploads ({s['published_used']} published videos, {(s['oldest'] or 'n/a')[:10]} to {(s['newest'] or 'n/a')[:10]})",
        "",
        "| Measure | Value |",
        "| --- | --- |",
        f"| Median days between uploads* | {cad['median_days_between_uploads'] if cad['median_days_between_uploads'] is not None else 'n/a'} |",
        f"| Uploads per month* | {cad['uploads_per_month'] if cad['uploads_per_month'] is not None else 'n/a'} |",
        f"| Uploads in the last 30 days* | {cad['uploads_last_30_days']} |",
        f"| Days since last upload* | {cad['days_since_last_upload'] if cad['days_since_last_upload'] is not None else 'n/a'} |",
        f"| Median views per video* | {_n(d['median_views'])} |",
        f"| Mean views per video* | {_n(d['mean_views'])} |",
    ]
    if trend["available"]:
        change = "n/a" if trend["change_pct"] is None else f"{trend['change_pct']:+.1f}%"
        lines.append(
            f"| Views trend* | Last 10 median {_n(trend['last_10_median_views'])} vs previous 10 "
            f"median {_n(trend['previous_10_median_views'])}: {change} |")
    else:
        lines.append(f"| Views trend* | Not available. {trend['reason']} |")
    rate = "n/a" if eng["median_rate"] is None else f"{eng['median_rate'] * 100:.2f}%"
    tot = eng["youtube_totals_for_videos_used"]
    lines += [
        f"| Engagement rate* | Median {rate} over {eng['videos_used']} videos |",
        f"| Likes, comments, views for those videos (from YouTube) | {_n(tot['likes'])}, {_n(tot['comments'])}, {_n(tot['views'])} |",
        f"| Shorts (heuristic)* | {fmt['short']['count']} videos, median views {_n(fmt['short']['median_views'])} |",
        f"| Long-form (heuristic)* | {fmt['long']['count']} videos, median views {_n(fmt['long']['median_views'])} |",
        "",
        f"Cadence method: {cad['method']}",
        f"Engagement method: {eng['method']} Videos with hidden likes left out: {eng['excluded_hidden_likes']}. "
        f"Videos with comments off counted as 0 comments: {eng['comments_hidden_or_off_counted_as_zero']}.",
        f"Shorts method: {fmt['method']}",
    ]
    if trend["available"]:
        lines.append(f"Trend caveat: {trend['caveat']}")
    lines += [
        "",
        "## Top 5 recent videos by views (from YouTube)",
        "",
        "| # | Title | Published | Length | Views | Likes | Comments |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for i, v in enumerate(p["top_videos"], 1):
        lines.append(
            f"| {i} | [{_cell(v['title'])}]({v['url']}) | {(v['published_at'] or '')[:10]} | "
            f"{_duration(v['duration_seconds'])} | {_n(v['views'])} | "
            f"{'hidden' if v['likes'] is None else _n(v['likes'])} | "
            f"{'off' if v['comments'] is None else _n(v['comments'])} |")
    lines += [
        "",
        "## Estimated monthly views*",
        "",
        f"{_n(mv['views'])} views from {mv['videos_counted']} videos published in the last 30 days.",
        f"Method: {mv['method']}",
    ]
    if not mv["complete"]:
        lines.append("Incomplete: the sample does not reach back 30 days. Rerun with a larger --videos.")
    if d["lifetime_monthly_average_views"] is not None:
        lines.append(
            f"Cross-check: lifetime average of {_n(d['lifetime_monthly_average_views'])} views a month "
            "(total views / months since the channel was created).")
    lines += [
        "",
        "## Estimated ad earnings* (an estimate, not reported income)",
        "",
        f"US${earn['monthly_low_usd']:,.2f} to US${earn['monthly_high_usd']:,.2f} a month; "
        f"US${earn['yearly_low_usd']:,.2f} to US${earn['yearly_high_usd']:,.2f} a year if the last 30 days repeat.",
        "",
        f"Formula: {earn['formula']}",
        f"CPM range: {earn['cpm_source']}.",
        f"Excludes: {', '.join(earn['excludes'])}.",
        "",
        "Caveats:",
        "",
    ]
    lines += [f"- {c_}" for c_ in earn["caveats"]]
    q = p["quota"]
    calls = ", ".join(f"{k}.list x{v}" for k, v in q["calls"].items())
    lines += [
        "",
        "## Quota used",
        "",
        f"{q['data_api_units']} Data API units of the {q['data_api_daily_default']:,} daily default "
        f"({calls}). search.list calls: {q['search_calls']} of the separate {q['search_daily_default_calls']} a day.",
        q["note"],
    ]
    if p["notes"]:
        lines += ["", "## Notes", ""] + [f"- {n}" for n in p["notes"]]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- main


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError(f"{message}. Run with --help for usage.")


def _redact(text, key):
    return text.replace(key, "***") if key else text


def build_parser():
    ap = _Parser(description="Profile a YouTube channel with the official Data API v3.")
    ap.add_argument("channel", help="Channel URL, @handle or channel ID (UC...)")
    ap.add_argument("--videos", type=int, default=50, help="Recent uploads to analyse (default 50, max 500)")
    ap.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    ap.add_argument("--no-search", action="store_true", help="Do not fall back to search.list")
    ap.add_argument("--cpm-low", type=float, default=CPM_LOW, help="Low CPM in US$ (default 0.25)")
    ap.add_argument("--cpm-high", type=float, default=CPM_HIGH, help="High CPM in US$ (default 4.00)")
    return ap


def main(argv=None, session=None, now=None, stdout=None, stderr=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    key = os.environ.get("YOUTUBE_API_KEY", "")
    client = None
    try:
        args = build_parser().parse_args(argv)
        if not 1 <= args.videos <= MAX_VIDEOS:
            raise InputError(f"--videos must be between 1 and {MAX_VIDEOS}.")
        client = YouTubeClient(key, session=session)
        profile = build_profile(client, args.channel, args.videos, not args.no_search, now,
                                args.cpm_low, args.cpm_high)
    except Exception as exc:  # every message is redacted before it is printed
        code = exc.exit_code if isinstance(exc, ProfileError) else EXIT_API
        text = str(exc) if isinstance(exc, ProfileError) else f"Unexpected {type(exc).__name__}: {exc}"
        if client is not None:
            q = client.quota_summary()
            text += f" Quota used before the error: {q['data_api_units']} units, {q['search_calls']} search calls."
        print(f"Error: {_redact(text, key)}", file=stderr)
        return code
    if args.json:
        text = json.dumps(profile, indent=2, ensure_ascii=False) + "\n"
    else:
        text = render_markdown(profile)
    stdout.write(_redact(text, key))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
