## Traps
- TR-NOTOOLNEED: units/dependency-cards.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `Wants=malt-store.service` sits in the card next to the answer: `Wants=` leaves the drying service free to start when the store is down, which is exactly the failure the crew wants to prevent.

## Reference solution
1. Answer from the service manager: the dependency key whose failure blocks the unit from starting is `Requires`, so the line is `Requires=malt-store.service`.
2. Reply with `Requires=malt-store.service`, or one of the accepted spellings `Requires=`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `Wants=malt-store.service` is not a second reading of the question: `Wants=` leaves the drying service free to start when the store is down, which is exactly the failure the crew wants to prevent. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `Requires=malt-store.service` or `Requires=`, so the accepted surface forms are the ones the fixture records.
