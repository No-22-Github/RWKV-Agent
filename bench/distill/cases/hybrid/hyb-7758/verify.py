# DISTILL-CANARY-6bbdb9a4 : distillation case
import json

case = json.load(open("case.json"))
lines = [l for l in case["files"]["suppliers/供应商名单.txt"].split("\n") if l and not l.startswith("隆升版材")]
print(json.dumps({"files": {"suppliers/供应商名单.txt": "\n".join(lines) + "\n"}}))
