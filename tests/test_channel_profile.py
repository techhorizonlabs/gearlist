"""Offline tests for skills/youtube-channel-profile/scripts/channel_profile.py.

HTTP is replaced by a fake session that serves the fixture JSON in
tests/fixtures. No network calls and no real API key.
"""

import copy
import importlib.util
import io
import json
import os
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
FAKE_KEY = "test-key-not-real-12345"
NOW = datetime(2026, 11, 5, 0, 0, tzinfo=timezone.utc)


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cp = load_module("channel_profile", "skills/youtube-channel-profile/scripts/channel_profile.py")


def fixture(name):
    return json.loads((FIXTURES / name).read_text())


class FakeResponse:
    def __init__(self, status, payload):
        self.status_code = status
        self._payload = payload

    def json(self):
        return copy.deepcopy(self._payload)


class FakeSession:
    """Routes Data API calls by endpoint name to fixture payloads."""

    def __init__(self, routes):
        self.routes = routes
        self.requests = []

    def get(self, url, params=None, timeout=None):
        endpoint = url.rsplit("/", 1)[-1]
        self.requests.append((endpoint, dict(params or {})))
        route = self.routes[endpoint]
        status, payload = route(params) if callable(route) else route
        return FakeResponse(status, payload)


def playlist_route(items_fixture="playlist_items_example.json"):
    items = fixture(items_fixture)["items"]

    def route(params):
        start = int(params.get("pageToken") or 0)
        size = int(params["maxResults"])
        page = items[start:start + size]
        body = {"kind": "youtube#playlistItemListResponse", "items": page,
                "pageInfo": {"totalResults": len(items), "resultsPerPage": size}}
        if start + size < len(items):
            body["nextPageToken"] = str(start + size)
        return 200, body
    return route


def videos_route(params):
    wanted = params["id"].split(",")
    by_id = {v["id"]: v for v in fixture("videos_example.json")["items"]}
    return 200, {"kind": "youtube#videoListResponse", "items": [by_id[i] for i in wanted if i in by_id]}


def example_routes(**overrides):
    routes = {
        "channels": (200, fixture("channels_example.json")),
        "playlistItems": playlist_route(),
        "videos": videos_route,
        "search": (200, fixture("search_example.json")),
    }
    routes.update(overrides)
    return routes


def run_main(argv, session):
    out, err = io.StringIO(), io.StringIO()
    with mock.patch.dict(os.environ, {"YOUTUBE_API_KEY": FAKE_KEY}):
        code = cp.main(argv, session=session, now=NOW, stdout=out, stderr=err)
    return code, out.getvalue(), err.getvalue()


def example_profile(limit=50, session=None):
    session = session or FakeSession(example_routes())
    client = cp.YouTubeClient(FAKE_KEY, session=session)
    return cp.build_profile(client, "@examplechannel", limit, now=NOW), session


class ParseInputTests(unittest.TestCase):
    def test_forms(self):
        cid = "UCEXAMPLEchannel00000001"
        self.assertEqual(cp.parse_channel_input(cid), ("id", cid))
        self.assertEqual(cp.parse_channel_input("@examplechannel"), ("handle", "@examplechannel"))
        self.assertEqual(cp.parse_channel_input("examplechannel"), ("handle", "@examplechannel"))
        self.assertEqual(cp.parse_channel_input("https://www.youtube.com/@examplechannel/videos"),
                         ("handle", "@examplechannel"))
        self.assertEqual(cp.parse_channel_input(f"youtube.com/channel/{cid}"), ("id", cid))
        self.assertEqual(cp.parse_channel_input("https://www.youtube.com/user/ExampleUser"),
                         ("username", "ExampleUser"))
        self.assertEqual(cp.parse_channel_input("https://www.youtube.com/c/ExampleCustom"),
                         ("custom", "ExampleCustom"))

    def test_video_links_are_rejected(self):
        for link in ("https://www.youtube.com/watch?v=EXAMPLEv002", "https://youtu.be/EXAMPLEv002",
                     "https://www.youtube.com/shorts/EXAMPLEv003"):
            with self.assertRaises(cp.InputError):
                cp.parse_channel_input(link)


