# DISTILL-CANARY-f2404837 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "合同/服务合同.md", "start": 4, "end": 6, "new": ["甲方应在验收后 30 日内付款。", "逾期按日万分之三计违约金。", "违约金总额不超过合同金额 5%。"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
