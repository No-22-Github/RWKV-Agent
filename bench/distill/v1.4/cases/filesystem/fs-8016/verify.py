# DISTILL-CANARY-0696cbd4 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
ledger = files["安装/台账.txt"].splitlines()
assert ledger[0] == "安装点 | 验收单 | 状态"
rows = {l.split(" | ")[0]: l for l in ledger[1:] if l.strip()}
assert "未回传" in rows["青云台一期"]
assert "已归档" in rows["青云台二期"]
assert not any("青云台一期" in p for p in files if p != "安装/台账.txt")
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "未回传", "没有回传"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
