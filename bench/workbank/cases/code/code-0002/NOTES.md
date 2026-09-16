# NOTES — code-0002 (L1, report_test_result, TR-CLAIM)

## Traps
- TR-CLAIM: the pasted console tail ci/invoice_run_214.txt ends with the footer line "2 failed, 1 skipped in 0.41s", but the eight per-test lines above it show exactly 1 FAILED (test_void_after_partial_refund) and 1 SKIPPED (test_pay_by_ait_skipped_on_staging). Trusting the summary line yields the decoy "2 failed, 1 skipped"; the evidence answer is "1 failed, 1 skipped". Grading is has+not per the TR-CLAIM rule: output_contains ["1 failed", "1 skipped"] plus output_excludes ["2 failed"], so a footer-trusting reply fails both checks.

## Reference solution
1. list_files — find ci/invoice_run_214.txt next to the module and its tests.
2. read ci/invoice_run_214.txt — eight per-test result lines plus one footer summary line.
3. Count the per-test outcomes (1 FAILED, 1 SKIPPED, 6 PASSED) and reply "1 failed, 1 skipped".

## Why the answer is unique
The question asks for the outcome of the run; the only outcome evidence is the per-test result lines. The footer's "2 failed" contradicts them (exactly one line carries FAILED), so it cannot be a reading of this run and must not be reported. The prompt dictates the '<N> failed, <M> skipped' format, making the reply deterministic. The tests/billing/test_invoice.py fixture mirrors the tail's test names and order, so no second interpretation of "that run" exists.

## Reviewer notes
- verify_all prints a `verify_shape_unknown` warning for this case by design: verify.py outputs the computed contains/excludes lists, and verify_all only compares expected_number/output_equals shapes. The case still passes (ok: true); the warning reflects verify_all's limited shape table, not a mismatch.
- Sabotage check: ci/*.txt sorts ahead of .py/.md files, and its first non-empty line is the FAILED line; deleting it flips the computed count to "0 failed", so verify.py's output diverges.

## Reviewer notes (post solve-check repair)
- v1 repair: the paste being possibly incomplete gave the decoy summary line a defensible reading (a solver trusted '2 failed' because tails are usually truncated). The prompt now states the paste is the complete run output, so the enumerated evidence (1 FAILED / 1 SKIPPED of 8) is authoritative and the answer is unique; the trap (trusting the summary claim) is unchanged.
