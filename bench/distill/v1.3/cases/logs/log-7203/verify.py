# DISTILL-CANARY-08ccdf33 : distillation case
import json
import re

case = json.load(open("case.json"))
lines = case["files"]["logs/fenjian-2026-08-19.log"].splitlines()

if not lines or not lines[0].startswith("# 凌波快递 城南分拣中心"):
    raise SystemExit("fixture guard failed: 日志头行缺失")
close = re.match(r"^# 日志收播 记录数=(\d+) 采集器=\S+$", lines[-1] if lines else "")
if close is None:
    raise SystemExit("fixture guard failed: 收播行缺失")
if int(close.group(1)) != len(lines) - 2:
    raise SystemExit("fixture guard failed: 记录数与收播行不符")

rec = re.compile(r"^(2026-08-19 \d\d:\d\d:\d\d) (INFO|WARN|ERROR) ([ABC]线) 包裹=(PKG-\d+) (.+)$")
per_pkg = {}
for line in lines[1:-1]:
    m = rec.match(line)
    if not m:
        raise SystemExit("unreadable log line: " + line)
    _, level, lane, pkg, msg = m.groups()
    if level == "ERROR" and msg.startswith("面单缺失"):
        per_pkg.setdefault(pkg, []).append(line)
count = len(per_pkg)
if count != 64:
    raise SystemExit(f"fixture guard failed: expected 64 label-missing packages, saw {count}")
if not any(len(rows) == 2 and rows[0] == rows[1] for rows in per_pkg.values()):
    raise SystemExit("fixture guard failed: collector re-send pairs are gone")
print(json.dumps({"expected_number": count}))
