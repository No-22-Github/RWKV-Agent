## Traps
- TR-NOTOOLNEED: the offsets sheet sits in the standards folder and the departure sits in the timetables folder, but the site clock and the offset are both standing figures; no file has to be opened. Leaving the offset off gives 82200.

## Reference solution
No steps; ref_calls is 0. The service leaves at 22:50 on a clock five hours and forty-five minutes ahead of UTC, so UTC is 17:05. In seconds after midnight that is 17 x 3,600 + 5 x 60. The answer is 61500.

## Why the answer is unique
The site clock runs ahead of UTC, so the UTC time is earlier than the clock time: 22:50 less 5:45 is 17:05, which is 61,500 seconds after midnight. 82,200 is the clock time left as it stands, which would read the site clock as UTC; the timetable holds every departure in UTC, so the offset has to come off. The delta yard row belongs to the other site, so it cannot be the offset that applies here.
