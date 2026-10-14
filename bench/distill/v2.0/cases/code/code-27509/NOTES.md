## Traps
- TR-DECOY: audit/emit.py 的 BANNER 字符串里有一句 TODO 文案，按文本搜索会多算一处、答成五处标记。 A careless pass reports `5`.

## Reference solution
1. Read audit/emit.py and audit/rules.py.
2. Count the TODO/FIXME comment lines per file; the BANNER string is a runtime text, not a marker.
3. Report which kinds appear in which file.

## Why the answer is unique
BANNER holds a TODO sentence as a string literal that gets emitted at runtime, so it is not an open marker; the markers are the FIXME in emit.py and the three TODOs in rules.py. No other file exists in audit/, so the per-file kind report is fixed.
