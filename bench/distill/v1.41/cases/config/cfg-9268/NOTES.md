## Traps
- TR-READONLY: services/_base/Dockerfile stays on node:16-alpine. TR-DECOY: `FROM nginx:1.16-alpine` in reports ends in 16-alpine too (`s/16-alpine/20-alpine/` changes it); reports' stage is `FROM node:16-alpine AS build`.
- Turn 2 changes part of what turn 1 did, so the final state is not a plain replace-everywhere.

## Reference solution
Turn 1:
1. bash: `find services -name Dockerfile | grep -v /_base/ | xargs sed -i 's/^FROM node:16-alpine/FROM node:20-alpine/'`
2. bash: `grep -rn '^FROM' services`
Final answer: DONE (api, web, reports, exporter, worker on node:20-alpine).
Turn 2:
1. bash: `sed -i 's/^FROM node:20-alpine/FROM node:16-alpine/' services/reports/Dockerfile services/exporter/Dockerfile`
2. bash: `grep -rn '^FROM' services`
Final answer: DONE (reports and exporter back on node:16-alpine, api/web/worker on node:20-alpine).

## Why the answer is unique
Only the files named by the requests change, in the order they were asked; everything else (README, protected files, look-alike lines) is byte-identical to the fixture. The README sentence fixes what stays.

## Five alternative phrasings of the task
1. Upgrade the services from node 16 to node 20, except the shared base, then reports and exporter go back to 16.
2. node:16-alpine -> node:20-alpine in every service Dockerfile (not _base); afterwards revert two services.
3. Switch all service images to Node 20, keep reports and exporter on 16.
4. Move the Dockerfiles to node 20 apart from _base; pin reports/exporter to node 16 again.
5. 把各服务 Dockerfile 的 node 从 16 升到 20，再把 reports 和 exporter 钉回 16
