## Traps
- TR-DECOY: `waivers/scan.py` names the annotation twice without annotating anything (its module note and the MARKER assignment), so matching every line that contains the text gives 6 instead of 4.

## Reference solution
1. Search the package for WAIVER-OPEN: the hits are the two mentions in waivers/scan.py plus one annotation line in each of waivers/__init__.py, waivers/review.py (two) and waivers/store.py (call 1).
2. Read waivers/scan.py: its two hits are a module note and the MARKER assignment, and the module scans annotations rather than carrying one (call 2).
3. Read the four annotated lines to confirm each is a comment on a line of code (call 3). The annotation lines are one in waivers/__init__.py, two in waivers/review.py and one in waivers/store.py, so the answer is 4.

## Why the answer is unique
The desk's rule is that an annotation is a marker written into a comment on a line of the module, and the scanner module keeps its own name for the marker in a string rather than annotating its lines; that is how waivers/scan.py both names the marker and marks nothing. Four lines carry the annotation in that sense, and the two mentions in the scanner are not annotation lines, so the count is 4.
