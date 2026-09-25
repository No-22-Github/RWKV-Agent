## Traps
- TR-NOTOOLNEED: transfer/rehearsal-options.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `--progress` sits in the card next to the answer: `--progress` reports a transfer that is really running, so files are already being written on the far side; the question asks for a report that moves nothing.

## Reference solution
1. Answer from the file-sync tool: the long-form option that prints what the sync would do without touching either side is `--dry-run`.
2. Reply with `--dry-run`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `--progress` is not a second reading of the question: `--progress` reports a transfer that is really running, so files are already being written on the far side; the question asks for a report that moves nothing. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `--dry-run`, so the accepted surface forms are the ones the fixture records.
