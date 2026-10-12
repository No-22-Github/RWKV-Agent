## Traps
- TR-NOTOOLNEED: a knowledge/how-to question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: `tail -n 50 -f /srv/demo/events.out` (or -F to survive rotation).

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of ['tail'].

## Five alternative phrasings of the task
1. Write the command to follow /srv/demo/events.out starting from its last 50 lines. Don't execute.
2. How can I watch /srv/demo/events.out live, showing the last 50 lines first? Just the command.
3. Give me a command to stream new entries of /srv/demo/events.out after printing 50 lines. No running it.
4. Which command tails /srv/demo/events.out with 50 lines of context and keeps following? I'll run it myself.
5. Command only, please: last 50 lines then follow for /srv/demo/events.out.
