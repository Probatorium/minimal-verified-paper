"""Two independent derivations of the same numbers must agree.

Path A is the Rabinowitz-Wagon spigot feeding floating-point statistics whose
tail probabilities come from an infinite series. Path B is Machin's formula
feeding exact rational statistics whose tail probabilities come from a recursion
anchored on a hand-rolled erfc. They share no project code.

Agreement between them is evidence; it is not proof. Two implementations can be
wrong in the same way if they share a misunderstanding rather than a line of
code -- which is why `stats_path_a_series.standardized_residual` carries a note
about the variance both paths use. Independence of code is the part that can be
checked mechanically, and this is where it is checked.
"""

import math

from checks import check
from src import frozen_claims
from src import stats_path_b_exact

ORDER = 30
NAME = "Double derivation across two independent code paths"
GATE = False

#: Absolute tolerance for agreement between the two paths on floating point
#: quantities. Far tighter than the precision at which any number is reported.
TOLERANCE = 1e-10


def run(context):
    results = []

    results.append(check(
        "DUAL-digits",
        context.digits_a == context.digits_b,
        "the two data paths produced different digit sequences at position %s"
        % _first_difference(context.digits_a, context.digits_b),
    ))

    for claim in frozen_claims.CLAIMS:
        if claim.kind != frozen_claims.COMPUTED_DUAL:
            continue
        value_a = context.values_a[claim.id]
        value_b = context.values_b[claim.id]
        rendered_a = frozen_claims.render(value_a, claim.fmt)
        rendered_b = frozen_claims.render(value_b, claim.fmt)
        agree = rendered_a == rendered_b and abs(float(value_a) - float(value_b)) <= TOLERANCE
        results.append(check(
            "DUAL-" + claim.id,
            agree,
            "%s differs between paths: A gives %s (%r), B gives %s (%r)"
            % (claim.id, rendered_a, float(value_a), rendered_b, float(value_b)),
        ))

    # Path B replaces the standard library's erfc with a series so that the two
    # paths do not lean on the same routine. That substitution is only legitimate
    # over the range where the series is accurate, so the range is pinned here.
    worst = max(
        abs(math.erfc(x / 10.0) - stats_path_b_exact.erfc_series(x / 10.0))
        for x in range(0, 31)
    )
    results.append(check(
        "DUAL-erfc-range",
        worst <= 1e-12,
        "path B's series erfc departs from the standard library by %g over the "
        "argument range 0 to 3, which is the range this paper uses" % worst,
    ))

    return results


def _first_difference(left, right):
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index + 1
    return "length %d vs %d" % (len(left), len(right))
