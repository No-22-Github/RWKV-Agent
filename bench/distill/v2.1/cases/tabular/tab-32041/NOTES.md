## Traps
- acc vs train_hours; seed filter is numeric
- fixture: ml/experiments.csv, 300 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 ml/experiments.csv
    awk -F, 'NR>1 && NF && $2=="lora-b" && $3=="code" && $4>=3{s+=$5;n++} END{printf "%.3f\n", s/n}' ml/experiments.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