class DurationAndShortsTests(unittest.TestCase):
    def test_parse_duration(self):
        self.assertEqual(cp.parse_duration("PT3M"), 180)
        self.assertEqual(cp.parse_duration("PT1H2M3S"), 3723)
        self.assertEqual(cp.parse_duration("P1DT1S"), 86401)
        self.assertEqual(cp.parse_duration("P0D"), 0)
        self.assertIsNone(cp.parse_duration("three minutes"))

    def test_shorts_heuristic_boundary(self):
        self.assertEqual(cp.classify_format(180), "short")
        self.assertEqual(cp.classify_format(181), "long")
        self.assertEqual(cp.classify_format(59), "short")
        self.assertEqual(cp.classify_format(0), "unknown")
        self.assertEqual(cp.classify_format(None), "unknown")

    def test_split_is_labelled_a_heuristic(self):
        profile, _ = example_profile()
        formats = profile["derived"]["formats"]
        self.assertEqual(formats["short"]["count"], 6)  # includes the 180 s video
        self.assertEqual(formats["long"]["count"], 17)  # includes the 181 s video
        self.assertEqual(formats["short"]["median_views"], 65000)
        self.assertIn("Heuristic", formats["method"])


class CadenceTests(unittest.TestCase):
    def test_median_gap_and_monthly_rate(self):
        newest = datetime(2026, 11, 1, tzinfo=timezone.utc)
        dates = [newest, newest - timedelta(days=2), newest - timedelta(days=6), newest - timedelta(days=12)]
        result = cp.compute_cadence(dates, NOW)
        self.assertEqual(result["median_days_between_uploads"], 4.0)  # gaps 2, 4, 6
        self.assertEqual(result["uploads_per_month"], round(3 / 12 * 30.44, 2))
        self.assertEqual(result["days_since_last_upload"], 4.0)
        self.assertEqual(result["uploads_last_30_days"], 4)

    def test_single_upload_has_no_gap(self):
        result = cp.compute_cadence([NOW - timedelta(days=1)], NOW)
        self.assertIsNone(result["median_days_between_uploads"])
        self.assertIsNone(result["uploads_per_month"])

    def test_fixture_cadence(self):
        cadence = example_profile()[0]["derived"]["cadence"]
        self.assertEqual(cadence["median_days_between_uploads"], 3.0)
        self.assertEqual(cadence["uploads_per_month"], 10.15)
        self.assertEqual(cadence["days_since_last_upload"], 1.7)
        self.assertEqual(cadence["uploads_last_30_days"], 10)


class EngagementTests(unittest.TestCase):
    def test_median_rate_and_exclusions(self):
        videos = [
            {"views": 1000, "likes": 40, "comments": 10},    # 0.05
            {"views": 2000, "likes": 50, "comments": 10},    # 0.03
            {"views": 500, "likes": None, "comments": 5},    # hidden likes, left out
            {"views": 1000, "likes": 20, "comments": None},  # comments off, 0.02
            {"views": 0, "likes": 0, "comments": 0},         # no views, left out
        ]
        result = cp.compute_engagement(videos)
        self.assertEqual(result["median_rate"], 0.03)
        self.assertEqual(result["videos_used"], 3)
        self.assertEqual(result["excluded_hidden_likes"], 1)
        self.assertEqual(result["excluded_zero_views"], 1)
        self.assertEqual(result["comments_hidden_or_off_counted_as_zero"], 1)
        self.assertEqual(result["youtube_totals_for_videos_used"],
                         {"likes": 110, "comments": 20, "views": 4000})

    def test_fixture_engagement(self):
        eng = example_profile()[0]["derived"]["engagement"]
        self.assertEqual(eng["videos_used"], 22)
        self.assertEqual(eng["excluded_hidden_likes"], 1)
        self.assertEqual(eng["comments_hidden_or_off_counted_as_zero"], 1)
        self.assertEqual(eng["median_rate"], 0.042)


