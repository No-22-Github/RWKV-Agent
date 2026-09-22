## Traps
- TR-PRECEDENCE: max_inflight_batches is set in all three layers —
  config/default.yaml (64), config/local.yaml (96, which includes
  default.yaml and loads after it) and environments/qa.env (180).
  README.md states the loading order: environment file, then local, then
  baseline. A model that stops at the local tuning file reports the decoy 96;
  stopping at the baseline gives 64.

## Reference solution
1. list_files — see config/, environments/, ops/, README.md
2. read_file README.md — the three layers and the order they are applied in
3. read_file config/default.yaml and config/local.yaml — baseline 64, local 96
4. read_file environments/qa.env — PARCEL_SORTER_MAX_INFLIGHT_BATCHES=180 →
   answer 180

## Why the answer is unique
Once the documented loading order is applied, exactly one value is in effect
for the qa environment: 180. The baseline (64) and local (96) values are the
losing layers, and the sensor poll keys in the same files are not asked
about. No other file in the tree sets max_inflight_batches.

<!-- WORKBANK-CANARY-b41e08f2 : this file must never enter training corpora -->
