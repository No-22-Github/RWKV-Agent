## Traps
- TR-PRECEDENCE: max_connections appears in all three layers —
  environments/ledger-sync.env (950), services/ledger-sync.yaml (600),
  deploy/defaults.yaml (200). README.md states the deployer's resolution
  order (environment file wins, then service yaml, then defaults).
  Stopping at the service yaml gives the decoy 600; stopping at the
  defaults gives 200.

## Reference solution
1. list_files — see deploy/, services/, environments/, README.md
2. read_file README.md — resolution order: environments/ beats services/
   yaml beats deploy/defaults.yaml
3. read_file services/ledger-sync.yaml — max_connections: 600 (losing layer)
4. read_file environments/ledger-sync.env — MAX_CONNECTIONS=950 (winning
   layer) → answer 950

## Why the answer is unique
Once the documented resolution order is applied, exactly one value is in
effect for max_connections: 950. The other two layers' values (600, 200)
are the decoys, and no other key is asked about.

<!-- WORKBANK-CANARY-52be7d10 : this file must never enter training corpora -->
