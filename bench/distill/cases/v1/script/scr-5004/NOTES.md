## Traps
- None. No trap tag is set: the option asked for is named in the request, and the script it goes into is the first file the request points at.

## Reference solution
1. Read hours.py: it reads every export under nights/, adds up the minutes per observer, prints one line per observer and then the totals line (call 1).
2. Add the --totals-only option (argparse, or a plain check of sys.argv) so that when it is given only the totals line is printed, leaving the per-observer lines and the totals line as they are otherwise (call 2).

## Why the answer is unique
The season minutes are the sum over all three monthly exports, so the one line the option prints is TOTAL followed by that sum. With the exports that are in the workspace and the October export added afterwards, the sum is 905:

    TOTAL,905

Writing the option so that it prints a stored figure rather than the total it computes cannot be the repair: the run covers the October export as well, and the figure would then answer for the wrong set of exports.

