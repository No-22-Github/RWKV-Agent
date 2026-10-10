## Traps
- TR-DECOY: logs/fleet-release.log holds a settlement rollout (build 4417) at 04:38:21Z, fourteen minutes before the loader's first failure, so it is the most recent rollout of the night and reads like the change to blame. The loader's failures name `upstream=ledger-sync`, and ledger-sync's own most recent rollout is build 4431 at 01:26:39Z, so 4417 is a change to a different service.

## Reference solution
1. List the workspace: README.md plus logs/payroll-loader.log and logs/fleet-release.log.
2. Read README.md: the loader logs a refused post against `upstream=<service>`, and the release journal records one rollout per line as service, build and node count.
3. Read logs/payroll-loader.log. It starts at 04:52:07Z, extraction succeeds and every failure from 04:52:11Z onward is `post upstream=ledger-sync status=503`.
4. Read logs/fleet-release.log. Rollouts of ledger-sync: build 4431 at 01:26:39Z, which is the last one before the failures began, so the answer is 4431.

## Why the answer is unique
The question asks for the build of the service the loader was calling, and the loader's own journal names that service on every failure line: ledger-sync. The release journal lists one rollout per service per night, so ledger-sync's build at the time of the failures is the last of its rollouts that precedes the first failure, which is 4431. The decoy 4417 is a settlement rollout: it is nearer in time, but settlement is not the service the loader was calling, and no failure line names it. Reading the release journal alone gives 4417 because it is the newest rollout in the file; pairing it with the service name from the loader journal gives 4431.

## Fixture notes
Both journals are plain text with one record per line and UTC timestamps, and README.md states that a service is rolled out at most once a night, so each service has exactly one build to consider. The loader's journal shows a single failing service, so no line has to be weighed against another.
