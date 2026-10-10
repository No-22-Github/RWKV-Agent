## Traps
- TR-TZ: logs/yard.log is stamped on the depot clock, eight hours ahead of UTC (README.md), while the question gives its window in UTC. Reading the clock times as UTC and counting the departures between 06:00 and 07:00 on the file gives 4; the same window in UTC is 14:00-15:00 on the depot clock, where five departures are recorded.

## Reference solution
1. List the workspace: README.md and logs/yard.log.
2. Read README.md: the controller stamps movements on the depot clock, which runs eight hours ahead of UTC, and OUT marks a vehicle leaving.
3. Read logs/yard.log. 06:00-07:00 UTC on 21 August 2026 is 14:00-15:00 on the journal's clock, and the OUT lines in that hour are 14:06:31, 14:19:44, 14:32:09, 14:47:26 and 14:58:03 = 5.

## Why the answer is unique
The prompt fixes the window in UTC and README.md fixes the clock the journal is written on, so the window maps to one hour of the journal with no choice left: the offset is a stated property of the depot clock, not something to infer from the data. Five OUT lines fall in that hour. The decoy 4 comes from treating the journal's clock as UTC and taking the 06:00-07:00 lines; counting every line in the correct hour instead of only the OUT ones gives 7. With the window converted, the answer is 5.

## Fixture notes
README.md defines OUT and IN, so a movement's direction is explicit. The journal covers the whole local day plus a closing record that accounts for all 30 movement lines, and no line carries a UTC offset, so the depot clock is the only reading of the stamps.
