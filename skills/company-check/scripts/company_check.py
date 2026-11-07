#!/usr/bin/env python3
"""Check a company in its own country's official register, and say what ran and what did not.

Routes by country to a sibling skill's script and runs it unchanged:
    AU  au-business-check  (ASIC always; ABN Lookup when ABR_GUID is set)
    UK  uk-companies-house (needs COMPANIES_HOUSE_API_KEY)
    US  us-sec-edgar       (needs SEC_USER_AGENT)
    NZ  nz-companies-office (needs NZBN_SUBSCRIPTION_KEY)
Keys are read only by the sibling scripts, from the environment, and are never printed.
Read-only GETs, Python 3 standard library only. Prints Markdown, or JSON with --json.

Usage:
    python3 company_check.py "Tech Horizon Labs" --country AU
    python3 company_check.py 00445790 --country UK
    python3 company_check.py AAPL --country US --json
"""

from __future__ import annotations

import argparse
import base64
import importlib.util
import io
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]
INSTALL = ("npx skills add techhorizonlabs/gearlist --skill company-check --skill au-business-check "
           "--skill asic-registers --skill abn-lookup --skill uk-companies-house --skill us-sec-edgar "
           "--skill nz-companies-office")
DEFAULT_LIMIT = 10
MAX_LIMIT = 50

EXIT_OK = 0
EXIT_INPUT = 2
EXIT_NEEDS = 3
EXIT_API = 4
EXIT_NETWORK = 5

COUNTRIES = {
    "AU": {
        "name": "Australia",
        "in": "Australia",
        "skill": "au-business-check",
        "module": "business_check",
        "name_flag": "--name",
        "needs": [{"env": "ABR_GUID", "required": False,
                   "what": "a free ABN Lookup GUID. Without it the ASIC registers still run, but GST "
                           "registration, ABN status and state are not checked",
                   "get": "https://abr.business.gov.au/Tools/WebServices"}],
        "register": "ASIC's company and business names registers, and ABN Lookup",
    },
    "UK": {
        "name": "United Kingdom",
        "in": "the United Kingdom",
        "skill": "uk-companies-house",
        "module": "companies_house",
        "name_flag": "--name",
        "needs": [{"env": "COMPANIES_HOUSE_API_KEY", "required": True,
                   "what": "a free Companies House API key",
                   "get": "https://developer.company-information.service.gov.uk/"}],
        "register": "the Companies House register",
    },
    "US": {
        "name": "United States",
        "in": "the United States",
        "skill": "us-sec-edgar",
        "module": "sec_edgar",
        "name_flag": "--search",
        "needs": [{"env": "SEC_USER_AGENT", "required": True,
                   "what": "a name and contact email that the SEC asks every automated request to declare",
                   "get": "https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data"}],
        "register": "SEC EDGAR, which covers companies that file with the SEC, mostly public companies",
    },
    "NZ": {
        "name": "New Zealand",
        "in": "New Zealand",
        "skill": "nz-companies-office",
        "module": "nzbn_lookup",
        "name_flag": "--search",
        "needs": [{"env": "NZBN_SUBSCRIPTION_KEY", "required": True,
                   "what": "an NZBN API subscription key. There is no fee, but MBIE asks for a signed API "
                           "Access Agreement and approves each subscription",
                   "get": "https://portal.api.business.govt.nz/api/nzbn"}],
        "register": "the NZBN Register, which holds the Companies Office registers",
    },
}

ALIASES = {
    "AU": "AU", "AUS": "AU", "AUSTRALIA": "AU",
    "UK": "UK", "GB": "UK", "GBR": "UK", "UNITED KINGDOM": "UK", "GREAT BRITAIN": "UK", "BRITAIN": "UK",
    "ENGLAND": "UK", "SCOTLAND": "UK", "WALES": "UK", "NORTHERN IRELAND": "UK",
    "US": "US", "USA": "US", "UNITED STATES": "US", "UNITED STATES OF AMERICA": "US", "AMERICA": "US",
    "NZ": "NZ", "NZL": "NZ", "NEW ZEALAND": "NZ", "AOTEAROA": "NZ",
}

SECRET_ENVS = ("ABR_GUID", "COMPANIES_HOUSE_API_KEY", "NZBN_SUBSCRIPTION_KEY", "SEC_USER_AGENT")

USE_RULE = (
    "Use this to check a business the user deals with. Do not use it to profile people: a sole "
    "trader's or a small company's name can be a person's name.")


class CheckError(Exception):
    exit_code = EXIT_INPUT


