## Traps
- TR-DUPROW: three Fellgate lots were booked in a second time, so adding every Fellgate row gives 2100.7 kilograms
  instead of 1829.4.
- TR-DECOY: the same file carries the Saltcoats station at 2706.1 kilograms. It is the larger figure on the page, so
  a reader who takes the busiest station, or skims past the station column, answers 2706.1.

## Reference solution
1. List the workspace: the August intake log and a short readme.
2. Read README.md: one row per lot, and the desk lost its session, so a lot can appear twice.
3. Read fleece_intake_2026-08.csv and keep the rows booked in at Fellgate, one row per lot_id.
4. Add the weights of the twenty Fellgate lots: 1829.4 kilograms.

## Why the answer is unique
The readme says one row per lot, and each reprinted Fellgate line repeats its lot_id, date, station, breed and
weight, so the repeats are the same lot booked twice and cannot be weighed again. The request names the Fellgate
station, and every row carries a station, so the Saltcoats and Braehill lots belong to other bookings. The
Fellgate lots come to 1829.4 kilograms.
