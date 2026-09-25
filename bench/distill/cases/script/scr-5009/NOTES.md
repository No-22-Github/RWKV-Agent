## Traps
- None. No trap tag is set: the sheet layout and the rate file are named in the script's notes, and the only fault is the library the script reaches for.

## Reference solution
1. Read departures.py: it imports yaml to read the route rates, which the standard library alone does not carry (call 1).
2. Read tariffs.yaml: two route keys, each on its own line as <route>: <pence>, which the standard library can read (call 2).
3. Rewrite the rate reader so it no longer reaches for yaml, leaving the fare arithmetic, the trip walk and the printed layout as they are (call 3).

## Why the answer is unique
Every trip is its passengers times the rate for its route, the rates are the two lines of tariffs.yaml, and the sheet is the per-trip line plus a totals line. With both monthly trip files in place the repaired script prints:

    2026-09-02,harbour,81.60
    2026-09-05,summit,83.60
    2026-09-12,harbour,98.40
    2026-09-16,summit,68.40
    2026-09-23,harbour,69.60
    2026-10-03,summit,98.80
    2026-10-07,harbour,88.80
    TOTAL,589.20

A repair that moves the rates out of tariffs.yaml and into the script contradicts the file the terminus keeps them in, and the last two trips arrive after the repair, so a rate copied into the code would have to be copied again rather than read. Leaving the trip files unread for the later month fails the same way: the sheet has to cover the trips in trips/ as they land.
