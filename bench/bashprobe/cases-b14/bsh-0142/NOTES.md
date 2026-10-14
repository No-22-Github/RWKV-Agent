## Traps
- The sandbox has no curl and no network; `curl https://tallyhook.dev/releases/4.2` fails with command not found. The page is reachable through the web fetch tool.

## Reference solution
1. bash: `curl -s https://tallyhook.dev/releases/4.2` -> command not found (optional; the recovery is the point)
2. web_fetch https://tallyhook.dev/releases/4.2
Final answer: Tallyhook 4.2 removed the --legacy-auth flag (and now needs Node 20+). curl isn't installed here, so I fetched the release notes with the web tool.

## Why the answer is unique
The page states one value.

## Five alternative phrasings of the task
1. What flag did Tallyhook 4.2 drop?
2. Check the Tallyhook 4.2 notes for removed flags.
3. Any breaking CLI change in Tallyhook 4.2?
4. Which option is gone in Tallyhook 4.2?
5. Read the 4.2 release notes and list removed flags.
