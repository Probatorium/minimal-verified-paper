# Uniformity of the First 1000 Decimal Digits of pi: A Minimal Stasis Artifact

Alexis García Hurtado · 2026 · version 1.0.0

A two-page statistical paper packaged so that the package fails if the paper and
the computation stop agreeing.

The method is called **Stasis**: every number a paper publishes is frozen as an
executable assertion inside the paper's own package, so that the package refuses
to pass whenever the text and the computation diverge. A number frozen that way
is a **frozen claim**, and freezing one is the unit of work.

The statistical result is small on purpose: a goodness-of-fit test of the first
thousand decimal digits of pi against an even spread, which does not reject. The
subject of the work is the apparatus around it. This repository is the minimal
worked example of Stasis, small enough to read in one sitting and to clone as a
starting point.

## Run it

```
python verify.py
```

That is the whole thing. Python 3 standard library, no third-party packages, no
network, no data files to fetch, about a second on a laptop. Exit status is 0
when every assertion holds and 1 otherwise, so it works as a build gate.

```
python verify.py -v      list every assertion, not just the failures
python verify.py --report   machine-readable output, one line per assertion
python make_figure.py    regenerate the figure from the data
python mutate.py         re-run the mutation study
```

## What Stasis does here

**1. Frozen claims.** Every number printed in `paper.md` is frozen in
`src/frozen_claims.py` with the exact string the manuscript uses. Verification
recomputes the value, compares it to that string, and then reads the manuscript
and confirms the string is still **where the claim says it is**: on the line an
anchor identifies, or exactly as many times as the claim declares. Change the
code and it fails; change the prose and it fails. Presence in the section is not
enough, and the reason is in design note 4.

**2. This map.** See below: each part of the paper, and the checks that hold it
up.

**3. Double derivation.** The digits are computed twice, by a spigot algorithm
and by Machin's formula, which share no code. The statistics are computed twice,
once in floating point with tail probabilities from an infinite series and once
in exact rational arithmetic with tail probabilities from a recursion. Every
reported quantity must come out the same both ways.

**4. Mutation study.** `mutate.py` corrupts the package on purpose, one way at a
time, and records which assertions die. The results are in
`mutation_report.md`. Assertions nobody has ever seen fail are not evidence.

**5. Structural invariants before statistics.** `check_10_structural_invariants.py`
is a gate: if the digit sequence is not a well-formed digit sequence, the run
stops and no p-value is ever produced. Corrupt input must not survive long
enough to look plausible.

**6. Forbidden phrases.** A watch list of strings the manuscript and its
surfaces may not contain: editing scars, and claims this particular paper is not
entitled to make. The list is in `src/forbidden_phrases.py` with the reasoning.
It lives there rather than here because the README is one of the watched
surfaces, so quoting the list here would fail the check.

**7. Cited versus computed.** Exactly one number in this paper comes from
outside: a published prefix of the decimal expansion of pi. It is declared in
`src/cited_constants.py` with its source, identifier and retrieval date, and the
package checks that both computation paths reproduce it. In the other direction,
`check_55_computed_not_hardcoded.py` parses the source and refuses to let a
computed result also exist as a literal in the code, where the two could drift
apart.

**8. Front matter, at every declared location.** Title, author, year and
version are declared once in `src/front_matter.py`. Every place each of them is
supposed to live is listed in `check_80_front_matter.py` -- the YAML field, the
level-one heading, the byline position, the BibTeX field -- and the value is
extracted from that place and compared. The year in the BibTeX record is read as
a field rather than searched for, because the digits `2026` also sit inside the
citation key.

## Claim-to-check map

Each part of the manuscript, and the assertions that support it. Ids are stable,
so an assertion named in `mutation_report.md` can be found here.

| Part of the paper | What is asserted | Where |
| --- | --- | --- |
| 1. Question | The stated sample size and category count match the ones the analysis uses. | `check_40_frozen_numbers.py` (`FRZ-n_digits_q`, `FRZ-n_categories_q`) |
| 2. Data | The two independent paths produce the same digits, and both agree with the published prefix. The prefix has a complete bibliographic record. | `check_10_structural_invariants.py`, `check_20_cited_constants.py`, `check_30_double_derivation.py` |
| 3. Null model and test | The expected count, the degrees of freedom and the significance level are the ones the code uses, computed both ways. | `check_30_double_derivation.py`, `check_40_frozen_numbers.py` |
| 4. Result | Every count, the statistic, the p-value and the post-hoc figures are recomputed on both paths, matched against the text, and drawn in the committed figure. | `check_30_double_derivation.py`, `check_40_frozen_numbers.py`, `check_60_figure.py` |
| 5. What this does not show | Contains no unclaimed number, and no phrasing from the watch list. | `check_50_manuscript_coverage.py`, `check_70_forbidden_phrases.py` |
| 6. How this paper verifies itself | The number of assertions, the number of mutants and the mutation counts are the real ones, read back from the suite and from the study. | `check_40_frozen_numbers.py`, `check_95_mutation_evidence.py`, `META-check-count` |
| The whole manuscript | No numeric literal anywhere in the text lacks a frozen claim; every claim points at a section that exists. | `check_50_manuscript_coverage.py` |
| The whole package | No computed result is hard-coded in the source. | `check_55_computed_not_hardcoded.py` |
| Every surface | Title, author and year identical everywhere; no provisional identifier anywhere. | `check_80_front_matter.py` |
| This map | Mentions every section of the paper and every check module. | `check_90_claim_map.py` |

