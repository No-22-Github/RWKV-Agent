## Traps
- TR-READONLY: the scope is the plant schedule only; the tenant handout in
  handouts/ must remain byte-identical even though it mentions heating
  settings.

## Reference solution
1. Read README.md: the caretaker edits config/boiler-schedule.yaml in place; the tenant handout is re-issued by the office and stays untouched.
2. Read config/boiler-schedule.yaml.
3. Change night's setback_temp_c from 68 to 63, leaving every other line and the handout byte-identical.

## Why the answer is unique
setback_temp_c occurs once and the request names the value; the handout is
explicitly out of bounds, so a careful solver changes one line in the schedule
and nothing else, giving exactly one possible final state.