class EarningsTests(unittest.TestCase):
    def test_formula(self):
        result = cp.estimate_earnings(1_000_000)
        self.assertEqual(result["monthly_low_usd"], 250.00)
        self.assertEqual(result["monthly_high_usd"], 4000.00)
        self.assertEqual(result["yearly_low_usd"], 3000.00)
        self.assertEqual(result["yearly_high_usd"], 48000.00)
        self.assertIn("1,000,000 estimated monthly views / 1,000 x US$0.25 = US$250.00", result["formula"])
        self.assertIn("/ 1,000 x US$4.00 = US$4,000.00", result["formula"])
        self.assertIn("Social Blade", result["cpm_source"])
        joined = " ".join(result["excludes"])
        for word in ("sponsorships", "memberships", "shopping"):
            self.assertIn(word, joined)
        self.assertTrue(any("niche" in c and "country" in c for c in result["caveats"]))

    def test_custom_cpm(self):
        result = cp.estimate_earnings(200_000, cpm_low=1.0, cpm_high=2.5)
        self.assertEqual((result["monthly_low_usd"], result["monthly_high_usd"]), (200.0, 500.0))

    def test_fixture_monthly_views_and_earnings(self):
        derived = example_profile()[0]["derived"]
        monthly = derived["estimated_monthly_views"]
        self.assertEqual(monthly["views"], 338000)  # ten videos published in the last 30 days
        self.assertEqual(monthly["videos_counted"], 10)
        self.assertTrue(monthly["complete"])
        earn = derived["estimated_earnings"]
        self.assertEqual((earn["monthly_low_usd"], earn["monthly_high_usd"]), (84.5, 1352.0))

    def test_short_sample_is_flagged_incomplete(self):
        profile, _ = example_profile(limit=5)
        self.assertFalse(profile["derived"]["estimated_monthly_views"]["complete"])
        self.assertTrue(any("does not reach back 30 days" in n for n in profile["notes"]))


class ProfileTests(unittest.TestCase):
    def test_totals_trend_top_and_quota(self):
        profile, session = example_profile()
        self.assertEqual(profile["channel"]["title"], "Example Channel")
        self.assertEqual(profile["channel"]["subscribers"], 412000)
        self.assertEqual(profile["sample"]["live_or_upcoming_excluded"], 1)
        trend = profile["derived"]["views_trend"]
        self.assertEqual((trend["last_10_median_views"], trend["previous_10_median_views"]), (23500, 32000))
        self.assertEqual(trend["change_pct"], -26.6)
        self.assertEqual([v["id"] for v in profile["top_videos"]][:3],
                         ["EXAMPLEv013", "EXAMPLEv007", "EXAMPLEv016"])
        quota = profile["quota"]
        self.assertEqual(quota["data_api_units"], 3)
        self.assertEqual(quota["search_calls"], 0)
        self.assertEqual(quota["calls"], {"channels": 1, "playlistItems": 1, "videos": 1})
        self.assertEqual(session.requests[0][1]["forHandle"], "@examplechannel")

    def test_pagination_and_batching_count_quota(self):
        with mock.patch.object(cp, "PAGE_SIZE", 10):
            profile, _ = example_profile()
        self.assertEqual(profile["sample"]["fetched"], 24)
        self.assertEqual(profile["quota"]["calls"], {"channels": 1, "playlistItems": 3, "videos": 3})
        self.assertEqual(profile["quota"]["data_api_units"], 7)

    def test_markdown_carries_disclosure_formula_and_quota(self):
        code, out, err = run_main(["@examplechannel"], FakeSession(example_routes()))
        self.assertEqual(code, 0, err)
        self.assertIn("They are not from YouTube.", out)
        self.assertIn("338,000 estimated monthly views / 1,000 x US$0.25 = US$84.50", out)
        self.assertIn("US$84.50 to US$1,352.00 a month", out)
        self.assertIn("3 Data API units", out)
        self.assertIn("Heuristic", out)
        self.assertNotIn(FAKE_KEY, out + err)

    def test_json_output(self):
        code, out, _ = run_main(["@examplechannel", "--json"], FakeSession(example_routes()))
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["source"], "YouTube Data API v3")
        self.assertEqual(len(data["videos"]), 24)
        self.assertNotIn(FAKE_KEY, out)


