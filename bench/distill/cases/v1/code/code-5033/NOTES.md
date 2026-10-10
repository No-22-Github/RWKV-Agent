## Traps
- TR-DECOY: the marker also sits in a loft note, in the constant in curing/marks.py and in the
  label template there, so counting every line that mentions it gives 7.

## Reference solution
1. Read curing/marks.py and see that a run is held when the marker is written in a comment on
   its line (call 1).
2. Count the annotated lines: curing/__init__.py, curing/loft.py, curing/packs.py and
   curing/salts.py each carry one (call 2).
3. The loft note, the constant and the template carry the marker outside a comment (call 3).

## Why the answer is unique
Four comment lines carry the annotation. The note in curing/loft.py is part of a description and
the two lines in curing/marks.py name the marker rather than holding a run, so counting them
reaches 7. The answer is 4.
