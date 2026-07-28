"""Strings the paper is not allowed to contain any more.

Two things are being policed at once: editing scars that mean the text is
unfinished, and sentences this paper is not entitled to write. The list itself
is in `src/forbidden_phrases.py`, with the reasoning for each family.

The README is a watched surface, so the README cannot quote the list -- it would
fail its own check. This is not an oversight; it is why the list lives in a
module and the README points at it.
"""

from checks import check
from src import forbidden_phrases
from src import manuscript

ORDER = 70
NAME = "Forbidden phrases absent from every watched surface"
GATE = False


def run(context):
    results = [check(
        "PHR-list-nonempty",
        len(forbidden_phrases.FORBIDDEN) > 0,
        "the forbidden phrase list is empty, so this check asserts nothing",
    )]

    for surface in forbidden_phrases.WATCHED_SURFACES:
        if not manuscript.exists(surface):
            results.append(check(
                "PHR-" + surface,
                False,
                "watched surface %s is missing" % surface,
            ))
            continue
        haystack = manuscript.read(surface).lower()
        hits = [phrase for phrase in forbidden_phrases.FORBIDDEN
                if phrase.lower() in haystack]
        results.append(check(
            "PHR-" + surface,
            not hits,
            "%s contains forbidden phrasing: %s" % (surface, ", ".join(repr(h) for h in hits)),
        ))

    return results
