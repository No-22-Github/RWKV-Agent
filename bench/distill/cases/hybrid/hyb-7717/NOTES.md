## Traps
- TR-DECOY: tests/germination-2026q3.csv holds the look-alike batches BT-2201, BT-2210 and
  BT-2101. Misreading the request as BT-2101 gives an average of 84.0 instead of 87.5.

## Reference solution
1. read_file README.md: rate is the germination percentage per sample.
2. read_file tests/germination-2026q3.csv. Turn 1: BT-2201's 8 samples average 87.5. Turn 2: BT-2210 averages 85.2, so BT-2201 is higher. Turn 3: the gap is 2.3 percentage points.
3. Turn 4: BT-2210 has 5 samples.

## Why the answer is unique
The three batch codes differ by one digit, but each row carries its batch and the averages are fixed once the rows are grouped: 87.5 (BT-2201), 85.2 (BT-2210), 84.0 (BT-2101). The comparison is between the two named batches, so BT-2201 wins by 2.3 points; the BT-2101 average answers neither question. BT-2210 owns exactly five sample rows.

## Five alternative phrasings of the task
1. hefeng seed q3 germination rates
2. average germination for batch bt-2201
3. which batch germinates higher bt-2201 or bt-2210
4. gap between the two batch averages
5. sample count for batch bt-2210
