## Traps
- TR-DECOY: counting the annotated lines rather than the files that carry one gives 4, because spinning/winding.py holds two annotated lines while the question asks for the files.

## Reference solution
1. Read spinning/__init__.py: one annotated line (call 1).
2. Read spinning/roving.py: one annotated line (call 2).
3. Read spinning/winding.py: two annotated lines, and spinning/marks.py names the marker as a value without annotating anything (call 3). The three files that carry at least one annotated line make the answer 3.

## Why the answer is unique
The decoy count 4 counts annotated lines: winding.py annotates two of its lines, so lines and files part company there. The question asks for files, and each of spinning/__init__.py, spinning/roving.py and spinning/winding.py carries at least one annotated line while spinning/marks.py carries none, which fixes the count at 3 no matter how many annotated lines a single file holds.
