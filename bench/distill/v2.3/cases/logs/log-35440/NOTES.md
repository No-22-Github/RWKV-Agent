## Traps
- TR-DECOY: the proper tool is offered; use it (never_offer: -).

## Reference solution
search_text 'ERROR billing ' (or bash grep -c) -> 10

## Why the answer is unique
Router lines that mention a billing header are decoys for a loose search.

Expected: 10
