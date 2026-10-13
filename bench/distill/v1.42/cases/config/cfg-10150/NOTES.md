## Traps
- TR-DECOY: the root settings.toml says 3. Every bash call starts at the workspace root, so a turn-2 `cat settings.toml` after turn 1's `cd apps/billing` reads the root copy.

## Reference solution
Turn 1: bash `cd apps/billing && ls` -> lists Cargo.toml among others.
Turn 2: read apps/billing/settings.toml by its full path (read tool or bash) -> 7.
Final answer turn 2: Billing's settings.toml sets retries = 7 (apps/billing/settings.toml; the root default is 3).

## Why the answer is unique
The question is about the file inside apps/billing.
