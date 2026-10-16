## Traps
- TR-DECOY: the bank has extra entries absent from the ledger (the other direction).

## Reference solution
1. sort both id lists, comm -23.
Reference commands (replayed in the sandbox): jq -r .ref finance/bank.jsonl | sort > /tmp/b.txt; tail -n +2 finance/ledger.csv | cut -d, -f1 | sort > /tmp/l.txt; comm -23 /tmp/l.txt /tmp/b.txt > /tmp/o.txt; cat /tmp/o.txt; wc -l < /tmp/o.txt
Final answer: turn 1 -> 7 INV-20222 INV-20450 INV-20470 INV-20871 INV-20875 INV-21045 INV-21101

## Why the answer is unique
Set difference, one direction.
