## Traps
- TR-DECOY: the user names one file; a backup, old, example or other-environment copy carries a different value (8080).

## Reference solution
1. read_file on the named file.
Final answer: The server listens on port 8443 (service/settings.toml; the .bak copy says 8080).

## Why the answer is unique
The user names the file; only it holds the current value. The copy with another value is a decoy.
Why bash is not the tool here: one named file and one fact, the read tool is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.

## Five alternative phrasings of the task
1. Which port is configured under [server] in service/settings.toml?
2. Check service/settings.toml and tell me the listening port.
3. service/settings.toml: what is `port` set to?
4. What's the server port in the toml settings file?
5. Tell me the port from service/settings.toml.
