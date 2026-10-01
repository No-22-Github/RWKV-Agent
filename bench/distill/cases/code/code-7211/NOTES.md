## Traps
- TR-NEARNAME: the package defines flush_queue_locked once and calls it 4 times; its name extends flush_queue as a substring, so a prefix search or a text count folds the twin in and overshoots. Matching names exactly, flush_queue has 12 call sites.

## Reference solution
1. Read README.md: the scope is galebreak/ and names match exactly.
2. Search the name flush_queue and read the line windows around the hits.
3. Keep only call expressions whose function name is exactly flush_queue; drop the definition and every flush_queue_locked call.
4. The count is 12.

## Why the answer is unique
The README pins the scope and exact-name matching; flush_queue_locked is a different function despite the shared prefix. The package holds exactly 12 call expressions of flush_queue.
