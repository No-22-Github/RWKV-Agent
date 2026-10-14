## Traps
- TR-PRECEDENCE: quiet_hours_start is defined in the base (23) and again in the
  building file (22); the building file wins. Reading only the base reports 23.
- TR-DECOY: the building file carries a comment mentioning the retired value 21;
  hash lines are remarks, not settings.

## Reference solution
1. Read config/guestbook-wangshan.yaml (path given in the prompt): the active
   line quiet_hours_start: 22 is the building's value; the commented 21 is a
   remark.
2. Read config/guestbook-base.yaml: the base carries 23.
3. Read README.md: the building file wins on same-name keys, so 22 is effective.

## Why the answer is unique
The README states both the layer order and that hash lines are remarks, so the
commented 21 is out by convention and the base 23 loses by order. Only the
active building line survives both rules, giving 22; no reading makes 21 or 23
effective.
