## Traps
- TR-NOTOOLNEED: sql/index-builds.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `CREATE INDEX` sits in the card next to the answer: A plain `CREATE INDEX` takes a lock that blocks writes for the whole build, which is the outage the question rules out.

## Reference solution
1. Answer from the database: the form that builds the index while writes continue is `CREATE INDEX CONCURRENTLY`.
2. Reply with `CONCURRENTLY`, the keyword that comes right after `CREATE INDEX` (the full phrase also contains it, so it is accepted too).

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `CREATE INDEX` is not a second reading of the question: A plain `CREATE INDEX` takes a lock that blocks writes for the whole build, which is the outage the question rules out. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `CONCURRENTLY` or `concurrently`, which is exactly the row the fixture card records for the chosen build.

## Review 2026-09-25
The criterion used to demand the whole phrase `CREATE INDEX CONCURRENTLY` while the prompt asks for the words that go *between* `CREATE` and `INDEX`; the teacher answered `CONCURRENTLY` (the correct reading) and was marked wrong 3/3. The criterion now accepts the word itself, and a full-phrase answer still matches because it contains it.

## Review 2026-09-29
The prompt misstated PostgreSQL's grammar by placing the keyword *between* `CREATE` and `INDEX`, when `CONCURRENTLY` actually follows `CREATE INDEX` (see postgresql.org/docs CREATE INDEX); the 2026-09-25 fix changed only the expect, so the fixture card still carried the full phrase and verify.py disagreed with expect. The prompt now asks for the keyword right after `CREATE INDEX` and the card row carries just the keyword, so fixture and expect are the same set.
