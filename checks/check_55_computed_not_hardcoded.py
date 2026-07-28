"""A computed number must not also exist as a literal in the code.

The other half of the cited/computed split. `check_20` makes sure a value taken
from a source has a record. This makes sure a value the paper derives is never
also written down by hand next to the code that derives it -- the failure where
a result and its own hard-coded copy drift apart and nobody notices, because the
hard-coded copy is what gets printed.

Implementation: every module under `src/` and `checks/` is parsed with the
standard library's `ast` and its numeric literals are collected. Comments and
strings are invisible to `ast`, so prose that mentions a number is not flagged
-- only executable code is. `src/frozen_claims.py` is exempt, because it is the
one place the frozen values are allowed to live.

Only COMPUTED_DUAL claims are guarded. A DECLARED value such as the number of
categories is supposed to appear in code -- that is what declaring it means.
"""

import ast
import os

from checks import check
from src import frozen_claims
from src import manuscript

ORDER = 55
NAME = "Computed values are not hard-coded anywhere in the source"
GATE = False

#: The one module allowed to contain the frozen values.
EXEMPT_MODULE = "frozen_claims.py"

#: Integer results below this are not guarded. A result of 9 cannot be
#: distinguished from the 9 in a range check or an array index, so guarding it
#: would produce noise rather than signal. Non-integer results are always
#: guarded, however small: a literal 4.74 in the source is never a coincidence.
#: This is a stated weakness of the check, not a hidden one.
SMALLEST_GUARDED_INTEGER = 10

#: Module-level names whose values are infrastructure metadata rather than
#: results, and whose literals are therefore not policed. `ORDER` is the run
#: position of a check module: `check_95_mutation_evidence.py` sets ORDER = 95,
#: which collided with an observed count of 95 and was reported as a hard-coded
#: result on the first run of this check. The exemption is narrow and named.
EXEMPT_ASSIGNMENT_NAMES = ("ORDER",)


def run(context):
    guarded = {}
    for claim in frozen_claims.CLAIMS:
        if claim.kind != frozen_claims.COMPUTED_DUAL:
            continue
        value = float(context.values_a[claim.id])
        if value == int(value) and abs(value) < SMALLEST_GUARDED_INTEGER:
            continue
        guarded.setdefault(frozen_claims.render(context.values_a[claim.id], claim.fmt), []).append(claim.id)

    offences = []
    for relative_path, literals in _numeric_literals().items():
        for literal in literals:
            for fmt in ("%d", "%.2f", "%.3f", "%.4f"):
                try:
                    rendered = frozen_claims.render(literal, fmt)
                except ValueError:
                    continue
                if rendered in guarded:
                    offences.append("%s in %s (claims: %s)"
                                    % (rendered, relative_path, ", ".join(guarded[rendered])))

    return [check(
        "SPLIT-no-hardcoded-results",
        not offences,
        "computed results appear as literals in the source, where they can drift "
        "from the computation that produced them: %s" % "; ".join(sorted(set(offences))),
    )]


def _numeric_literals():
    """{relative path: [numeric literals]} for every module we police."""
    found = {}
    for directory in ("src", "checks"):
        folder = os.path.join(manuscript.ROOT, directory)
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".py") or name == EXEMPT_MODULE:
                continue
            path = os.path.join(folder, name)
            with open(path, "r", encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=path)
            exempt = set()
            for node in ast.walk(tree):
                if (isinstance(node, ast.Assign)
                        and len(node.targets) == 1
                        and isinstance(node.targets[0], ast.Name)
                        and node.targets[0].id in EXEMPT_ASSIGNMENT_NAMES):
                    exempt.update(id(child) for child in ast.walk(node))
            literals = [
                node.value for node in ast.walk(tree)
                if isinstance(node, ast.Constant)
                and isinstance(node.value, (int, float))
                and not isinstance(node.value, bool)
                and id(node) not in exempt
            ]
            found[os.path.join(directory, name)] = literals
    return found
