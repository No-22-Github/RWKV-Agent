## Traps
- TR-DECOY: the retired copy of the desk under `replay_retired/` carries the same annotation on two of its lines. Counting the marker over the whole workspace gives 6 instead of the 4 lines under replay/.

## Reference solution
1. List the workspace: the desk is the replay/ package, with a retired copy beside it under replay_retired/ (call 1).
2. Read the four modules of replay/: the annotations are the header of replay/__init__.py, two comments in replay/holds.py and one in replay/runner.py (call 2 to 4 reads in total).
3. Read replay_retired/ to confirm the two annotated lines there belong to the retired copy (call 5). The desk's package carries four annotation lines, so the answer is 4.

## Why the answer is unique
The question counts the lines under replay/, and replay_retired/ is not under replay/: it is a separate top-level package with its own __init__.py, nothing in replay/ imports it and its own header records that it is retired and kept for the review file. Its two annotated lines therefore answer a question that was not asked, and the four lines inside replay/ carry the marker once each, so the count is 4.
