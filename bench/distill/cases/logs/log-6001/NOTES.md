## Traps
- TR-DUPROW: logs/berth-loading.log contains three exact copies of LOAD COMPLETE lines left by the export retry, so the journal shows 19 COMPLETE lines for 16 physical loads. Counting COMPLETE lines gives 19.

## Reference solution
1. List the workspace: README.md and logs/berth-loading.log.
2. Read README.md: the export retried, so lines can appear twice, and a tanker loads once per run.
3. Read logs/berth-loading.log and collect the tankers behind LOAD COMPLETE lines: 16 distinct tankers = 16 completed loads.

## Why the answer is unique
The question asks for completed loads, and README.md states a tanker loads once per run, so the repeated journal lines are the same load written twice, not extra loads. Every repeated line matches its original byte for byte, including the timestamp, so no reading of the file turns them into separate tankers. The decoy 19 comes from counting COMPLETE lines; the count of distinct tankers behind them is 16.
