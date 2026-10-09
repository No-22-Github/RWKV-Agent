## Traps
- TR-TRUNC: edge.log is past every read cap.
- TR-DUPROW-like: the same request_id is throttled more than once; counting lines over-counts. Answer counts distinct request IDs.

## Reference solution
1. bash: `grep 'status=429' traces/edge.log | sed 's/.*request_id=\([^ ]*\).*/\1/' | sort -u | wc -l`
Final answer: 199 distinct requests were throttled with 429 (unique request_id values in traces/edge.log; repeats of the same request are counted once).

## Why the answer is unique
The prompt asks for requests, not log lines.
