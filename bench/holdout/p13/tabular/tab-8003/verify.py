# DISTILL-CANARY-d2e9a982 : p13-holdout eval case (eval-only, never training data)
import csv
import hashlib
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["export-sept.csv"])))
if not rows or "商品" not in rows[0] or "件数" not in rows[0]:
    raise SystemExit("sales export layout changed; the snapshot is void")
products = {row["商品"]: int(row["件数"]) for row in rows}
if products.get("合计") is not None:
    del products["合计"]
top = sorted(products.items(), key=lambda kv: -kv[1])[:2]
snapshot = {
    path: hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]
    for path, content in sorted(files.items())
}
snapshot["top_products"] = ",".join(name for name, _ in top)
print(json.dumps({"files": snapshot}))
