"""Priced builds (builds.json): part lists with retailer prices, and their checks.

builds.json holds build groups. Each group wraps one researched package and adds what the page
needs around it:

    id              the page address, /builds/<id>/
    group           the Gearlist group whose page links to it
    data            the researcher's package, copied as supplied: builds, a pricebook with one row
                    per retailer listing, models, notes and technical sources
    roles           pricebook id -> what the part is (Processor, Motherboard, ...)
    entries         pricebook id -> the id of a matching entry in resources.json
    model_entries   model tag -> the id of a matching entry in resources.json
    withheld        build id -> why the build is kept off the page until its data is corrected
    page            every other string the page shows: headings, column names, labels and
                    sentence templates. site/build_site.py holds no wording of its own for this page.

Nothing here is a quote, and nothing has been bought. The checks keep it that way:

    check(data, resources)   -> list of problems; build.py and site/build_site.py both refuse to
                                build when it is not empty
    money(amount)            -> "A$8,630", or "A$338.50" when there are cents
    long_date(iso)           -> "13 November 2026"
    rows_by_id(group)        -> pricebook id -> row
    build_cents(build, rows) -> the sum of a build's parts, in cents, so sums are exact
    shown_builds(group)      -> the builds the page shows, which leaves out the withheld ones
    graphics_cards(group, build) -> the pricebook rows of a build's dedicated graphics cards
    same_part_shops(group)   -> parts listed at more than one shop, each listing with how its
                                price compares
    fill(template, **values) -> a page template with its {placeholders} filled
    split_link(template)     -> the text before and after {link} in a sentence that carries a link
"""
import re
import string
from datetime import date
from urllib.parse import urlsplit

from guides import source_ok

ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
# One line of text: no control characters, and no line or paragraph separators.
NOT_ONE_LINE = re.compile("[\x00-\x1f\x7f\x85\u2028\u2029]")
DASHES = re.compile("[\u2013\u2014]")
# Prices are written A$8,630. A dollar sign without the A is refused.
BARE_DOLLAR = re.compile(r"(?<!A)\$")
MONEY = re.compile(r"A\$(\d[\d,]*(?:\.\d{2})?)")
# Words we do not use about a build. "Best" is here because Gearlist does not rank builds.
HYPE = re.compile(r"\b(seamless(?:ly)?|powerful|robust|unlock(?:s|ed|ing)?|leverag(?:e|es|ed|ing)|"
                  r"game-?chang(?:ing|er)|best)\b", re.I)
# Retailers whose listings are not published: their site terms do not allow it, or the terms
# could not be confirmed. Each is (name, the host its listings live on).
EXCLUDED_RETAILERS = (
    ("JW Computers", "jw.com.au"),
    ("Computer Alliance", "computeralliance.com.au"),
    ("RamCity", "ramcity.com.au"),
)
CURRENCY = "AUD"
STOCK_STATUSES = ("in_stock", "out_of_stock", "conditional")
# The role that marks a dedicated graphics card.
GPU_ROLE = "Graphics card"
MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

SHORT_MAX = 120   # names, roles, retailers, SKUs, stock labels, topics, page labels
NOTE_MAX = 400    # sentences: notes, conditions, trade-offs, page templates

# The researcher's top-level sentences. Each is printed on the page as written.
DATA_NOTES = ("introduction", "price_basis", "totals_exclude", "unverified", "capacity_note", "stock_note",
              "memory_note", "model_license_note", "evaluation_note", "selection_note")
BUILD_TEXT = ("name", "main_tradeoff", "upgrade_path", "verification")
ROW_SHORT = ("part", "sku", "retailer", "stock", "warranty_displayed")
ROW_NOTES = ("tax_basis", "verification", "access_notes")
MODEL_TEXT = ("tag", "quant", "purpose", "fit", "context")

