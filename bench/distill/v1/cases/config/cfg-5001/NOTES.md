## Traps
- TR-PRECEDENCE: `cache_size_mb` is set in all three layers — 256 in `config/defaults.yaml`, 384 in `config/production.yaml`, 576 as `INGEST_CACHE_MB` in `deploy/production.env`. `README.md` says the process environment is the first source that counts, so a solver that reads the profile file as "the production config" and stops reports 384.

## Reference solution
1. List the workspace: `README.md`, `config/`, `deploy/` and an unrelated `docs/on-call` note are visible.
2. Read `README.md`: a setting takes the value from the first source that defines it — the process environment (filled from `deploy/<deployment>.env`), then `config/<deployment>.yaml`, then `config/defaults.yaml`; the environment variable for `cache_size_mb` is `INGEST_CACHE_MB`.
3. Read `deploy/production.env`, the file the platform runner exports for the production deployment: `INGEST_CACHE_MB=576` is set, so the environment layer wins and the effective cache size is 576.

## Why the answer is unique
The decoy 384 is the value in `config/production.yaml`, but that file is only the second layer of the three: `README.md` states that the process environment is consulted first, and `deploy/production.env` is the exact file the platform runner exports into the process environment of the production deployment, with `INGEST_CACHE_MB=576`. Because the top layer defines the key, neither the profile value nor the shipped default of 256 can apply, and nothing else in the workspace sets `cache_size_mb`. The answer is 576.
