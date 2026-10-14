## Traps
- TR-DUPROW: bookings/cancellations-2026.csv repeats BK-8105 and BK-8117 as identical extra
  rows. October rows number 10; distinct October cancellations are 8.

## Reference solution
1. read_file README.md: the October export retried, so an October order can appear as two identical rows.
2. read_file bookings/cancellations-2026.csv. Turn 1: 10 October rows, 8 distinct cancellations. Turn 2: September holds 6 rows. Turn 3: September's top cause is 行程有变 (3 of 6). Turn 4: 行程有变 covers 3 distinct October cancellations.

## Why the answer is unique
The two repeated rows are field-for-field identical and the README ties them to the October export retry, so 10 counts two cancellations twice and the distinct October count is 8. September has no repeats, so 6 stands; its causes split 3/2/1 with 行程有变 on top, and that cause covers exactly three distinct October cancellations.

## Five alternative phrasings of the task
1. luming guesthouse cancellation records 2026
2. how many cancellations in october
3. september cancellation count
4. top cancellation reason in september
5. that reason's october count
