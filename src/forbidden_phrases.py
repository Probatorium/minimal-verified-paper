"""Strings the manuscript and its surfaces must never contain again.

Two families:

  * PLACEHOLDERS -- editing scars. A paper that ships with an unresolved marker
    in it has shipped an unfinished sentence. The package refuses.
  * OVERCLAIMS -- sentences this particular paper is not entitled to write. A
    chi-square test that fails to reject does not confirm anything, does not
    prove anything, and says nothing about the normality of pi. These strings
    are the ways that mistake is usually phrased.

The overclaim list is paper-specific by design. When this package is reused as a
template, that list should be rewritten for the new paper's own temptations.

NOTE FOR ANYONE EDITING THE README: the phrases live here and only here. If the
README quoted them, the README would fail its own check. `check_70` treats the
README as a watched surface and skips `src/`, which is the only place the list
is allowed to appear.
"""

#: Editing scars: markers that mean "not finished".
PLACEHOLDERS = (
    "TODO",
    "FIXME",
    "TBD",
    "XXX",
    "DOI pending",
    "lorem ipsum",
    "PLACEHOLDER",
    "citation needed",
    "??",
)

#: Claims this paper is not entitled to make, in their usual phrasings.
OVERCLAIMS = (
    "we prove",
    "this proves",
    "proves that",
    "the digits of pi are random",
    "pi is normal",
    "establishes normality",
    "accept the null",
    "the null hypothesis is true",
    "highly significant",
    "confirms the hypothesis",
)

FORBIDDEN = PLACEHOLDERS + OVERCLAIMS

#: Surfaces watched for forbidden phrases. `src/` is excluded because the list
#: itself lives there.
WATCHED_SURFACES = (
    "paper.md",
    "README.md",
    "CITATION.bib",
    "references.bib",
    "mutation_report.md",
)
