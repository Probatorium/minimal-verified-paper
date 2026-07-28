---
title: "Uniformity of the First 1000 Decimal Digits of pi: A Minimal Stasis Artifact"
author: Alexis García Hurtado
year: 2026
version: 1.0.0
---

# Uniformity of the First 1000 Decimal Digits of pi: A Minimal Stasis Artifact

Alexis García Hurtado

A deliberately small statistical result, published together with an artifact
that refuses to build unless every number in this text still matches the
computation that produced it.

## 1. Question

The decimal expansion of pi is not random: it is a fixed sequence, determined
once and for all. Nonetheless it is an old and unresolved question whether its
digits are distributed as if they had been drawn at random. This paper asks the
narrowest version of that question that can be answered honestly with a short
computation: do the first 1000 decimal digits of pi depart from an even spread
over the 10 possible digit values by more than sampling variation would explain?

The answer, given below, is no. The result is unremarkable and is meant to be.
It exists here as a carrier for the verification apparatus described in the
final section, which is the actual subject of the work.

## 2. Data

The data are computed, not downloaded. The package generates the first 1000
decimal digits of pi twice, by two unrelated methods:

- a bounded spigot algorithm working on an array of small integers, which
  produces digits one at a time using nothing but integer division;
- Machin's arctangent identity summed in fixed-point arithmetic on a single
  large integer.

The two implementations share no code. They are required to agree digit for
digit. As an external anchor, the first 100 digits of both are also compared
against the published decimal expansion of pi recorded in the On-Line
Encyclopedia of Integer Sequences (Sloane, sequence A000796); that published
prefix is the only value in this work taken from a source rather than derived,
and it is declared as such in `src/cited_constants.py` with its record.

Choosing a computable object was a deliberate constraint. There is no file to
download, no licence to respect, no server to outlive the paper, and no version
of the data that a reader could fail to obtain. Anyone can regenerate the input
from the algorithms named above.

## 3. Null model and test

Let the observed count of digit `d` be the number of times `d` occurs among the
1000 decimal digits. The null model is that the digits are drawn independently
and uniformly from the 10 possible values, so that every digit has expected
count 100.

The test is Pearson's goodness-of-fit statistic `X2`, the sum over the ten
digits of the squared difference between observed and expected count divided by
the expected count. Under the null model, and for expected counts this far above
the conventional minimum, `X2` is approximately chi-square distributed with 9
degrees of freedom. The reported p-value is the upper-tail probability of that
distribution. The significance level was fixed in advance at 0.05.

This is an approximation, not an exact test. The chi-square distribution is the
limiting distribution of `X2`, and the multinomial counts are only asymptotically
normal. With an expected count of 100 in every cell the approximation is
standard practice, and the conclusion below does not sit near the threshold
where the difference could matter.

## 4. Result

The observed counts are:

| Digit | Observed count |
| ----- | -------------- |
| `0`   | 93             |
| `1`   | 116            |
| `2`   | 103            |
| `3`   | 102            |
| `4`   | 93             |
| `5`   | 97             |
| `6`   | 94             |
| `7`   | 95             |
| `8`   | 101            |
| `9`   | 106            |

![Observed count of each decimal digit among the first 1000 decimal digits of
pi, with the dashed line marking the count expected under the uniform null
model.](figures/digit_frequencies.svg)

The goodness-of-fit statistic is `X2` equal to 4.74 on 9 degrees of freedom,
giving p equal to 0.8564. At the significance level of 0.05 fixed above, the
uniform null model is not rejected. The counts are, if anything, closer to the
expectation than a typical draw from the null model would be.

The largest single deviation is the digit `1`, with a count of 116. Examined on
its own, under a binomial null, its standardized residual is 1.6865, which
corresponds to a two-sided p-value of 0.0917. That digit was selected because it
was the most extreme, so the unadjusted value overstates the evidence; adjusting
for the 10 simultaneous comparisons by the Bonferroni method gives 0.917. There
is nothing here.

## 5. What this does not show

The test looks only at how often each digit occurs. It is blind to order: any
rearrangement of the same digits gives exactly the same counts, the same
statistic and the same p-value. A sequence with strong serial structure would
pass it unchanged.

Failing to reject a null model is not evidence for it. The result is compatible
with an even spread of digits and it is also compatible with many alternatives
that 1000 observations cannot separate.

The result bears on one prefix of one constant. It says nothing about the open
question of the normality of pi in the sense of Borel, which concerns the
limiting frequency of every block of digits in every base, and which no finite
computation can settle.

## 6. How this paper verifies itself

This artifact applies Stasis. Stasis is the practice of freezing every number a
paper publishes as an executable assertion inside the paper's own package, so
that the package refuses to pass whenever the text and the computation stop
agreeing; a number frozen that way is called a frozen claim.

Running `python verify.py` executes 104 assertions in about a second, using only
the Python standard library and no network. Every number printed in the two
preceding sections is a frozen claim: it exists inside the package carrying the
exact string this text uses. If the computation changes, the claim fails. If
this text is edited so that a number no longer matches, the claim fails as well,
because the package reads the manuscript and checks that each frozen string
still appears in the section it belongs to. A separate check walks the
manuscript and refuses any numeric literal that no frozen claim covers.

The apparatus is described in full in `README.md`, which also carries the map
from each part of this paper to the checks that support it. Besides freezing the
numbers, it runs structural invariants before any statistic is computed, so that
a malformed input dies before it can produce a plausible result; it extends the
double derivation described above to every reported quantity; it enforces a
separation between values taken from a source and values derived here; it holds
a watch list of phrases this text may not contain; and it compares the title,
author and year across the manuscript, the README and the BibTeX record,
character for character.

The evidence that these assertions bite is a mutation study, reported in
`mutation_report.md`. It corrupts the package on purpose in 12 different ways
and records which assertions die. Every mutant is caught. The weakest kills 1
assertion and the strongest kills 35, and the report names them individually,
including the mutant that swaps two digits deep in the sequence, which changes
no count and is therefore visible only to the comparison between the two
computation paths. That case is the informative one: it marks the edge of what
this apparatus covers.

The count of mutants in the paragraph above is itself a frozen claim, and it did
not update itself. It read eleven until a twelfth mutant was added, one that
alters the title of this work on a single surface and leaves the others intact,
so that the study would exercise the longest string the package compares rather
than only the shortest. The verification then failed, named the claim, and
printed both the value it expected and the value it had found. Only afterwards
was the figure in this text changed. That sequence is the method operating on
itself, and it is the intended one: a frozen claim never follows the work, it
contradicts the work until a person decides which of the two is wrong.

## References

Rabinowitz, S. and Wagon, S. (1995). A spigot algorithm for the digits of pi.
*The American Mathematical Monthly* 102(3), 195-203.

Sloane, N. J. A., editor. Sequence A000796, decimal expansion of pi. *The
On-Line Encyclopedia of Integer Sequences*, OEIS Foundation Inc.
Available at https://oeis.org/A000796
