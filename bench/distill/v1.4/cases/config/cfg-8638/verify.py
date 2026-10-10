# DISTILL-CANARY-330cebd3 : distillation case
import json

case = json.load(open("case.json"))
PATH, OLD, NEW, SECTION, TICKET = '养殖/饲喂.yaml', '    每次投喂kg: 12.5   # 含补料', '    每次投喂kg: 11.0   # 含补料', '  B栏:', ('养殖/兽医意见.txt', 'B栏近期消化不良，每次投喂量减到 11.0 kg，次数不变。A栏正常。\n')
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
