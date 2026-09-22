## Traps
- TR-MISSING: telemetry/transcode-jobs.jsonl holds twelve records and three of them carry no render time, one in each shape - tr-8842 has render_ms null, tr-8846 has render_ms as the empty string, and tr-8849 has no render_ms key at all. README.md states that the quoted render time averages only over jobs that carry one. A reader who folds the three durationless rows in as zero sums the same 19620 ms over all twelve records and reports 1635.

## Reference solution
1. list_files to see the workspace layout (1)
2. read_file README.md for how the quoted render time is defined (2)
3. read_file telemetry/transcode-jobs.jsonl and keep the nine records that carry a render time, discarding tr-8842 (null), tr-8846 (empty string) and tr-8849 (no key) (3)
4. Add the nine durations (1830 + 2410 + 1620 + 2980 + 2140 + 1750 + 3620 + 1230 + 2040 = 19620 ms) and divide by nine, giving 2180.0 ms (4)

## Why the answer is unique
The README fixes the denominator: the average is taken over the jobs that carry a render time, and exactly nine of the twelve records do while three do not. The three non-carrying records are distinguishable in the data by three different shapes, but all three mean the same thing to the stated rule, so no reading of the export produces a denominator other than nine. Folding the three in as zero gives 1635, which the README rule excludes, and dividing only by a subset of the nine is not a reading any wording of the rule supports. The answer is 2180.0 ms.
