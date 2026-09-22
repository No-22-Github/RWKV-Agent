## Traps
- TR-NUMFMT: every elapsed value in telemetry/label-print-jobs.jsonl is a string carrying its unit, either a millisecond form (940ms, 275ms, 410ms, 720ms, 530ms) or a second form (1.6s, 2.05s, 1.25s, 3.4s, 1.08s). Aggregating the field directly fails, and a reader who strips the suffix and adds the bare numbers gets 940 + 1.6 + 275 + 2.05 + 410 + 1.25 + 720 + 3.4 + 1.08 + 530 = 2884.38 ms, which mixes two units.

## Reference solution
1. list_files to see the workspace layout (1)
2. read_file telemetry/label-print-jobs.jsonl and read the elapsed field of each of the ten records (2)
3. Convert every elapsed value to milliseconds (1.6s -> 1600, 2.05s -> 2050, 1.25s -> 1250, 3.4s -> 3400, 1.08s -> 1080) and add them to the millisecond values: 940 + 1600 + 275 + 2050 + 410 + 1250 + 720 + 3400 + 1080 + 530 (3)

## Why the answer is unique
Each of the ten records carries exactly one elapsed value and the two suffixes present, ms and s, have fixed meanings, so every value converts to a single number of milliseconds. The prompt fixes the requested unit as milliseconds, which removes any choice of reporting unit. Summing the ten converted values gives 12255 ms; the unit-blind sum 2884.38 rests on treating a value of 1.6 seconds as 1.6 milliseconds, which no reading of the field supports. The answer is 12255 ms.
