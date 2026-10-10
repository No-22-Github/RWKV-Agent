## Traps
- TR-DUPROW: the collector re-sent 6 REJECTED lines unchanged (same timestamp and reference), so the journal holds 29 REJECTED lines covering 23 shipments. Counting lines answers 29; merging the re-sends by reference answers 23.

## Reference solution
1. Read README.md: line grammar, the re-send rule, one line per export attempt.
2. Search status=REJECTED and read the line windows around the hits.
3. Collect the shipment references, merging identical re-sent lines.
4. The distinct count is 23.

## Why the answer is unique
Re-sent lines repeat every field of their original, so the README's one-line-per-attempt rule makes them the same shipment; no reading turns a re-send into a second shipment, and ACCEPTED or HELD lines fail the status test. The distinct count is 23.
