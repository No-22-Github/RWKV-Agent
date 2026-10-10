## Traps
- TR-NOTOOLNEED: the token card and README are props; the token is fixed by the notation itself. The near-miss decoy `PT1.5H` writes a fractional hour, which the notation does not allow: every component is an integer, so the minutes have to be carried in their own field.

## Reference solution
1. Answer from the notation: a period starts with `P`, a time part is introduced by `T`, and each component is an integer followed by its designator.
2. Reply with `PT1H30M`, the minute-only spelling `PT90M` being the same duration.

## Why the answer is unique
The question fixes the duration and the notation, and the notation gives one token per component: `P` for the period, `T` to enter the time part, then `1H` for the hour and `30M` for the minutes. `PT1.5H` is not a reading of the question because a decimal fraction is not a valid component value in that notation, and `PT90M` states the identical duration in the same notation, so it is accepted as the same token written differently.
