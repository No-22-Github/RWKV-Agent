## Traps
- none: single-layer config, the asked key is defined once and the question
  names it directly. Base L0 of the family.

## Reference solution
1. Read config/membership.json (path given in the prompt): redeem_threshold is 500.

## Why the answer is unique
The README states config/membership.json is the only effective config file, so
there is no second layer or campaign override to weigh. The key appears exactly
once in the file and no other key carries a similar meaning, so a careful solver
has exactly one value to report: 500.
