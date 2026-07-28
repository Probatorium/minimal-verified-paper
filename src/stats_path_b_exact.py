"""Path B statistics: exact rational arithmetic and a recursive tail.

Independent re-derivation of everything in `stats_path_a_series.py`. The two
modules import nothing from each other and use different mathematics:

  * the chi-square statistic from the algebraically rearranged identity
        X^2 = 10 * sum(O^2) / n - n
    evaluated in exact `fractions.Fraction` arithmetic, so there is no rounding
    at all;
  * the chi-square upper tail by the exact recursion
        Q(x, k + 2) = Q(x, k) + (x/2)^(k/2) e^(-x/2) / Gamma(k/2 + 1)
    anchored at Q(x, 1) = erfc(sqrt(x/2)) and Q(x, 2) = e^(-x/2);
  * erfc from the Maclaurin series of erf, not from `math.erfc`, so that the two
    paths do not both lean on the same library routine.

If Path A and Path B agree it is because the mathematics agrees, not because
one called the other.
"""

import math
from fractions import Fraction

#: Number of possible decimal digits, i.e. the number of categories in the test.
N_CATEGORIES = 10


def digit_counts(digits):
    """Observed count of each digit 0-9, as a list of length 10.

    Path B counts by rendering the sequence as a string and asking the string
    how many times each character occurs -- a different code path in a different
    part of the interpreter from Path A's explicit loop.
    """
    text = "".join(str(d) for d in digits)
    return [text.count(str(d)) for d in range(N_CATEGORIES)]


def chi_square_statistic(counts):
    """Pearson's X^2 against the uniform null, as an exact Fraction.

    Derivation of the form used here, starting from the textbook definition with
    E = n / 10:
        sum (O - n/10)^2 / (n/10)
          = (10/n) * (sum O^2 - 2*(n/10)*sum O + 10*(n/10)^2)
          = (10/n) * (sum O^2 - n^2/10)
          = 10 * sum(O^2) / n - n
    """
    n = sum(counts)
    sum_of_squares = sum(observed * observed for observed in counts)
    return Fraction(N_CATEGORIES * sum_of_squares, n) - n


def chi_square_sf(x, df):
    """Upper tail P(X^2 >= x) for `df` degrees of freedom, by exact recursion."""
    x = float(x)
    if x <= 0:
        return 1.0
    if df % 2 == 1:
        tail = erfc_series(math.sqrt(x / 2.0))
        k = 1
    else:
        tail = math.exp(-x / 2.0)
        k = 2
    while k + 2 <= df:
        log_term = (k / 2.0) * math.log(x / 2.0) - x / 2.0 - math.lgamma(k / 2.0 + 1.0)
        tail += math.exp(log_term)
        k += 2
    return tail


def erfc_series(x):
    """1 - erf(x), with erf from its Maclaurin series.

    erf(x) = (2/sqrt(pi)) * sum_{k>=0} (-1)^k x^(2k+1) / (k! (2k+1))

    The series is alternating, so it is accurate for the moderate arguments this
    paper needs (|x| below about 3) and would lose precision for large x. It is
    never called here with a large argument; `check_30_double_derivation.py`
    pins it against the standard library over the range actually used.
    """
    if x < 0:
        return 2.0 - erfc_series(-x)
    term = x
    total = x
    k = 1
    while True:
        term *= -x * x / k
        contribution = term / (2 * k + 1)
        total += contribution
        if abs(contribution) <= abs(total) * 1e-18 or k > 10000:
            break
        k += 1
    erf = 2.0 / math.sqrt(math.pi) * total
    return 1.0 - erf


def standardized_residual(observed, n):
    """Standardized residual of one category, as an exact Fraction over a sqrt.

    Same null as Path A -- Binomial(n, 1/10) -- reached by writing the variance
    as an exact rational before taking the single unavoidable square root.
    """
    p = Fraction(1, N_CATEGORIES)
    expected = Fraction(n) * p
    variance = Fraction(n) * p * (1 - p)
    return float(Fraction(observed) - expected) / math.sqrt(float(variance))


def normal_two_sided_p(z):
    """P(|Z| >= |z|) for a standard normal Z, via the series-based erfc."""
    return erfc_series(abs(z) / math.sqrt(2.0))


def bonferroni(p, n_tests):
    """Family-wise adjusted p-value, computed as an exact product then clamped."""
    scaled = Fraction(n_tests) * Fraction(p)
    return float(min(Fraction(1), scaled))
