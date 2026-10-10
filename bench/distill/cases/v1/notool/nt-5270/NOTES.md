## Traps
- TR-NOTOOLNEED: vcs/setaside-cards.tsv and README.md are workspace props. The rule is a property of the tool or format itself, so nothing on disk has to be read before replying. The near-miss decoy `git stash` sits in the card next to the answer: plain `git stash` keeps only tracked changes and leaves the never-added survey files in the tree, which is the opposite of what was asked; `--all` goes too far because it would also sweep away the ignored scratch file the question keeps in place.

## Reference solution
1. Answer from the version-control tool: stashing untracked files along with tracked changes is `--include-untracked`, whose short form is `-u`, so the command is `git stash --include-untracked`.
2. Reply with `git stash --include-untracked`, or one of the accepted spellings `git stash -u` / `git stash push -u`.

## Why the answer is unique
The question asks for one behaviour, and the answer is the canonical way to ask the tool for it. `git stash` is not a second reading of the question: plain `git stash` keeps only tracked changes and leaves the never-added survey files in the tree, which is the opposite of what was asked; `--all` goes too far because it would also sweep away the ignored scratch file the question keeps in place. The workspace card restates the same choice for the crew's own records and changes nothing about it. Scored with output_contains_any over `git stash --include-untracked`, `git stash -u` or `git stash push -u` (v2: the explicit `push` spelling is the same command in every git ≥ 2.16), so the accepted surface forms are the ones the fixture records.
