## Traps
- TR-NOTOOLNEED: sql/index-builds.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `CREATE INDEX` sits in the card next to the answer: A plain `CREATE INDEX` takes a lock that blocks writes for the whole build, which is the outage the question rules out.

## Reference solution
1. Answer from the database: the form that builds the index while writes continue is `CREATE INDEX CONCURRENTLY`.
2. Reply with `CONCURRENTLY`, the word that goes between `CREATE` and `INDEX` (the full phrase also contains it, so it is accepted too).

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `CREATE INDEX` is not a second reading of the question: A plain `CREATE INDEX` takes a lock that blocks writes for the whole build, which is the outage the question rules out. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `CREATE INDEX CONCURRENTLY` or `create index concurrently`, so the accepted surface forms are the ones the fixture records.

## Review 2026-09-25
The criterion used to demand the whole phrase `CREATE INDEX CONCURRENTLY` while the prompt asks for the words that go *between* `CREATE` and `INDEX`; the teacher answered `CONCURRENTLY` (the correct reading) and was marked wrong 3/3. The criterion now accepts the word itself, and a full-phrase answer still matches because it contains it.
