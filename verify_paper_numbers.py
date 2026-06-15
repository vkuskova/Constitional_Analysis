#!/usr/bin/env python3
"""
verify_paper_numbers.py
=======================
Entry point for the paper-number audit for
"Terms of Engagement in Constitutions: The State and Nonstate Law"
(Powell & Bambrick).

Recomputes every reported number from the committed source artifacts and asserts
each matches the paper. Prints a per-check PASS/FAIL line and a final tally.

Usage:
    pip install -r requirements.txt
    python verify_paper_numbers.py

Expected output:  62/62 checks passed
"""

import sys
from verifier_core import run_all_checks


def main():
    print("=" * 70)
    print("  PAPER NUMBER VERIFICATION")
    print("  Terms of Engagement in Constitutions (Powell & Bambrick)")
    print("=" * 70)
    print()

    passed, failed, results = run_all_checks(verbose=True)

    # Group summary by section
    print("\nSummary by section:")
    sections = {}
    for cid, sec, status, paper, val, claim in results:
        sections.setdefault(sec, [0, 0])
        if status == "PASS":
            sections[sec][0] += 1
        else:
            sections[sec][1] += 1
    for sec in sorted(sections):
        p, f = sections[sec]
        flag = "" if f == 0 else f"  <-- {f} FAILED"
        print(f"  {sec:<20} {p} passed, {f} failed{flag}")

    print()
    if failed == 0:
        print(f"SUCCESS: all {passed} checks passed.")
        sys.exit(0)
    else:
        print(f"FAILURE: {failed} of {passed + failed} checks failed.")
        print("See the FAIL lines above. Each indicates a number in the paper")
        print("that does not match the value recomputed from source data.")
        sys.exit(1)


if __name__ == "__main__":
    main()
