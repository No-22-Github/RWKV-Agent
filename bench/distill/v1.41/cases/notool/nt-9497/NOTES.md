## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: `split -b 100M /tmp/bigdump.sql part_`; cat part_* rejoins them.

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['split'].

## Five alternative phrasings of the task
1. Give me a command to break /tmp/bigdump.sql into 100 MB chunks with the prefix part_. Don't execute it.
2. How do I split /tmp/bigdump.sql into 100M pieces? Command only.
3. Write the split invocation for 100 MB parts of /tmp/bigdump.sql, prefix part_; I'll run it later.
4. I need /tmp/bigdump.sql chopped into 100 MB files called part_aa, part_ab... Show the command but don't run it.
5. Command (not executed) to cut a big SQL dump into 100-megabyte segments?