# Every string the page shows that is not in the researcher's data, with the placeholders each
# template may use. site/build_site.py and build.py read these from builds.json.
PAGE_TEXT = {
    "title_tag": {"title"},
    "description": {"introduction", "low", "high", "date"},
    "og_alt": {"title", "date"},
    "og_tile_title": {"count"},
    "og_tile_text": set(),
    "checked_line": {"date"},
    "read_line": {"date"},
    "default_label": set(),
    "no_dedicated_gpu": set(),
    "compare_heading": set(),
    "parts_heading": set(),
    "shops_heading": set(),
    "pricebook_heading": set(),
    "models_heading": set(),
    "sources_heading": set(),
    "notes_heading": set(),
    "build_summary": {"name", "total"},
    "sku": {"sku"},
    "each": {"quantity", "price"},
    "total_row": set(),
    "items_line": {"items", "retailers"},
    "listing_link": set(),
    "listing_link_context": {"part", "retailer"},
    "lowest": set(),
    "equal_lowest": set(),
    "more": {"amount"},
    "integrated_graphics": {"link"},
    "integrated_graphics_link": set(),
    "withheld_note": {"names"},
    "model_entry_link": set(),
    "markdown_link": set(),
    "json_link": set(),
    "back_link": {"group"},
    "group_link": {"link", "date"},
    "llms_line": {"date"},
}
# Templates that carry one link, written {link}.
PAGE_LINKED = ("integrated_graphics", "group_link")
PAGE_COLUMNS = {"compare_columns": 5, "parts_columns": 6, "shops_columns": 6, "pricebook_columns": 5,
                "models_columns": 4}
# What a listing says in the Compared column when it cannot be the lowest, by stock_status.
PAGE_NOT_COMPARED = "not_compared"


def cents(amount):
    return round(amount * 100)


def money(amount):
    """A$8,630 for a whole number of dollars, A$338.50 otherwise. Takes dollars."""
    dollars, rest = divmod(cents(amount), 100)
    return f"A${dollars:,}" + (f".{rest:02d}" if rest else "")


def long_date(iso):
    y, m, d = (int(p) for p in iso.split("-"))
    return f"{d} {MONTHS[m - 1]} {y}"


def fill(template, **values):
    return template.format(**values)


def split_link(template, **values):
    """The text before and after {link}, with any other placeholders filled."""
    before, after = template.split("{link}")
    return before.format(**values), after.format(**values)


def rows_by_id(group):
    return {row["id"]: row for row in group["data"]["pricebook"]}


def build_cents(build, rows):
    """The sum of a build's parts in cents. `rows` maps pricebook id to row."""
    return sum(cents(rows[p["id"]]["price_aud"]) * p["quantity"] for p in build["parts"])


def shown_builds(group):
    withheld = group.get("withheld") or {}
    return [b for b in group["data"]["builds"] if b["id"] not in withheld]


def graphics_cards(group, build):
    rows, roles = rows_by_id(group), group["roles"]
    return [rows[p["id"]] for p in build["parts"] if roles[p["id"]] == GPU_ROLE]


def buyable(row):
    """True when a listing can count towards a total and so can be the lowest price."""
    return row["usable_in_component_total"] is True and row["stock_status"] == "in_stock"


def same_part_shops(group):
    """Parts the pricebook lists at more than one shop: [(sku, [(row, kind, cents_more)])], in
    pricebook order, buyable listings first and cheapest first. kind is "lowest", "equal_lowest",
    "more" or "not_compared". The page turns it into words, so the cheapest listing is never
    marked by colour alone."""
    by_sku = {}
    for row in group["data"]["pricebook"]:
        by_sku.setdefault(row["sku"], []).append(row)
    out = []
    for sku, rows in by_sku.items():
        if len({r["retailer"] for r in rows}) < 2:
            continue
        prices = [cents(r["price_aud"]) for r in rows if buyable(r)]
        low = min(prices) if prices else None
        noted = []
        for r in sorted(rows, key=lambda r: (not buyable(r), cents(r["price_aud"]))):
            price = cents(r["price_aud"])
            if not buyable(r):
                noted.append((r, "not_compared", 0))
            elif price == low:
                noted.append((r, "lowest" if prices.count(low) == 1 else "equal_lowest", 0))
            else:
                noted.append((r, "more", price - low))
        out.append((sku, noted))
    return out


# Checks ----------------------------------------------------------------------------------

def _real_date(text):
    if not isinstance(text, str) or not ISO_DATE.fullmatch(text):
        return False
    try:
        date.fromisoformat(text)
    except ValueError:
        return False
    return True


