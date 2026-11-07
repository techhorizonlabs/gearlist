"""Offline stand-ins for Companies House, SEC EDGAR and the NZBN API, for the company check pack tests.

Saved from live read-only calls on 7 November 2026 (tests/fixtures/company_registers):
- ch_401_*.json: Companies House answers to a call with no key and with a made-up key.
- nzbn_401_missing_key.json: the NZBN API answer to a call with no key.
- sec_*: SEC EDGAR answers fetched with a declared user agent. The ticker file and Apple's
  submissions record are trimmed, and contact details in them are replaced by placeholders.

No call was made with a Companies House key or an NZBN subscription key, so every Companies
House and NZBN record that carries data is synthetic. The builders below use the field names
in each API's published definition.
"""

import base64
import importlib.util
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "company_registers"
FAKE_CH_KEY = "0f0e0d0c-test-key-not-real-0000"
FAKE_NZ_KEY = "a1b2c3d4e5f60718293a4b5c6d7e8f90"
FAKE_AGENT = "Example Test Org ops@example.com"

_spec = importlib.util.spec_from_file_location("au_fakes", Path(__file__).resolve().parent / "au_fakes.py")
au = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(au)

load_module = au.load_module
LocalServer = au.LocalServer
DripServer = au.DripServer
fetch_threads = au.fetch_threads


def fixture_bytes(name):
    return (FIXTURES / name).read_bytes()


def fixture_json(name):
    return json.loads(fixture_bytes(name))


def body(data):
    return json.dumps(data).encode("utf-8")


def basic(key):
    return "Basic " + base64.b64encode((key + ":").encode()).decode()


class FakeHttp:
    """Records every URL and the extra headers, and answers through handler(url) -> (status, bytes)."""

    def __init__(self, handler):
        self.handler = handler if callable(handler) else (lambda url: handler)
        self.urls = []
        self.headers = []

    def __call__(self, url, timeout=None, headers=None):
        self.urls.append(url)
        self.headers.append(dict(headers or {}))
        return self.handler(url)

    def path(self, index):
        return urlparse(self.urls[index]).path

    def params(self, index):
        return {k: v[0] for k, v in parse_qs(urlparse(self.urls[index]).query).items()}


class HeaderServer:
    """A local HTTP server that records each request's headers and answers 200 with {}."""

    def __init__(self):
        import http.server
        import threading

        seen = self.seen = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                seen.append(dict(self.headers.items()))
                self.send_response(200)
                self.send_header("Content-Length", "2")
                self.end_headers()
                self.wfile.write(b"{}")

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


# ---------------------------------------------------------------- Companies House (synthetic)


def ch_profile(**overrides):
    """A synthetic company profile, with fields from Companies House's companyProfile definition."""
    data = {
        "company_name": "SYNTHETIC TEST TRADING LIMITED",
        "company_number": "00000006",
        "company_status": "active",
        "type": "ltd",
        "jurisdiction": "england-wales",
        "date_of_creation": "2019-03-04",
        "registered_office_address": {
            "address_line_1": "1 Example Street", "locality": "Exampletown", "postal_code": "EX1 1EX",
            "country": "England",
        },
        "sic_codes": ["62012"],
        "accounts": {"next_accounts": {"due_on": "2026-12-31", "overdue": False},
                     "last_accounts": {"period_end_on": "2025-03-31"}},
        "confirmation_statement": {"last_made_up_to": "2026-03-04", "next_due": "2027-03-18", "overdue": False},
        "can_file": True,
        "links": {"self": "/company/00000006", "filing_history": "/company/00000006/filing-history",
                  "officers": "/company/00000006/officers"},
        "etag": "synthetic",
    }
    data.update(overrides)
    return 200, body(data)


def ch_search(items, total=None):
    data = {"kind": "search#companies", "items": items, "items_per_page": 10, "start_index": 0,
            "total_results": len(items) if total is None else total}
    return 200, body(data)


