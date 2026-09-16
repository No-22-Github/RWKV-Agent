## Traps
- None (L0 baseline). The port appears exactly once, in the only deployment
  config file for notify-hub.

## Reference solution
1. list_files — see services/notify-hub.yaml, README.md, ops/
2. read_file services/notify-hub.yaml — port: 8431 → answer 8431

## Why the answer is unique
services/notify-hub.yaml is the only deployment config for notify-hub and
contains exactly one port key; the asset inventory and README carry no port
information, so no second reading of the question is possible.

<!-- WORKBANK-CANARY-9f34c1ab : this file must never enter training corpora -->
