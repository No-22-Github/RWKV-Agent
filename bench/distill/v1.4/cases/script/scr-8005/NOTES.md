## Traps
- Pattern jobs/*/words.csv requires the file to be directly in the language folder; fr has none there.

## Reference solution
Read script, list jobs/, adjust glob to recursive, read back. Note ** also matches zero dirs so jobs/de/words.csv still counted.

## Why the answer is unique
Recursive pattern covers dated subfolders of each language.
The fixed script prints:
de 3050
fr 3050
