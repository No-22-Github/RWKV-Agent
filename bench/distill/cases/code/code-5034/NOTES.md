## Traps
- TR-DECOY: the constant in sluice/marks.py names the marker too, so a sweep that counts every
  file mentioning it reaches 6.

## Reference solution
1. Read sluice/marks.py and see that a run is held when the marker is written in a comment on
   its line (call 1).
2. Count the files with an annotated line: sluice/__init__.py, sluice/gates.py,
   sluice/outfall.py, sluice/runlog.py and sluice/weir.py (call 2).
3. sluice/marks.py carries the marker only in its constant (call 3).

## Why the answer is unique
Five files carry the annotation in a comment. sluice/marks.py names the marker in its constant
without holding a run, so counting every file that mentions it reaches 6. The answer is 5.
