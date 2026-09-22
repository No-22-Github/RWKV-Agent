## Traps
None - L0 baseline of fam-script-fix-03. The shipped sla_report.py parses the
CSV with DictReader but adds the minute field straight to an integer
accumulator, so every launch dies on the first overdue ticket with
`TypeError: unsupported operand type(s) for +: 'int' and 'str'` before a single
report line is printed. The one bug is a missing conversion; nothing about the
counting, the sweep or the layout is wrong.

## Reference solution
1. read_file README.md - the console capture and the failing line (1)
2. read_file sla_report.py - find `overdue.get(queue, 0) + row[...]` and the
   text cells coming out of DictReader (2)
3. write_file sla_report.py - convert the minute field before summing (3)

ref_calls = 3. The second input set (a further tickets extract nested two
levels down) is written into the workspace copy before the offline run, so a
repair that hardcodes per-queue figures or stops sweeping the tree fails.

## Why the answer is unique
The only defect is the missing integer conversion; the sweep pattern, the
`first_response_ok == "no"` filter, the header and the ascending queue order are
already correct in the shipped file, so the repaired script's byte-exact stdout
is forced to be:

```
queue,overdue_minutes
Billing,786
Deliveries,206
Integrations,910
Onboarding,633
total,2535
```

Adding `int(...)` cannot change any other behaviour, and every amount is an
integer minute count, so no rounding or formatting choice is left open.

<!-- WORKBANK-CANARY-7b3d1f9c : this file must never enter training corpora -->
