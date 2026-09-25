## Traps
- TR-MULTISRC: the depot has two barriers and each keeps its own journal, so both files hold part of the answer. Reading only logs/north-gate.log gives 6 and reading only logs/south-gate.log gives 4; the question asks for the depot, so the two counts have to be added.
- TR-TZ: the north barrier stamps the depot clock, eight hours ahead of UTC (README.md), while the south barrier stamps in UTC. Taking the north file's clock for UTC as well, and counting its 06:00-08:00 lines, gives 3 there and 7 in total instead of 10.

## Reference solution
1. List the workspace: README.md plus logs/north-gate.log and logs/south-gate.log.
2. Read README.md: the north barrier writes on the depot clock (eight hours ahead of UTC), the south barrier writes in UTC, and OUT marks a departure.
3. Read logs/north-gate.log. 06:00-08:00 UTC is 14:00-16:00 on the north clock, where the OUT lines are 14:05:21, 14:23:56, 14:52:33, 15:14:47, 15:33:02 and 15:51:28 = 6.
4. Read logs/south-gate.log. Its OUT lines between 06:00:00 and 08:00:00 UTC are 06:08:44, 06:31:19, 07:12:56 and 07:48:02 = 4. The two barriers together make 10.

## Why the answer is unique
The question asks for the depot, and README.md says the depot runs two barriers, each of which writes one line per movement, so the departures in the window are spread over both files and neither file contains the other's movements. The window is given in UTC: the south file needs no conversion and the north file needs the eight-hour offset its README states. Six departures at the north barrier and four at the south make 10. The decoys come from dropping one of the two sources (6 or 4) or from reading the north clock as UTC (7, or 6 if only that file is used). With both sources and the offset applied, the answer is 10.

## Fixture notes
README.md defines OUT and IN and states each file's clock, and each journal closes with a record accounting for all of its movement lines (25 north, 20 south), so neither file is a fragment. The two files never share a vehicle id, which keeps the two sources readable independently.
