# NOTES — code-0006 (L1, report_test_result, TR-CLAIM)

## Traps
- TR-CLAIM: the capture's last line claims `2 failed, 9 passed`, but the
  per-test evidence lists three `FAILED` lines (test_currency_lock_on_refund,
  test_loyalty_points_reversal, test_warehouse_return_window). Trusting the
  footer gives the decoy 2; counting the recorded outcomes gives the expected
  3.

## Reference solution
1. Read ci/returns_suite_tail.txt, the unmodified capture of the credit-suite
   run.
2. Read tests/test_credit.py and confirm the suite declares twelve tests, all
   of which appear exactly once in the capture, so the capture is the complete
   record of the run.
3. Count the `FAILED` outcome lines: three, against nine `PASSED`; the footer's
   claim of two disagrees with the evidence. (3 steps, matching tags.ref_calls.)

## Why the answer is unique
The capture is stated to be untrimmed, and the twelve per-test lines match the
twelve tests declared in tests/test_credit.py one for one, so the per-test
outcomes are the complete evidence of what ran. Exactly three of those lines
end in `FAILED`, and the expected answer is 3. The footer is a claim about the
run, not a record of it; a reply of 2 accepts a number the capture's own lines
contradict.
