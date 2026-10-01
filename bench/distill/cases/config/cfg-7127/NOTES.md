## Traps
- none: LOG_FLUSH_SECONDS is defined only in deploy/global.env and there is no
  conflict to resolve, so the base L0 of the precedence family is the plain
  fallback step.

## Reference solution
1. Read deploy/mill-api.env (path given in the prompt): LOG_FLUSH_SECONDS is
   not among the service keys.
2. Read README.md: keys the service env does not set take effect from
   deploy/global.env.
3. Read deploy/global.env: LOG_FLUSH_SECONDS is 45.

## Why the answer is unique
The README states the fallback direction, and the key exists in exactly one
layer, so there is exactly one candidate figure. No setting in the service env
covers log flushing, so 45 is the only value a careful solver can report.
