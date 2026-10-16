## Traps
- TR-DECOY: only looking at the department's direct employees undercounts.

## Reference solution
1. jq recurse(.teams[]) then employees[] select level.
Reference commands (replayed in the sandbox): jq '[.departments[]|select(.name=="Platform")|recurse(.teams[])|.employees[]|select(.level==8)]|length' hr/org.json
Final answer: turn 1 -> 30 ; turn 2 -> 2 

## Why the answer is unique
Whole Platform subtree, level threshold inclusive.
