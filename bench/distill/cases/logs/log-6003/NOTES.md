## Traps
- TR-DECOY: logs/crac-alarms.log mixes three units and two levels. Unit kilmorie-crac-3 raises six ERROR lines (code=FANSTALL) and kilmorie-crac-2 adds six WARN lines carrying the same HISENSE code as its ERRORs. Counting ERROR lines across the two units gives 11.

## Reference solution
1. List the workspace: README.md and logs/crac-alarms.log.
2. Read README.md: three units journal into one file and every line names its unit and level.
3. Read logs/crac-alarms.log and count lines at level ERROR with host=kilmorie-crac-2: 15:41, 16:41, 18:41, 19:41, 20:41 = 5.

## Why the answer is unique
Each line names exactly one host and one level, so "ERROR alarms of kilmorie-crac-2" picks one disjoint set of lines. The sibling unit's six ERRORs fail the host filter and the host's own six WARN lines fail the level filter; the decoy 11 is what remains if either filter is dropped. Applying both leaves 5.
