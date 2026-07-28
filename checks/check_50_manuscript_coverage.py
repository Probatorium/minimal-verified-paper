"""No number in the manuscript without a check behind it.

`check_40` verifies the numbers that are declared. This one closes the other
door: it walks the manuscript and insists that every numeric literal it finds is
the text of some frozen claim. A number an author typed straight into the prose
has no computation behind it, and this is where it is caught.

WHAT IS DELIBERATELY NOT SCANNED, and why:
  * the front matter block -- identity metadata, checked character for character
    by `check_80`;
  * inline code and fenced blocks -- symbols and file names, not quantities;
  * link and image targets -- paths, not quantities;
  * the References section -- volumes, pages and years, which are part of a
    bibliographic record rather than a result.
These exemptions are declared in `src/manuscript.py`, not buried here.

KNOWN LIMIT. Coverage is by string, so a small integer that happens to match
some claim's text passes wherever it appears. Freezing '10' as the number of
categories means a stray '10' elsewhere in the prose would not be caught. The
check is a floor, not a ceiling.
"""

from checks import check
from src import frozen_claims
from src import manuscript

ORDER = 50
NAME = "Manuscript number coverage: no unclaimed figures in the text"
GATE = False


def run(context):
    text = manuscript.read(manuscript.PAPER)
    all_sections = manuscript.sections(text)
    known = set(claim.text for claim in frozen_claims.CLAIMS)

    orphans = []
    for heading, body in all_sections.items():
        if heading in manuscript.SECTIONS_EXEMPT_FROM_NUMBER_COVERAGE:
            continue
        for token in manuscript.numbers_in(body):
            if token not in known:
                orphans.append("%s in section %r" % (token, heading))

    results = [check(
        "COV-orphan-numbers",
        not orphans,
        "the manuscript reports numbers that no frozen claim covers: %s"
        % ", ".join(orphans),
    )]

    missing_sections = sorted(
        set(claim.section for claim in frozen_claims.CLAIMS) - set(all_sections)
    )
    results.append(check(
        "COV-sections-exist",
        not missing_sections,
        "frozen claims point at manuscript sections that do not exist: %s"
        % ", ".join(missing_sections),
    ))

    return results
