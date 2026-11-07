"""Short buying guides shown at the top of a group page (guides.json), and their checks.

A guide answers one practical question for a group, such as which hardware set-up suits which
job. Its text is plain sentences. The only markup is [[entry-id]], which becomes a link to that
entry's page. Every section lists the official sources its facts come from.

    check(guides, entries) -> list of problems; build.py and site/build_site.py both refuse to build
                              when it is not empty
    parts(text)            -> [(kind, value)] with kind "text" or "link" (an entry id)
    source_ok(url)         -> True for an https URL with a real hostname and nothing else in it
    md_text(text)          -> guide text encoded for Markdown, so it reads as the same plain text
                              the HTML page shows
"""
import re
from urllib.parse import urlsplit

LINK = re.compile(r"\[\[([a-z0-9][a-z0-9-]*)\]\]")
NOT_ONE_LINE = re.compile("[\x00-\x1f\x7f\x85\u2028\u2029]")
DASHES = re.compile("[\u2013\u2014]")
# Characters with a meaning in Markdown or HTML are not allowed in guide text, so it renders
# the same everywhere. [[id]] links are the one exception and are removed before this check.
MARKUP = re.compile(r"[<>`*_\[\]|#~@\\]")
HEADING_MAX = 80
PARAGRAPH_MAX = 700


def parts(text):
    out, pos = [], 0
    for m in LINK.finditer(text):
        if m.start() > pos:
            out.append(("text", text[pos:m.start()]))
        out.append(("link", m.group(1)))
        pos = m.end()
    if pos < len(text):
        out.append(("text", text[pos:]))
    return out


def source_ok(url):
    if not isinstance(url, str) or NOT_ONE_LINE.search(url) or re.search(r"[\s<>\"'\\`]", url):
        return False
    try:
        u = urlsplit(url)
        port = u.port
    except ValueError:
        return False
    host = u.hostname or ""
    return (u.scheme == "https" and bool(host) and "." in host and not u.username and not u.password
            and port in (None, 443) and re.fullmatch(r"[a-z0-9.-]+", host) is not None)


# Markdown that a single line of plain text could start by accident: list items, headings,
# block quotes, thematic breaks and ordered lists.
LEADING = re.compile(r"^(?:([-+*>#=])|(\d+)([.)]))")
MD_ESCAPE = re.compile(r"([\\`*_\[\]|#~!@])")


def md_text(text, start=True):
    """start is True when the text begins a Markdown line (a title, heading or the first part of a
    paragraph). Leading whitespace there is written as character references, so it cannot indent
    the line into a list, rule or code block."""
    text = str(text)
    if NOT_ONE_LINE.search(text):
        raise ValueError("guide text must be one line")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = MD_ESCAPE.sub(r"\\\1", text)
    if not start:
        text = text.replace("://", ":\\/\\/")
        return re.sub(r"(?i)\bwww\.", "www\\.", text)
    indent = len(text) - len(text.lstrip(" "))
    text = "&#32;" * indent + text[indent:]
    m = LEADING.match(text)
    if m:
        if m.group(1):
            text = "\\" + text
        else:
            text = m.group(2) + "\\" + m.group(3) + text[m.end():]
    text = text.replace("://", ":\\/\\/")
    return re.sub(r"(?i)\bwww\.", "www\\.", text)


def _check_text(where, text, limit, ids, problems):
    if not isinstance(text, str) or not text.strip():
        problems.append(f"{where}: text is empty")
        return
    if text != text.strip():
        problems.append(f"{where}: has spaces at the start or end")
    if NOT_ONE_LINE.search(text):
        problems.append(f"{where}: must be one line of text")
    if len(text) > limit:
        problems.append(f"{where}: over {limit} characters")
    if DASHES.search(text):
        problems.append(f"{where}: has an en or em dash; use a comma, colon or full stop")
    if MARKUP.search(LINK.sub("", text)):
        problems.append(f"{where}: has Markdown or HTML characters or an email address; only [[entry-id]] links are allowed")
    for kind, value in parts(text):
        if kind == "link" and value not in ids:
            problems.append(f"{where}: links to [[{value}]], which is not an entry id")


def check(guides, entries):
    problems = []
    ids = {e["id"] for e in entries}
    groups = {e["category"] for e in entries}
    for name, g in (guides.get("groups") or {}).items():
        where = f"guides.json {name}"
        if name not in groups:
            problems.append(f"{where}: no such group")
        _check_text(f"{where} title", g.get("title"), HEADING_MAX, ids, problems)
        sections = g.get("sections")
        if not isinstance(sections, list) or not sections:
            problems.append(f"{where}: needs at least one section")
            continue
        for i, s in enumerate(sections, 1):
            sw = f"{where} section {i}"
            _check_text(f"{sw} heading", s.get("heading"), HEADING_MAX, ids, problems)
            paras = s.get("paragraphs")
            if not isinstance(paras, list) or not paras:
                problems.append(f"{sw}: needs at least one paragraph")
            else:
                for j, p in enumerate(paras, 1):
                    _check_text(f"{sw} paragraph {j}", p, PARAGRAPH_MAX, ids, problems)
            sources = s.get("sources")
            if not isinstance(sources, list) or not sources:
                problems.append(f"{sw}: list the official sources its facts come from")
            else:
                for u in sources:
                    if not source_ok(u):
                        problems.append(f"{sw}: source {ascii(u)} must be one https URL with a hostname")
    return problems
