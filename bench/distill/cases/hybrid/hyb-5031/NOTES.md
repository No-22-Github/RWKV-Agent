## Traps
- TR-EARLYHIT: the first result is Brackenmere Water's own schedule and its snippet gives
  the charge for the licence on every row of the log (0.42 per cubic metre), so one search
  is enough and the case caps web_search at 1. The Cranmoor catchment page is the decoy:
  its 0.35 applies to another licence and gives 417.55 instead of 501.06.

## Reference solution
1. list_files: the workspace holds abstraction/september-2026.csv and README.md.
2. read_file abstraction/september-2026.csv: eight September rows for licence LR-22/451,
   adding up to 138 + 165 + 151 + 120 + 178 + 149 + 160 + 132 = 1193 cubic metres.
3. web_search "brackenmere abstraction charge": the regional schedule is the first result
   and its snippet gives 0.42 per cubic metre for LR-22/451.
4. Multiply: 1193 x 0.42 = 501.06.

## Why the answer is unique
The licence number is written on every row of the log and the schedule states one charge
per licence, so the figure for LR-22/451 is the one that applies. The Cranmoor catchment
note prices a different licence in another catchment, and the schedule itself names its
0.35 as belonging to LR-22/302, so it cannot be the charge for the September volumes. The
schedule adds that the charge is raised monthly on the reported volumes, which is what the
log holds: 501.06.

## Five alternative phrasings of the task
1. brackenmere water abstraction charges licence
2. brackenmere licence LR-22/451 charge per cubic metre
3. brackenmere abstraction charge for the september volumes
4. brackenmere water regional schedule 2026
5. cost of abstraction under brackenmere water
