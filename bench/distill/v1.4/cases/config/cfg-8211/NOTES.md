## Traps
- Two -80 freezers with different thresholds; the README maps room 204 to F-80A.

## Reference solution
只提供 list_files / read_file / search_text 三个工具，正常检索后作答。
终答示例：The freezer in room 204 is F-80A, and its alarm threshold is -70 C (equipment/freezers.json).
判据见 case.json（contains=['-70'] any=[] excl=[]）。

## Why the answer is unique
Room 204 is F-80A, whose alarm_c is -70; F-80B is -65.
