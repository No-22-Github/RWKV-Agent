## Traps
- tab separated; kwh vs peak_kwh
- fixture: energy/readings.tsv, 500 data rows, delimiter '\t'

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 energy/readings.tsv
    awk -F'\t' 'NR>1 && NF && $1=="M-104"{s+=$3} END{printf "%.1f\n", s}' energy/readings.tsv
Turn 2:
    awk -F'\t' 'NR>1 && NF && $1=="M-102"{s+=$4} END{printf "%.1f\n", s}' energy/readings.tsv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
