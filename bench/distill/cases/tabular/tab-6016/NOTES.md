## Traps
- TR-DECOY: the same week also holds 4 outbound Crushed shale loads, and 5 Crushed rock loads
  arrived as inbound restocks. A reader who takes every Crushed rock-like OUT line without
  separating the two materials reports 12 loads instead of 8.

## Reference solution
1. List the workspace: the June weighbridge sheet and a readme.
2. Read README.md: OUT loads leave the quarry for customers.
3. Read weighbridge_2026-06.csv and count OUT rows with material Crushed rock dated 15-21 June:
   8.

## Why the answer is unique
The ticket labels every movement with a direction and an exact material, so Crushed rock and
Crushed shale are different products and IN movements never leave the quarry. The decoy 12 folds
the shale loads into the count, but the material column distinguishes them on every row, so the
outbound Crushed rock count is 8.
