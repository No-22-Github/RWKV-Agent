## Traps
- TR-NOTOOLNEED: reference/pattern-notes.tsv and README.md are props. A pattern that repeats a captured group is a property of the regular-expression language, so no file has to be read. The near-miss decoy `\b(\w+)\s+\w+\b` matches any two words in a row, so an ordinary phrase like "fold in the" is reported as a doubled word.

## Reference solution
1. Answer from the regular-expression language: the second word is the same as the first only if the first is captured in a group and referred back to, which is `(\w+)` and `\1`, with `\b` keeping the match on whole words and `\s+` spanning the gap.
2. Reply with `\b(\w+)\s+\1\b`, or the same fragment with an explicit word class, `\b([A-Za-z]+)\s+\1\b`.

## Why the answer is unique
The question asks for the same word twice, and only a back-reference to a captured group makes the second occurrence equal to the first, which is what `(\w+)` followed by `\1` states; the word boundaries keep the fragment from matching inside longer words. `\b(\w+)\s+\w+\b` cannot be a reading of the question: with a second independent word class it matches any two words in sequence, which is not a repetition.
