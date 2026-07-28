"""Every number the manuscript reports, frozen as an executable assertion.

This file is the contract between the text and the computation. Each entry says:

  * `text`   -- the literal string that must appear in the manuscript;
  * `fmt`    -- how the computed value is rendered before comparison;
  * `section`-- the manuscript section the number must appear in;
  * `kind`   -- where the number comes from (see below).

`checks/check_40_frozen_numbers.py` fails if a computed value stops rendering to
`text`, and fails if `text` stops appearing in that section of the manuscript.
Either direction of drift -- the code changing or the prose changing -- breaks
the build. That is the whole point.

Kinds
-----
COMPUTED_DUAL : derived by this package along two independent paths
                (`stats_path_a_series` and `stats_path_b_exact`, fed by
                `data_path_a_spigot` and `data_path_b_machin`).
COMPUTED_META : derived by the package about itself (how many checks it runs,
                what the mutation study found). One path only; there is no
                second way to count your own checks.
DECLARED      : a choice, not a derivation -- the sample size, the number of
                categories, the significance level. Declaring these as claims
                keeps them from being quietly edited in the prose alone.
CITED         : taken from an outside source; see `cited_constants.py`.

To add a number to the paper: add it here first, run the verification, and only
then write it in the text. Numbers that appear in the text without an entry here
are caught by `check_50`, not tolerated.
"""

from collections import namedtuple
from fractions import Fraction

from . import cited_constants
from . import data_path_a_spigot
from . import data_path_b_machin
from . import stats_path_a_series
from . import stats_path_b_exact

COMPUTED_DUAL = "COMPUTED_DUAL"
COMPUTED_META = "COMPUTED_META"
DECLARED = "DECLARED"
CITED = "CITED"

Claim = namedtuple("Claim", "id kind section text fmt description")


# --------------------------------------------------------------------------
# Design choices. These are not derived from anything; they are decisions, and
# saying so is part of the method.
# --------------------------------------------------------------------------

#: How many decimal digits of pi the analysis uses. Chosen so that the whole
#: verification, including the deliberately slow spigot path, runs in about a
#: second, and so that the expected count per digit (100) is comfortably above
#: the conventional minimum of five for a chi-square approximation.
N_DIGITS = 1000

#: The ten possible decimal digits: the number of categories in the test.
N_CATEGORIES = 10

#: Significance level, fixed before looking at the data.
ALPHA = 0.05

#: The digit whose count is examined post hoc in section 4. It is chosen by the
#: data (it is the modal digit), which is exactly why its p-value is reported
#: only after a Bonferroni adjustment over all ten digits.
POST_HOC_CATEGORIES = N_CATEGORIES


CLAIMS = (
    # -- 1. Question -------------------------------------------------------
    Claim("n_digits_q", DECLARED, "1. Question", "1000", "%d",
          "Sample size, stated in the question."),
    Claim("n_categories_q", DECLARED, "1. Question", "10", "%d",
          "Number of possible digit values, stated in the question."),

    # -- 2. Data -----------------------------------------------------------
    Claim("n_digits_data", DECLARED, "2. Data", "1000", "%d",
          "Sample size, restated where the data are described."),
    Claim("n_reference_digits", CITED, "2. Data", "100", "%d",
          "Length of the published pi prefix used as an external anchor."),

    # -- 3. Null model and test -------------------------------------------
    Claim("n_categories_null", DECLARED, "3. Null model and test", "10", "%d",
          "Number of categories in the null model."),
    Claim("expected_count", COMPUTED_DUAL, "3. Null model and test", "100", "%d",
          "Expected count per digit under the uniform null: n divided by k."),
    Claim("degrees_of_freedom", COMPUTED_DUAL, "3. Null model and test", "9", "%d",
          "Degrees of freedom: number of categories minus one."),
    Claim("alpha", DECLARED, "3. Null model and test", "0.05", "%.2f",
          "Significance level fixed in advance."),

    # -- 4. Result ---------------------------------------------------------
    Claim("count_0", COMPUTED_DUAL, "4. Result", "93", "%d", "Observed count of digit 0."),
    Claim("count_1", COMPUTED_DUAL, "4. Result", "116", "%d", "Observed count of digit 1."),
    Claim("count_2", COMPUTED_DUAL, "4. Result", "103", "%d", "Observed count of digit 2."),
    Claim("count_3", COMPUTED_DUAL, "4. Result", "102", "%d", "Observed count of digit 3."),
    Claim("count_4", COMPUTED_DUAL, "4. Result", "93", "%d", "Observed count of digit 4."),
    Claim("count_5", COMPUTED_DUAL, "4. Result", "97", "%d", "Observed count of digit 5."),
    Claim("count_6", COMPUTED_DUAL, "4. Result", "94", "%d", "Observed count of digit 6."),
    Claim("count_7", COMPUTED_DUAL, "4. Result", "95", "%d", "Observed count of digit 7."),
    Claim("count_8", COMPUTED_DUAL, "4. Result", "101", "%d", "Observed count of digit 8."),
    Claim("count_9", COMPUTED_DUAL, "4. Result", "106", "%d", "Observed count of digit 9."),
    Claim("chi_square", COMPUTED_DUAL, "4. Result", "4.74", "%.2f",
          "Pearson chi-square statistic against the uniform null."),
    Claim("degrees_of_freedom_result", COMPUTED_DUAL, "4. Result", "9", "%d",
          "Degrees of freedom, restated with the result."),
    Claim("p_value", COMPUTED_DUAL, "4. Result", "0.8564", "%.4f",
          "Upper-tail probability of the chi-square statistic."),
    Claim("largest_count", COMPUTED_DUAL, "4. Result", "116", "%d",
          "The largest observed count across the ten digits."),
    Claim("post_hoc_z", COMPUTED_DUAL, "4. Result", "1.6865", "%.4f",
          "Standardized residual of the modal digit under the binomial null."),
    Claim("post_hoc_p", COMPUTED_DUAL, "4. Result", "0.0917", "%.4f",
          "Two-sided normal p-value for that residual, before adjustment."),
    Claim("post_hoc_comparisons", DECLARED, "4. Result", "10", "%d",
          "Number of simultaneous comparisons in the Bonferroni adjustment."),
    Claim("post_hoc_p_adjusted", COMPUTED_DUAL, "4. Result", "0.917", "%.3f",
          "Bonferroni-adjusted p-value for the modal digit."),

    # -- 5. What this does not show ---------------------------------------
    Claim("n_digits_limits", DECLARED, "5. What this does not show", "1000", "%d",
          "Sample size, restated where its limits are discussed."),

    # -- 6. How this paper verifies itself --------------------------------
    Claim("n_checks", COMPUTED_META, "6. How this paper verifies itself", "104", "%d",
          "Total number of checks the verification runs, counting this one."),
    Claim("n_mutants", COMPUTED_META, "6. How this paper verifies itself", "11", "%d",
          "Number of mutants in the mutation study."),
    Claim("min_checks_killed", COMPUTED_META, "6. How this paper verifies itself", "1", "%d",
          "Fewest checks killed by any single mutant."),
    Claim("max_checks_killed", COMPUTED_META, "6. How this paper verifies itself", "35", "%d",
          "Most checks killed by any single mutant."),
)


