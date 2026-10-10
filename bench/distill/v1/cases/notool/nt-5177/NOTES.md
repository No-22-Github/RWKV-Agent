## Traps
- TR-NOTOOLNEED: vcs/push-flag-cards.tsv and README.md are props. The flag that guards a history rewrite is a property of the version control tool, so nothing has to be read before replying. The near-miss decoy `--force` replaces the remote tip whatever state it is in, which discards the work the question wants protected.

## Reference solution
1. Answer from the tool's own vocabulary: the flag that replaces the remote tip only while the remote branch is where the local copy expects it is `--force-with-lease`.
2. Reply with `--force-with-lease`.

## Why the answer is unique
The question asks for a push that replaces the remote tip and refuses once the branch has moved on, and `--force-with-lease` is the flag whose name and behaviour are exactly that condition. `--force` cannot be a reading of the question: it overwrites the remote branch regardless of what arrived there since the last fetch, so the refusing behaviour the question asks for is absent.
