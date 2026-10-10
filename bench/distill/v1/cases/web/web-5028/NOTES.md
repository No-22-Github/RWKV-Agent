## Traps
- TR-EARLYHIT: the first result is the Bracklowe reference and its snippet gives the
  busy sweep interval (23 minutes), so one search is enough and the case caps
  web_search at 1. The 240 minute idle interval on the same table is the decoy: it
  applies once the queue has nothing to do, which the question excludes. The second
  page is a trial-only limit (68 minutes) and does not apply to paid workspaces.

## Reference solution
1. Search for the Bracklowe sweep defaults: the reference page is the first result
   and its snippet carries the busy interval, with the trial limits page listed
   beside it.
2. Open docs.bracklowe.example/reference/sweep-defaults and read the
   busy_sweep_interval_minutes row: a queue that still holds work is swept every
   23 minutes.

## Why the answer is unique
The page pairs each interval with the state it applies to: 23 minutes while the
queue holds work and 240 minutes once it is empty. The question keeps the queue
busy, so only the busy row applies. The trial page's 68 minutes is written for trial
workspaces and the page says paid workspaces are not held to those limits, so it
cannot be the interval for this queue.

## Five alternative phrasings of the task
1. bracklowe sweep defaults
2. bracklowe busy sweep interval
3. how often does bracklowe sweep a busy queue
4. bracklowe scheduler reference sweep settings
5. bracklowe idle sweep interval