def ch_item(**overrides):
    item = {
        "kind": "searchresults#company", "title": "SYNTHETIC TEST TRADING LIMITED", "company_number": "00000006",
        "company_status": "active", "company_type": "ltd", "date_of_creation": "2019-03-04",
        "address_snippet": "1 Example Street, Exampletown, EX1 1EX", "links": {"self": "/company/00000006"},
        "address": {"address_line_1": "1 Example Street"},
    }
    item.update(overrides)
    return item


# ---------------------------------------------------------------- SEC EDGAR


def sec_routes(submissions=None, tickers="sec_company_tickers_trimmed.json"):
    """Ticker file and submissions from the saved fixtures. submissions maps a CIK to (status, bytes)."""
    submissions = submissions or {}

    def handler(url):
        if url == "https://www.sec.gov/files/company_tickers.json":
            return (200, fixture_bytes(tickers)) if isinstance(tickers, str) else tickers
        cik = urlparse(url).path.rsplit("CIK", 1)[-1].split(".")[0]
        if cik in submissions:
            return submissions[cik]
        if cik == "0000320193":
            return 200, fixture_bytes("sec_submissions_CIK0000320193_trimmed.json")
        return 404, fixture_bytes("sec_404_missing_cik.xml")

    return handler


def sec_person():
    """A synthetic insider-only record: no SIC, no ticker, no state of incorporation."""
    return 200, body({
        "cik": "0009999999", "entityType": "other", "sic": "", "sicDescription": "", "tickers": [],
        "exchanges": [], "name": "SYNTHETIC PERSON NAME", "stateOfIncorporation": "",
        "insiderTransactionForOwnerExists": 1, "insiderTransactionForIssuerExists": 0,
        "addresses": {"business": {"city": "SOMEWHERE", "stateOrCountry": "NY"}},
        "filings": {"recent": {"form": ["4"], "filingDate": ["2026-11-01"]}, "files": []},
    })


# ---------------------------------------------------------------- NZBN (synthetic)


def nz_entity(**overrides):
    """A synthetic NZBN FullEntity, with fields from MBIE's NZBN v5 definition."""
    data = {
        "entityStatusCode": "50", "entityName": "SYNTHETIC TEST LIMITED", "nzbn": "9429000106078",
        "entityTypeCode": "LTD", "entityTypeDescription": "NZ Limited Company",
        "entityStatusDescription": "Registered", "registrationDate": "2015-02-03T00:00:00.000+13:00",
        "sourceRegister": "COMPANY", "sourceRegisterUniqueIdentifier": "1234567",
        "lastUpdatedDate": "2026-10-01T10:00:00.000+13:00",
        "emailAddresses": [{"emailAddress": "person@example.com", "emailPurpose": "EMAIL"}],
        "phoneNumbers": [{"phoneNumber": "5550000", "phoneAreaCode": "09"}],
        "addresses": {"links": [], "addressList": [
            {"address1": "1 Example Road", "address2": "Exampleton", "postCode": "1010", "countryCode": "NZ",
             "addressType": "REGISTERED", "startDate": "2015-02-03T00:00:00.000+13:00"},
            {"address1": "Old Office", "postCode": "1011", "countryCode": "NZ", "addressType": "REGISTERED",
             "startDate": "2010-01-01T00:00:00.000+13:00", "endDate": "2015-02-02T00:00:00.000+13:00"},
            {"address1": "PO Box 1", "postCode": "1012", "countryCode": "NZ", "addressType": "POSTAL"},
        ]},
        "industryClassifications": [{"classificationCode": "M700010", "classificationDescription": "Computer programming service"}],
        "tradingNames": [{"name": "SYNTHETIC TRADING", "startDate": "2016-01-01T00:00:00.000+13:00"},
                         {"name": "OLD TRADING NAME", "endDate": "2016-01-01T00:00:00.000+13:00"}],
        "gstNumbers": [{"gstNumber": "123-456-789", "startDate": "2015-03-01T00:00:00.000+13:00"}],
        "websites": [{"url": "https://example.com"}],
        "company-details": {
            "annualReturnLastFiled": "2026-02-10T00:00:00.000+13:00", "stockExchangeListed": False,
            "removalCommenced": False, "insolvencies": [],
            "shareholding": {"numberOfShares": 100, "shareAllocation": [{"allocation": 100, "shareholder": [
                {"type": "Individual", "individualShareholder": {"fullName": "SYNTHETIC SHAREHOLDER"},
                 "shareholderAddress": {"address1": "9 Home Street"}}]}]},
        },
        "roles": [{"roleType": "Director", "roleStatus": "ACTIVE",
                   "rolePerson": {"firstName": "SYNTHETIC", "lastName": "DIRECTOR"}}],
    }
    data.update(overrides)
    return 200, body(data)


