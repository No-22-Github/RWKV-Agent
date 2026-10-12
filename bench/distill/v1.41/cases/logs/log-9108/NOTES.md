## Traps
- TR-TRUNC: edge-events.log is 188KB, past read_file's 64KB cap and bash's 8KB output cap; counting the visible part undercounts.
- TR-DECOY: code E40210 begins with E4021; a prefix grep counts 236 instead of 121.

## Reference solution
1. bash: `grep -c 'code=E4021 ' var/edge-events.log`
Final answer: There are 121 lines with code E4021 in var/edge-events.log (E40210 is a different code).

## Why the answer is unique
README pins that codes are exact; the grep pattern ends with a space so E40210 does not match.

## Alternative phrasings
1. How many events in var/edge-events.log carry error code E4021?
2. Count lines with code=E4021 in the edge events log; README explains the code format.
3. edge-events.log: number of E4021 entries? Exact code only.
4. Tell me how many times code E4021 shows up in var/edge-events.log.
5. How often did the upstream timeout code E4021 occur in edge-events.log?
