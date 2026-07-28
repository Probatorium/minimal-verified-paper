"""Every number the paper reports, checked against the computation and the text.

For each entry in `src/frozen_claims.py` this asks two questions:

  1. does the value the package computes still render to the frozen string?
  2. does that string still appear in the section of the manuscript that is
     supposed to contain it?

Both directions matter. Question 1 fails when the code changes; question 2 fails
when the prose changes. A package that only answered question 1 would let an
author edit a number in the text and still pass.

ONE DEFERRED ASSERTION. The claim `n_checks` counts the checks this very suite
produces, so its value is not known until the suite has finished. Its text is
checked here; its value is checked by `verify.py` after the run, as the result
`META-check-count`. That is the only assertion not made inside a check module,
and it is called out here so that no reader has to discover it by accident.
"""

from checks import check
from src import frozen_claims
from src import manuscript

ORDER = 40
NAME = "Frozen numbers: computed value and manuscript text agree"
GATE = False


def run(context):
    paper_sections = manuscript.sections(manuscript.read(manuscript.PAPER))
    results = []

    for claim in frozen_claims.CLAIMS:
        value = context.value_for_claim(claim)
        problems = []

        if value is None:
            if claim.id != "n_checks":
                problems.append("no value available for this claim")
        else:
            try:
                rendered = frozen_claims.render(value, claim.fmt)
            except ValueError as error:
                rendered = None
                problems.append(str(error))
            if rendered is not None and rendered != claim.text:
                problems.append(
                    "computed value renders as %s but the manuscript is frozen at %s"
                    % (rendered, claim.text))

        if claim.section not in paper_sections:
            problems.append("section %r does not exist in the manuscript" % claim.section)
        else:
            tokens = manuscript.numbers_in(paper_sections[claim.section])
            if claim.text not in tokens:
                problems.append(
                    "the string %s does not appear in manuscript section %r"
                    % (claim.text, claim.section))

        results.append(check(
            "FRZ-" + claim.id,
            not problems,
            "%s (%s): %s" % (claim.id, claim.kind, "; ".join(problems)),
        ))

    return results