class HiddenSubscriberTests(unittest.TestCase):
    def test_hidden_count_is_not_guessed(self):
        session = FakeSession(example_routes(
            channels=(200, fixture("channels_hidden_subscribers.json")),
            playlistItems=(200, {"kind": "youtube#playlistItemListResponse", "items": []}),
        ))
        client = cp.YouTubeClient(FAKE_KEY, session=session)
        profile = cp.build_profile(client, "@examplehidden", now=NOW)
        self.assertIsNone(profile["channel"]["subscribers"])
        self.assertTrue(profile["channel"]["subscribers_hidden"])
        self.assertEqual(profile["derived"]["estimated_monthly_views"]["views"], 0)
        markdown = cp.render_markdown(profile)
        self.assertIn("Hidden by the channel owner", markdown)
        self.assertIn("hides the subscriber count", markdown)


class ErrorTests(unittest.TestCase):
    def test_quota_exceeded_on_first_call(self):
        session = FakeSession(example_routes(channels=(403, fixture("error_quota_exceeded.json"))))
        code, out, err = run_main(["@examplechannel"], session)
        self.assertEqual(code, cp.EXIT_QUOTA)
        self.assertEqual(out, "")
        self.assertIn("quotaExceeded", err)
        self.assertIn("midnight Pacific Time", err)
        self.assertIn("Quota used before the error: 1 units", err)
        self.assertNotIn("<a href", err)

    def test_quota_exceeded_mid_run(self):
        session = FakeSession(example_routes(videos=(403, fixture("error_quota_exceeded.json"))))
        code, _, err = run_main(["@examplechannel"], session)
        self.assertEqual(code, cp.EXIT_QUOTA)
        self.assertIn("3 units", err)

    def test_channel_not_found(self):
        session = FakeSession(example_routes(
            channels=(200, fixture("channels_empty.json")),
            search=(200, {"kind": "youtube#searchListResponse", "items": []}),
        ))
        code, _, err = run_main(["@nobodyhere"], session)
        self.assertEqual(code, cp.EXIT_INPUT)
        self.assertIn("No YouTube channel matches", err)

    def test_search_fallback_is_flagged(self):
        def channels(params):
            return 200, fixture("channels_empty.json" if "forHandle" in params else "channels_example.json")

        profile, session = example_profile(session=FakeSession(example_routes(channels=channels)))
        self.assertTrue(profile["resolved_by"].startswith("search.list fallback"))
        self.assertEqual(profile["quota"]["search_calls"], 1)
        self.assertTrue(any("found by search" in n for n in profile["notes"]))

    def test_no_search_flag(self):
        session = FakeSession(example_routes(channels=(200, fixture("channels_empty.json"))))
        code, _, _ = run_main(["@examplechannel", "--no-search"], session)
        self.assertEqual(code, cp.EXIT_INPUT)
        self.assertNotIn("search", [r[0] for r in session.requests])

    def test_invalid_key(self):
        session = FakeSession(example_routes(channels=(400, fixture("error_key_invalid.json"))))
        code, _, err = run_main(["@examplechannel"], session)
        self.assertEqual(code, cp.EXIT_API)
        self.assertIn("API key not valid", err)

    def test_missing_key_makes_no_call(self):
        session = FakeSession(example_routes())
        err = io.StringIO()
        with mock.patch.dict(os.environ, {}, clear=True):
            code = cp.main(["@examplechannel"], session=session, now=NOW, stdout=io.StringIO(), stderr=err)
        self.assertEqual(code, cp.EXIT_INPUT)
        self.assertIn("YOUTUBE_API_KEY is not set", err.getvalue())
        self.assertEqual(session.requests, [])

    def test_network_error_redacts_key(self):
        class Broken:
            def get(self, url, params=None, timeout=None):
                raise ConnectionError(f"Max retries exceeded with url: {url}?key={params['key']}")

        code, _, err = run_main(["@examplechannel"], Broken())
        self.assertEqual(code, cp.EXIT_NETWORK)
        self.assertNotIn(FAKE_KEY, err)
        self.assertIn("key=***", err)


