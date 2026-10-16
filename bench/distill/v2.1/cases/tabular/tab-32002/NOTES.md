## Traps
- status vs status_note: grep for 'open' would also hit nothing wrong but column choice matters for 'escalated'
- fixture: exports/tickets_q3.csv, 400 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 exports/tickets_q3.csv
    awk -F, -v p=3 -v s=5 'NR>1 && $p=="P1" && $s=="open"{n++} END{print n+0}' exports/tickets_q3.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
