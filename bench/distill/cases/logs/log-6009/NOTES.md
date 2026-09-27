## Traps
- TR-CLAIM: the closing SUMMARY line claims defrosts_completed=9 with all_ok=true, but the nine cycle lines show eight result=ok cycles and one result=aborted cycle (02:19). Reading the count off the banner gives 9.

## Reference solution
1. List the workspace: README.md and logs/defrost-cycles.log.
2. Read README.md: a cycle counts as completed when its own line reports result=ok, and the summary comes from a separate reporting job.
3. Read logs/defrost-cycles.log and count cycle lines with result=ok = 8.

## Why the answer is unique
Each cycle line carries the authoritative result for that cycle, and the README defines completion by that result field, so a cycle that aborted is not a completed cycle under any reading of the file. The SUMMARY line is a claim from a separate job, and its 9 conflicts with the evidence it summarises; the README's provenance note removes any reason to prefer the claim over the per-cycle results. The evidence yields 8.
