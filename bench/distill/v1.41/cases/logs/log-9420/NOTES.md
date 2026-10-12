## Traps
- TR-DECOY: exact answer 70; the loose reading (prefix match on event and reply) gives 138.
- TR-MULTISRC: 3 files; the first file alone gives 30.

## Reference solution
Turn 1: bash: `cat rsvp/*.txt | awk -F'\t' '$2=="Workshop" && $3=="yes"' | wc -l` -> 70
Final answer: 70 replies.

## Why the answer is unique
event and reply are whole-value columns. The README (rsvp/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Count of plain yes replies to Workshop?
2. Rows with event Workshop and reply yes, summed over all waves.
3. Per rsvp/README.md, how many yes RSVPs does Workshop have?
4. How many guests answered yes (not yes+1) for Workshop?
5. Number of Workshop RSVP rows whose reply is exactly yes.
