## Traps
- None. Baseline for family fam-log-longtail-05: a single plain-text service log with one
  level per record. The log carries many INFO/WARN lines from six components and exactly one
  FATAL record, so "which component stopped" has a single answer.

## Reference solution
1. list_files to see the workspace layout; the service writes logs/claimdesk-api.log (1)
2. read_file README.md to learn the record grammar (`module=` names the emitting component,
   FATAL means the component stopped) (2)
3. Scan logs/claimdesk-api.log for the FATAL record and report its module,
   `policy-renderer` (3)

## Why the answer is unique
The level field appears once per line and only one line carries FATAL:
`2025-11-04 11:47:02.889 FATAL [claimdesk-api] module=policy-renderer ...`. Every other
record is INFO, WARN or ERROR, so no other line can be promoted to the answer; `policy-renderer`
occurs on no other line, while the components that do recur (claim-intake, document-store,
fraud-scorer, notify-dispatch, payout-ledger, audit-index) are never at FATAL level. The scored
answer is the module name `policy-renderer`.
