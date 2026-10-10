## Traps
- TR-NOTOOLNEED: the options table and README are props; the option belongs to the runner's own command line. The near-miss decoy `--durations-min=10` sets a threshold in seconds rather than a count of phases, so it lists whatever happened to be slow instead of the ten slowest.

## Reference solution
1. Answer from the runner's option set: one option controls how many duration measurements are printed.
2. Reply exactly `--durations=10`.

## Why the answer is unique
The question fixes both the count and the shape, and the runner has a single option for reporting duration measurements; giving it the number ten is what turns it into the ten slowest phases in the summary. `--durations-min=10` counts seconds, not phases, so it cannot answer the question, and the question pins the token form, leaving `--durations=10` as the expected string.
