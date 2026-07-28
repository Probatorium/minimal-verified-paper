#!/usr/bin/env python3
"""Mutation study: corrupt the package on purpose and see what dies.

    python mutate.py            run the study and rewrite mutation_report.md
    python mutate.py --dry-run  run the study and print, without writing

A suite of assertions that has never failed is a suite nobody has tested. This
script makes a throwaway copy of the package, applies one deliberate corruption
to it, runs `verify.py` inside the copy, and records exactly which assertions
went from passing to failing. Nothing here touches the real package.

Two numbers are reported per mutant, and the distinction matters:

  killed      assertions that ran and failed. This is the mutation score.
  not reached assertions that never ran, because a gate check stopped the suite
              first. A mutant that stops the run at the gate is caught early and
              hard: the analysis never happens. Counting those as "killed" would
              flatter the suite, so they are reported separately.

A mutant that kills nothing is a hole in the suite, and `check_95` refuses to
let the paper ship with one.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import manuscript

DATA = "input data"
SURFACE = "published surface"

#: Each mutant is one deliberate corruption: a single textual substitution
#: applied to one file of a throwaway copy. `expectation` says, in plain words,
#: what the study is trying to find out -- written before the study is run, so
#: that a surprising result stays visible as a surprise.
MUTANTS = (
    dict(
        name="data_digit_flipped",
        family=DATA,
        path="src/data_path_a_spigot.py",
        old="    return decimals[:n]",
        new=("    corrupted = decimals[:n]\n"
             "    corrupted[500] = (corrupted[500] + 1) % 10\n"
             "    return corrupted"),
        expectation="One digit of path A is wrong. The two paths should disagree, "
                    "two counts should move, and every downstream statistic with them.",
    ),
    dict(
        name="data_tail_zeroed",
        family=DATA,
        path="src/data_path_a_spigot.py",
        old="    return decimals[:n]",
        new=("    corrupted = decimals[:n]\n"
             "    return corrupted[:800] + [0] * (n - 800)"),
        expectation="A fifth of the sequence is replaced by zeros. Structurally still "
                    "a digit sequence, so it passes the gate and is caught by the "
                    "statistics instead. Should be the worst-hit mutant.",
    ),
    dict(
        name="data_truncated",
        family=DATA,
        path="src/data_path_b_machin.py",
        old="    return [int(c) for c in decimals[:n]]",
        new="    return [int(c) for c in decimals[:n - 1]]",
        expectation="One digit short. Should die at the gate, before any statistic "
                    "is computed, and therefore kill few assertions while blocking all "
                    "of them.",
    ),
    dict(
        name="data_adjacent_swap",
        family=DATA,
        path="src/data_path_a_spigot.py",
        old="    return decimals[:n]",
        new=("    corrupted = decimals[:n]\n"
             "    corrupted[500], corrupted[501] = corrupted[501], corrupted[500]\n"
             "    return corrupted"),
        expectation="Two digits swapped deep in the sequence. Counts are unchanged, so "
                    "every statistic is unchanged. Only the comparison between the two "
                    "paths can notice. This is the mutant that shows what the suite "
                    "does NOT cover.",
    ),
    dict(
        name="cited_constant_corrupted",
        family=DATA,
        path="src/cited_constants.py",
        old='        "1415926535"',
        new='        "1415926536"',
        expectation="The published anchor is altered. Both computation paths should "
                    "part company with it.",
    ),
    dict(
        name="manuscript_number_edited",
        family=SURFACE,
        path="paper.md",
        old="`X2` equal to 4.74 on 9",
        new="`X2` equal to 4.75 on 9",
        expectation="The prose is edited and nothing else. The headline mechanism: the "
                    "frozen figure is no longer in the text, and the new number is "
                    "covered by no claim.",
    ),
    dict(
        name="frozen_value_edited",
        family=SURFACE,
        path="src/frozen_claims.py",
        old='"0.8564", "%.4f"',
        new='"0.8563", "%.4f"',
        expectation="The frozen value is edited and the prose is not. The same "
                    "mechanism from the other side.",
    ),
    dict(
        name="result_hardcoded_in_source",
        family=SURFACE,
        path="src/stats_path_a_series.py",
        old="    p = 1.0 / N_CATEGORIES",
        new=("    p = 1.0 / N_CATEGORIES\n"
             "    cached_statistic = 4.74"),
        expectation="A computed result is written into the code by hand, where it can "
                    "drift from the computation. The cited/computed split should catch it.",
    ),
    dict(
        name="figure_gone_stale",
        family=SURFACE,
        path="figures/digit_frequencies.svg",
        old=">116</text>",
        new=">117</text>",
        expectation="The committed figure no longer shows the committed data.",
    ),
    dict(
        name="forbidden_phrase_reintroduced",
        family=SURFACE,
        path="paper.md",
        # Anchored on a single line: the manuscript is hard-wrapped, so a target
        # phrase that spans a line break never matches.
        old="is nothing here.",
        new="is nothing here. In short, this proves that the digits are even.",
        expectation="A sentence this paper is not entitled to write is added back.",
    ),
    dict(
        name="front_matter_drifted",
        family=SURFACE,
        path="README.md",
        old="Alexis García Hurtado",
        new="Alexis Garcia Hurtado",
        expectation="One accent dropped on one surface. Exact comparison should catch "
                    "what a fuzzy one would not.",
    ),
)

#: Files and folders never copied into a mutant.
SKIP = ("__pycache__", ".git", ".pytest_cache")


def run_verification(directory):
    """Run verify.py inside `directory` and return {check id: True/False}."""
    completed = subprocess.run(
        [sys.executable, "verify.py", "--report"],
        cwd=directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    outcome = {}
    for line in completed.stdout.split("\n"):
        match = re.match(r"^(PASS|FAIL) (\S+)$", line.strip())
        if match:
            outcome[match.group(2)] = match.group(1) == "PASS"
    gate_stopped = "GATE_STOPPED" in completed.stdout
    if not outcome:
        raise RuntimeError("verify.py produced no machine-readable output in %s:\n%s"
                           % (directory, completed.stdout))
    return outcome, gate_stopped


def copy_package(destination):
    def ignore(_directory, names):
        return [name for name in names if name in SKIP]
    shutil.copytree(ROOT, destination, ignore=ignore)


def apply_mutation(directory, mutant):
    path = os.path.join(directory, *mutant["path"].split("/"))
    with open(path, "r", encoding="utf-8") as handle:
        text = handle.read()
    if text.count(mutant["old"]) != 1:
        raise RuntimeError(
            "mutant %r does not apply cleanly: its target text occurs %d times in %s"
            % (mutant["name"], text.count(mutant["old"]), mutant["path"]))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text.replace(mutant["old"], mutant["new"]))


def study():
    baseline, baseline_gated = run_verification(ROOT)
    baseline_failures = sorted(name for name, ok in baseline.items() if not ok)
    surviving = set(name for name, ok in baseline.items() if ok)

    rows = []
    workspace = tempfile.mkdtemp(prefix="mutation_study_")
    try:
        for index, mutant in enumerate(MUTANTS):
            directory = os.path.join(workspace, "mutant_%02d" % index)
            copy_package(directory)
            apply_mutation(directory, mutant)
            outcome, gated = run_verification(directory)

            killed = sorted(name for name in surviving
                            if name in outcome and not outcome[name])
            not_reached = sorted(name for name in surviving if name not in outcome)
            rows.append(dict(mutant=mutant, killed=killed,
                             not_reached=not_reached, gated=gated))
            print("  %-32s killed %3d   not reached %3d%s"
                  % (mutant["name"], len(killed), len(not_reached),
                     "   [stopped at the gate]" if gated else ""))
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    return baseline_failures, baseline_gated, rows


def report(baseline_failures, baseline_gated, rows):
    counts = [len(row["killed"]) for row in rows]
    lines = []
    add = lines.append

    add("# Mutation study")
    add("")
    add("Generated by `mutate.py`. Every row is one deliberate corruption of a")
    add("throwaway copy of this package, followed by a full run of `verify.py`")
    add("inside that copy.")
    add("")
    add("**killed** counts assertions that ran and failed. **not reached** counts")
    add("assertions that never ran because a gate check stopped the suite first;")
    add("those are caught even harder, but counting them as killed would flatter")
    add("the suite, so they are kept apart.")
    add("")
    add("```")
    add("MUTANTS: %d" % len(rows))
    add("MIN_CHECKS_KILLED: %d" % min(counts))
    add("MAX_CHECKS_KILLED: %d" % max(counts))
    add("```")
    add("")

    if baseline_failures:
        add("The baseline run of this package was NOT clean. The assertions below")
        add("were already failing before any mutation, and are excluded from every")
        add("count in this report: %s" % ", ".join("`%s`" % name for name in baseline_failures))
        add("")
    else:
        add("The baseline run of this package was clean: every assertion passed")
        add("before any mutation was applied.")
        add("")
    if baseline_gated:
        add("The baseline run stopped at the gate, so this report is not")
        add("trustworthy until that is fixed.")
        add("")

    add("## Summary")
    add("")
    add("| Mutant | Family | Killed | Not reached |")
    add("| ------ | ------ | -----: | ----------: |")
    for row in rows:
        add("| `%s` | %s | %d | %d |"
            % (row["mutant"]["name"], row["mutant"]["family"],
               len(row["killed"]), len(row["not_reached"])))
    add("")

    add("## What each mutant killed")
    add("")
    for row in rows:
        mutant = row["mutant"]
        add("### `%s`" % mutant["name"])
        add("")
        add("Family: %s. Target: `%s`." % (mutant["family"], mutant["path"]))
        add("")
        add("Expected before running: %s" % mutant["expectation"])
        add("")
        if row["gated"]:
            add("The suite stopped at the structural gate. The statistics were never")
            add("computed, which is the intended behaviour for input this broken.")
            add("")
        add("Killed %d assertion(s): %s"
            % (len(row["killed"]),
               ", ".join("`%s`" % name for name in row["killed"]) or "none"))
        add("")
        if row["not_reached"]:
            add("Never reached %d assertion(s), the first being `%s`."
                % (len(row["not_reached"]), row["not_reached"][0]))
            add("")

    return "\n".join(lines) + "\n"


def main(argv):
    dry_run = "--dry-run" in argv
    print("running the mutation study over %d mutants" % len(MUTANTS))
    baseline_failures, baseline_gated, rows = study()
    text = report(baseline_failures, baseline_gated, rows)

    if dry_run:
        print("")
        print(text)
        return 0

    destination = os.path.join(manuscript.ROOT, manuscript.MUTATION_REPORT)
    with open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("")
    print("wrote %s" % manuscript.MUTATION_REPORT)
    counts = [len(row["killed"]) for row in rows]
    print("mutants %d, fewest killed %d, most killed %d"
          % (len(rows), min(counts), max(counts)))
    if min(counts) == 0:
        print("A mutant survived. That is a hole in the suite, not a success.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
