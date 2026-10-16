## Traps
- TR-DECOY: ~300 hosts match; the direction matters.

## Reference solution
1. strip port, sort, comm -23 and comm -13.
Reference commands (replayed in the sandbox): sed 's/^target: //; s/:9100$//' mon/targets.yml | sort > /tmp/m.txt; jq -r .hostname mon/cmdb.jsonl | sort > /tmp/c.txt; comm -13 /tmp/m.txt /tmp/c.txt > /tmp/o.txt; cat /tmp/o.txt; wc -l < /tmp/o.txt
Final answer: turn 1 -> 5 srv-0443 srv-1346 srv-1462 srv-1723 srv-2381; turn 2 -> 6 srv-0069 srv-0085 srv-0419 srv-0885 srv-1089 srv-1661

## Why the answer is unique
Both differences are exact sets.
