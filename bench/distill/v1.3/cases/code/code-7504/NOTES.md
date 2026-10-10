## Traps
- TR-DECOY: src/pipeline_cli.py 的 print 里有一句字符串 "TODO: rotate the alert banner text"，按文本搜索会把它算进标记数，答成 11。 A careless pass reports `11`.

## Reference solution
1. Read the three pipeline modules in src/.
2. Count only the TODO/FIXME comment lines, leaving the banner string out.
3. Report the total and the kinds found.

## Why the answer is unique
The banner text in pipeline_cli.py is a string literal inside print(), not a comment, so the open markers are the ten comment lines: two in pipeline.py, two in pipeline_cli.py and six in pipeline_util.py. Both TODO and FIXME appear, and no module hides another marker, so the count is 10.
