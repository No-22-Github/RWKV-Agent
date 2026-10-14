## Traps
- TR-NOTOOLNEED: schema/extra-key-rules.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `"additionalProperties": true` sits in the card next to the answer: `"additionalProperties": true` is the default that lets undeclared keys through, which is exactly how the mistyped key passes today.

## Reference solution
1. Answer from the schema language: the line that forbids undeclared properties is `"additionalProperties": false`.
2. Reply with `"additionalProperties": false`, or one of the accepted spellings `additionalProperties: false`, `"additionalProperties":false`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `"additionalProperties": true` is not a second reading of the question: `"additionalProperties": true` is the default that lets undeclared keys through, which is exactly how the mistyped key passes today. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `"additionalProperties": false` or `additionalProperties: false` or `"additionalProperties":false`, so the accepted surface forms are the ones the fixture records.
