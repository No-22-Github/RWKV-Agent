## Traps
- None. Only one summary in the release log names load balancing, so there is no second version for a solver to weigh against 2.7.0.

## Reference solution
1. Read README.md: the log is one row per release, oldest first, and the summary column says what each release changed.
2. Read releases/release-log.csv: the first summary naming load balancing sits on the 2.7.0 row. The answer is 2.7.0.

## Why the answer is unique
The log carries one row per release and exactly one summary names load balancing, so 2.7.0 is the only version the log can support. The 1.9.4 summary is SNMP monitoring, 2.3.1's is ramp-down and charts, and the rest name other work; the checklist mentions nothing about drive firmware versions. The answer is 2.7.0.
