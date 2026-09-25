## Traps
- TR-DECOY: the label template in tanning/marks.py and the label built in tanning/racks.py both
  carry the marker inside a string, so counting every line that mentions it gives 5.

## Reference solution
1. Read tanning/marks.py and see that a lot is held when the marker is written in a comment on
   its line, while a string that carries the marker is a label (call 1).
2. Count the annotated lines: tanning/__init__.py, tanning/pits.py and tanning/racks.py each
   carry one (call 2).
3. tanning/marks.py carries the marker only in its constant and its label template (call 3).

## Why the answer is unique
Three comment lines carry the annotation. The template in tanning/marks.py and the rack label
string are labels rather than holds, so counting them reaches 5 and counting the template line
alone reaches 4. The answer is 3.
