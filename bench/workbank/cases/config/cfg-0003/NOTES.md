## Traps
- TR-RULEFILE: the merge semantics live in docs/flag-guide.md.
  express_checkout is default-off and atlasgrocer's tenant file switches
  it on, but the guide's beta allowlist (loyalty_multiplier_v2,
  bulk_importer) does not include express_checkout, so it stays off for
  that tenant. Skipping the handbook and reading only the tenant file
  gives the decoy "yes".

## Reference solution
1. list_files — see flags/, docs/, README.md
2. read_file flags/defaults.yaml — express_checkout: false
3. read_file flags/tenants/atlasgrocer.yaml — express_checkout: true
4. read_file docs/flag-guide.md — a tenant file can turn a default-off
   flag on only if the flag is in the beta allowlist; express_checkout is
   not listed → answer "no"

## Why the answer is unique
The allowlist in the handbook is exhaustive and express_checkout is
absent from it, so the tenant switch cannot take effect; every other
flag's merged state is unambiguous from the same two files plus the
handbook, leaving no second reading of the question.

<!-- WORKBANK-CANARY-c07a48e3 : this file must never enter training corpora -->
