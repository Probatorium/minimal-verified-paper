"""Title, author, year and version, checked at every declared location.

WHAT CHANGED, AND WHY. This check used to ask whether the declared string
appeared anywhere in each surface. A defect injection study over this package
measured what that costs: of twenty front matter drifts injected one surface at
a time, nine escaped, and every one of them escaped for the same reason. The
title lives twice in `paper.md`, in the YAML block and again in the level-one
heading; the author lives twice, in the field and in the byline. Altering one
copy left the other satisfying a whole-file substring search. The year in
`CITATION.bib` escaped for a neighbouring reason: the string `2026` survives
inside the citation key `garciahurtado2026uniformity`, so the year field could
be changed without the check noticing.

So the check no longer searches. It declares, below, every place each string is
supposed to live -- which file, and which field, heading, byline position or
BibTeX entry -- extracts the value from exactly that place, and compares it. A
location that stops matching is named individually.

DOI POLICY, unchanged. `src/front_matter.py` carries `DOI = None` until the work
is deposited. While it is None no surface may contain a DOI-shaped string for
this work, so there is nothing provisional to forget. When a real DOI is
registered, the same check flips to demanding it everywhere.
"""

import re
from collections import namedtuple

from checks import check
from src import front_matter
from src import manuscript

ORDER = 80
NAME = "Front matter identical at every declared location"
GATE = False

#: Anything shaped like a DOI. Deliberately loose: it should over-match rather
#: than let a provisional identifier through.
DOI_SHAPED = re.compile(r"10\.\d{4,9}/[^\s,;)\]}\"']+")

#: One place a front matter string is supposed to live. `slug` names the
#: location in the check id, so a failure says which copy drifted.
Location = namedtuple("Location", "surface field slug describe extract")


def _yaml_field(key):
    """The value of `key` in a document's '---' front matter block."""
    def extract(text):
        block = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not block:
            return None
        for line in block.group(1).split("\n"):
            name, separator, value = line.partition(":")
            if separator and name.strip() == key:
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                return value
        return None
    return extract


def _heading(text):
    """The text of the level-one heading."""
    for line in text.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _byline(index=None, prefix=None):
    """The byline: the first non-empty line under the level-one heading.

    `index` picks one field out of a byline separated by middots; `prefix` is
    stripped from it when present, so that 'version 1.0.0' yields the version.
    """
    def extract(text):
        lines = text.split("\n")
        for position, line in enumerate(lines):
            if not line.startswith("# "):
                continue
            for following in lines[position + 1:]:
                if following.strip():
                    value = following.strip()
                    if index is None:
                        return value
                    parts = [part.strip() for part in value.split("·")]
                    if index >= len(parts):
                        return None
                    part = parts[index]
                    if prefix and part.startswith(prefix):
                        part = part[len(prefix):]
                    return part
            return None
        return None
    return extract


def _bibtex_field(key):
    """The braced value of one BibTeX field, read as a field and not as text.

    Reading the field is the whole point for the year: `2026` also occurs inside
    the citation key, so a substring search cannot tell a correct year from a
    stale one sitting next to a key that happens to contain the digits.
    """
    def extract(text):
        found = re.search(r"^\s*%s\s*=\s*\{(.*)\},?\s*$" % re.escape(key),
                          text, re.MULTILINE)
        return found.group(1) if found else None
    return extract


#: Every place a front matter string lives. Adding a surface means adding its
#: locations here; there is no fallback that would quietly accept a new copy.
LOCATIONS = (
    Location("paper.md", "title", "yaml", "YAML front matter field", _yaml_field("title")),
    Location("paper.md", "author", "yaml", "YAML front matter field", _yaml_field("author")),
    Location("paper.md", "year", "yaml", "YAML front matter field", _yaml_field("year")),
    Location("paper.md", "version", "yaml", "YAML front matter field", _yaml_field("version")),
    Location("paper.md", "title", "heading", "level-one heading", _heading),
    Location("paper.md", "author", "byline", "byline under the heading", _byline()),

    Location("README.md", "title", "heading", "level-one heading", _heading),
    Location("README.md", "author", "byline", "first byline field", _byline(0)),
    Location("README.md", "year", "byline", "second byline field", _byline(1)),
    Location("README.md", "version", "byline", "third byline field",
             _byline(2, prefix="version ")),

    Location("CITATION.bib", "title", "field", "BibTeX field", _bibtex_field("title")),
    Location("CITATION.bib", "author", "field", "BibTeX field", _bibtex_field("author")),
    Location("CITATION.bib", "year", "field", "BibTeX field", _bibtex_field("year")),
    Location("CITATION.bib", "version", "field", "BibTeX field", _bibtex_field("version")),
)

DECLARED = {
    "title": front_matter.TITLE,
    "author": front_matter.AUTHOR,
    "year": front_matter.YEAR,
    "version": front_matter.VERSION,
}


def run(context):
    results = []
    cache = {}

    for location in LOCATIONS:
        check_id = "FM-%s-%s-%s" % (location.field, location.surface, location.slug)
        if not manuscript.exists(location.surface):
            results.append(check(check_id, False, "surface %s is missing" % location.surface))
            continue
        if location.surface not in cache:
            cache[location.surface] = manuscript.read(location.surface)
        found = location.extract(cache[location.surface])
        expected = DECLARED[location.field]
        if found is None:
            detail = ("the %s of %s carries no %s at all; the location declared in "
                      "this check does not exist in the file"
                      % (location.describe, location.surface, location.field))
        else:
            detail = ("the %s of %s reads %r but src/front_matter.py declares %r"
                      % (location.describe, location.surface, found, expected))
        results.append(check(check_id, found == expected, detail))

    results.append(check(
        "FM-citation-key",
        front_matter.CITATION_KEY in manuscript.read(manuscript.CITATION),
        "CITATION.bib does not use the declared citation key %r"
        % front_matter.CITATION_KEY,
    ))

    surfaces = sorted(set(location.surface for location in LOCATIONS))
    if front_matter.DOI is None:
        stray = []
        for surface in surfaces:
            if manuscript.exists(surface):
                stray.extend("%s: %s" % (surface, hit)
                             for hit in DOI_SHAPED.findall(manuscript.read(surface)))
        results.append(check(
            "FM-doi-policy",
            not stray,
            "no DOI has been registered for this work, yet a DOI-shaped string "
            "appears on a front matter surface: %s" % ", ".join(stray),
        ))
    else:
        missing = [surface for surface in surfaces
                   if front_matter.DOI not in manuscript.read(surface)]
        results.append(check(
            "FM-doi-policy",
            not missing,
            "the registered DOI %s is absent from: %s"
            % (front_matter.DOI, ", ".join(missing)),
        ))

    return results
