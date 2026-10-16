## Traps
- TR-ABSENT: retention_days 在被问的范围内没有定义。
- TR-DECOY: US file sets retention_days: 365; the EU file has none, and the README says there is no default.

## Reference solution
Read eu.yaml: no retention_days; README: no global default.

## Why the answer is unique
eu.yaml does not set retention_days and the README says there is no global default; 365 is only the US value.
