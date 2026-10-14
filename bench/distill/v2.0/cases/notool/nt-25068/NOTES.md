## Traps
- TR-NOTOOLNEED: the task table and README restate the same schedule for the pan crew; the expression itself is a property of the five-field format. The near-miss decoy `30 2 1 * 1` restricts the weekday field as well, so the task would be skipped in every month whose first day is not a Monday.

## Reference solution
1. Answer from the format: the first two fields are minute and hour, the third is the day of the month, and the last two stay open.
2. Reply exactly `30 2 1 * *`.

## Why the answer is unique
The question fixes the time and the day of the month and adds that the weekday does not matter, and the five-field format has one position for each of those facts: minute 30, hour 2, day of month 1, with the month and weekday fields left as wildcards. Filling the weekday field cannot be a reading of the question, because the text says the weekday is irrelevant. The punctuation and spacing are pinned by the question, so the expected string is `30 2 1 * *`.
