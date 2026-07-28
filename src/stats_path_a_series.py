"""Path A statistics: floating point, tail probabilities by infinite series.

Every quantity the paper reports is computed here AND, by a different route, in
`stats_path_b_exact.py`. The two modules import nothing from each other.

Path A's flavour:
  * the chi-square statistic in the textbook form  sum (O - E)^2 / E, in floats;
  * the chi-square upper tail from the Maclaurin series of the regularized
    lower incomplete gamma function;
  * the two-sided normal tail from the standard library's `math.erfc`.

Known limitation, stated because the method requires stating it: computing an
upper tail as 1 - P(a, y) loses relative precision when the tail is tiny. The
p-values this paper reports are not tiny, so the two paths agree to well within
the tolerance declared in `frozen_claims.py`. A paper reporting p = 1e-12 could
not use this path.
"""

import math

#: Number of possible decimal digits, i.e. the number of categories in the test.
N_CATEGORIES = 10


def digit_counts(digits):
    """Observed count of each digit 0-9, as a list of length 10.

    Path A counts by walking the sequence once and incrementing a bucket.
    """
    counts = [0] * N_CATEGORIES
    for d in digits:
        counts[d] += 1
    return counts


def chi_square_statistic(counts):
    """Pearson's X^2 against the uniform null, as a float.

    Textbook form: sum over categories of (observed - expected)^2 / expected.
    """
    n = sum(counts)
    expected = n / N_CATEGORIES
    return sum((observed - expected) ** 2 / expected for observed in counts)


def chi_square_sf(x, df):
    """Upper tail P(X^2 >= x) for `df` degrees of freedom.

    Uses Q(a, y) = 1 - P(a, y) with the series
        P(a, y) = e^-y * y^a * sum_{n>=0} y^n / Gamma(a + n + 1).
    """
    if x <= 0:
        return 1.0
    a = df / 2.0
    y = x / 2.0
    term = 1.0 / math.gamma(a + 1.0)
    total = term
    n = 1
    while True:
        term *= y / (a + n)
        total += term
        if term <= total * 1e-17 or n > 100000:
            break
        n += 1
    lower = math.exp(-y + a * math.log(y)) * total
    return 1.0 - lower


def standardized_residual(observed, n):
    """Standardized residual of one category under the uniform multinomial null.

    Under the null the count of a single digit is Binomial(n, 1/10), so its
    standard deviation is sqrt(n * (1/10) * (9/10)), not sqrt(expected). Using
    sqrt(expected) here would inflate the residual; the two paths would still
    agree, because they would be wrong together. This is why the residual is
    also checked against a tabulated value in `check_30_double_derivation.py`.
    """
    p = 1.0 / N_CATEGORIES
    expected = n * p
    sd = math.sqrt(n * p * (1.0 - p))
    return (observed - expected) / sd


def normal_two_sided_p(z):
    """P(|Z| >= |z|) for a standard normal Z, via the library's erfc."""
    return math.erfc(abs(z) / math.sqrt(2.0))


def bonferroni(p, n_tests):
    """Family-wise adjusted p-value for `n_tests` simultaneous comparisons."""
    return min(1.0, p * n_tests)
