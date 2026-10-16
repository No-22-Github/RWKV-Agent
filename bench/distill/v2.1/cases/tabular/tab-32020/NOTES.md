## Traps
- amount vs amount_refunded; a grep-based sum would take both
- fixture: bank/card_txn.csv, 470 data rows, delimiter ','

## Reference solution
(each command replayed in the just-bash sandbox by build.py)
Turn 1:
    head -3 bank/card_txn.csv
    awk -F',' 'NR>1 && NF && $2=="Metro Mart"{s+=$3} END{printf "%.2f\n", s}' bank/card_txn.csv
Turn 2:
    awk -F',' 'NR>1 && NF && $2=="Metro Mart"{s+=$4} END{printf "%.2f\n", s}' bank/card_txn.csv

## Why the answer is unique
verify.py recomputes every answer from the fixture with python csv; build.py requires the sandbox output of the reference commands to agree with it.
