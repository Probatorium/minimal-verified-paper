#!/usr/bin/env python3
"""
check_declared_values.py - no value is declared on two surfaces without a check tying them.

WHY THIS EXISTS, and it is worth being blunt about it. A commit hash that pins
this package was declared on two surfaces, in `subject.py` of the study and in
that study's README, with nothing tying them. They drifted. A stranger following
the README would have checked out the wrong commit, hit the study's refusal, and
concluded that the package does not run.

That is not silent aging. It is **M1 in its pure form**: a value stated twice,
with no executable comparison between the statements. It is the exact failure
this package exists to make impossible, and the mechanism was simply ABSENT from
it. The author of the mechanism and the author of the failure are the same
person, which is the one thing the Nature case cannot offer.

The generalisation is the rule this file enforces:

    **Any value that appears on more than one surface needs a check that ties
    the surfaces together, and the check must fail if a surface stops carrying
    the value at all.**

The second half is "presence is not location" applied to surfaces. A check that
only compares the surfaces it finds will pass happily after one of them is
deleted, so the surfaces are DECLARED and a missing one is a failure.

WHAT THIS FILE TIES HERE. The CODECHECK manifest names the files a codechecker
will compare. `codecheck_run.py` produces files. Nothing connected the two: the
manifest could name a file the runner never writes, or the runner could be
renamed and the manifest silently go stale. That is the same duplication in a
different costume.

The number of checks and the number of mutants are already tied by the suite's
own self-description assertions inside `verify.py`, so they are not repeated
here. This file names them anyway, so that a reader can see they were considered
rather than forgotten.

Usage:
    python check_declared_values.py
"""

import io
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))

#: Files the CODECHECK manifest is allowed to name, and what produces each one.
#: A manifest entry outside this map is a value declared with no producer.
PRODUCERS = {
    "codecheck/report.txt": "codecheck_run.py",
    "figures/digit_frequencies.svg": "make_figure.py",
}

#: Values already tied by another mechanism, named here so that they are visibly
#: considered rather than silently omitted.
TIED_ELSEWHERE = (
    ("number of checks", "paper.md and verify.py",
     "verify.py asserts its own check count in the suite self-description"),
    ("number of mutants", "paper.md and mutate.py",
     "mutate.py reports the count it actually generated"),
)


def manifest_entries():
    ruta = os.path.join(AQUI, "codecheck.yml")
    if not os.path.exists(ruta):
        return None
    texto = io.open(ruta, encoding="utf-8").read()
    return re.findall(r"^\s*-\s*file:\s*(\S+)\s*$", texto, re.M)


def main():
    print("DECLARED VALUES: no value on two surfaces without a check tying them")
    print("")
    fallos = []

    entradas = manifest_entries()
    if entradas is None:
        fallos.append("codecheck.yml does not exist, so the manifest declares "
                      "nothing and cannot be tied to anything")
        entradas = []
    else:
        print("  CODECHECK manifest: %d entry(ies)" % len(entradas))

    for rel in entradas:
        productor = PRODUCERS.get(rel)
        if productor is None:
            fallos.append("the manifest names %r and NOTHING in this package is "
                          "declared to produce it. Either it is stale, or a "
                          "producer must be declared. REMEDY: add it to PRODUCERS "
                          "in check_declared_values.py, or remove the manifest "
                          "entry" % rel)
            continue
        if not os.path.exists(os.path.join(AQUI, productor)):
            fallos.append("the manifest names %r, produced by %s, and %s does not "
                          "exist. REMEDY: restore %s or drop the manifest entry"
                          % (rel, productor, productor, productor))
            continue
        existe = os.path.exists(os.path.join(AQUI, rel.replace("/", os.sep)))
        print("    %-34s <- %-18s %s"
              % (rel, productor, "present" if existe else "NOT YET PRODUCED"))
        if not existe:
            fallos.append("the manifest names %r and the file is absent. A "
                          "codechecker would find an empty comparison. REMEDY: run "
                          "`python %s` before publishing" % (rel, productor))

    for rel, productor in sorted(PRODUCERS.items()):
        if rel not in entradas:
            fallos.append("%s is declared to be produced by %s and the manifest "
                          "does NOT name it. A produced artifact outside the "
                          "manifest is invisible to the codechecker. REMEDY: add "
                          "it to codecheck.yml, or remove it from PRODUCERS"
                          % (rel, productor))

    print("")
    print("  values tied by another mechanism, listed so they are visibly considered:")
    for nombre, donde, como in TIED_ELSEWHERE:
        print("    %-18s on %-24s %s" % (nombre, donde, como))

    print("")
    if fallos:
        print("FAIL: %d" % len(fallos))
        for f in fallos:
            print("   X %s" % f)
        return 1
    print("OK: every manifest entry has a declared producer, every declared "
          "producer is in")
    print("    the manifest, and every named file exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
