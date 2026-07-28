"""Path B: decimal digits of pi by Machin's arctangent formula in fixed point.

    pi = 16 * arctan(1/5) - 4 * arctan(1/239)          (Machin, 1706)

Each arctangent is summed as an alternating series in fixed-point integer
arithmetic, so the result is exact up to a known truncation guard. This shares
no code with Path A (`data_path_a_spigot.py`) and uses a completely different
mathematical identity and a completely different arithmetic strategy (one big
integer versus an array of small ones).

Independence is not absolute: both paths run on the same CPython interpreter and
use its built-in integers. The claim is that they share no project code and no
algorithm, which is what makes an agreement between them informative. See the
"Limits" section of the README.
"""

#: Extra decimal places carried through the fixed-point arithmetic so that the
#: returned digits are unaffected by truncation of the series.
GUARD_DIGITS = 20


def pi_decimal_digits(n, guard=GUARD_DIGITS):
    """Return the first `n` decimal digits of pi as a list of ints 0-9.

    The leading "3" is NOT included: element 0 is the first digit after the
    decimal point. Same contract as `data_path_a_spigot.pi_decimal_digits`.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    scale = 10 ** (n + guard)
    pi_scaled = 4 * (4 * _arccot(5, scale) - _arccot(239, scale))
    text = str(pi_scaled)
    if not text.startswith("3"):
        raise RuntimeError("Machin sum did not produce a number starting with 3")
    decimals = text[1:]
    if len(decimals) < n:
        raise RuntimeError("Machin sum produced fewer digits than requested")
    return [int(c) for c in decimals[:n]]


def _arccot(x, scale):
    """arctan(1/x) in fixed point, i.e. round(scale * arctan(1/x)).

    Sums 1/x - 1/(3x^3) + 1/(5x^5) - ... until the term underflows to zero.
    """
    power = scale // x
    total = power
    divisor = 3
    sign = -1
    x_squared = x * x
    while power:
        power //= x_squared
        total += sign * (power // divisor)
        sign = -sign
        divisor += 2
    return total
