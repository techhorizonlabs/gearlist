"""Offline stand-ins for data.gov.au and ABN Lookup, for the Australian business pack tests.

The fixtures in tests/fixtures/au_business were saved from real read-only calls on
7 November 2026. ABN Lookup was only ever called with an unregistered GUID, so every
ABN Lookup response that carries data is synthetic and built in the tests themselves.
"""

import importlib.util
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "au_business"
COMPANIES_ID = "5c3914e6-413e-4a2c-b890-bf8efe3eabf2"
BUSINESS_NAMES_ID = "55ad4b1c-5eeb-44ea-8b29-d410da431be3"
FAKE_GUID = "a1b2c3d4-test-guid-not-real-0000"


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LocalServer:
    """A throwaway HTTP server on 127.0.0.1 for transport tests. It never touches the internet.

    handler(path, write) is called per request; write(status, headers, chunks, delay) sends a reply.
    """

    def __init__(self, handler):
        import http.server
        import threading
        import time

        hits = self.hits = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                hits.append(self.path)
                status, headers, chunks, delay = handler(self.path)
                self.send_response(status)
                for key, value in headers.items():
                    self.send_header(key, value)
                self.end_headers()
                try:
                    for chunk in chunks:
                        self.wfile.write(chunk)
                        self.wfile.flush()
                        time.sleep(delay)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.server.block_on_close = False
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def fixture_bytes(name):
    return (FIXTURES / name).read_bytes()


def fixture_json(name):
    return json.loads(fixture_bytes(name))


def body(data):
    return json.dumps(data).encode("utf-8")


def ckan_success(records, total=None):
    """A datastore_search answer in the shape data.gov.au returned on 7 November 2026."""
    return body({"success": True, "result": {"records": records, "total": len(records) if total is None else total}})


class FakeHttp:
    """Records every URL and answers through a handler(url) -> (status, bytes)."""

    def __init__(self, handler):
        self.handler = handler
        self.urls = []

    def __call__(self, url, timeout=None):
        self.urls.append(url)
        return self.handler(url)

    def params(self, index):
        parsed = urlparse(self.urls[index])
        return parsed.path.rsplit("/", 1)[-1], {k: v[0] for k, v in parse_qs(parsed.query).items()}


def ckan_handler(routes):
    """routes maps (dataset, "filters" or "q", field) to a fixture name, (status, bytes) or a callable.

    dataset is "companies" or "business_names". package_show is answered from the saved fixtures.
    """

    def handler(url):
        parsed = urlparse(url)
        action = parsed.path.rsplit("/", 1)[-1]
        qs = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        if action == "package_show":
            key = ("package_show", qs["id"])
            if key in routes:
                return resolve(routes[key], qs)
            return 200, fixture_bytes(f"ckan_package_show_{qs['id'].replace('-', '_')}.json")
        dataset = {COMPANIES_ID: "companies", BUSINESS_NAMES_ID: "business_names"}[qs["resource_id"]]
        mode = "filters" if "filters" in qs else "q"
        (field,) = json.loads(qs[mode]).keys()
        return resolve(routes[(dataset, mode, field)], qs)

    return handler


def resolve(route, qs):
    if callable(route):
        route = route(qs)
    if isinstance(route, str):
        return 200, fixture_bytes(route)
    return route


ABN_ROUTES = {
    ("companies", "filters", "ABN"): "ckan_companies_abn_30701463961.json",
    ("business_names", "filters", "BN_ABN"): "ckan_business_names_abn_30701463961.json",
}
EMPTY_ABN_ROUTES = {
    ("companies", "filters", "ABN"): "ckan_companies_abn_99000000000.json",
    ("business_names", "filters", "BN_ABN"): "ckan_business_names_abn_99000000000.json",
}
BUNNINGS_ACN_ROUTES = {
    ("companies", "filters", "ACN"): "ckan_companies_acn_008672179.json",
    ("business_names", "filters", "BN_ABN"): "ckan_business_names_abn_26008672179.json",
}
NAME_ROUTES = {
    ("companies", "filters", "Company Name"): "ckan_companies_exact_tech_horizon_labs.json",
    ("companies", "q", "Company Name"): "ckan_companies_q_tech_horizon_labs.json",
    ("business_names", "filters", "BN_NAME"): "ckan_business_names_exact_tech_horizon_labs.json",
    ("business_names", "q", "BN_NAME"): "ckan_business_names_q_tech_horizon_labs.json",
}


def abr_details(**overrides):
    """A synthetic AbnDetails or AcnDetails answer. Field names match the live responses of 7 November 2026."""
    data = {
        "Abn": "", "AbnStatus": "", "AbnStatusEffectiveFrom": "", "Acn": "", "AddressDate": None,
        "AddressPostcode": "", "AddressState": "", "BusinessName": [], "EntityName": "",
        "EntityTypeCode": "", "EntityTypeName": "", "Gst": None, "Message": "",
    }
    data.update(overrides)
    return 200, ("c(" + json.dumps(data) + ")").encode("utf-8")


SYNTHETIC_FOUND = dict(
    Abn="99000000000", AbnStatus="Active", AbnStatusEffectiveFrom="2020-01-01",
    EntityName="SYNTHETIC TEST ENTITY", EntityTypeCode="IND", EntityTypeName="Individual/Sole Trader",
    Gst="2020-01-01", AddressState="QLD", AddressPostcode="4000", BusinessName=["SYNTHETIC TRADING"],
)
