## Traps
- None. Every line in the journal is one opening of one bed, and the bed is named on the line, so counting the north-bed lines is the whole task.

## Reference solution
1. List the workspace: README.md and logs/irrigation.log.
2. Read logs/irrigation.log and count the lines whose `bed` is north: the file holds 18 openings, 11 of them for the north bed.

## Why the answer is unique
README.md says the controller opens a single valve at a time and writes a line for every opening, and the journal covers one day with no rotation inside it, so every opening of the day is present exactly once. Each line names its bed, and the north-bed openings number 11; the south-bed openings are the 7 lines on the other bed and cannot be counted as north ones. The `minutes` field is how long each opening was set to run, so summing it answers a different question.

## Fixture notes
Every line carries a UTC stamp on 8 September 2026, and the openings of the two beds are interleaved through the day rather than grouped. The `minutes` and `litres` values are that opening's running time and water volume, and neither they nor any stamp carries the count that answers the question.
