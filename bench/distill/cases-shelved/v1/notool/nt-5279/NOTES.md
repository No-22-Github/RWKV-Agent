## Traps
- TR-NOTOOLNEED: sql/plan-prefixes.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `EXPLAIN` sits in the card next to the answer: `EXPLAIN` alone only prints the planner's estimates and never runs the statement, so it cannot show measured times and row counts.

## Reference solution
1. Answer from the database: the prefix that executes the statement and returns the plan with measured times is `EXPLAIN ANALYZE`.
2. Reply with `EXPLAIN ANALYZE`, or one of the accepted spellings `explain analyze`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `EXPLAIN` is not a second reading of the question: `EXPLAIN` alone only prints the planner's estimates and never runs the statement, so it cannot show measured times and row counts. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `EXPLAIN ANALYZE` or `explain analyze`, so the accepted surface forms are the ones the fixture records.
