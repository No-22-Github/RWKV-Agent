## Traps
- TR-DECOY: the grand total of all claims is not the answer.

## Reference solution
1. comm -23 claim ids vs invoice ids, then sum cents of those with jq, divide by 100.
Reference commands (replayed in the sandbox): tail -n +2 报销/invoices.csv | cut -d, -f1 | sort > /tmp/i.txt; jq -r .claim 报销/claims.jsonl | sort > /tmp/c.txt; comm -23 /tmp/c.txt /tmp/i.txt > /tmp/n.txt; cat /tmp/n.txt; jq -s --rawfile n /tmp/n.txt '($n|split("\n")) as $m|map(select(.claim as $c|$m|index($c)))|map(.cents)|add/100' 报销/claims.jsonl
Final answer: turn 1 -> 21203.83 BX30058 BX30203 BX30245 BX30515 BX30583 BX30959 BX31163

## Why the answer is unique
Set difference then exact integer-cent sum.