def claims_by_id():
    return {claim.id: claim for claim in CLAIMS}


def render(value, fmt):
    """Render a computed value the way the manuscript prints it."""
    if isinstance(value, Fraction):
        value = float(value)
    if fmt == "%d":
        rounded = round(float(value))
        if abs(float(value) - rounded) > 1e-9:
            raise ValueError("value %r is not an integer but is formatted as one" % (value,))
        return fmt % rounded
    return fmt % float(value)


def analyse(digits, stats_module):
    """Run the analysis over an already-obtained digit sequence.

    The digits are passed in rather than fetched here so that the structural
    invariants in `check_10` can run against them BEFORE any statistic is
    computed. A corrupt sequence must die before it can produce a plausible
    p-value.

    Returns a dict keyed by claim id. Calling this with (path A digits, path A
    stats) and with (path B digits, path B stats) must give the same rendered
    numbers; `check_30_double_derivation.py` is what insists on it.
    """
    counts = stats_module.digit_counts(digits)
    n = sum(counts)

    expected = Fraction(n, N_CATEGORIES)
    degrees_of_freedom = N_CATEGORIES - 1
    statistic = stats_module.chi_square_statistic(counts)
    p_value = stats_module.chi_square_sf(statistic, degrees_of_freedom)

    largest = max(counts)
    z = stats_module.standardized_residual(largest, n)
    post_hoc_p = stats_module.normal_two_sided_p(z)
    adjusted = stats_module.bonferroni(post_hoc_p, POST_HOC_CATEGORIES)

    values = {
        "expected_count": expected,
        "degrees_of_freedom": degrees_of_freedom,
        "degrees_of_freedom_result": degrees_of_freedom,
        "chi_square": statistic,
        "p_value": p_value,
        "largest_count": largest,
        "post_hoc_z": z,
        "post_hoc_p": post_hoc_p,
        "post_hoc_p_adjusted": adjusted,
    }
    for digit in range(N_CATEGORIES):
        values["count_%d" % digit] = counts[digit]
    return values, counts


def digits_path_a():
    return data_path_a_spigot.pi_decimal_digits(N_DIGITS)


def digits_path_b():
    return data_path_b_machin.pi_decimal_digits(N_DIGITS)


def analyse_path_a(digits):
    return analyse(digits, stats_path_a_series)


def analyse_path_b(digits):
    return analyse(digits, stats_path_b_exact)


def declared_values():
    """The DECLARED claims, resolved from the constants at the top of this file."""
    return {
        "n_digits_q": N_DIGITS,
        "n_digits_data": N_DIGITS,
        "n_digits_limits": N_DIGITS,
        "n_categories_q": N_CATEGORIES,
        "n_categories_null": N_CATEGORIES,
        "alpha": ALPHA,
        "post_hoc_comparisons": POST_HOC_CATEGORIES,
    }


def cited_values():
    """The CITED claims, resolved from `cited_constants.py`."""
    return {
        "n_reference_digits": len(cited_constants.reference_digits()),
    }
