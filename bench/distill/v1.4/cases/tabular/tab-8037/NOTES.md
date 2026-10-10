## Traps
- TR-ABSENT: data/mobile-reader-september.csv only covers six market days through 19 September (1959.42 pounds); data/README.md says the reader moved to the new processor account on 22 September and takings from that day on haven't been exported yet. Presenting 7639.88 + 1959.42 = 9599.30 as the September total is the decoy answer.
- TR-MULTISRC: reading only one of the two files misses a channel entirely; the terminal total alone is 7639.88.

## Reference solution
1. List data/: two takings CSVs and a README.
2. Sum card-takings-september.csv: both terminals, all nine market days, 7639.88 pounds complete.
3. Read mobile-reader-september.csv and the README: six days only, later days unexported pending the processor migration.
Final answer (2-4 sentences): The market's two card terminals took 7639.88 pounds in September, and that figure is complete. The borrowed mobile reader only has takings through 19 September (1959.42 pounds); from the 22nd on its takings settled on the new processor account and haven't been exported yet, so the September total across all readers cannot be settled yet. I can re-run the total once the processor exports the missing days. Criteria: contains 7639.88 (either spelling); the partial sum 9599.30 may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Changelog
- v2：去掉部分合计的排除：S5 三遍老师都给出「已记录合计 X，但不完整」，这是 v1.4 §4.1「只能答一部分」示范的写法，被排除词误判；完整性改由逐条读终答把关。

## Why the answer is unique
9599.30 treats six exported reader days as a full month, and the README states the later days are still on the new processor, so it is not the September total; 7639.88 alone ignores the reader channel. The certain part is the terminals' complete total, and the defensible reply names the export gap and the next step.
