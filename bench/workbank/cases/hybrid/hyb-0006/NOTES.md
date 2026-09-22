## Traps
- TR-NOTOOLNEED: the version the pipeline was built against is recorded locally in pipeline/deps.lock (wrenfield==0.9.3), so the task needs no lookup at all. The two wrenfield pages in the fixture carry no release numbers, so a model that goes to the web first spends calls and learns nothing; the manifest pin of 0.8.1 is the decoy a model reaches for if it reads only the package list and never the lock. This is graded on the edit result; the turn's "tools": [] is discipline metadata only, not a pass/fail gate.

## Reference solution
1. read_file pipeline/deps.lock; it records the resolved build, wrenfield==0.9.3 (1)
2. read_file pipeline/requirements.txt; the wrenfield pin is 0.8.1 and the other two entries must survive (2)
3. write_file pipeline/requirements.txt with the wrenfield pin set to 0.9.3 (3); reply DONE

## Why the answer is unique
README.md states that deps.lock records the exact version of every package the pipeline was built against, and the prompt asks for agreement with that build. The lock names exactly one wrenfield version, 0.9.3, and the generated file is not to be edited, so the edit is confined to the requirements entry. The contains-checks on the three pins plus unchanged checks on deps.lock, README.md and pipeline/transform.py pin down the result. Nothing in the workspace or the fixture offers a second candidate version.

## Five alternative phrasings of the task
1. wrenfield version in the bellhaven pipeline
2. wrenfield python library documentation
3. wrenfield configuration library
4. wrenfield serialise python objects
5. wrenfield package releases

## Grading note
v1 carried `expect.tools: []` on the turn. That is the zero-call contract - it
says the case is answered without touching a tool at all - and it contradicted
the reference solution's three workspace calls, so every passing run was scored
against a contract the case does not have. What TR-NOTOOLNEED means here is
narrower: the pin the prompt asks for is already in pipeline/deps.lock, so
going to the web to find it is the failure. v2 says exactly that with
`forbidden_tools: ["web_search", "web_fetch"]`. `expect.max_calls` cannot
express it - the loader rejects a budget below 1, so a zero budget makes the
case invalid.

<!-- WORKBANK-CANARY-8b31e07a : this file must never enter training corpora -->
