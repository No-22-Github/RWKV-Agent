## Traps
- TR-DATEFMT: service dates mix ISO, slash and month-name styles, and the readme fixes the slash
  style as day first. The booking dated 05/06/2026 ran on 5 June carrying 48 passengers, which
  puts June on top with 412. A reader who swaps the fields moves that booking to 6 May, handing
  the quarter to May with 449.

## Reference solution
1. List the workspace: the second-quarter booking log and a readme.
2. Read README.md: slash dates are day-month-year.
3. Read bookings/coach_bookings_q2_2026.csv, resolve every service date, total passengers per
   month, and take the busiest month's total: 412.

## Why the answer is unique
The readme pins slash dates to day first, so 05/06/2026 is a June service and stays in June;
under that reading June totals 412, ahead of May's 401 and April's 356. The swapped reading that
produces 449 contradicts the readme, and no other row crosses a month boundary under either
reading. The answer is 412.
