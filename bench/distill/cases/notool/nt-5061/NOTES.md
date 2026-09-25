## Traps
- TR-NOTOOLNEED: the pattern card and README describe the intake rule but the pattern itself comes from regex syntax. The near-miss decoy `\d+$` anchors only the end: it accepts "kwh 2201", which is exactly the kind of note the question says must be rejected.

## Reference solution
1. Answer from the syntax: rejecting any other character at either end means anchoring both ends, and "one or more digits" is `\d+`.
2. Reply with `^\d+$`, with `^[0-9]+$` an equivalent spelling.

## Why the answer is unique
The question's "entire line" and "nothing else" have one expression in a line-oriented matcher: the start anchor, the digit run, and the end anchor, all present. A pattern anchored on one side only cannot reject a line that carries a timestamp next to a number, and the looser `\d+` allows a match anywhere in the line, so neither is a reading of the question. `\A\d+\Z` is the same assertion spelled with the unambiguous start and end anchors.
