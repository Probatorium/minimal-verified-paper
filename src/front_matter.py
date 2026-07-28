"""The single source of truth for the identity of this work.

Every surface that names the paper -- the manuscript, the README, the BibTeX
self-citation -- must reproduce these strings character for character.
`checks/check_80_front_matter.py` enforces that.

Why a module and not a config file: a config file would need a parser, and a
parser is a dependency. A Python module is read by the interpreter that is
already running.
"""

#: The canonical title of this work. One string, reproduced character for
#: character on every surface that names it. It carries both halves of what this
#: artifact is: the statistical case it reports, and the method it demonstrates.
TITLE = "Uniformity of the First 1000 Decimal Digits of pi: A Minimal Stasis Artifact"

AUTHOR = "Alexis García Hurtado"

YEAR = "2026"

VERSION = "1.0.0"

# The BibTeX key under which this work cites itself.
CITATION_KEY = "garciahurtado2026uniformity"

# Set to the registered DOI string (e.g. "10.5281/zenodo.1234567") once the
# work is deposited. While it is None, check_80 enforces the stricter rule:
# NO surface may contain a DOI-shaped string for this work. This is how the
# package refuses to carry a placeholder identifier. See DESIGN NOTE 3 in the
# README.
DOI = None

#: Surfaces that must agree on the strings above. Paths are relative to the
#: package root.
FRONT_MATTER_SURFACES = ("paper.md", "README.md", "CITATION.bib")
