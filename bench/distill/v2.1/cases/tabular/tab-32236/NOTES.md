## Traps
- TR-DECOY: roster-only people exist too.

## Reference solution
1. comm -23 payroll roster.
Reference commands (replayed in the sandbox): tail -n +2 hr/payroll-sep.csv | cut -d, -f1 | sort > /tmp/p.txt; tail -n +2 hr/roster.csv | cut -d, -f1 | sort > /tmp/r.txt; comm -23 /tmp/p.txt /tmp/r.txt > /tmp/o.txt; cat /tmp/o.txt; wc -l < /tmp/o.txt
Final answer: turn 1 -> 7 E1135 E1636 E1652 E1809 E2087 E2142 E2177

## Why the answer is unique
Direction fixed by the question.
