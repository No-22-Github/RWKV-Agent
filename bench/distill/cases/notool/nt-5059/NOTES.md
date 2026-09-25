## Traps
- TR-NOTOOLNEED: the pattern cards and the README are props; the fragment is a property of regular-expression syntax itself. The near-miss decoy is `\w{2,4}`: its bounds are right, but without the lazy marker the engine takes the longest run that fits, which is exactly what the question rules out.

## Reference solution
1. Answer from the syntax: a bounded repetition is written `{2,4}`, the class of word characters is `\w`, and the trailing `?` makes the repetition settle for the smallest count that still allows a match.
2. Reply with `\w{2,4}?`.

## Why the answer is unique
The question pins both halves of the fragment: "two to four" fixes the repetition bounds, and "settle for the shortest run that fits" fixes the lazy form, which is spelled by appending `?` to the quantified atom. `\w{2,4}` cannot be a reading of the question because a greedy repetition consumes as much as it can, so the fragment that answers it is `\w{2,4}?`, with the expanded class `[A-Za-z0-9_]{2,4}?` the same expression written out.
