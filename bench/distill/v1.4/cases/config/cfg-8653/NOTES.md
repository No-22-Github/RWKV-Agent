## Traps
- TR-DECOY: exporter has byte-identical limits lines further down.
- replace_lines must cover the whole run of 2 lines (start_line 8, end_line 9) and content must have 2 lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read k8s/deploy-pipeline.yaml; the target lines are 8-9.
2. replace_lines start_line 8, end_line 9 with:
           cpu: 1000m
           memory: 1Gi
3. Read k8s/deploy-pipeline.yaml back to confirm.
Final answer, one sentence then DONE on its own line: Updated k8s/deploy-pipeline.yaml lines 8-9 (2 lines), re-read the file to confirm. / DONE Criteria: file equals the expected text exactly; output contains DONE.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
