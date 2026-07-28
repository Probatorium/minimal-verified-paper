"""Source code for the minimal self-verifying paper.

Two rules govern this package:

1. Nothing in here hard-codes a number that the paper reports. All reported
   numbers live in `frozen_claims.py`, and
   `checks/check_55_computed_not_hardcoded.py` enforces that they do not appear
   as literals anywhere else.
2. Values taken from an outside source live in `cited_constants.py` with a
   bibliographic record. Values the paper derives are computed here. Never the
   other way round.
"""
