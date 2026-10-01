## Traps
- TR-DECOY: in the canonical source the name calibrate_stream appears before the definition — a TODO comment (line 594), a log template string (line 1031), and a second comment (line 1213); sensors.py adds an import mention. Taking the first hit or an echo as the definition answers with the wrong line. The definition is the single `def calibrate_stream(` line, 1704.

## Reference solution
1. Read README.md: it names tidewatch/ingest.py as the canonical source whose line numbers the package quotes.
2. Search the name calibrate_stream and read the line windows around the hits.
3. Rule out the comment, the log template and the sensors.py mention; a definition is a `def` line.
4. The `def calibrate_stream(` line in the canonical source is 1704.

## Why the answer is unique
The README pins the canonical source, so line numbers come from exactly one file; a definition is a `def` line, which rules out the comment, the log template and the import mention. Inside the canonical file the name echoes 4 times but `def calibrate_stream(` matches once. The answer is 1704.
