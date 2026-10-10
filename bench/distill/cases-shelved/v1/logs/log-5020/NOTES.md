## Traps
- TR-DECOY: the render queue also holds jobs whose `outcome` is failed or cancelled, and their records look like the others, so totalling `runtime_ms` over the queue without reading `outcome` gives 1377709 instead of 1102526.

## Reference solution
1. List the workspace: README.md and logs/queue.jsonl.
2. Read README.md: one record per job, `runtime_ms` is how long the job held the queue, and `outcome` is how the run ended.
3. Read logs/queue.jsonl, or filter it to `queue` = render and `outcome` = completed, and total `runtime_ms`: the 19 records that survive sum to 1102526.

## Why the answer is unique
The question asks for the jobs the render queue finished, and README.md says `outcome` records how each run ended, so a job recorded as failed or cancelled is not one of them. 19 render records carry outcome=completed and their run times add up to 1102526. The decoy 1377709 keeps the 3 render jobs that failed or were cancelled, which never finished; totalling one other queue, or the whole file, answers different questions. With `outcome` read, the answer is 1102526.

## Fixture notes
All `runtime_ms` values are bare integers, no record of another queue shares a job name with a render job, and the file covers 18 August 2026 only, so no date filtering is needed.
