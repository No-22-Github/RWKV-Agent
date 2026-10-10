## Traps
- TR-NOTOOLNEED: the token card, README and bench note are props; the expression is fixed by the range syntax. The near-miss decoy `~1.8` is the patch-level range: it stops at the next minor release, so it would leave out 1.9, which the plant has covered.

## Reference solution
1. Answer from the syntax: a lower bound is written `>=`, an upper bound is written `<`, and the two are separated by a space.
2. Reply with `>=1.8 <2.0`, with the caret form `^1.8.0` stating the same window.

## Why the answer is unique
The question fixes both ends of the window: everything from 1.8.0 up, and nothing at 2.0.0 or above. That is a lower bound and an exclusive upper bound, which the syntax writes `>=1.8 <2.0`; the caret form is defined to mean exactly the same window, so it is accepted as a second spelling. `~1.8` cannot be a reading, because the tilde notation is defined to stop at the next minor version, which contradicts the question's requirement that 1.9 be admitted.
