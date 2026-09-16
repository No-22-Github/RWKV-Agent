## Traps
- TR-DEFN: the "active workspace" definition (window = the 30 days ending on
  the report date, both endpoints counted -> 2026-08-10..2026-09-08;
  success-only; post-report sign-ins excluded) lives in README.md. The script
  implements everything except the window start: REPORT_END - 30 days starts
  the window on 2026-08-09, one day early. On this data that looks plausible
  and inflates the report by exactly one workspace, WS-4417 (only sign-in
  2026-08-09T23:58). The plausible-but-wrong output is
  "weekly active workspaces: 8" with window 2026-08-09..2026-09-08; the
  correct report has 7 workspaces. trap_decoys is null (write/script case).

## Reference solution
1. read_file README.md - the documented definition and exact window dates (1)
2. read_file weekly_active.py - locate the window computation (2)
3. read_file signins.csv - boundary rows around 2026-08-09/10 confirm the
   off-by-one (WS-4417) (3)
4. write_file weekly_active.py - window start = report end - 29 days
   (equivalently hardcode 2026-08-10); format unchanged (4)

ref_calls = 4.

## Why the answer is unique
The README fixes the window dates and the success-only, report-date-capped
semantics; the script already implements the rest and its printed format, so
the only correct output is the 7-workspace report with window
2026-08-10..2026-09-08. Data avoids other boundaries: WS-4388 (failed-only
inside the window) and WS-4471 (successes only after the report date) stay
excluded under both windows, and no account sits exactly on 2026-09-08/09
except WS-4455 (inside for both).

<!-- WORKBANK-CANARY-e58a1d42 : this file must never enter training corpora -->
