## Traps
- TR-DECOY: deploy/service.env 里有一行注释掉的 LISTEN_PORT=8080，粗读会当成现行端口。 A careless pass reports `8080`.

## Reference solution
1. List deploy/ to find the env file and the port list.
2. Read deploy/service.env, skipping the commented line, and take the live values.
3. Read deploy/used-ports.list to confirm which port is current, then answer.

## Why the answer is unique
The 8080 value sits behind a leading # and the used-ports ledger marks 8080 as retired, so the live port is the uncommented LISTEN_PORT=8443. SERVICE_NAME and LOG_LEVEL appear once each and are uncommented, so the effective set is unique.
