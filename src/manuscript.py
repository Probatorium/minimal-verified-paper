"""Reading the manuscript and its sibling surfaces as data.

The checks treat `paper.md` as an object to be inspected, not as prose to be
trusted. This module provides the small amount of parsing they need. It uses no
third-party parser on purpose: a dependency here would be a dependency of the
verification itself.
"""

import os
import re

#: Package root, i.e. the directory containing paper.md.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAPER = "paper.md"
README = "README.md"
CITATION = "CITATION.bib"
REFERENCES = "references.bib"
MUTATION_REPORT = "mutation_report.md"
FIGURE = os.path.join("figures", "digit_frequencies.svg")

#: Key under which `sections()` returns everything before the first '## '
#: heading: the title line and the byline.
PREAMBLE = "(front)"

#: Sections the number-coverage check skips, with the reason it is allowed to.
#:   (front)    -- title and byline; their exact strings are checked instead by
#:                 check_80, character for character, across every surface. The
#:                 manuscript must not report a result before section 1.
#:   References -- volumes, pages and years, which belong to a bibliographic
#:                 record rather than to a result.
#: Declared here, in the open, rather than buried inside a check.
SECTIONS_EXEMPT_FROM_NUMBER_COVERAGE = (PREAMBLE, "References")


def read(relative_path):
    """Read a surface of this package as text."""
    with open(os.path.join(ROOT, relative_path), "r", encoding="utf-8") as handle:
        return handle.read()


def exists(relative_path):
    return os.path.exists(os.path.join(ROOT, relative_path))


def front_matter_block(text):
    """Return the key/value block fenced by '---' at the top of a document.

    A four-line parser instead of a YAML library. It accepts 'key: value' lines
    only, which is all any surface here needs.
    """
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def sections(text):
    """Split a markdown document into {heading: body} at '## ' headings.

    The heading key is the text after '## ', e.g. '4. Result'.
    """
    result = {}
    current = PREAMBLE
    buffer = []
    for line in text.split("\n"):
        if line.startswith("## "):
            result[current] = "\n".join(buffer)
            current = line[3:].strip()
            buffer = []
        else:
            buffer.append(line)
    result[current] = "\n".join(buffer)
    return result


#: A number as it can appear in prose: an integer or a decimal.
#:
#: The lookbehind stops it matching inside identifiers like 'A000796' or
#: 'check_50', and stops '05' being read out of '0.05'. The lookahead stops it
#: matching a prefix of a longer number, while still allowing a sentence-final
#: full stop: '0.05.' at the end of a sentence yields '0.05', not nothing.
#: Getting that wrong is not hypothetical -- the first version of this pattern
#: silently failed to see any number that ended a sentence, and the frozen-claim
#: check reported it as missing from the manuscript.
NUMBER_PATTERN = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w]|\.\d)")


def strip_uninspected_regions(text):
    """Remove the parts of a document whose numbers are not paper claims.

    Removed, and why:
      * the '---' front matter block: its numbers are identity metadata, checked
        character for character by check_80 instead;
      * fenced code blocks and inline code spans: symbols such as `X2` and file
        names such as `check_40_frozen_numbers.py` are not reported quantities;
      * markdown link and image targets: paths, not results.
    """
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\]\([^)]*\)", "]( )", text)
    return text


def numbers_in(text):
    """Every numeric literal in `text`, in order, after stripping the above."""
    return NUMBER_PATTERN.findall(strip_uninspected_regions(text))
