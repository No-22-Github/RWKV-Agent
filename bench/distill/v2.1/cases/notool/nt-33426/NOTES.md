## Traps
- TR-AMBIG: two or more workspace items fit and nothing in the request or context picks one; answering for one (or all) is the failure.

## Reference solution
两份日志，追问哪一份；用户答 worker 后 grep -c ERROR 得 14。

## Why the answer is unique
Turn 1 uses no writing tool, asks which one and names the candidates; turn 2 fixes the target and the answer is recomputed from the fixture.
