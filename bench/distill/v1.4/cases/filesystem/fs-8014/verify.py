# DISTILL-CANARY-c82a29fc : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
ledger = files["服务单/台账.txt"].splitlines()
assert ledger[0] == "服务单 | 机器SN | 日期 | 说明"
rows = {l.split(" | ")[1]: l for l in ledger[1:] if l.strip()}
assert "RS-21087" in rows and "经销商" in rows["RS-21087"]
assert not any("RS-21087" in p for p in files if p.endswith(".md"))
assert any("21078" in p for p in files)
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "未归档", "没有归档", "留在经销商系统"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
