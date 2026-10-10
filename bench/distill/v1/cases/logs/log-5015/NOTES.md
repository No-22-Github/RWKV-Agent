## Traps
- None. The journal holds a single FAULT line and the closing line accounts for every event, so the floor on that line is the whole answer.

## Reference solution
1. List the workspace: README.md and logs/lift-controller.log.
2. Read logs/lift-controller.log. One line carries FAULT: `2026-09-11T07:14:56Z FAULT floor=4 code=E07 door=2`, so the car was at floor 4.

## Why the answer is unique
README.md says FAULT is written once, when the controller takes the car out of service, and that it names the floor the car was at; the closing line reports 14 event lines, which is what the journal holds above it. Only one line in the file carries FAULT, and it reads floor=4, so the answer is 4. Reading the floor of the last landing call before the fault (floor=6 at 07:08:41) answers a different question, and so does counting trips.

## Fixture notes
Every event line carries a UTC stamp on 11 September 2026 and the closing line makes the file self-checking. Floors 1 to 7 are all served by the car, so floor numbers in the journal are ordinary traffic rather than signals.
