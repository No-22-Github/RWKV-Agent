# DISTILL-CANARY-220ec0bf : p13 holdout eval case (eval-only, never for training)
#
# 判据是缺失汇报（output_contains_any + output_excludes），没有可独立重算的值，
# 本脚本只回显夹具快照：基线必填项与两处配置的差集。
import csv
import io
import json

case = json.load(open("case.json"))
required = [
    r["配置项"].strip()
    for r in csv.DictReader(io.StringIO(case["files"]["配置基线.csv"]))
    if r["是否必填"].strip() == "是"
]
present = set()
commented = []
for path in ("app.yaml", "deploy.env"):
    for line in case["files"][path].splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            if s and ("=" in s or ":" in s):
                commented.append(s)
            continue
        sep = "=" if "=" in s else (":" if ":" in s else None)
        if sep:
            present.add(s.split(sep, 1)[0].strip())
print(json.dumps({
    "required": required,
    "present": sorted(present),
    "missing": sorted(k for k in required if k not in present),
    "commented_lines": commented,
}, ensure_ascii=False))
