## Traps
- TR-NOTOOLNEED: ops/shell-option-cards.tsv and README.md are props. How bash expands a wildcard that matches nothing is a property of the shell, so nothing has to be read before replying. The near-miss decoy `shopt -s failglob` also changes what happens on no match, but it makes the command abort instead of expanding to an empty list, which is the opposite of what the question asks for.

## Reference solution
1. Answer from bash: the option that makes an unmatched wildcard expand to nothing is `nullglob`, set through `shopt -s`.
2. Reply with the line `shopt -s nullglob`.

## Why the answer is unique
The question asks for an empty expansion, and `nullglob` is the bash option whose whole meaning is that an unmatched pattern expands to zero words. `failglob` cannot be a reading of the question: it turns a non-matching pattern into an error that aborts the command, so the sweep would stop rather than take the empty-list branch the question describes.
