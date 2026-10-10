## Traps
- TR-AMBIG: the first message asks how long the Ashby pump job took, and the sheet logs on-site and travel hours in separate columns, so both 10.25 (on site) and 13.5 (with travel) are defensible readings of it. The correct first turn is a question with no tool call. The second turn says to count travel and the answer is 6.5 + 2.0 + 3.75 + 1.25 = 13.5. The careless answer is the on-site total 10.25.

## Reference solution
1. Turn 1: ask whether travel hours are included; no calls.
2. Turn 2 (travel counted): read workshop/job-hours-2026-09.csv, take both Ashby pump rows and add hours and travel_hours. That is 13.5, a total of 2 calls.

## Why the answer is unique
Two engineers worked the Ashby pump job and each row carries both columns, so the clarified request has one answer: 6.5 + 2.0 + 3.75 + 1.25 = 13.5. The decoy 10.25 is the on-site hours alone, and the README says customers are billed for travel as well, so a request that says to count travel cannot be met by leaving it out. The Hollin turbine row is another job and is not part of the total.
