"""The README must map every claim in the paper to the check that holds it up.

The map is the reader's entry point: it lets someone go from a sentence in the
manuscript to the assertion that supports it without reading any code. A map
that has fallen behind the paper is worse than no map, so it is checked like
everything else.

Two directions again. Every section of the manuscript must appear in the map, so
no part of the paper is unaccounted for; and every check module must appear in
it, so no check is doing work the reader was never told about.
"""

from checks import check
from src import manuscript

ORDER = 90
NAME = "README claim-to-check map covers the paper and the suite"
GATE = False

#: The README heading that introduces the map.
MAP_HEADING = "## Claim-to-check map"


def run(context):
    readme = manuscript.read(manuscript.README)
    results = [check(
        "MAP-present",
        MAP_HEADING in readme,
        "the README has no %r section" % MAP_HEADING,
    )]

    block = readme.split(MAP_HEADING, 1)[-1].split("\n## ", 1)[0]

    paper_sections = [
        heading for heading in manuscript.sections(manuscript.read(manuscript.PAPER))
        if heading not in manuscript.SECTIONS_EXEMPT_FROM_NUMBER_COVERAGE
    ]
    uncovered = [heading for heading in paper_sections if heading not in block]
    results.append(check(
        "MAP-covers-paper",
        not uncovered,
        "the claim map does not mention these manuscript sections: %s"
        % ", ".join(uncovered),
    ))

    unlisted = [name for name in context.check_module_names if name not in block]
    results.append(check(
        "MAP-covers-checks",
        not unlisted,
        "the claim map does not mention these check modules: %s" % ", ".join(unlisted),
    ))

    return results
