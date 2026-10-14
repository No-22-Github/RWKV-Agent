## Traps
- TR-NOTOOLNEED: sql/sort-tail.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `NULLS FIRST` sits in the card next to the answer: `NULLS FIRST` puts the empty prices at the top of the list, which is the opposite end from the one the dairy wants.

## Reference solution
1. Answer from the database: the clause that places rows with a null value after all the others is `NULLS LAST`.
2. Reply with `NULLS LAST`, or one of the accepted spellings `nulls last`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `NULLS FIRST` is not a second reading of the question: `NULLS FIRST` puts the empty prices at the top of the list, which is the opposite end from the one the dairy wants. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `NULLS LAST` or `nulls last`, so the accepted surface forms are the ones the fixture records.
