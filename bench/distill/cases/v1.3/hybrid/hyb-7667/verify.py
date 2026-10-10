# DISTILL-CANARY-70b0c477 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
page = next(e["content"] for e in case["web_fixture"] if "notices/ext-2026-09" in e.get("url", ""))
m = re.search(r"王翠英的分机由\s*\d+\s*调整为\s*(\d+)", page)
if not m:
    raise SystemExit("extension change not found in the notice")
reader = csv.DictReader(io.StringIO(case["files"]["客户服务部/应急联络表.csv"]))
out = io.StringIO()
writer = csv.DictWriter(out, fieldnames=reader.fieldnames, lineterminator="\n")
writer.writeheader()
for r in reader:
    if str(r["姓名"]).strip() == "王翠英":
        r["分机"] = m.group(1)
    writer.writerow(r)
print(json.dumps({"files": {"客户服务部/应急联络表.csv": out.getvalue()}}, ensure_ascii=False))
