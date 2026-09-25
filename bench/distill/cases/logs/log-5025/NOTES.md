## Traps
- TR-TZ: README.md says the intake equipment stamps the dairy's own clock, three hours ahead of UTC, so the 03:00-06:00 UTC window is 06:00-09:00 on the stamps. Reading the stamps as UTC takes the 03:00-06:00 lines instead and gives 72760 litres rather than 72470.

## Reference solution
1. List the workspace: README.md and logs/intake.log.
2. Read README.md: tanker lines are stamped on the dairy's clock, which runs three hours ahead of UTC, and the closing line accounts for every tanker line.
3. Read logs/intake.log. 03:00-06:00 UTC is 06:00-09:00 on the stamps, where the tankers are 06:14:17 (10850 litres), 06:47:52 (13210), 07:09:26 (11960), 07:41:03 (12640), 08:12:38 (10730) and 08:44:15 (13080); those six loads come to 72470 litres.

## Why the answer is unique
README.md states the offset and the question gives the window in UTC, so the stamps have to be shifted back three hours before the window is applied; after the shift the window is the six tanker lines listed above, and no other line falls inside it. Their loads total 72470 litres. The decoy 72760 is what the same window returns if the stamps are read as UTC, which is a different part of the day, and totalling the whole journal answers a third question. With the offset applied, the answer is 72470.

## Fixture notes
The journal holds one plant day, 16 September 2026, and the closing line accounts for all of its tanker lines. Every litres value is different from the others so the window's contents can be checked line by line.
