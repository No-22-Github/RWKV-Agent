# DISTILL-CANARY-41ab8b45 : distillation case
import json

case = json.load(open("case.json"))
PATH, OLD, NEW, SECTION, TICKET = 'bastion/session.toml', 'idle_timeout_min = 15   # compliance: <= 15', 'idle_timeout_min = 10   # compliance: <= 15', None, ('bastion/SEC-209.txt', 'SEC-209: idle_timeout_min must be 10 for all bastion hosts effective immediately.\nOwner: R. Valdez\n')
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
