## Traps
- TR-NOTOOLNEED: vcs/prune-cards.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `git fetch --tags` sits in the card next to the answer: `git fetch --tags` only adds tag refs; it never removes anything, so the deleted branches would still be listed after it runs.

## Reference solution
1. Answer from the version-control tool: the fetch option that deletes remote-tracking refs which no longer exist on the remote is `--prune`, so the command is `git fetch --prune`.
2. Reply with `git fetch --prune`, or one of the accepted spellings `git fetch -p`, `--prune`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `git fetch --tags` is not a second reading of the question: `git fetch --tags` only adds tag refs; it never removes anything, so the deleted branches would still be listed after it runs. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `git fetch --prune` or `git fetch -p` or `--prune`, so the accepted surface forms are the ones the fixture records.
