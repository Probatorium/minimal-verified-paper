"""Path A: decimal digits of pi by the Rabinowitz-Wagon bounded spigot algorithm.

The algorithm uses only integer arithmetic on a fixed-length array of small
integers. It shares no code and no numerical technique with Path B
(`data_path_b_machin.py`), which sums an arctangent series in fixed-point big
integers. Two independent routes to the same digit string.

Reference for the algorithm:
    Rabinowitz, S. and Wagon, S. (1995). "A Spigot Algorithm for the Digits of
    pi". The American Mathematical Monthly 102(3), 195-203.
    (Cited for the method only. No numeric value in this paper is taken from
    that source; see `cited_constants.py` for values that are.)

The algorithm's accuracy degrades in its last few digits, so callers request
`guard` extra digits and keep only the first `n`.
"""

#: Extra digits computed beyond the ones returned, to absorb the tail error of
#: the bounded spigot. 30 is far more than the handful the algorithm can lose.
GUARD_DIGITS = 30


def pi_decimal_digits(n, guard=GUARD_DIGITS):
    """Return the first `n` decimal digits of pi as a list of ints 0-9.

    The leading "3" is NOT included: element 0 is the first digit after the
    decimal point. So the list starts [1, 4, 1, 5, 9, ...].
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    total = n + guard
    stream = _spigot(total)
    # _spigot emits a spurious leading 0, then the integer part 3, then the
    # decimals. Drop the first two.
    decimals = stream[2:]
    if len(decimals) < n:
        raise RuntimeError("spigot produced fewer digits than requested")
    return decimals[:n]


def _spigot(n):
    """Raw Rabinowitz-Wagon output: a leading 0, the digit 3, then decimals."""
    length = 10 * n // 3 + 1
    remainders = [2] * length
    emitted = []
    held_nines = 0
    predigit = 0

    for _ in range(n):
        carry = 0
        for i in range(length - 1, -1, -1):
            value = 10 * remainders[i] + carry * (i + 1)
            remainders[i] = value % (2 * i + 1)
            carry = value // (2 * i + 1)
        remainders[0] = carry % 10
        carry //= 10

        if carry == 9:
            # Cannot emit yet: a later carry may turn this 9 into a 0.
            held_nines += 1
        elif carry == 10:
            # The carry propagates: the held 9s become 0s and predigit rises.
            emitted.append(predigit + 1)
            emitted.extend([0] * held_nines)
            predigit = 0
            held_nines = 0
        else:
            emitted.append(predigit)
            predigit = carry
            emitted.extend([9] * held_nines)
            held_nines = 0

    emitted.append(predigit)
    return emitted
