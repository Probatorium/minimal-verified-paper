"""Structural invariants of the data, run BEFORE any statistic is computed.

This is the gate. If the digit sequence is not what a digit sequence has to be,
the run stops here and no p-value is ever produced. The failure mode this
prevents is the dangerous one: corrupt input that still yields a plausible,
publishable-looking number.

Nothing in this module computes a statistic. It only asks whether the object of
study is the kind of object the rest of the paper assumes.
"""

from checks import check

ORDER = 10
NAME = "Structural invariants of the digit sequence"
GATE = True


def run(context):
    results = []
    expected_length = context.n_digits

    for label, digits in (("a", context.digits_a), ("b", context.digits_b)):
        prefix = "INV-len-" + label
        results.append(check(
            prefix,
            len(digits) == expected_length,
            "path %s produced %d digits, expected %d" % (label, len(digits), expected_length),
        ))

        results.append(check(
            "INV-type-" + label,
            all(isinstance(d, int) for d in digits),
            "path %s produced a non-integer element" % label,
        ))

        results.append(check(
            "INV-range-" + label,
            all(0 <= d <= 9 for d in digits),
            "path %s produced an element outside 0-9" % label,
        ))

        distinct = set(digits)
        results.append(check(
            "INV-support-" + label,
            len(distinct) == 10,
            "path %s uses only %d of the 10 possible digit values; a sequence "
            "missing a category cannot be tested against a 10-category null"
            % (label, len(distinct)),
        ))

        results.append(check(
            "INV-nonconstant-" + label,
            len(distinct) > 1,
            "path %s produced a constant sequence" % label,
        ))

        results.append(check(
            "INV-head-" + label,
            digits[:2] == [1, 4],
            "path %s does not start 1, 4 as the decimal expansion of pi must" % label,
        ))

    # Invariants of the METHOD, not of the data: the two paths must really be two.
    # The failure this catches is an implementation quietly aliasing the other,
    # which would make every agreement between them meaningless.
    results.append(check(
        "INV-paths-distinct-data",
        context.data_module_a is not context.data_module_b
        and context.data_module_a.pi_decimal_digits is not context.data_module_b.pi_decimal_digits,
        "the two data paths resolve to the same function; the double derivation "
        "would be a tautology",
    ))

    results.append(check(
        "INV-paths-distinct-stats",
        context.stats_module_a is not context.stats_module_b
        and context.stats_module_a.chi_square_sf is not context.stats_module_b.chi_square_sf,
        "the two statistics paths resolve to the same implementation; the double "
        "derivation would be a tautology",
    ))

    return results
