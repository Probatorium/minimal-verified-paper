"""The checks that hold this paper up.

Every check module exposes:

    ORDER : int   -- run order; lower runs first
    NAME  : str   -- human-readable name, also used in the README claim map
    GATE  : bool  -- if True, a failure here stops the run before later checks
    run(context) -> list[Result]

A `Result` is one assertion with a stable id. Ids are stable so that the
mutation study can name exactly which assertions a corrupted input kills.
"""

from collections import namedtuple

Result = namedtuple("Result", "id ok detail")


def passed(check_id, detail=""):
    return Result(check_id, True, detail)


def failed(check_id, detail):
    return Result(check_id, False, detail)


def check(check_id, condition, detail_on_failure, detail_on_success=""):
    """One assertion, phrased so that the failure message is written up front."""
    if condition:
        return passed(check_id, detail_on_success)
    return failed(check_id, detail_on_failure)
