# DISTILL-CANARY-9298a541 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["work/README.txt"].startswith("Work area.")
assert case["files"]["work/c/report.tmp.md"].startswith("content of")
out = {}
for path, text in case["files"].items():
    if path.endswith(".tmp") and not path.startswith("work/pinned/"):
        continue
    out[path] = text
print(json.dumps({"files": out}))
