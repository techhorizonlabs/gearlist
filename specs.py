"""Comparison specs on Gearlist entries, and the plain-text Markdown cells they become.

Hardware and Models entries carry `specs`: a list of [label, value] pairs from the maker's or
provider's own pages. A group page shows them as a comparison table (site/build_site.py), and the
group's Markdown copy repeats the table. Specs are data, so they must stay plain text there:

    check(entries)  -> list of problems; build.py refuses to build when it is not empty
    md_cell(text)   -> one Markdown table cell that renders as the same plain text
"""
import re

LABEL_MAX = 40
VALUE_MAX = 120
# One line of text: no control characters, and no line or paragraph separators.
NOT_ONE_LINE = re.compile("[\x00-\x1f\x7f\x85\u2028\u2029]")
DASHES = re.compile("[\u2013\u2014]")
# Markdown punctuation that can start emphasis, code, a link, an image, a heading, a table cell,
# strikethrough or an email autolink. Each gets a backslash; backslash itself first, so an escape cannot be undone.
MD_PUNCTUATION = re.compile(r"([\\`*_\[\]|#!~@])")


def check(entries):
    problems = []
    for e in entries:
        if "specs" not in e:
            continue
        name = e.get("id", "?")
        specs = e["specs"]
        if not isinstance(specs, list) or not specs:
            problems.append(f"{name}: specs must be a non-empty list of [label, value] pairs")
            continue
        labels = []
        for pair in specs:
            if not (isinstance(pair, list) and len(pair) == 2 and all(isinstance(x, str) for x in pair)):
                problems.append(f"{name}: each spec must be [label, value], both text: {ascii(pair)}")
                continue
            label, value = pair
            labels.append(label)
            for kind, text, limit in (("label", label, LABEL_MAX), ("value", value, VALUE_MAX)):
                if not text.strip():
                    problems.append(f"{name}: a spec {kind} is empty")
                elif text != text.strip():
                    problems.append(f"{name}: spec {kind} {ascii(text)} has spaces at an end")
                if NOT_ONE_LINE.search(text):
                    problems.append(f"{name}: spec {kind} {ascii(text)} must be one line of text")
                if len(text) > limit:
                    problems.append(f"{name}: spec {kind} {ascii(text)} is over {limit} characters")
                if DASHES.search(text):
                    problems.append(f"{name}: spec {kind} {ascii(text)} has an en or em dash; use a comma, colon or full stop")
        if len(set(labels)) != len(labels):
            problems.append(f"{name}: a spec label is repeated")
    return problems


def md_cell(text):
    """Text for one Markdown table cell. HTML is escaped, Markdown punctuation and pipes get a
    backslash, and URL starts are broken so they do not become links."""
    text = str(text)
    if NOT_ONE_LINE.search(text):
        raise ValueError("a Markdown table cell must be one line of text")
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = MD_PUNCTUATION.sub(r"\\\1", text)
    text = text.replace("://", ":\\/\\/")
    return re.sub(r"(?i)\bwww\.", "www\\.", text)