def resolve_country(text):
    key = " ".join(re.sub(r"[^A-Za-z ]", " ", str(text or "")).upper().split())
    code = ALIASES.get(key)
    if not code:
        supported = ", ".join(f"{c} ({s['name']})" for c, s in COUNTRIES.items())
        raise CheckError(
            f"This pack has no register for {str(text or '')[:40]!r}. It covers {supported}. Ask the "
            "user which country the business is registered in.")
    return code


def load_sibling(skill, module):
    path = SKILLS_DIR / skill / "scripts" / f"{module}.py"
    if not path.is_file():
        raise CheckError(f"The {skill} skill is not installed beside this one. Install the pack: {INSTALL}")
    spec = importlib.util.spec_from_file_location(f"company_check_{module}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _form_pattern(form):
    """A regex for one form of a secret. Percent escapes match in either case (%2F and %2f)."""
    parts = re.split(r"(%[0-9A-Fa-f]{2})", form)
    return "".join(("%(?i:" + p[1:] + ")") if re.fullmatch(r"%[0-9A-Fa-f]{2}", p) else re.escape(p)
                   for p in parts)


def scrub(text, environ):
    """Belt and braces: the sibling scripts never print a key, and this removes any that slipped through,
    in every URL encoding, as the Companies House Basic token, and each email in SEC_USER_AGENT in any case."""
    exact, any_case = set(), set()
    q = urllib.parse
    for name in SECRET_ENVS:
        value = (environ.get(name) or "").strip()
        if len(value) < 4:
            continue
        values = {value} | set(re.findall(r"[^\s@<>]+@[^\s@<>]+\.[A-Za-z]{2,}", value))
        for v in values:
            target = any_case if "@" in v and name == "SEC_USER_AGENT" else exact
            target |= {v, q.quote(v), q.quote(v, safe=""), q.quote_plus(v)}
        if name == "COMPANIES_HOUSE_API_KEY":
            token = base64.b64encode((value + ":").encode("utf-8")).decode("ascii")
            exact |= {token, token.rstrip("=")}
    for forms, flags in ((exact, 0), (any_case, re.IGNORECASE)):
        forms = sorted((f for f in forms if f), key=len, reverse=True)
        if forms:
            text = re.sub("|".join(_form_pattern(f) for f in forms), "***", text, flags=flags)
    return text


def needs_status(spec, environ):
    return [dict(n, set=bool((environ.get(n["env"]) or "").strip())) for n in spec["needs"]]


def run_sibling(code, mod, argv, environ, now, fetchers, sleep):
    out, err = io.StringIO(), io.StringIO()
    if code == "AU":
        exit_code = mod.main(argv, ckan_fetch=fetchers.get("ckan"), abr_fetch=fetchers.get("abr"), now=now,
                             stdout=out, stderr=err, environ=environ)
    elif code == "UK":
        exit_code = mod.main(argv, fetch=fetchers.get("companies_house"), now=now, stdout=out, stderr=err,
                             environ=environ)
    elif code == "US":
        kwargs = {"sleep": sleep} if sleep else {}
        exit_code = mod.main(argv, fetch=fetchers.get("sec"), now=now, stdout=out, stderr=err, environ=environ,
                             **kwargs)
    else:
        exit_code = mod.main(argv, fetch=fetchers.get("nzbn"), now=now, stdout=out, stderr=err, environ=environ)
    return exit_code, out.getvalue(), err.getvalue()


def fence(text):
    """Wrap text in a message tag. Every angle bracket inside is escaped, so nothing can close it."""
    body = str(text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"<untrusted_message>\n{body}\n</untrusted_message>"


def long_date(day):
    return f"{day.day} {day.strftime('%B')} {day.year}"


def md_inline(text):
    text = " ".join(str(text if text is not None else "").split())
    return "".join("\\" + ch if ch in set("\\`*_[]<>#|") else ch for ch in text)


def outcome(code, spec, sibling_exit, missing):
    """What happened, in one line, and the exit code for company-check."""
    skill = spec["skill"]
    if missing:
        names = " and ".join(n["env"] for n in missing)
        return f"{skill} did not run: {names} is not set.", EXIT_NEEDS
    if sibling_exit in (0, 1):
        if code == "AU":
            return f"{skill} ran. Its Sources section says which registers it read.", EXIT_OK
        return f"{skill} ran." + (" It found no match." if sibling_exit == 1 else ""), EXIT_OK
    if sibling_exit == 3:
        if code == "US":
            return f"{skill} stopped: SEC_USER_AGENT must give a name and a contact email.", EXIT_NEEDS
        return f"{skill} stopped: the register did not accept the key.", EXIT_NEEDS
    if sibling_exit == 2:
        return f"{skill} stopped: it refused the input. Read its message.", EXIT_INPUT
    if sibling_exit == 5:
        return f"{skill} stopped: the register could not be reached, or did not answer in time.", EXIT_NETWORK
    return f"{skill} stopped: the register answered with an error.", EXIT_API


def render(code, spec, query, needs, line, sibling_out, sibling_err, now):
    lines = [
        "# Company check",
        "",
        f"Checked {long_date(now.date())} for {md_inline(query)} in {spec['in']}, using {spec['register']}.",
        "",
        "## What ran",
        "",
        f"- {line}",
    ]
    for n in needs:
        state = "set" if n["set"] else "not set"
        kind = "needed" if n["required"] else "optional"
        lines.append(f"- {n['env']} ({kind}): {state}. It holds {n['what']}."
                     + ("" if n["set"] else " Ask the human to set it. Do not ask them to paste it into the chat.")
                     + f" How to get one: {n['get']}")
    lines += ["- Other countries this pack covers: "
              + ", ".join(f"{c} ({s['name']})" for c, s in COUNTRIES.items() if c != code) + "."]
    if sibling_err.strip():
        # A skill's message can quote the register or the network, so all of it is fenced, on one line.
        lines += ["", "Message from the skill:", "", fence(" ".join(sibling_err.split()))]
    lines += ["", f"- {USE_RULE}", ""]
    if sibling_out.strip():
        lines += ["---", "", sibling_out.rstrip()]
    return "\n".join(lines).rstrip() + "\n"


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CheckError(f"{message}. Run with --help for usage.")


def build_parser():
    ap = _Parser(description="Check a company in its country's official register: AU, UK, US or NZ.")
    ap.add_argument("query", help="A company name, or a company number, ABN, ACN, CIK, ticker or NZBN")
    ap.add_argument("--country", required=True, help="AU, UK (or GB), US or NZ")
    ap.add_argument("--name", action="store_true", help="Search a number as a name")
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"Matches per source (default {DEFAULT_LIMIT}, max {MAX_LIMIT})")
    ap.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    return ap


def main(argv=None, fetchers=None, now=None, stdout=None, stderr=None, environ=None, sleep=None):
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    environ = os.environ if environ is None else environ
    now = now or datetime.now().astimezone()
    fetchers = fetchers or {}
    try:
        args = build_parser().parse_args(argv)
        if not 1 <= args.limit <= MAX_LIMIT:
            raise CheckError(f"--limit must be between 1 and {MAX_LIMIT}.")
        query = " ".join(str(args.query).split())
        if not query:
            raise CheckError("Give a company name or number.")
        code = resolve_country(args.country)
        spec = COUNTRIES[code]
        mod = load_sibling(spec["skill"], spec["module"])
        needs = needs_status(spec, environ)
        missing = [n for n in needs if n["required"] and not n["set"]]
        sibling_exit, sibling_out, sibling_err = None, "", ""
        if not missing:
            sub = [query, "--limit", str(args.limit)]
            if args.name:
                sub.append(spec["name_flag"])
            if args.json:
                sub.append("--json")
            sibling_exit, sibling_out, sibling_err = run_sibling(
                code, mod, sub, environ, now, fetchers, sleep)
    except CheckError as exc:
        print(scrub(f"Error: {exc}", environ), file=stderr)
        return exc.exit_code
    except Exception as exc:  # report, do not raise a traceback at the agent
        print(scrub(f"Error: unexpected {type(exc).__name__}. Details follow.\n\n" + fence(" ".join(str(exc).split())), environ), file=stderr)
        return EXIT_API
    line, exit_code = outcome(code, spec, sibling_exit, missing)
    if args.json:
        try:
            result = json.loads(sibling_out) if sibling_out.strip() else None
        except ValueError:
            result = None
        payload = {
            "checked_at": now.isoformat(timespec="seconds"),
            "query": query,
            "country": {"code": code, "name": spec["name"]},
            "skill": spec["skill"],
            "ran": exit_code == EXIT_OK,
            "outcome": line,
            "skill_exit_code": sibling_exit,
            "needs": [{k: n[k] for k in ("env", "required", "set", "what", "get")} for n in needs],
            "message": sibling_err.strip() or None,
            "use_rule": USE_RULE,
            "result": result,
        }
        text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    else:
        text = render(code, spec, query, needs, line, sibling_out, sibling_err, now)
    stdout.write(scrub(text, environ))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
