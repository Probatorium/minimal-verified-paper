#!/usr/bin/env python3
"""Verify this paper. One command, standard library only, no network.

    python verify.py            run every check and print a summary
    python verify.py -v         list every individual assertion
    python verify.py --report   machine-readable "PASS <id>" / "FAIL <id>" lines

Exit status is 0 if every assertion holds and 1 otherwise. That is what makes
this usable as the gate on a build: the paper either agrees with its own
computation or it does not compile.

Order matters. `checks/check_10_structural_invariants.py` is marked as a gate:
if the digit sequence is not structurally sound the run stops there, before any
statistic exists. A corrupt input should never get far enough to produce a
plausible p-value.
"""

import importlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import data_path_a_spigot
from src import data_path_b_machin
from src import frozen_claims
from src import manuscript
from src import stats_path_a_series
from src import stats_path_b_exact

CHECKS_DIRECTORY = os.path.join(ROOT, "checks")
CHECK_MODULE_PATTERN = re.compile(r"^check_\d+_[a-z_]+\.py$")


class Context(object):
    """Everything the checks need, computed once and only when first asked for.

    The laziness is not an optimisation. It is what lets the structural
    invariants run before any statistic exists: nothing computes a count or a
    p-value until a check actually asks for one, and the gate check asks only
    for the digits.
    """

    def __init__(self, check_module_names):
        self.n_digits = frozen_claims.N_DIGITS
        self.check_module_names = check_module_names
        self.data_module_a = data_path_a_spigot
        self.data_module_b = data_path_b_machin
        self.stats_module_a = stats_path_a_series
        self.stats_module_b = stats_path_b_exact
        #: Filled in by the runner after the suite finishes; see check_40's note.
        self.n_checks = None
        self._cache = {}

    def _memo(self, key, producer):
        if key not in self._cache:
            self._cache[key] = producer()
        return self._cache[key]

    @property
    def digits_a(self):
        return self._memo("digits_a", frozen_claims.digits_path_a)

    @property
    def digits_b(self):
        return self._memo("digits_b", frozen_claims.digits_path_b)

    @property
    def _analysis_a(self):
        return self._memo("analysis_a", lambda: frozen_claims.analyse_path_a(self.digits_a))

    @property
    def _analysis_b(self):
        return self._memo("analysis_b", lambda: frozen_claims.analyse_path_b(self.digits_b))

    @property
    def values_a(self):
        return self._analysis_a[0]

    @property
    def counts_a(self):
        return self._analysis_a[1]

    @property
    def values_b(self):
        return self._analysis_b[0]

    @property
    def counts_b(self):
        return self._analysis_b[1]

    @property
    def mutation_summary(self):
        return self._memo("mutation", self._read_mutation_summary)

    def _read_mutation_summary(self):
        """Parse the machine-readable block `mutate.py` writes into its report."""
        summary = {}
        if not manuscript.exists(manuscript.MUTATION_REPORT):
            return summary
        text = manuscript.read(manuscript.MUTATION_REPORT)
        for key, label in (("n_mutants", "MUTANTS"),
                           ("min_checks_killed", "MIN_CHECKS_KILLED"),
                           ("max_checks_killed", "MAX_CHECKS_KILLED")):
            match = re.search(r"^%s: (\d+)$" % label, text, re.MULTILINE)
            if match:
                summary[key] = int(match.group(1))
        return summary

    def value_for_claim(self, claim):
        """Resolve a frozen claim to the value the package currently computes."""
        if claim.kind == frozen_claims.COMPUTED_DUAL:
            return self.values_a[claim.id]
        if claim.kind == frozen_claims.DECLARED:
            return frozen_claims.declared_values()[claim.id]
        if claim.kind == frozen_claims.CITED:
            return frozen_claims.cited_values()[claim.id]
        if claim.kind == frozen_claims.COMPUTED_META:
            if claim.id == "n_checks":
                return self.n_checks
            return self.mutation_summary.get(claim.id)
        raise ValueError("unknown claim kind %r" % claim.kind)


def discover_check_modules():
    """Import every checks/check_NN_*.py, in run order."""
    names = sorted(name for name in os.listdir(CHECKS_DIRECTORY)
                   if CHECK_MODULE_PATTERN.match(name))
    modules = [importlib.import_module("checks." + name[:-3]) for name in names]
    modules.sort(key=lambda module: module.ORDER)
    return names, modules


def run_all():
    """Run the suite. Returns (results, gate_stopped_at_or_None)."""
    names, modules = discover_check_modules()
    context = Context(names)
    results = []
    grouped = []

    for module in modules:
        module_results = list(module.run(context))
        grouped.append((module, module_results))
        results.extend(module_results)
        if module.GATE and any(not result.ok for result in module_results):
            return context, grouped, results, module

    # The one assertion that cannot live inside a check module: the number of
    # assertions. It is known only once the suite has finished, and it counts
    # itself, so the total below includes this very result.
    from checks import check
    total = len(results) + 1
    context.n_checks = total
    claim = frozen_claims.claims_by_id()["n_checks"]
    meta = check(
        "META-check-count",
        frozen_claims.render(total, claim.fmt) == claim.text,
        "the suite ran %d checks but the manuscript is frozen at %s"
        % (total, claim.text),
    )
    results.append(meta)
    grouped.append((None, [meta]))
    return context, grouped, results, None


def main(argv):
    verbose = "-v" in argv or "--verbose" in argv
    machine = "--report" in argv

    context, grouped, results, gate = run_all()
    failures = [result for result in results if not result.ok]

    if machine:
        for result in results:
            print("%s %s" % ("PASS" if result.ok else "FAIL", result.id))
        print("TOTAL %d" % len(results))
        print("FAILED %d" % len(failures))
        if gate is not None:
            print("GATE_STOPPED %s" % gate.__name__)
        return 1 if failures else 0

    return _print_human(grouped, results, failures, gate, verbose)


def _print_human(grouped, results, failures, gate, verbose):
    for module, module_results in grouped:
        title = module.NAME if module is not None else "Suite self-description"
        bad = [result for result in module_results if not result.ok]
        status = "ok" if not bad else "FAIL"
        print("[%-4s] %-58s %3d checks" % (status, title, len(module_results)))
        for result in module_results:
            if verbose and result.ok:
                print("         . %s" % result.id)
            if not result.ok:
                print("         X %s: %s" % (result.id, result.detail))

    print("")
    print("%d checks, %d failed" % (len(results), len(failures)))
    if gate is not None:
        print("")
        print("STOPPED AT THE GATE: %s failed, so no statistic was computed."
              % gate.NAME)
        print("This is the intended behaviour. A corrupt input must not reach "
              "the analysis.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
