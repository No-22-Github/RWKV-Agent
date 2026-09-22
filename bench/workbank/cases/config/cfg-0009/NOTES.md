## Traps
- None. cfg-0009 is the plain completeness comparison of the family: the
  platform key template (templates/service-keys.yaml) lists seven keys and the
  live config (config/payment-settler.yaml) declares six of them, so exactly one
  key is absent. There is no second source, no override layer and no absent
  item to tempt a wrong exit.

## Reference solution
1. list_files (1)
2. read_file templates/service-keys.yaml — the required key set: service_name,
   listen_port, retry_backoff_ms, max_inflight_batches,
   graceful_shutdown_seconds, ledger_endpoint, telemetry_sample_rate (2)
3. read_file config/payment-settler.yaml — six of the seven keys are present
   and retry_backoff_ms is not declared (3)
4. answer retry_backoff_ms

## Why the answer is unique
templates/service-keys.yaml is the only file that enumerates required keys, and
config/payment-settler.yaml is the only settings file for the named service;
the two sets differ by exactly one member, retry_backoff_ms. Every other key in
the template has a literal `key: value` line in the config, and the config
declares no key outside the template, so no second candidate exists. The ops
note carries no key names. verify.py recomputes the difference from the two
fixture files and refuses to print anything when the difference is not exactly
one key, so the reply is the single missing key name.

<!-- WORKBANK-CANARY-4b1e7a92 : this file must never enter training corpora -->
