## Traps
- TR-NOTOOLNEED: infra/guard-blocks.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `lifecycle { create_before_destroy = true }` sits in the card next to the answer: `create_before_destroy` still replaces the resource, so the only copy of the intake index would be destroyed and rebuilt; the crew wants the change refused.

## Reference solution
1. Answer from the infrastructure tool: the lifecycle block whose setting makes a plan fail before destroying the resource is `lifecycle { prevent_destroy = true }`.
2. Reply with `lifecycle { prevent_destroy = true }`, or one of the accepted spellings `prevent_destroy = true`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `lifecycle { create_before_destroy = true }` is not a second reading of the question: `create_before_destroy` still replaces the resource, so the only copy of the intake index would be destroyed and rebuilt; the crew wants the change refused. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `lifecycle { prevent_destroy = true }` or `prevent_destroy = true`, so the accepted surface forms are the ones the fixture records.
