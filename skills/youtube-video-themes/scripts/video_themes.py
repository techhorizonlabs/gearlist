#!/usr/bin/env python3
"""Find recurring topics and opening hooks in a creator's YouTube videos.

Transcripts come from the youtube-transcript-api library, or from caption
files the human supplies with --transcript-dir. Topics are a plain count of
stopword-filtered phrases (n-grams), not a topic model. With --for-agent the
script skips counting and prints the transcripts for the agent's own model.
Nothing is written to disk.

Usage:
    python3 channel_profile.py @handle --json | python3 video_themes.py --from-profile - --pick top -n 5
    python3 video_themes.py --videos VIDEO_ID [VIDEO_ID ...]
    python3 video_themes.py --transcript-dir ./captions
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

STOPWORDS = set("""
a about above after again against all also am an and any are aren't as at be
because been before being below between both but by can can't cannot could
couldn't did didn't do does doesn't doing don't down during each few for from
further had hadn't has hasn't have haven't having he he'd he'll he's her here
here's hers herself him himself his how how's i i'd i'll i'm i've if in into is
isn't it it's its itself let's me more most mustn't my myself no nor not of off
on once only or other ought our ours ourselves out over own same shan't she
she'd she'll she's should shouldn't so some such than that that's the their
theirs them themselves then there there's these they they'd they'll they're
they've this those through to too under until up very was wasn't we we'd we'll
we're we've were weren't what what's when when's where where's which while who
who's whom why why's will with won't would wouldn't you you'd you'll you're
you've your yours yourself yourselves
""".split())

# Spoken filler and YouTube boilerplate. Edit this set for a niche where one of
# these words is the topic (a channel about video editing needs "video").
SPOKEN_FILLER = set("""
um uh umm uhh er ah oh okay ok yeah yes yep yup like just really actually
basically literally gonna wanna gotta kinda sorta right well know mean thing
things stuff lot lots little bit going get gets got go goes went make makes
made say says said see look looking want need even still now today way much
many something anything everything every kind sort guys hey hi hello welcome
video videos channel subscribe music applause laughter thank thanks one two
three back come take put let lets there's that's we're you're i'm it's don't
""".split())

STOP = STOPWORDS | SPOKEN_FILLER
ANNOTATION_RE = re.compile(r"\[[^\]]*\]|\([^)]*\)")
TOKEN_RE = re.compile(r"[^\W_]+(?:'[^\W_]+)?")
TIMESTAMP_RE = re.compile(
    r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})\s*-->\s*"
)
TAG_RE = re.compile(r"<[^>]+>")
VIDEO_ID_IN_NAME_RE = re.compile(r"\[([A-Za-z0-9_-]{11})\]")

STATUS = {
    "TranscriptsDisabled": "captions are turned off for this video",
    "NoTranscriptFound": "no transcript in the requested languages",
    "VideoUnavailable": "video unavailable",
    "InvalidVideoId": "not a valid video ID",
    "VideoUnplayable": "video cannot be played",
    "AgeRestricted": "age restricted, needs a signed-in session (not supported here)",
    "PoTokenRequired": "YouTube wants a token this library cannot supply",
    "IpBlocked": "blocked by YouTube (rate limited, or a cloud IP)",
    "RequestBlocked": "blocked by YouTube (rate limited, or a cloud IP)",
    "YouTubeRequestFailed": "request to YouTube failed",
}
BLOCKED = {"IpBlocked", "RequestBlocked"}

AGENT_INSTRUCTIONS = (
    "Read these transcripts and list the recurring topics across videos, the "
    "promises each video makes in its first minute, and the formats the creator "
    "repeats. Quote short phrases as evidence and give the video ID for each. "
    "Auto-generated captions contain recognition errors, so do not quote names "
    "or numbers from them without checking the video."
)


# ---------------------------------------------------------------- text


def tokenise(text):
    text = ANNOTATION_RE.sub(" ", text.replace("\u2019", "'").lower())
    return TOKEN_RE.findall(text)


def count_phrases(tokens, sizes=(1, 2, 3), stop=STOP):
    """Count n-grams that do not start or end with a stopword."""
    counts = Counter()
    for n in sizes:
        for i in range(len(tokens) - n + 1):
            gram = tokens[i:i + n]
            if gram[0] in stop or gram[-1] in stop:
                continue
            if n == 1 and (len(gram[0]) < 3 or gram[0].isdigit()):
                continue
            if n > 1 and len(set(gram)) == 1:
                continue
            counts[" ".join(gram)] += 1
    return counts


def drop_subsumed(rows):
    """Drop a phrase when a longer phrase containing it has the same counts."""
    def key(r):
        return (r.get("videos"), r["mentions"])
    kept = []
    for r in rows:
        inner = f" {r['phrase']} "
        if not any(o is not r and inner in f" {o['phrase']} " and key(o) == key(r) for o in rows):
            kept.append(r)
    return kept


def recurring(per_video, top=15, words=1):
    """Rank phrases by how many videos use them, then by total mentions."""
    videos_using, mentions = Counter(), Counter()
    for counts in per_video:
        for phrase, n in counts.items():
            if (len(phrase.split()) == 1) != (words == 1):
                continue
            videos_using[phrase] += 1
            mentions[phrase] += n
    min_videos = 2 if len(per_video) > 1 else 1
    ranked = sorted(
        (p for p in videos_using if videos_using[p] >= min_videos and mentions[p] >= 2),
        key=lambda p: (-videos_using[p], -mentions[p], p),
    )
    rows = [{"phrase": p, "videos": videos_using[p], "mentions": mentions[p]} for p in ranked]
    return drop_subsumed(rows)[:top]


def hook_text(snippets, seconds=60):
    """Text spoken in the first `seconds`. Untimed text gives the first 150 words."""
    if snippets and all(s.get("start") is None for s in snippets):
        words = " ".join(s["text"] for s in snippets).split()
        return " ".join(words[:150])
    parts = [s["text"] for s in snippets if s.get("start") is not None and s["start"] < seconds]
    return re.sub(r"\s+", " ", ANNOTATION_RE.sub(" ", " ".join(parts))).strip()


def full_text(snippets):
    return re.sub(r"\s+", " ", " ".join(s["text"] for s in snippets)).strip()


# ---------------------------------------------------------------- sources


def fetch_transcripts(videos, languages, api=None, delay=1.0, sleep=time.sleep):
    """Fetch transcripts one by one. Stops early if YouTube blocks requests."""
    if api is None:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
        except ImportError:
            raise SystemExit(
                "youtube-transcript-api is not installed. Run: pip install -r requirements.txt"
            )
        api = YouTubeTranscriptApi()
    results, blocked = [], False
    for i, video in enumerate(videos):
        base = {"id": video["id"], "title": video.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={video['id']}",
                "views": video.get("views"), "published_at": video.get("published_at")}
        if blocked:
            results.append({**base, "status": "skipped",
                            "reason": "skipped after YouTube blocked an earlier request"})
            continue
        if i and delay:
            sleep(delay)
        try:
            fetched = api.fetch(video["id"], languages=languages)
        except Exception as exc:  # the library raises one class per failure
            name = type(exc).__name__
            blocked = name in BLOCKED
            results.append({**base, "status": "failed", "error": name,
                            "reason": STATUS.get(name, "could not fetch the transcript")})
            continue
        snippets = [{"text": s.text, "start": float(s.start), "duration": float(s.duration)}
                    for s in fetched]
        results.append({**base, "status": "ok", "source": "youtube-transcript-api",
                        "language": getattr(fetched, "language_code", None),
                        "auto_generated": getattr(fetched, "is_generated", None),
                        "snippets": snippets})
    return results


def _cue_start(match):
    hours, minutes, seconds, millis = match.groups()
    return int(hours or 0) * 3600 + int(minutes) * 60 + int(seconds) + int(millis.ljust(3, "0")) / 1000


def parse_caption_file(text, suffix):
    """Parse .vtt or .srt into timed snippets; anything else is untimed text."""
    if suffix not in (".vtt", ".srt"):
        return [{"text": line.strip(), "start": None, "duration": None}
                for line in text.splitlines() if line.strip()]
    snippets, start, last = [], None, None
    for line in text.splitlines():
        line = line.strip()
        match = TIMESTAMP_RE.match(line)
        if match:
            start = _cue_start(match)
            continue
        if not line or start is None or line.isdigit() or line.startswith(("WEBVTT", "NOTE", "Kind:", "Language:")):
            continue
        clean = TAG_RE.sub("", line).strip()
        if clean and clean != last:  # auto captions repeat rolling lines
            snippets.append({"text": clean, "start": start, "duration": None})
            last = clean
    return snippets


def read_transcript_dir(folder):
    results = []
    for path in sorted(Path(folder).iterdir()):
        if path.suffix.lower() not in (".vtt", ".srt", ".txt") or not path.is_file():
            continue
        match = VIDEO_ID_IN_NAME_RE.search(path.name)
        vid = match.group(1) if match else path.name.split(".")[0]
        snippets = parse_caption_file(path.read_text(encoding="utf-8", errors="replace"),
                                      path.suffix.lower())
        results.append({"id": vid, "title": path.stem, "url": f"https://www.youtube.com/watch?v={vid}",
                        "views": None, "published_at": None, "status": "ok" if snippets else "failed",
                        "reason": None if snippets else "file has no caption text",
                        "source": f"local file {path.name}", "language": None,
                        "auto_generated": None, "snippets": snippets})
    return results


def select_from_profile(profile, pick="top", n=5, fmt="any"):
    videos = [v for v in profile.get("videos", [])
              if v.get("live_status", "none") == "none" and v.get("views") is not None]
    if fmt != "any":
        videos = [v for v in videos if v.get("format") == fmt]
    if pick == "top":
        videos.sort(key=lambda v: v["views"], reverse=True)
    else:
        videos.sort(key=lambda v: v.get("published_at") or "", reverse=True)
    return videos[:n]


# ---------------------------------------------------------------- analysis


def analyse(results, hook_seconds=60, top=15):
    ok = [r for r in results if r["status"] == "ok"]
    per_video = []
    for r in ok:
        counts = count_phrases(tokenise(full_text(r["snippets"])))
        per_video.append(counts)
        repeated = [{"phrase": p, "mentions": c}
                    for p, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
                    if len(p.split()) > 1 and c >= 2]
        r["top_phrases"] = drop_subsumed(repeated)[:8]
        r["hook"] = hook_text(r["snippets"], hook_seconds)
        r["words"] = len(tokenise(full_text(r["snippets"])))
    return {
        "recurring_phrases": recurring(per_video, top=top, words=2),
        "recurring_words": recurring(per_video, top=top, words=1),
    }


def build_report(results, channel_title=None, hook_seconds=60, for_agent=False, max_chars=15000):
    ok = [r for r in results if r["status"] == "ok"]
    report = {
        "channel": channel_title,
        "mode": "agent" if for_agent else "local-count",
        "transcripts_requested": len(results),
        "transcripts_fetched": len(ok),
        "auto_generated": sum(1 for r in ok if r.get("auto_generated")),
        "hook_seconds": hook_seconds,
        "method": (
            "Transcripts passed to the agent's own model; no local counting."
            if for_agent else
            "Counts of 1 to 3 word phrases after removing English stopwords and "
            "spoken filler. Ranked by how many videos use a phrase, then by mentions. "
            "This is a word count, not a topic model."
        ),
        "not_fetched": [{"id": r["id"], "title": r["title"], "reason": r.get("reason")}
                        for r in results if r["status"] != "ok"],
    }
    if for_agent:
        report["instructions"] = AGENT_INSTRUCTIONS
        report["videos"] = []
        for r in ok:
            text = full_text(r["snippets"])
            report["videos"].append({
                "id": r["id"], "title": r["title"], "url": r["url"], "views": r["views"],
                "language": r.get("language"), "auto_generated": r.get("auto_generated"),
                "hook": hook_text(r["snippets"], hook_seconds),
                "transcript": text[:max_chars] + (" [truncated]" if len(text) > max_chars else ""),
            })
        return report
    report.update(analyse(results, hook_seconds))
    report["videos"] = [
        {k: r.get(k) for k in ("id", "title", "url", "views", "published_at", "source",
                               "language", "auto_generated", "words", "top_phrases", "hook")}
        for r in ok
    ]
    return report


def render_markdown(report):
    title = report["channel"] or "selected videos"
    lines = [
        f"# Content themes: {title}",
        "",
        f"Transcripts: {report['transcripts_fetched']} of {report['transcripts_requested']} fetched, "
        f"{report['auto_generated']} auto-generated. Auto captions contain recognition errors.",
        f"Method: {report['method']}",
        "",
    ]
    if report["mode"] == "agent":
        lines += ["## Instructions for the agent", "", report["instructions"], ""]
        for v in report["videos"]:
            lines += [f"## {v['title'] or v['id']}", "", f"{v['url']} | views {v['views'] if v['views'] is not None else 'n/a'} | "
                      f"captions: {'auto-generated' if v['auto_generated'] else 'uploaded or unknown'}, {v['language'] or 'n/a'}",
                      "", f"Hook (first {report['hook_seconds']} s): {v['hook']}", "", "Transcript:", "", v["transcript"], ""]
    else:
        for heading, key in (("Recurring phrases across videos", "recurring_phrases"),
                             ("Recurring words across videos", "recurring_words")):
            lines += [f"## {heading}", "", "| Phrase | Videos | Mentions |", "| --- | --- | --- |"]
            rows = report[key] or []
            lines += [f"| {r['phrase']} | {r['videos']} | {r['mentions']} |" for r in rows]
            if not rows:
                lines.append("| none found | | |")
            lines.append("")
        lines += ["## Per video", ""]
        for v in report["videos"]:
            caps = "auto-generated" if v["auto_generated"] else ("uploaded" if v["auto_generated"] is False else "unknown")
            phrases = ", ".join(f"{p['phrase']} ({p['mentions']})" for p in v["top_phrases"]) or "none repeated"
            lines += [
                f"### {v['title'] or v['id']}",
                "",
                f"{v['url']} | views {v['views'] if v['views'] is not None else 'n/a'} | "
                f"{(v['published_at'] or 'n/a')[:10]} | captions: {caps}, {v['language'] or 'n/a'} | {v['words']} words",
                "",
                f"Top phrases: {phrases}",
                "",
                f"Hook (first {report['hook_seconds']} s): {v['hook'] or '(no speech in the first minute)'}",
                "",
            ]
    if report["not_fetched"]:
        lines += ["## Not fetched", ""]
        lines += [f"- {r['id']}{' (' + r['title'] + ')' if r['title'] else ''}: {r['reason']}"
                  for r in report["not_fetched"]]
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------- main


def build_parser():
    ap = argparse.ArgumentParser(description="Recurring topics and first-minute hooks from YouTube transcripts.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-profile", metavar="FILE", help="JSON from channel_profile.py --json, or - for stdin")
    src.add_argument("--videos", nargs="+", metavar="VIDEO_ID", help="Video IDs to fetch")
    src.add_argument("--transcript-dir", metavar="DIR", help="Folder of .vtt, .srt or .txt captions the human supplied")
    ap.add_argument("--pick", choices=("top", "latest"), default="top", help="With --from-profile: top by views or latest")
    ap.add_argument("-n", type=int, default=5, help="Videos to fetch with --from-profile (default 5, max 25)")
    ap.add_argument("--format", choices=("any", "long", "short"), default="any", help="Filter by the Shorts heuristic")
    ap.add_argument("--languages", nargs="+", default=["en"], help="Transcript languages in order of preference")
    ap.add_argument("--hook-seconds", type=int, default=60, help="Length of the opening hook (default 60)")
    ap.add_argument("--delay", type=float, default=1.5, help="Seconds between transcript requests (default 1.5)")
    ap.add_argument("--for-agent", action="store_true", help="Print transcripts for the agent's own model instead of counting")
    ap.add_argument("--max-chars", type=int, default=15000, help="Transcript characters per video with --for-agent")
    ap.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    return ap


def main(argv=None, api=None, stdin=None, stdout=None, sleep=time.sleep):
    stdout = stdout or sys.stdout
    args = build_parser().parse_args(argv)
    if not 1 <= args.n <= 25:
        print("Error: -n must be between 1 and 25.", file=sys.stderr)
        return 2
    channel_title = None
    if args.transcript_dir:
        if not Path(args.transcript_dir).is_dir():
            print(f"Error: {args.transcript_dir} is not a folder.", file=sys.stderr)
            return 2
        results = read_transcript_dir(args.transcript_dir)
    else:
        if args.from_profile:
            try:
                raw = (stdin or sys.stdin).read() if args.from_profile == "-" else Path(args.from_profile).read_text()
                profile = json.loads(raw)
            except (OSError, ValueError) as exc:
                print(f"Error: could not read the profile JSON ({exc}). Run channel_profile.py with --json.",
                      file=sys.stderr)
                return 2
            channel_title = (profile.get("channel") or {}).get("title")
            videos = select_from_profile(profile, args.pick, args.n, args.format)
        else:
            videos = [{"id": v} for v in args.videos]
        if not videos:
            print("Error: no videos to fetch.", file=sys.stderr)
            return 2
        results = fetch_transcripts(videos, args.languages, api=api, delay=args.delay, sleep=sleep)
    report = build_report(results, channel_title, args.hook_seconds, args.for_agent, args.max_chars)
    if args.json:
        json.dump(report, stdout, indent=2, ensure_ascii=False)
        stdout.write("\n")
    else:
        stdout.write(render_markdown(report))
    return 0 if report["transcripts_fetched"] else 1


if __name__ == "__main__":
    sys.exit(main())
