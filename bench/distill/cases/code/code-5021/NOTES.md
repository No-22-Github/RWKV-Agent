## Traps
- TR-DECOY: ledger/marks.py names the marker twice without annotating anything, once as the ANNOTATION value and once inside a template string, so matching every line that contains the text gives 5 instead of 3.

## Reference solution
1. Read ledger/__init__.py: one annotated line at the top of the package (call 1).
2. Read ledger/entries.py and ledger/report.py: one annotated line in each (call 2).
3. Read ledger/marks.py: its two mentions of the text are a value and a string template, which the module's own note calls values rather than annotations (call 3). The annotated lines are one in ledger/__init__.py, one in ledger/entries.py and one in ledger/report.py, so the answer is 3.

## Why the answer is unique
The decoy count 5 comes from reading the marker's text wherever it appears: marks.py holds the marker as a value and inside a template string, and a value a module compares against is not an annotation on the line that holds it. That is how the same module can name the marker twice while carrying no annotation of its own. Three lines carry the marker in a comment, so the answer is 3.
