## Traps
- TR-MISSING: the eight in-window departures mix four kinds of turnaround values: three carry NA, a dash or an empty field and five carry clock times. Counting departures instead of reported turnarounds answers 8.

## Reference solution
1. List the workspace: README.md and logs/dock-journal.log.
2. Read README.md: only hh:mm:ss values are turnaround times; NA, the dash and the empty field report no time.
3. Read logs/dock-journal.log and count in-window departures whose turnaround matches hh:mm:ss: 08:04, 08:17, 08:31, 08:46, 08:52 = 5.

## Why the answer is unique
The README enumerates exactly what the turnaround field can hold and only the clock-time values report a time, so each of the eight in-window lines is either counted or not under one rule. The mixed NA, dash and empty values are the dock system's documented no-time markers, not a second kind of time. Counting all departures, the decoy 8, ignores the field the question asks about. The answer is 5.
