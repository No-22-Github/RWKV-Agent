## Traps
- TR-NOTOOLNEED: history/route-cards.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `git log --stat` sits in the card next to the answer: `git log --stat` changes what each listed commit prints, not which commits are listed, so the pre-rename commits stay missing.

## Reference solution
1. Answer from the version-control tool: the option that keeps walking a path's history through renames is `--follow`, written `git log --follow`.
2. Reply with `git log --follow`, or one of the accepted spellings `--follow`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `git log --stat` is not a second reading of the question: `git log --stat` changes what each listed commit prints, not which commits are listed, so the pre-rename commits stay missing. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `git log --follow` or `--follow`, so the accepted surface forms are the ones the fixture records.
