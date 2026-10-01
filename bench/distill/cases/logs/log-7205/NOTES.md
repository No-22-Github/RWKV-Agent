## Traps
- TR-TZ: door3-gw stamps Europe/London local time (+01:00), one hour ahead of UTC. Its 29 in-window alarms are stamped 22:xx+01:00 (they describe 21:xx UTC), while its 17 alarms stamped 21:xx+01:00 describe 20:xx UTC and fall outside. Counting stamps that merely read 21:xx gives 50; converting each stamp to the instant it describes gives 62.

## Reference solution
1. Read README.md: two writers, the +01:00 local stamping of door3-gw, and that incident windows are quoted in UTC.
2. Sample the journal head: the writer named on every line and the two stamp shapes (Z and +01:00).
3. Collect the ALARM lines whose message starts with "door-open".
4. Convert each stamp to UTC (door3-gw: subtract one hour) and keep those in 21:00:00-22:00:00 UTC.
5. Count them: 62 (33 portal-utc + 29 door3-gw).

## Why the answer is unique
README.md fixes the meaning of every stamp: a Z stamp is UTC and a +01:00 stamp is local time one hour ahead, and windows are quoted in UTC. With that rule each alarm belongs to exactly one instant, so window membership is forced; no alarm sits on 21:00:00 or 22:00:00 UTC, so inclusive and exclusive readings agree. The naive stamp-string count (50) is the decoy, not a second reading: it counts door3-gw lines by the clock they were written with instead of the instant they describe. The answer is 62.
