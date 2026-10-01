# DISTILL-CANARY-b55a6535 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
text = case["files"]["exports/booth-0802.csv"]
lines = [l for l in text.splitlines() if l.strip()]
body = "\n".join(lines[2:])
rows = list(csv.DictReader(io.StringIO(body)))
errors = [r for r in rows if (r.get("event") or "").strip() == "ERROR"]
resolved = [r for r in rows if "replaced" in (r.get("note") or "")]
if not errors:
    raise SystemExit(1)
first = errors[0]
stamp = (first.get("timestamp") or "").split()
facts = [
    stamp[1] if len(stamp) > 1 else stamp[0],
    (first.get("code") or "").strip(),
    "replaced" if resolved else "",
]
print(json.dumps({"expected_contains_any": facts}))
