#!/usr/bin/env python3
"""Regenerate the paper's figure from the data.

    python make_figure.py

Separate from `verify.py` on purpose. Verification never writes: it only reads
the committed figure and compares it against what the data currently render. If
regenerating were part of verification, a stale figure would silently fix itself
and nobody would learn that it had gone stale.

So the workflow is: change the analysis, run this, look at the difference, and
commit the new figure deliberately.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import figure
from src import frozen_claims
from src import manuscript


def main():
    digits = frozen_claims.digits_path_a()
    values, counts = frozen_claims.analyse_path_a(digits)
    svg = figure.render_svg(counts, float(values["expected_count"]))

    destination = os.path.join(manuscript.ROOT, manuscript.FIGURE)
    folder = os.path.dirname(destination)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(svg)

    print("wrote %s (%d bytes)" % (manuscript.FIGURE, len(svg)))
    print("run verify.py to confirm it matches the frozen counts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