def _text(where, text, limit, problems, prose=False, empty_ok=False):
    if not isinstance(text, str):
        problems.append(f"{where}: must be text")
        return
    if not text.strip():
        if not (empty_ok and text == ""):
            problems.append(f"{where}: text is empty")
        return
    if text != text.strip():
        problems.append(f"{where}: has spaces at the start or end")
    if NOT_ONE_LINE.search(text):
        problems.append(f"{where}: must be one line of text, with no control characters")
    if len(text) > limit:
        problems.append(f"{where}: over {limit} characters")
    if DASHES.search(text):
        problems.append(f"{where}: has an en or em dash; use a comma, colon, full stop or the word to")
    if BARE_DOLLAR.search(text):
        problems.append(f"{where}: write prices as A$8,630")
    if prose and HYPE.search(text):
        problems.append(f"{where}: uses the word {HYPE.search(text).group(0)!r}; say what it costs and what it trades off")


def _strings(value, path=""):
    """Every string in a JSON value, with where it sits."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, inner in value.items():
            yield from _strings(key, f"{path} key")
            yield from _strings(inner, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for i, inner in enumerate(value, 1):
            yield from _strings(inner, f"{path}[{i}]")


def _host(url):
    try:
        return (urlsplit(url).hostname or "") if isinstance(url, str) else ""
    except ValueError:
        return ""


def _url(where, url, problems):
    if not source_ok(url):
        problems.append(f"{where}: {ascii(url)} must be one https URL with a hostname")
    elif re.search(r"[?#()]", url):
        problems.append(f"{where}: {ascii(url)} must not carry a query string, a fragment or brackets; "
                        "link the page itself, with no tracking or affiliate parameters")


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _placeholders(where, template, allowed, problems):
    try:
        fields = [(name, spec, conv) for _, name, spec, conv in string.Formatter().parse(template) if name is not None]
    except ValueError:
        problems.append(f"{where}: has an unmatched curly bracket")
        return []
    for name, spec, conv in fields:
        if name not in allowed or spec or conv:
            ok = ", ".join("{" + a + "}" for a in sorted(allowed)) or "none"
            problems.append(f"{where}: uses {{{name}}}; the placeholders it may use are: {ok}")
    return [name for name, _, _ in fields]


def _check_page(where, page, problems):
    if not isinstance(page, dict):
        problems.append(f"{where}: page must be an object holding the page's own wording")
        return
    for key, allowed in PAGE_TEXT.items():
        _text(f"{where} page {key}", page.get(key), NOTE_MAX, problems, prose=True)
        if isinstance(page.get(key), str):
            used = _placeholders(f"{where} page {key}", page[key], allowed, problems)
            if key in PAGE_LINKED and used.count("link") != 1:
                problems.append(f"{where} page {key}: must hold {{link}} once")
    for key, n in PAGE_COLUMNS.items():
        cols = page.get(key)
        if not (isinstance(cols, list) and len(cols) == n):
            problems.append(f"{where} page {key}: must list {n} column names")
            continue
        for i, col in enumerate(cols, 1):
            _text(f"{where} page {key} {i}", col, SHORT_MAX, problems, prose=True)
            if isinstance(col, str):
                _placeholders(f"{where} page {key} {i}", col, set(), problems)
    notes = page.get(PAGE_NOT_COMPARED)
    if not isinstance(notes, dict) or set(notes) != set(STOCK_STATUSES):
        problems.append(f"{where} page {PAGE_NOT_COMPARED}: needs one label for each of {', '.join(STOCK_STATUSES)}")
    else:
        for status, label in notes.items():
            _text(f"{where} page {PAGE_NOT_COMPARED} {status}", label, SHORT_MAX, problems, prose=True)
            if isinstance(label, str):
                _placeholders(f"{where} page {PAGE_NOT_COMPARED} {status}", label, set(), problems)
    unknown = set(page) - set(PAGE_TEXT) - set(PAGE_COLUMNS) - {PAGE_NOT_COMPARED}
    if unknown:
        problems.append(f"{where} page: has labels the page does not use: {', '.join(sorted(unknown))}")


def _check_pricebook(where, data, problems):
    rows = {}
    pricebook = data.get("pricebook")
    if not isinstance(pricebook, list) or not pricebook:
        problems.append(f"{where}: needs a pricebook with at least one listing")
        return rows
    for i, row in enumerate(pricebook, 1):
        if not isinstance(row, dict):
            problems.append(f"{where} pricebook row {i}: must be an object")
            continue
        rid = row.get("id")
        rw = f"{where} pricebook {rid if isinstance(rid, str) else i}"
        if not isinstance(rid, str) or not ID.fullmatch(rid):
            problems.append(f"{rw}: id must be lowercase letters, digits and single hyphens")
            continue
        if rid in rows:
            problems.append(f"{rw}: id is repeated")
            continue
        for key in ROW_SHORT:
            _text(f"{rw} {key}", row.get(key), SHORT_MAX, problems)
        for key in ROW_NOTES:
            _text(f"{rw} {key}", row.get(key), NOTE_MAX, problems)
        _text(f"{rw} conditions", row.get("conditions"), NOTE_MAX, problems, empty_ok=True)
        url = row.get("source")
        _url(f"{rw} source", url, problems)
        retailer = row.get("retailer") if isinstance(row.get("retailer"), str) else ""
        for name, host in EXCLUDED_RETAILERS:
            if retailer.strip().lower() == name.lower() or _host(url) == host or _host(url).endswith("." + host):
                problems.append(f"{rw}: listings from {name} are not published")
        price = row.get("price_aud")
        price_ok = _number(price) and price > 0 and abs(price * 100 - round(price * 100)) < 1e-6
        if not price_ok:
            problems.append(f"{rw}: price_aud must be a number above zero with at most two decimal places")
        if row.get("currency") != CURRENCY:
            problems.append(f"{rw}: currency must be {CURRENCY}")
        status, usable = row.get("stock_status"), row.get("usable_in_component_total")
        if status not in STOCK_STATUSES:
            problems.append(f"{rw}: stock_status must be one of {', '.join(STOCK_STATUSES)}")
        if not isinstance(usable, bool):
            problems.append(f"{rw}: usable_in_component_total must be true or false")
        elif usable and status in STOCK_STATUSES and status != "in_stock":
            problems.append(f"{rw}: is marked usable in a total but its stock_status is {status}")
        if not _real_date(row.get("checked_date")):
            problems.append(f"{rw}: checked_date must be a real date written YYYY-MM-DD")
        elif _real_date(data.get("source_checked")) and row["checked_date"] > data["source_checked"]:
            problems.append(f"{rw}: checked_date is after the package's source_checked date")
        if price_ok and isinstance(usable, bool) and status in STOCK_STATUSES and isinstance(row.get("sku"), str):
            rows[rid] = row
    by_sku = {}
    for row in rows.values():
        by_sku.setdefault(row["sku"], []).append(row)
    for sku, same in by_sku.items():
        if len({r.get("part") for r in same}) > 1:
            problems.append(f"{where} pricebook: listings of {ascii(sku)} must share one part name")
        if len({r.get("retailer") for r in same}) < len(same):
            problems.append(f"{where} pricebook: {ascii(sku)} is listed twice at one retailer")
    return rows


def _check_builds(where, group, rows, problems):
    data = group["data"]
    withheld = group.get("withheld") if isinstance(group.get("withheld"), dict) else {}
    roles = group.get("roles") if isinstance(group.get("roles"), dict) else {}
    builds = data.get("builds")
    totals = {}
    if not isinstance(builds, list) or not builds:
        problems.append(f"{where}: needs at least one build")
        return totals
    ids = []
    for i, build in enumerate(builds, 1):
        if not isinstance(build, dict):
            problems.append(f"{where} build {i}: must be an object")
            continue
        bid = build.get("id")
        bw = f"{where} build {bid if isinstance(bid, str) else i}"
        if not isinstance(bid, str) or not ID.fullmatch(bid):
            problems.append(f"{bw}: id must be lowercase letters, digits and single hyphens")
            continue
        if bid in ids:
            problems.append(f"{bw}: id is repeated")
            continue
        ids.append(bid)
        for key in BUILD_TEXT:
            _text(f"{bw} {key}", build.get(key), NOTE_MAX, problems, prose=True)
        if build.get("currency") != CURRENCY:
            problems.append(f"{bw}: currency must be {CURRENCY}")
        parts = build.get("parts")
        good = isinstance(parts, list) and bool(parts)
        if not good:
            problems.append(f"{bw}: parts must be a non-empty list of pricebook ids with quantities")
        seen = set()
        for part in parts if good else []:
            quantity = part.get("quantity") if isinstance(part, dict) else None
            if not (isinstance(part, dict) and isinstance(part.get("id"), str) and isinstance(quantity, int)
                    and not isinstance(quantity, bool) and quantity >= 1):
                problems.append(f"{bw}: each part needs a pricebook id and a whole quantity of 1 or more: {ascii(part)}")
                good = False
                continue
            part_id = part["id"]
            if part_id not in rows:
                problems.append(f"{bw}: part {ascii(part_id)} is not a pricebook id")
                good = False
                continue
            if part_id in seen:
                problems.append(f"{bw}: part {part_id} is listed twice; raise its quantity instead")
                good = False
            seen.add(part_id)
            # A listing that is out of stock, conditional or otherwise not usable in a total
            # must not count towards one. A withheld build stays off the page instead.
            if rows[part_id]["usable_in_component_total"] is not True and bid not in withheld:
                problems.append(f"{bw}: part {part_id} is not usable in a component total "
                                f"(stock_status {rows[part_id]['stock_status']}), so the build cannot be published; "
                                "correct the listing or add the build to withheld")
        total = build.get("total_aud")
        if not _number(total) or total <= 0:
            problems.append(f"{bw}: total_aud must be a number above zero")
        elif good:
            want = build_cents(build, rows)
            if cents(total) != want:
                problems.append(f"{bw}: total_aud is {money(total)} but its parts add up to {money(want / 100)}, "
                                f"a difference of {money(abs(cents(total) - want) / 100)}")
            else:
                totals[bid] = want
        included = build.get("dedicated_gpu_included")
        if not isinstance(included, bool):
            problems.append(f"{bw}: dedicated_gpu_included must be true or false")
        elif good and all(part_id in roles for part_id in seen):
            if included != any(roles[part_id] == GPU_ROLE for part_id in seen):
                problems.append(f"{bw}: dedicated_gpu_included is {str(included).lower()} but its parts say otherwise")
    for bid in withheld:
        if bid not in ids:
            problems.append(f"{where} withheld: {ascii(bid)} is not a build id")
    default = data.get("default_build")
    if default not in ids:
        problems.append(f"{where}: default_build {ascii(default)} is not a build id")
    elif default in withheld:
        problems.append(f"{where}: default_build {default} is withheld, so the page has no build to mark")
    if ids and all(bid in withheld for bid in ids):
        problems.append(f"{where}: every build is withheld")
    return totals


def _check_figures(where, data, rows, totals, problems):
    """Every A$ figure in the notes and in a build's trade-off or upgrade path must come from the
    pricebook: a listing's price, a line total, a build total, or the difference between two
    build totals or two listings. Conditions quote the retailer's own page, so they are not
    checked here."""
    allowed = set(totals.values())
    allowed |= {abs(a - b) for a in totals.values() for b in totals.values()}
    prices = [cents(r["price_aud"]) for r in rows.values()]
    allowed |= set(prices) | {abs(p - q) for p in prices for q in prices}
    texts = [(f"{where} {key}", data.get(key)) for key in DATA_NOTES]
    for build in data.get("builds") or []:
        if not isinstance(build, dict):
            continue
        if build.get("id") in totals:
            allowed |= {cents(rows[p["id"]]["price_aud"]) * p["quantity"] for p in build["parts"]}
        texts += [(f"{where} build {build.get('id')} {key}", build.get(key)) for key in ("main_tradeoff", "upgrade_path")]
    for label, text in texts:
        for figure in MONEY.findall(text) if isinstance(text, str) else []:
            if cents(float(figure.replace(",", ""))) not in allowed:
                problems.append(f"{label}: A${figure} is not a pricebook price, a build total or a difference between two of them")


def _check_models(where, data, problems):
    models = data.get("models")
    tags = []
    if not isinstance(models, list):
        problems.append(f"{where}: models must be a list")
        return tags
    for i, m in enumerate(models, 1):
        if not isinstance(m, dict):
            problems.append(f"{where} model {i}: must be an object")
            continue
        mw = f"{where} model {m.get('tag') if isinstance(m.get('tag'), str) else i}"
        for key in MODEL_TEXT:
            _text(f"{mw} {key}", m.get(key), NOTE_MAX, problems, prose=key != "tag")
        if m.get("tag") in tags:
            problems.append(f"{mw}: tag is repeated")
        tags.append(m.get("tag"))
        if not _number(m.get("size_gb")) or m["size_gb"] <= 0:
            problems.append(f"{mw}: size_gb must be a number above zero")
        _url(f"{mw} url", m.get("url"), problems)
    return tags


def _check_maps(where, group, rows, tags, entry_ids, problems):
    roles = group.get("roles")
    if not isinstance(roles, dict):
        problems.append(f"{where}: roles must map every pricebook id to what the part is")
    else:
        for rid in rows:
            if rid not in roles:
                problems.append(f"{where} roles: {rid} has no role")
        for rid, role in roles.items():
            if rid not in rows:
                problems.append(f"{where} roles: {ascii(rid)} is not a pricebook id")
            _text(f"{where} roles {rid}", role, SHORT_MAX, problems, prose=True)
        by_sku = {}
        for rid, row in rows.items():
            by_sku.setdefault(row["sku"], set()).add(roles.get(rid))
        for sku, found in by_sku.items():
            if len(found) > 1:
                problems.append(f"{where} roles: listings of {ascii(sku)} must share one role")
    for key, known, what in (("entries", set(rows), "a pricebook id"), ("model_entries", set(tags), "a model tag")):
        links = group.get(key, {})
        if not isinstance(links, dict):
            problems.append(f"{where}: {key} must be an object")
            continue
        for name, entry in links.items():
            if name not in known:
                problems.append(f"{where} {key}: {ascii(name)} is not {what}")
            if entry not in entry_ids:
                problems.append(f"{where} {key}: {ascii(entry)} is not an entry id in resources.json")
    withheld = group.get("withheld", {})
    if not isinstance(withheld, dict):
        problems.append(f"{where}: withheld must map a build id to the reason it is held back")
    else:
        for bid, reason in withheld.items():
            _text(f"{where} withheld {bid}", reason, NOTE_MAX, problems, prose=True)


def check(data, resources):
    problems = []
    entry_ids = {e["id"] for e in resources}
    categories = {e["category"] for e in resources}
    groups = data.get("groups") if isinstance(data, dict) else None
    if not isinstance(groups, list) or not groups:
        return ["builds.json: needs a groups list with at least one build group"]
    # Nothing in the file, shown or not, may hold a control character or an en or em dash.
    for path, text in _strings(data):
        if NOT_ONE_LINE.search(text):
            problems.append(f"builds.json {path}: has a control character or a line break")
        if DASHES.search(text):
            problems.append(f"builds.json {path}: has an en or em dash; use a comma, colon, full stop or the word to")
    seen = set()
    for i, group in enumerate(groups, 1):
        if not isinstance(group, dict):
            problems.append(f"builds.json group {i}: must be an object")
            continue
        gid = group.get("id")
        where = f"builds.json {gid if isinstance(gid, str) else i}"
        if not isinstance(gid, str) or not ID.fullmatch(gid):
            problems.append(f"{where}: id must be lowercase letters, digits and single hyphens, since it is the page address")
        elif gid in seen:
            problems.append(f"{where}: id is repeated")
        seen.add(gid)
        if group.get("group") not in categories:
            problems.append(f"{where}: group {ascii(group.get('group'))} is not a Gearlist group")
        _check_page(where, group.get("page"), problems)
        pack = group.get("data")
        if not isinstance(pack, dict):
            problems.append(f"{where}: data must hold the researched package")
            continue
        _text(f"{where} title", pack.get("title"), SHORT_MAX, problems, prose=True)
        for key in DATA_NOTES:
            _text(f"{where} {key}", pack.get(key), NOTE_MAX, problems, prose=True)
        if not _real_date(pack.get("source_checked")):
            problems.append(f"{where}: source_checked must be a real date written YYYY-MM-DD")
        if pack.get("currency") != CURRENCY:
            problems.append(f"{where}: currency must be {CURRENCY}, since prices are written A$")
        _url(f"{where} integrated_graphics_source", pack.get("integrated_graphics_source"), problems)
        sources = pack.get("technical_sources")
        if not isinstance(sources, list):
            problems.append(f"{where}: technical_sources must be a list")
        else:
            for n, s in enumerate(sources, 1):
                if not isinstance(s, dict):
                    problems.append(f"{where} technical source {n}: must be an object")
                    continue
                _text(f"{where} technical source {n} topic", s.get("topic"), SHORT_MAX, problems, prose=True)
                _url(f"{where} technical source {n} url", s.get("url"), problems)
        rows = _check_pricebook(where, pack, problems)
        totals = _check_builds(where, group, rows, problems)
        _check_figures(where, pack, rows, totals, problems)
        tags = _check_models(where, pack, problems)
        _check_maps(where, group, rows, tags, entry_ids, problems)
    return problems
