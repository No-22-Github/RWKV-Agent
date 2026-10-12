## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: grep is a process whose command line contains 'nginx', so ps lists it; use pgrep, or grep '[n]ginx', or pipe through grep -v grep.

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['pgrep', '[n]ginx', 'grep -v', 'itself', 'its own', 'own process'].

## Five alternative phrasings of the task
1. Why does grep show up in its own ps aux | grep results?
2. How do I stop `ps aux | grep name` from listing the grep process?
3. Why do I see a grep line when filtering ps output?
4. Is there a cleaner alternative to ps aux | grep for finding a process?
5. What's the trick with `grep '[n]ginx'` in ps pipelines?
