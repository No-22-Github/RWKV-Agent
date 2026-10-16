## Traps
- TR-ABSENT: retry_delay_s 在被问的范围内没有定义。
- TR-DECOY: weekly_rollup defines retry_delay_s: 90; nightly_load only has max_retries.

## Reference solution
Read nightly_load.yaml: no retry_delay_s.

## Why the answer is unique
nightly_load.yaml has max_retries: 4 but no retry_delay_s; 90 is weekly_rollup's value.
