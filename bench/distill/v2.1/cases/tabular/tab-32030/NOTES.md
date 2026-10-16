## Traps
- tab separated; OK rows dominate the raw count
- fixture: ops/errors.tsv, 560 data rows, delimiter '\t'

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 ops/errors.tsv
    awk -F'\t' 'NR>1 && NF && $3!="OK"{print $3}' ops/errors.tsv | sort | uniq -c | sort -rn | head -n 3

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
