## Traps
- TR-DECOY: the log keeps two FAULT lines (3 and 9 September) that fall in the overhaul
  window the README excludes, plus five WARN lines that read like faults. Faults after the
  15 September recovery line are 4; all FAULT lines are 6.

## Reference solution
1. read_file README.md: only FAULT lines logged after the 15 September recovery count toward the month.
2. read_file logs/crane-faults-2026-09.log. Turn 1: FAULT lines dated 18, 21, 24, 27 September = 4. Turn 2: of those, 塔吊三号 owns 2. Turn 3: 三号's two faults name 吊钩限位 and 变频器.

## Why the answer is unique
The two pre-recovery FAULT lines and the WARN lines are the salient wrong pools: taking all FAULT lines gives 6, taking FAULT+WARN gives 11, but the README excludes everything logged in the overhaul window and the request asks for FAULT only, leaving the four post-recovery lines. Cutting to 塔吊三号 leaves exactly two, and their part names appear verbatim on those lines.

## Five alternative phrasings of the task
1. panshi building materials september crane faults
2. fault records after the mid-september overhaul
3. tower crane three faults in the second half of september
4. which parts failed on tower crane three
5. september crane log fault count by unit
