## Traps
- TR-NEARNAME: the request says the second yard, which the v1 paperwork calls
  the overflow yard; in the config the section is spill_yard. Raising
  main_yard's 60 kW limit or renaming the section is the trap.

## Reference solution
1. Read README.md: the overflow yard maps to the spill_yard section.
2. Read config/chargers.yaml.
3. Change spill_yard's session_limit_kw from 45 to 80, leaving every other line as it is.

## Why the answer is unique
The README maps the overflow yard to spill_yard explicitly, so main_yard's
limit stays 60 and the section keeps its name. The value 45 appears once, the
line shape is preserved, and no other key is involved, so the edited file has
exactly one possible content.
