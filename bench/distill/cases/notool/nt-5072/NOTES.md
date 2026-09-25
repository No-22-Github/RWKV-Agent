## Traps
- TR-NOTOOLNEED: the options table and README are props; the selection expression is the runner's own syntax. The near-miss decoy `-m "slow"` selects the opposite set: it runs only the marked checks, which is the opposite of what the question asks.

## Reference solution
1. Answer from the runner's selection syntax: the mark filter takes an expression, and the expression language has a negation operator.
2. Reply with `-m "not slow"`, whose single-quoted spelling is the same option.

## Why the answer is unique
The question says every check except the marked ones, which the expression language spells as the mark's name under its negation operator, and the run needs the selection option to carry that expression. `-m "slow"` names the marked checks alone and so runs the opposite set, while dropping the quotes is a shell-level choice that does not change the expression. The two quoted spellings are the same answer for the two shells the team uses.
