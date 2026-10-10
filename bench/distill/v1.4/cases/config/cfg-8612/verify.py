# DISTILL-CANARY-f949430d : distillation case
import json

case = json.load(open("case.json"))
PATH, OLD, NEW, SECTION, TICKET = '鱼塘/增氧机.yaml', '  启动溶氧阈值: 4.5    # mg/L，低于即启动', '  启动溶氧阈值: 5.0    # mg/L，低于即启动', None, ('鱼塘/农技员记录.txt', '9月18日 建议启动溶氧阈值提到 5.0 mg/L，停止阈值先不动。\n9月11日 曾提议停止阈值 7.0，已否决。\n')
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
