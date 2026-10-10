## Traps
- None. Turn 2 works from the offset-line config read in turn 1: make-ready 45 min minus wash-up 25 min is 20 min. The digital-row unit has no such fields.

## Reference solution
1. Turn 1: read pressroom/offset-line.yaml: shift ends at 16:30. Final answer in one sentence: the offset-line shift ends at 16:30.
Turn 2, no tool call: the same config lists wash-up 25 min and make-ready 45 min, so make-ready runs 20 minutes longer. Final answer in one sentence. Criteria: turn 1 contains 16:30; turn 2 is zero-call and says 20 (with or without the unit).

## Why the answer is unique
The two durations appear once each in the offset-line config, and their difference is a single subtraction; the digital-row config carries neither field. Both numbers were in the turn-1 read, and the user forbade more tool calls.
