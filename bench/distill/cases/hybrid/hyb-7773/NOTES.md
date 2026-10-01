## Traps
- TR-AMBIG: September bookings appear in the live file and, partially, in the archive; reading the archive gives 5 hours and misses three bookings. Turn 1 must name both files and ask which to count.

## Reference solution
1. Turn 1: list the reservations directory, see the live and archive files, name both and ask which to use.
2. Turn 2: the user picks the live file.
3. Read reservations/reservations-2026-09.csv and sum the hours column: 3+2+4+5+3.
4. Total 17 and reply with the number alone.

## Why the answer is unique
 The decoy 5 counts only the two archived rows; the live file holds all five September bookings per the README, so after the user picks it the only reading is 17 hours.

## Five alternative phrasings of the task
1. How many hours are booked in September?
2. Total the September booking hours.
3. What is our September hours total?
4. Add up the hours on the September bookings.
5. Count the booked hours for September.
