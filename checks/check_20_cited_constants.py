"""What the paper takes from a source, and whether it still agrees with it.

Mechanism: the split between cited and computed. A value from outside is
declared with its record; a value the paper derives is computed. This check
enforces the split in both directions:

  * every cited constant carries a complete, resolvable record;
  * every cited constant is actually used, so no citation is decorative;
  * the cited value agrees with what the package computes, which is the only
    reason to cite it;
  * the cited value is not copy-pasted anywhere else in the source, so there is
    exactly one place a reader has to trust.
"""

import os
import re

from checks import check
from src import cited_constants
from src import manuscript

ORDER = 20
NAME = "Cited constants and their records"
GATE = False

#: An identifier a reader can actually resolve: a URL or a DOI.
RESOLVABLE = re.compile(r"^(https?://\S+|10\.\d{4,9}/\S+)$")


def run(context):
    results = []

    for constant in cited_constants.ALL_CITED_CONSTANTS:
        complete = all(
            isinstance(getattr(constant, field), str) and getattr(constant, field).strip()
            for field in ("key", "description", "source", "identifier", "retrieved", "quoted_context")
        )
        results.append(check(
            "CIT-record-" + constant.key,
            complete,
            "cited constant %s has an empty field; a value from a source without "
            "a full record is an unsourced value" % constant.key,
        ))

        results.append(check(
            "CIT-identifier-" + constant.key,
            bool(RESOLVABLE.match(constant.identifier)),
            "cited constant %s has identifier %r, which is neither a URL nor a DOI"
            % (constant.key, constant.identifier),
        ))

        results.append(check(
            "CIT-consumed-" + constant.key,
            bool(constant.consumed_by.strip()),
            "cited constant %s declares no consumer; an unused citation is "
            "decoration" % constant.key,
        ))

    # The reason to cite the constant at all: it is an outside anchor for our
    # own arithmetic. Both computation paths must reproduce it.
    reference = cited_constants.reference_digits()
    for label, digits in (("a", context.digits_a), ("b", context.digits_b)):
        computed_prefix = digits[:len(reference)]
        first_mismatch = _first_mismatch(computed_prefix, reference)
        results.append(check(
            "CIT-agrees-" + label,
            first_mismatch is None,
            "path %s disagrees with the published expansion at decimal position "
            "%s" % (label, first_mismatch),
        ))

    results.append(check(
        "CIT-single-source-of-truth",
        _occurrences_outside_declaration(cited_constants.PI_FIRST_100_DECIMALS.value) == [],
        "the cited digit string is duplicated in %s; a cited value must live in "
        "exactly one place" % _occurrences_outside_declaration(
            cited_constants.PI_FIRST_100_DECIMALS.value),
    ))

    return results


def _first_mismatch(computed, reference):
    for index, (left, right) in enumerate(zip(computed, reference)):
        if left != right:
            return index + 1
    return None


def _occurrences_outside_declaration(value):
    """Files, other than the declaration itself, that contain the cited string."""
    needle = value[:40]
    found = []
    for directory in ("src", "checks"):
        folder = os.path.join(manuscript.ROOT, directory)
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".py") or name == "cited_constants.py":
                continue
            with open(os.path.join(folder, name), "r", encoding="utf-8") as handle:
                if needle in handle.read():
                    found.append(os.path.join(directory, name))
    return found
