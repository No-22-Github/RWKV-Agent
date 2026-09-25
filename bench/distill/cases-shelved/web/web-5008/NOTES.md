## Traps
- TR-EARLYHIT: the first result, marshlight.example/python-sdk/releases, already states the newest Python SDK default, so one search is enough; marshlight.example/node-sdk/releases is a second page for the Node SDK whose 6 attempts is the decoy.

## Reference solution
1. Search once for the Marshlight SDK releases: the first result is the Python SDK page, whose snippet gives 4 attempts in 2.9.0, and the Node SDK page is listed with it.
2. Open marshlight.example/python-sdk/releases and confirm that the newest entry, 2.9.0 of 2026-08-05, raises the default retry attempts to 4; answer 4.

## Why the answer is unique
The two pages are the release histories of two different SDKs, and the question names the Python SDK. Its newest entry, 2.9.0, states 4 attempts, while 2 is the value of the two older Python entries. 6 is the newest default of the Node SDK, which the question does not ask about, and 45 is the Node SDK keepalive in seconds, not an attempt count.

## Five alternative phrasings of the task
Every query below carries the fixture keyword marshlight, so each one is answered by a fixture entry.
1. marshlight python sdk releases
2. marshlight sdk default retry attempts
3. marshlight python sdk newest release defaults
4. marshlight client retry attempts default
5. marshlight sdk release notes
