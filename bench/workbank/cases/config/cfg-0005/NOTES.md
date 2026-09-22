## Traps
- None (L0 baseline). The workspace has two config layers — the fleet
  baseline in config/defaults.yaml and the environment file
  environments/eu-west.env — but only the environment file carries a port
  for tariff-calc, so there is no losing value to be confused with the
  effective one. The defaults file sets tariff-calc timeouts and retries and
  meter-bridge's port is a different service's key.

## Reference solution
1. list_files — see config/defaults.yaml, environments/eu-west.env, ops/ and
   README.md
2. read_file config/defaults.yaml — the tariff-calc block has
   request_timeout_seconds and retry_attempts, no port
3. read_file environments/eu-west.env — TARIFF_CALC_PORT=7714 → answer 7714

## Why the answer is unique
7714 is the only port key that belongs to tariff-calc anywhere in the tree;
the baseline file carries no port for the service and METER_BRIDGE_PORT
belongs to a different service. The ops notes and README carry no port
information, so no second reading of the question is possible.

<!-- WORKBANK-CANARY-3a7f2c9d : this file must never enter training corpora -->
