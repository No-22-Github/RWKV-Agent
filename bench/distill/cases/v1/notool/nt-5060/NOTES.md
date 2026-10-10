## Traps
- TR-NOTOOLNEED: the pattern card and README are workspace props; the fragment is decided by Python's regex syntax alone. The near-miss decoy `(?<code>\d{4})` is the .NET and Perl spelling for a named group, which Python rejects with "unknown extension", so a model that reaches for the most familiar-looking angle syntax produces a pattern the parser cannot load.

## Reference solution
1. Answer from the syntax: Python names a capture group with `?P<name>` inside the parentheses.
2. Reply with `(?P<code>\d{4})`, the character class `[0-9]` being an accepted spelling of `\d`.

## Why the answer is unique
The question fixes the name, the atom and the exact repetition count, so only the syntax of the group itself is left open, and Python has exactly one spelling for a named group: `(?P<name>...)`. `(?<code>\d{4})` is not a competing reading but a different dialect that raises an error when compiled by the interpreter the question names, and the unnamed `(\d{4})` would force the caller to count groups instead of using the required name. The card on disk records the same fragment for the next operator.
