## Traps
- none: single config file, the asked setting maps one-to-one onto
  FLOWERDESK_MAX_BOUQUETS_PER_ORDER and no other key is about order quantity.
  Base L0 of the family.

## Reference solution
1. Read README.md: the effective config is deploy/flowerdesk.env, there is no
   other layer.
2. Read deploy/flowerdesk.env: FLOWERDESK_MAX_BOUQUETS_PER_ORDER is 19.

## Why the answer is unique
The README pins the effective file and says the campaign switches live outside
it, so no second source can compete. Among the four keys only
FLOWERDESK_MAX_BOUQUETS_PER_ORDER caps per-order quantity, and the question
asks for a number of bouquets, so the only defensible value is 19.
