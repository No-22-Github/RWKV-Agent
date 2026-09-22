## Traps
- TR-PRECEDENCE: hold_queue_depth is set in deploy/defaults.yaml (120), in
  deploy/local.yaml (200, which includes the defaults and loads after them)
  and in the staging overlay deploy/staging/dispatch-router.yaml (350).
  README.md gives the layer order. A model that stops at the local tuning
  file reports the decoy 200; stopping at the baseline gives 120.
- TR-DECOY: deploy/prod/dispatch-router.yaml has the same file name as the
  staging overlay, sorts before deploy/staging/ in a listing, carries more
  keys and comments, and README.md flags it as the reference overlay. It
  belongs to a different environment, so reading it yields 900, the recorded
  decoy, for a question about staging.

## Reference solution
1. list_files — the deploy/ tree, README.md and ops/
2. read_file README.md — the layer order and the prod overlay reference
3. read_file deploy/defaults.yaml and deploy/local.yaml — baseline 120, local
   200
4. read_file deploy/staging/dispatch-router.yaml — hold_queue_depth: 350; the
   prod overlay under deploy/prod/ is a different environment
5. answer 350

## Why the answer is unique
The question names the staging environment, and exactly one overlay under
deploy/staging/ sets hold_queue_depth (350). The prod overlay under
deploy/prod/ is the same file name but resolves for production, not staging,
so its 900 cannot be the staging value; the baseline (120) and local (200)
values are overridden by the staging overlay. No other file sets the key.

<!-- WORKBANK-CANARY-e08b3a6c : this file must never enter training corpora -->
