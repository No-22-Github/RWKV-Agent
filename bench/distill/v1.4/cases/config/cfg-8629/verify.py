# DISTILL-CANARY-c40dab85 : distillation case
import json

case = json.load(open("case.json"))
PATH, OLD, NEW, SECTION, TICKET = 'services/orders/.env.prod', 'DB_POOL_SIZE=20      # per instance; max_connections is 400', 'DB_POOL_SIZE=30      # per instance; max_connections is 400', None, None
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
