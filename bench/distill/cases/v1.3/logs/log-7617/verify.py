# DISTILL-CANARY-ad10fdfe : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
text = case["files"]["exports/kiln-0530.csv"]
lines = [l for l in text.splitlines() if l.strip()]
body = "\n".join(lines[2:])
rows = list(csv.DictReader(io.StringIO(body)))
faults = [r for r in rows if (r.get("代码") or "").strip() == "E-21"]
fixed = [r for r in rows if "更换" in (r.get("说明") or "")]
if not faults:
    raise SystemExit(1)
first = (faults[0].get("时间") or "").split()
facts = [
    first[1] if len(first) > 1 else first[0],
    "E-21",
    "加热片" if fixed else "",
]
print(json.dumps({"expected_contains_any": facts}))
