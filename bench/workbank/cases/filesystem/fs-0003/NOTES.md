## Traps
- TR-DECOY: two directories hold a file with the identical name roster.csv. sites/ardmore/roster.csv belongs to the closed Ardmore facility, sorts first in listings and text searches, is the larger of the two, and carries its own night shift_lead extension 3926. Only sites/roseburg/roster.csv is in scope. Answering 3926 means the decoy roster was read instead of the active one.

## Reference solution
1. list_files the workspace and notice the two same-named roster.csv files (call 1)
2. read README.md to learn which site is active (call 2)
3. read sites/roseburg/roster.csv (call 3)
4. answer 4417, the single shift_lead extension in the active roster (call 4)

## Why the answer is unique
The active roster has exactly one shift_lead row (night, extension 4417); site_manager and loader rows carry other extensions. The retired roster is out of scope by the README's site status, and its own shift_lead rows are not a single unambiguous alternative anyway.
