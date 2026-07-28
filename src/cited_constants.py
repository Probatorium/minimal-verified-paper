"""Values this work takes from an outside source, each with its record.

The rule this file implements (mechanism 7 of the method): a value that comes
from a source is DECLARED here, with enough bibliographic detail that a reader
can go and check it. A value the work derives is COMPUTED in code and never
written down by hand. Never the other way round.

`checks/check_20_cited_constants.py` enforces three things about this file:
  1. every record is complete and carries a resolvable identifier;
  2. every record is actually consumed by a check (no decorative citations);
  3. where a cited value overlaps something the package computes, they agree --
     which is the point of citing it at all.
"""

from collections import namedtuple

CitedConstant = namedtuple(
    "CitedConstant",
    "key value description source identifier retrieved quoted_context consumed_by",
)

#: The first 100 decimal digits of pi, as published, used as an external anchor
#: for both computation paths. If our arithmetic drifted, this catches it
#: without appealing to our own arithmetic.
PI_FIRST_100_DECIMALS = CitedConstant(
    key="PI_FIRST_100_DECIMALS",
    value=(
        "1415926535"
        "8979323846"
        "2643383279"
        "5028841971"
        "6939937510"
        "5820974944"
        "5923078164"
        "0628620899"
        "8628034825"
        "3421170679"
    ),
    description=(
        "Decimal digits of pi in positions 1 through 100 after the decimal "
        "point, transcribed from the published decimal expansion."
    ),
    source="OEIS Foundation Inc., The On-Line Encyclopedia of Integer Sequences, sequence A000796 (Decimal expansion of Pi)",
    identifier="https://oeis.org/A000796",
    retrieved="2026-07-28",
    quoted_context=(
        "Sequence A000796 is titled 'Decimal expansion of Pi (or Archimedes' "
        "number or Ludolph's number)' and begins 3, 1, 4, 1, 5, 9, 2, 6, 5, "
        "3, 5, 8, 9, 7, 9, ... The value above drops the leading 3 and keeps "
        "the next 100 terms."
    ),
    consumed_by="check_20_cited_constants",
)

ALL_CITED_CONSTANTS = (PI_FIRST_100_DECIMALS,)


def reference_digits():
    """The cited prefix as a list of ints, for comparison with computed digits."""
    return [int(c) for c in PI_FIRST_100_DECIMALS.value]
