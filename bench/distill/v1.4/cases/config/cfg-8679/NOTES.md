## Traps
- TR-DECOY: Both ports sit on VLAN 20; only Gi1/0/14 changes.

## Reference solution
1. Read the basis tickets/CHG-4410.txt: the new value is 130.
2. Read switch/access-ports.cfg: line 2, `description AP-lobby
 switchport access vlan 20`, is the one to change.
3. replace_lines line 2 with `description AP-lobby
 switchport access vlan 130`; the rest of the line stays.
4. Read switch/access-ports.cfg back to confirm.
Final answer example: Port Gi1/0/14 in switch/access-ports.cfg now uses VLAN 130 per CHG-4410; Gi1/0/15 stays on VLAN 20.
Criteria: exact target file content.

## Why the answer is unique
Exactly one entry in the basis qualifies and the target line occurs once, so the resulting file is unique.
