# DISTILL-CANARY-9822e4a5 : distillation case
import json

case = json.load(open("case.json"))
PATH, OLD, NEW, SECTION, TICKET = '景区/闸机.toml', '每分钟限流 = 40   # 人/分钟', '每分钟限流 = 30   # 人/分钟', '[东门]', ('景区/应急通知.md', '# 应急通知（2026-10-01）\n\n| 闸机 | 每分钟限流 |\n|---|---|\n| 东门 | 30 |\n\n西门暂不调整。\n')
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
