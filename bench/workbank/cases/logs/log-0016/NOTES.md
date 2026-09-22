## Traps
- TR-MISSING: telemetry/edge-requests.jsonl holds eighteen records and three carry no elapsed value, one in each shape - e0147a is null, a70c46 is the empty string, and f16b83 has no elapsed key. README.md states that a request the collector did not observe to completion carries no elapsed value and is accounted as having exceeded the goal. A reader who passes over the three durationless records counts only the eight measured requests above one second and reports 8.
- TR-NUMFMT: every recorded elapsed value is a string carrying its unit, either millisecond (740ms, 315ms, 868ms, 640ms, 488ms, 912ms) or second (1.92s, 2.4s, 1.05s, 3.05s, 1.38s, 0.92s, 2.75s, 1.18s, 1.61s). A reader who compares the bare numeric part of each value against 1000 finds none of the measured requests above the line, and with the three durationless requests counted lands on 3.

## Reference solution
1. list_files to see the workspace layout (1)
2. read_file README.md for the one-second objective and how a request the collector did not observe to completion is accounted (2)
3. read_file telemetry/edge-requests.jsonl and convert each recorded elapsed to milliseconds: 1.92s, 2.4s, 1.05s, 3.05s, 1.38s, 2.75s, 1.18s and 1.61s exceed 1000 ms (eight requests); 740ms, 315ms, 868ms, 640ms, 488ms, 912ms and 0.92s do not (3)
4. Add the three durationless records (null, empty string, absent key) to the eight measured requests above the line, giving 11 (4)

## Why the answer is unique
Two rules fix the count and both are stated in README.md. First, exceeding the goal means an elapsed time greater than one second, which strict reading excludes the 0.92s record and includes the eight values above 1000 ms; the ms and s suffixes have single fixed meanings so each record converts to exactly one number of milliseconds. Second, a record the collector did not observe to completion carries no elapsed value and is accounted as exceeding the goal, which adds exactly the three durationless records in their three shapes. No other record is ambiguous: status, route and timestamp do not enter the count, and there is no record with an unparseable elapsed value. The count is 11.
