#!/usr/bin/env python3
"""
codecheck_run.py - the CODECHECK entry point, and the reason it exists.

THE PROBLEM. A CODECHECK manifest is validated against the files that the
workflow CREATES. This package's verification creates nothing: `verify.py` reads
the manuscript and the sources, compares every published number against a fresh
computation, prints a report to stdout and exits 0 or 1. With that, the manifest
would be empty and there would be nothing for a codechecker to compare.

WHY THE OBVIOUS FIX IS THE WRONG ONE. "Verification never writes" is design
property 6 in this package's README. It is published, it is part of what the
package claims, and adding a `--report FILE` flag to `verify.py` would break it
literally while appearing to be a convenience. A published property is not a
detail to be quietly relaxed when it becomes inconvenient; that is precisely the
failure this package exists to make impossible.

THE RESOLUTION. `verify.py` is not touched and still never writes. This wrapper
runs it as a subprocess, captures what it printed, and writes that transcript to
`codecheck/report.txt`. The separation is the point:

    verify.py         reads, compares, prints, exits. Writes nothing. Unchanged.
    codecheck_run.py  runs verify.py and records what it said.

The artifact a codechecker compares is therefore a TRANSCRIPT OF THE
VERIFICATION, not an output of it, and the property survives verbatim.

The exit code is propagated, so a failing verification fails the CODECHECK.

Usage:
    python codecheck_run.py
"""

import io
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "codecheck")


def main():
    if not os.path.isdir(SALIDA):
        os.makedirs(SALIDA)
    # La figura tambien esta en el manifest, asi que se regenera antes, y su
    # generador SI escribe: make_figure.py existe para eso. La doctrina que no se
    # rompe es la de verify.py, no la de todo el paquete.
    subprocess.run([sys.executable, os.path.join(AQUI, "make_figure.py")],
                   stdout=subprocess.DEVNULL, cwd=AQUI)
    proc = subprocess.run([sys.executable, os.path.join(AQUI, "verify.py")],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          cwd=AQUI)
    texto = proc.stdout.decode("utf-8", "replace")
    sys.stdout.write(texto)

    ruta = os.path.join(SALIDA, "report.txt")
    with io.open(ruta, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Transcript of `python verify.py`, captured by codecheck_run.py.\n")
        f.write("# verify.py itself writes nothing. This file is a record of what\n")
        f.write("# it printed, not an output of it. See the module docstring.\n")
        f.write("# exit status: %d\n" % proc.returncode)
        f.write("#\n")
        f.write(texto)
    print("")
    print("codecheck_run.py: transcript written to codecheck/report.txt")
    print("codecheck_run.py: verify.py exit status %d" % proc.returncode)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
