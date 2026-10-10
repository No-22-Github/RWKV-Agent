## Traps
- TR-NOTOOLNEED: archive/reading-options.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `tar -xzf` sits in the card next to the answer: `tar -xzf` also reads the compressed stream, but it extracts the members onto disk, and the clerk was asked for the names only.

## Reference solution
1. Answer from the archive tool: the listing flag `t` with the gzip filter `z` and the file operand `f` gives `tar -tzf`.
2. Reply with `tar -tzf`, or one of the accepted spellings `tar tzf`, `tar -tzvf`, `tar tzvf`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `tar -xzf` is not a second reading of the question: `tar -xzf` also reads the compressed stream, but it extracts the members onto disk, and the clerk was asked for the names only. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `tar -tzf` or `tar tzf` or `tar -tzvf` or `tar tzvf`, so the accepted surface forms are the ones the fixture records.
