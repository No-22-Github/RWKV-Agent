# DISTILL-CANARY-31045152 : p13-holdout eval case (eval-only, never training data)
import csv
import hashlib
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["budget-2026.csv"])))
if not rows or "category" not in rows[0] or "amount_q3" not in rows[0]:
    raise SystemExit("budget export layout changed; the snapshot is void")
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(files.items())
}
print(json.dumps({"files": snapshot}))
