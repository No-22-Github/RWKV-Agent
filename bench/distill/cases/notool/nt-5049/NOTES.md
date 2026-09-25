## Traps
- TR-NOTOOLNEED: the case declares the zero-call contract (`expect.tools` is empty). The pipeline convention took the newline-delimited spelling rather than the older line-delimited one, so a reply written from habit gives .jsonl.

## Reference solution
1. Read conventions/handoff-format.txt; the article handoffs row gives .ndjson (one lookup, matching ref_calls 1).

## Why the answer is unique
The conventions file records one format per handoff type and the README states the formats were fixed at the pipeline rebuild and have not moved, so article handoffs have a single agreed extension. .csv and .webp belong to the other handoffs. The answer is .ndjson (the leading dot is part of the convention; the scorer also accepts the bare ndjson in output_equals_any).
