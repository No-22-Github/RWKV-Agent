## Traps
- price base year and compounding are only in the summary; using $63.40 flat is wrong

## Reference solution
1. read_file ppa/summary.md: $63.40 per MWh in 2024, escalating 2.5% per year, compounding.
2. calculator: 63.40 * 1.025^2 * 482.6 = 32145.81.
Final answer：The 2026 cost is $32145.81: $63.40/MWh escalated twice at 2.5% (2025, 2026), times 482.6 MWh.。判据：contains 32145.81 (thousands separator / trailing zeros optional), calculator used。

## Why the answer is unique
Base year 2024, so 2026 has two compounding escalations; kWh to MWh divides by 1000.
