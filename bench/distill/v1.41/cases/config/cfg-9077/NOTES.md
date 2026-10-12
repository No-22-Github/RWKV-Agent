## Traps
- TR-DECOY: config/server.toml.bak still says 30; the live file says 45.

## Reference solution
1. read_file config/server.toml
Final answer: read_timeout_s is 45 seconds in config/server.toml (the .bak copy has the old 30).

## Why the answer is unique
The user names config/server.toml; only it holds the live value.
Why bash is not the tool here: one named file and one fact: read_file is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.
