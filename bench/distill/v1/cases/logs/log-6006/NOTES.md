## Traps
- TR-ABSENT: the journal records scale readings and inspection notes only, and README.md says so. Swarm captures are never recorded, so the count cannot be determined and the answer is UNKNOWN. A model that mistakes the three NOTE lines mentioning the queen for swarm evidence answers 3.

## Reference solution
1. List the workspace: README.md and logs/hivescale.log.
2. Read README.md: the journal records weights, temperatures and inspection notes, and nothing else.
3. Read logs/hivescale.log. Every line is a scale reading or an inspection NOTE; a search for a swarm capture finds zero records, so the journal never records one.
4. Answer in plain prose: I checked README.md and logs/hivescale.log. The journal records weights, temperatures and inspection notes only, and no line records a swarm capture; the NOTE lines are queen sightings, a different event, so no capture count can be given.

## Why the answer is unique
README scopes the journal to exactly three kinds of lines and the file contains only those kinds, so there is no line a faithful reading could count as a swarm capture; the count of swarm-capture records in the workspace is zero. The NOTE lines record queen sightings, which the README lists as inspection notes; they are a different event from a capture, so their count is not an answer to this question either. With no record of the asked-for event kind, a faithful answer states what was checked, names the missing swarm captures, and does not borrow a count from a different event.
