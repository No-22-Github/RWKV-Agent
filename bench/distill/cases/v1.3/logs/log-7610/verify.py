# DISTILL-CANARY-394f30b8 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
text = case["files"]["exports/rigging-w34.csv"]
lines = [l for l in text.splitlines() if l.strip()]
body = "\n".join(lines[2:])
rows = list(csv.DictReader(io.StringIO(body)))
breaks = [r for r in rows if (r.get("event") or "").strip() == "BREAKDOWN"]
if not breaks:
    raise SystemExit(1)
b = breaks[0]
detail = (b.get("detail") or "").strip()
facts = [
    (b.get("time") or "").strip(),
    "brake pads" if "seized" in detail else "",
    "SL-2",
]
print(json.dumps({"expected_contains_any": facts}))
