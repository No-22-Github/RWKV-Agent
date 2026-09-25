## Traps
- TR-DECOY: two of the modules bind the helper under the shorter name trim, so a count that
  searches for the imported name alone finds 2 call sites instead of 5.

## Reference solution
1. Read the decks and hulls modules and find the import each carries (call 1).
2. Note that decks/rail.py and hulls/lines.py bind the helper as trim, while hulls/faired.py
   keeps the name (call 2).
3. Count the calls: decks/rail.py has one under trim, hulls/faired.py has two under check_trim
   and hulls/lines.py has two under trim (call 3).

## Why the answer is unique
Every call goes to the helper the store defines; the alias changes the name at the call site, not
the helper. Searching for check_trim alone finds the two calls in hulls/faired.py and misses the
three aliased ones, which gives 2. The answer is 5.