def nz_search(items, total=None):
    return 200, body({"pageSize": 10, "page": 0, "totalItems": len(items) if total is None else total,
                      "items": items, "links": []})


def nz_item(**overrides):
    item = {"entityStatusCode": "50", "entityName": "SYNTHETIC TEST LIMITED", "nzbn": "9429000106078",
            "entityTypeCode": "LTD", "entityTypeDescription": "NZ Limited Company",
            "entityStatusDescription": "Registered", "registrationDate": "2015-02-03T00:00:00.000+13:00",
            "sourceRegisterUniqueId": "1234567", "tradingNames": [], "classifications": [],
            "previousEntityNames": ["SYNTHETIC OLD NAME LIMITED"], "links": []}
    item.update(overrides)
    return item


# ---------------------------------------------------------------- response controls
#
# SAGE's response controls for PR 21 (response_controls.py, against head 254b011). Thirteen
# answers are not a valid answer to the request, and each reader must report them as an API
# error (exit 4). Eight are healthy: three valid records (exit 0), two valid empty searches and
# three record requests answered HTTP 404 (exit 1, no match). Every body is synthetic or one of
# the saved SEC responses above.

class Control:
    def __init__(self, country, query, case, status, data, exit_code):
        self.country, self.query, self.case = country, query, case
        self.status, self.data, self.exit_code = status, data, exit_code

    @property
    def healthy(self):
        return self.exit_code != 4

    def answer(self):
        return self.status, body(self.data)

    def __repr__(self):
        return f"{self.country} {self.case}"


DIRECT = (("UK", "00000006"), ("NZ", "9429000106078"), ("US", "320193"))


def response_controls(country=None):
    apple = fixture_json("sec_submissions_CIK0000320193_trimmed.json")
    rows = []
    for code, query in DIRECT:
        rows.append(Control(code, query, "empty_object", 200, {}, 4))
        rows.append(Control(code, query, "error_object", 200, {"error": "fixture unavailable"}, 4))
    rows += [
        Control("UK", "00000006", "wrong_company_id", 200, json.loads(ch_profile(company_number="99999999")[1]), 4),
        Control("NZ", "9429000106078", "wrong_nzbn", 200, json.loads(nz_entity(nzbn="9429041234563")[1]), 4),
        Control("US", "320193", "wrong_cik", 200, dict(apple, cik="9999999999"), 4),
    ]
    for code in ("UK", "NZ"):
        rows.append(Control(code, "Synthetic Trading", "missing_search_items", 200, {}, 4))
        rows.append(Control(code, "Synthetic Trading", "invalid_search_items", 200, {"items": [{}]}, 4))
    rows += [
        Control("UK", "00000006", "valid_profile", 200, json.loads(ch_profile()[1]), 0),
        Control("NZ", "9429000106078", "valid_profile", 200, json.loads(nz_entity()[1]), 0),
        Control("US", "320193", "valid_profile", 200, apple, 0),
        Control("UK", "Synthetic Trading", "valid_empty_search", 200, json.loads(ch_search([])[1]), 1),
        Control("NZ", "Synthetic Trading", "valid_empty_search", 200, json.loads(nz_search([])[1]), 1),
    ]
    rows += [Control(code, query, "actual_404", 404, {}, 1) for code, query in DIRECT]
    return [r for r in rows if country in (None, r.country)]