## Files

```
paper.md                  the manuscript, two pages
README.md                 this file
CITATION.bib              how to cite this work
references.bib            works the paper cites
verify.py                 the single command
mutate.py                 the mutation study
make_figure.py            regenerates the figure
mutation_report.md        generated evidence that the assertions bite
figures/                  the committed figure
src/
  front_matter.py         title, author, year: declared once
  data_path_a_spigot.py   digits of pi, route one
  data_path_b_machin.py   digits of pi, route two
  stats_path_a_series.py  statistics, route one
  stats_path_b_exact.py   statistics, route two
  cited_constants.py      values taken from a source, with their records
  frozen_claims.py        every number the paper reports
  forbidden_phrases.py    strings the paper may not contain
  manuscript.py           reading the paper as data
  figure.py               the figure as a pure function of the counts
checks/
  check_10_structural_invariants.py
  check_20_cited_constants.py
  check_30_double_derivation.py
  check_40_frozen_numbers.py
  check_50_manuscript_coverage.py
  check_55_computed_not_hardcoded.py
  check_60_figure.py
  check_70_forbidden_phrases.py
  check_80_front_matter.py
  check_90_claim_map.py
  check_95_mutation_evidence.py
```

## Design notes

**1. Why computable data.** The input is generated by the package from two
algorithms. There is no download, no licence, no server that has to outlive the
paper, and no chance that a reader obtains a different version of the data. The
cost is that the example is a toy; the benefit is that it is a toy anyone can
run in ten years.

**2. Independence is bounded.** The two computation paths share no project code
and no algorithm, but they do share CPython and its integer arithmetic. Two
implementations can also be wrong in the same way if they share a
misunderstanding rather than a line of code, which is why the published prefix
of pi is cited as an outside anchor. Agreement between the paths is evidence,
not proof, and the claim made here is only the one that can be checked
mechanically.

**3. No provisional identifier.** `src/front_matter.py` declares `DOI = None`
until the work is deposited. While it is None, the package forbids any
DOI-shaped string on any front matter surface. Nothing provisional can be left
behind and forgotten, because anything provisional would fail the build. When a
real identifier exists, writing it into that one file flips the same check into
demanding it everywhere.

A note on how that interacts with the watch list: some of the strings on the
list are ordinary words when a document is describing the method rather than
using it. This README had to be reworded once for exactly that reason. The check
matches text, not intent, and rewording the prose is the correct response.

**4. Presence is not location, and this package learned that the hard way.**
An external defect injection study measured this package and found one blind
spot twice over. Of twenty front matter drifts injected one surface at a time,
nine escaped, all of them because a string that lives in two places could be
edited in one while a whole-file search found the other. Of the manuscript
numbers it edited, every string that occurs once in its section was caught and
every string that occurs more than once escaped. Both checks now anchor to a
declared location: `check_80` extracts each value from the field, heading or
byline position it belongs to, and each frozen claim either names the line it
sits on or freezes how many times it appears. The five escapes are kept as
permanent mutants so the repair cannot rot.

What remains a floor rather than a ceiling: the check that refuses unclaimed
numbers still works by string, so a small integer matching some claim's text
passes wherever it appears, and the check that refuses hard-coded results still
ignores integers below ten. Both limits are written down in the checks
themselves rather than left for a reader to discover.

**5. One assertion lives outside the check modules.** The suite counts its own
assertions, and that number is not known until the suite has finished, so it is
made by `verify.py` at the end as `META-check-count`. It is the only exception,
and it is named here so that nobody has to find it by accident.

**6. Verification never writes.** `verify.py` only reads. The figure is
regenerated by a separate command, so a stale figure is reported rather than
silently repaired. Finding out that something went stale is the point.

## Reusing this as a template

This repository is Stasis in its smallest complete form: eight mechanisms, one
command, one worked example. To apply Stasis to a paper of your own, replace the
data, the statistics and the manuscript, and keep the shape. The parts
that carry over unchanged are `manuscript.py`, the check modules, `verify.py`
and `mutate.py`. The parts that must be rewritten for a new paper are
`front_matter.py`, `frozen_claims.py`, `cited_constants.py`, the watch list in
`forbidden_phrases.py`, and the map in this README. A watch list copied from
another paper is not a watch list; each paper has its own temptations.

The discipline that makes the rest work: freeze a number before you write it.
Add the frozen claim, run the verification, and only then type the value into
the prose. A number that reaches the manuscript before it has been frozen is a
number nothing is holding.

## Licence

Code under the MIT licence, text under CC BY 4.0. See `LICENSE`.
