"""Title, author and year, compared character for character across surfaces.

Papers acquire surfaces -- the manuscript, the README, the BibTeX entry, later a
landing page -- and those surfaces drift. A subtitle gets added in one place, an
accent gets dropped in another, a year rolls over. The comparison here is exact
string equality, not a fuzzy match, because a citation that differs by one
character is a citation that does not resolve.

DOI POLICY. `src/front_matter.py` carries `DOI = None` until the work is
deposited. While it is None this check enforces the strict version: no surface
may contain a DOI-shaped string for this work. That is how the package refuses
to ship a provisional identifier -- there is no placeholder to forget to
replace, because a placeholder would fail the build. Once a real DOI is
registered and written into `front_matter.py`, the same check flips to demanding
that every surface contains it exactly.
"""

import re

from checks import check
from src import front_matter
from src import manuscript

ORDER = 80
NAME = "Front matter identical across manuscript, README and BibTeX"
GATE = False

#: Anything shaped like a DOI. Deliberately loose: the point is to catch
#: provisional identifiers, so it should over-match rather than under-match.
DOI_SHAPED = re.compile(r"10\.\d{4,9}/[^\s,;)\]}\"']+")

FIELDS = (
    ("title", front_matter.TITLE),
    ("author", front_matter.AUTHOR),
    ("year", front_matter.YEAR),
)


def run(context):
    results = []

    for surface in front_matter.FRONT_MATTER_SURFACES:
        if not manuscript.exists(surface):
            for field, _ in FIELDS:
                results.append(check(
                    "FM-%s-%s" % (field, surface), False,
                    "surface %s is missing" % surface))
            continue
        text = manuscript.read(surface)
        for field, expected in FIELDS:
            results.append(check(
                "FM-%s-%s" % (field, surface),
                expected in text,
                "%s does not contain the %s exactly as declared in "
                "src/front_matter.py: expected %r" % (surface, field, expected),
            ))

    results.append(check(
        "FM-citation-key",
        front_matter.CITATION_KEY in manuscript.read(manuscript.CITATION),
        "CITATION.bib does not use the declared citation key %r"
        % front_matter.CITATION_KEY,
    ))

    if front_matter.DOI is None:
        stray = []
        for surface in front_matter.FRONT_MATTER_SURFACES:
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
        missing = [surface for surface in front_matter.FRONT_MATTER_SURFACES
                   if front_matter.DOI not in manuscript.read(surface)]
        results.append(check(
            "FM-doi-policy",
            not missing,
            "the registered DOI %s is absent from: %s"
            % (front_matter.DOI, ", ".join(missing)),
        ))

    return results
