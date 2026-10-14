## Traps
- None. No trap tag is set: the module notes name the limits file, and the hold is the named
  limit there.

## Reference solution
1. Read press/cycle.py: the press cycle works to the limit it imports from press.limits (call 1).
2. Read press/limits.py: HOLD_SECONDS is 14 (call 2).

## Why the answer is unique
The hold is HOLD_SECONDS, the only limit named for the time the press keeps a mould under
pressure; the cycle file adds its own overhead on top only to work out the length of a whole run
of tiles, which is a different figure. MAX_MOULDS counts moulds, not seconds. The answer is 14.
