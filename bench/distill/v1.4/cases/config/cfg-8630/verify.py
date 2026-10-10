# DISTILL-CANARY-28c0c6f6 : distillation case
import json

case = json.load(open("case.json"))
PATH, OLD, NEW, SECTION, TICKET = 'gateway/limits.toml', 'burst = 10     # allow short spikes', 'burst = 20     # allow short spikes', '[login]', ('tickets/GW-318.txt', 'GW-318\n1. login.burst -> 20\n2. search.rate -> 80 (blocked, waiting on capacity review)\n')
if TICKET:
    assert case["files"][TICKET[0]] == TICKET[1], "ticket changed"
assert set(case["files"]) == {PATH} | ({TICKET[0]} if TICKET else set())
text = case["files"][PATH]
lines = text.splitlines(keepends=True)
start = 0
if SECTION is not None:
    hits = [i for i, l in enumerate(lines) if l.rstrip("\n") == SECTION]
    assert len(hits) == 1, hits
    start = hits[0]
idx = [i for i, l in enumerate(lines) if i >= start and l.rstrip("\n") == OLD]
assert idx, "target line missing"
if SECTION is None:
    assert len(idx) == 1, idx
lines[idx[0]] = NEW + "\n"
print(json.dumps({"files": {PATH: "".join(lines)}}, ensure_ascii=False))
