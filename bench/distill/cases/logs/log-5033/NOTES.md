## Traps
- TR-DUPROW: logs/collections.jsonl was written by a retried export, so five of the 5 September jobs sit in the file as two identical records each. Totalling the `bins` of every R7 record of that day counts those jobs twice and gives 474 instead of 382; three of the five rewritten jobs are R7 jobs.

## Reference solution
1. List the workspace: README.md and logs/collections.jsonl.
2. Read README.md: one record per job, `round` names the round, `day` the collection day and `bins` how many bins the job emptied; the export was retried and wrote a job out again when the first attempt had already stored it.
3. Read logs/collections.jsonl and keep the R7 records of 5 September 2026. Twelve jobs appear, three of them written out twice with identical fields; the twelve jobs emptied 34+28+41+19+37+25+43+31+22+39+27+36 = 382 bins.

## Why the answer is unique
README.md says a record is written per job and that the second export attempt wrote a job out again when the first attempt had already stored it, so two records carrying the same job reference are one job that emptied its bins once, and the `bins` of a job are counted once. The decoy 474 is what the R7 records of the day add up to when the three rewritten jobs are counted twice, and the 6 September records are the same round on another day. With each job counted once, the answer is 382.

## Fixture notes
A rewritten record repeats its first record in every field, including `ts`, so the two copies are indistinguishable and the job reference is what identifies them. The rewritten R7 jobs sit in the middle of the day rather than at its end, and the R6 records of the same day are mixed in so the round filter has to be applied as well.
