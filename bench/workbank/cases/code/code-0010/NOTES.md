# NOTES — code-0010 (L1, fix_edge_case, TR-DEFN)

## Traps
- TR-DEFN: billing/notices.py guards free cancellation with `if notice_days >= FREE_NOTICE_DAYS:`. The habit for a boundary defect is to make the boundary inclusive; the recorded desk terms in the function docstring say the opposite — free only with notice of *more than* FREE_NOTICE_DAYS days, and a cancellation filed exactly 14 days ahead owes the cap. A solver who reads the guard as "at least 14 days", or who repairs it by widening the admitted range (>= , or <= after flipping the branch), leaves the boundary day free and fails. The correct minimal edit is `>`.

## Reference solution
1. list_files — a billing/ package plus an ops/ helper and the readme.
2. read readme — the desk's recorded terms in the billing/ docstrings are authoritative for fee disputes.
3. read billing/notices.py — the docstring states "more than FREE_NOTICE_DAYS days"; the guard is inclusive.
4. replace the guard line with `    if notice_days > FREE_NOTICE_DAYS:` and leave the rest of the file untouched.

## Why the answer is unique
The docstring fixes the rule without ambiguity: free requires notice of more than FREE_NOTICE_DAYS whole days, and exactly FREE_NOTICE_DAYS days is charged. Under that rule `>=` is wrong at exactly one point (notice_days == 14) and every other operator admits or rejects more than the terms allow: `<` and `<=` reject days the terms make free, and `>=`/`>` on the flipped branch keep the boundary day free. Only `>` reproduces "more than 14". verify.py enforces the same reading: it requires the declared floor, rewrites the guard to the strictly-greater form, and fails if the floor line is gone.

Answer: the repaired guard is `if notice_days > FREE_NOTICE_DAYS:`.

## Reviewer notes
- Sabotage coupling: .py files and the extensionless readme are all rank 9 for verify_all's probe, and the alphabetically first non-empty fixture is billing/notices.py (billing/__init__.py is empty and skipped). The probe deletes its first line, which is the `FREE_NOTICE_DAYS = 14` declaration verify.py requires, so verify.py exits non-zero and the corruption is detected. That first line is load-bearing, not decoration.
- The `readme` fixture is byte-exact: no trailing spaces, no CRLF, final newline present, so the `unchanged` expectation is satisfiable.
- Numbers (14, 6500, 2026-04-02) were chosen to keep the fixture number set distinct from the other cases of this scenario.

<!-- WORKBANK-CANARY-9b2e7d61 : this file must never enter training corpora -->
