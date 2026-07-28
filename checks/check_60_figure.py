"""The committed figure must be the figure the data produce.

A figure is a claim drawn instead of written, and it goes stale the same way a
number does. `src/figure.py` renders the chart as a pure function of the counts,
so the check is simply: render it again and compare byte for byte.

The failure this catches is the ordinary one -- data change, someone reruns the
analysis, nobody regenerates the image, and the paper ships a picture of an
earlier result.
"""

from checks import check
from src import figure
from src import frozen_claims
from src import manuscript

ORDER = 60
NAME = "Committed figure matches the committed data"
GATE = False


def run(context):
    results = []

    present = manuscript.exists(manuscript.FIGURE)
    results.append(check(
        "FIG-present",
        present,
        "the figure %s is missing; run make_figure.py" % manuscript.FIGURE,
    ))
    if not present:
        return results

    on_disk = manuscript.read(manuscript.FIGURE)
    expected = figure.render_svg(context.counts_a, float(context.values_a["expected_count"]))
    results.append(check(
        "FIG-matches-data",
        on_disk == expected,
        "the committed figure is not what the current data render; it is stale. "
        "Run make_figure.py and inspect the difference before committing it.",
    ))

    labelled = [
        claim.text for claim in frozen_claims.CLAIMS
        if claim.id.startswith("count_") and claim.text not in on_disk
    ]
    results.append(check(
        "FIG-labels-counts",
        not labelled,
        "the figure does not display these frozen counts: %s" % ", ".join(labelled),
    ))

    results.append(check(
        "FIG-referenced",
        manuscript.FIGURE.replace("\\", "/") in manuscript.read(manuscript.PAPER),
        "the manuscript does not reference the figure it ships",
    ))

    return results