class ReviewRegressionTests(unittest.TestCase):
    """Cases found by an independent review on 5 November 2026."""

    def test_key_redacted_from_error_reason(self):
        session = FakeSession(example_routes(channels=(403, {"error": {"errors": [{"reason": FAKE_KEY}]}})))
        code, out, err = run_main(["@examplechannel"], session)
        self.assertEqual(code, cp.EXIT_API)
        self.assertNotIn(FAKE_KEY, out + err)

    def test_key_redacted_when_body_decoding_raises(self):
        class Response:
            status_code = 500

            def json(self):
                raise RuntimeError(FAKE_KEY)

        class Session:
            def get(self, url, params=None, timeout=None):
                return Response()

        code, out, err = run_main(["@examplechannel"], Session())
        self.assertEqual(code, cp.EXIT_API)
        self.assertNotIn(FAKE_KEY, out + err)

    def test_key_redacted_from_argument_errors(self):
        code, _, err = run_main(["@examplechannel", "--videos", FAKE_KEY], FakeSession(example_routes()))
        self.assertEqual(code, cp.EXIT_INPUT)
        self.assertNotIn(FAKE_KEY, err)
        self.assertIn("***", err)

    def test_key_redacted_from_echoed_input(self):
        url = f"https://www.youtube.com/@examplechannel?key={FAKE_KEY}"
        code, out, _ = run_main([url, "--json"], FakeSession(example_routes()))
        self.assertEqual(code, 0)
        self.assertNotIn(FAKE_KEY, out)

    def test_unexpected_error_is_reported_not_raised(self):
        broken = {"kind": "youtube#videoListResponse",
                  "items": [{"id": "EXAMPLEv002", "snippet": {"publishedAt": "not a date"}}]}
        code, _, err = run_main(["@examplechannel"], FakeSession(example_routes(videos=(200, broken))))
        self.assertEqual(code, cp.EXIT_API)
        self.assertIn("Unexpected ValueError", err)

    def test_more_channel_inputs(self):
        self.assertEqual(cp.parse_channel_input("/user/ExampleUser"), ("username", "ExampleUser"))
        self.assertEqual(cp.parse_channel_input("/c/ExampleCustom"), ("custom", "ExampleCustom"))
        self.assertEqual(cp.parse_channel_input("YOUTUBE.COM/@examplechannel"), ("handle", "@examplechannel"))
        self.assertEqual(cp.parse_channel_input("//www.youtube.com/@examplechannel"), ("handle", "@examplechannel"))
        self.assertEqual(cp.parse_channel_input("m.youtube.com/@examplechannel/videos"), ("handle", "@examplechannel"))
        with self.assertRaises(cp.InputError):
            cp.parse_channel_input("https://example.com/@examplechannel")

    def test_fractional_seconds_are_not_rounded_into_a_short(self):
        self.assertEqual(cp.parse_duration("PT180.4S"), 180.4)
        self.assertEqual(cp.classify_format(cp.parse_duration("PT180.4S")), "long")

    def test_uploads_missing_from_videos_list_are_noted(self):
        items = fixture("playlist_items_example.json")["items"]
        items.append({"kind": "youtube#playlistItem", "contentDetails": {"videoId": "EXAMPLEv099"}})
        playlist = (200, {"kind": "youtube#playlistItemListResponse", "items": items})
        profile, _ = example_profile(session=FakeSession(example_routes(playlistItems=playlist)))
        self.assertTrue(any("not returned by videos.list" in n for n in profile["notes"]))


if __name__ == "__main__":
    unittest.main()
