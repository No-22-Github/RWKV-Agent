## Traps
- TR-NOTOOLNEED: reference/flag-cards.tsv and README.md are props. Which inline flag changes the dot is a property of the regular-expression language, so no file has to be read before replying. The near-miss decoy `(?m)` is the flag people confuse with this one: it changes where the anchors match and leaves the dot exactly as it was.

## Reference solution
1. Answer from the regular-expression language: the single-letter inline flag whose meaning is that the dot also matches a line break is `s`.
2. Reply with the fragment as it is written at the front of a pattern, `(?s)`.

## Why the answer is unique
The question asks for the dot to accept a line break, and `s` is the flag letter that changes precisely that; written as an inline fragment it is `(?s)`. `(?m)` cannot be a reading of the question: it alters the meaning of the anchors so that they match at each line end, and a dot still refuses to match the line break the entries contain.
