## Traps
- TR-DATEFMT: placed_on mixes ISO, slash and month-name styles, and the readme fixes the slash
  style as day first. Order AP-636 dated 12/06/2026 was placed on 12 June, inside the window; a
  reader who swaps the fields dates it 6 December and counts 4 orders instead of 5.

## Reference solution
1. List the workspace: the June order book and a readme.
2. Read README.md: slash dates are day-month-year.
3. Read orders/orders_june_2026.csv, resolve every placed_on date, and count orders from 8 to 14
   June 2026 inclusive: 5.

## Why the answer is unique
The readme pins the slash style to day first, so 12/06/2026 is 12 June and stays in the window,
while 03/06, 18/06, 21/06, 25/06 and 28/06 are June days outside it and 08/07/2026 is July. The
month-name and ISO rows carry their own months. Only the misread of the 12/06 row changes the
count, and that reading contradicts the readme, so the answer is 5.
