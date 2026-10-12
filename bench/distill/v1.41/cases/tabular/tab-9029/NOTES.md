## Traps
- TR-TRUNC: readings.csv is ~137KB, past the 64KB read cap and the 8KB output cap; the first 64KB only sums to 2795.8.
- TR-DECOY: M-2040 and M-204B contain M-204 as a substring (a prefix match gives 10797.0).
- TR-DEFN: meters/README.md says void rows must not be counted (keeping them gives 6555.3).

## Reference solution
1. bash: `awk -F, '$2=="M-204" && $4!="void" {s+=$3} END{printf "%.1f\n", s}' meters/readings.csv`
Final answer: meter M-204 recorded 5992.1 kWh in total (void readings excluded, estimates included).

## Why the answer is unique
Meter and flag are exact fields; the README fixes which flags count.
