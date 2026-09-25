## Traps
- TR-NOTOOLNEED: the clause file and README are props for the same rule; the answer follows from paging arithmetic. The near-miss decoy `LIMIT 20 OFFSET 20` is the second page: it has the right page length but skips the wrong number of items, the mistake that appears when the offset is read as a page number.

## Reference solution
1. Answer from arithmetic: pages of twenty items, so the third page starts after forty items and returns twenty of them.
2. Reply with `LIMIT 20 OFFSET 40`, whose MySQL spelling is `LIMIT 40, 20`.

## Why the answer is unique
The question fixes both the page size and the page number, and the two quantities determine the clause completely: a length of 20 and a skip of 40. Any other offset names a different page, so `LIMIT 20 OFFSET 20` answers a question nobody asked, and the ordering clause is given by the question, which leaves `LIMIT 20 OFFSET 40` as the only clause; `LIMIT 40, 20` is the same clause in the engines that take the offset first.
