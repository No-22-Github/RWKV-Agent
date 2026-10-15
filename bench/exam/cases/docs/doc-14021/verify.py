# EXAM-CANARY-03c2b3b1 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
prompt = " ".join(t["prompt"] for t in case["turns"]) + json.dumps(case.get("files", {}), ensure_ascii=False) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
facts = ["PO-88213", "2026-09-25"]
for f in facts:
    assert f in prompt, f
import csv, io
rows = list(csv.DictReader(io.StringIO(case["files"]["供应商/通讯录.csv"])))
mail = [r["邮箱"] for r in rows if r["公司"] == "恒达配件"][0]
derived = [mail, "PO-88213", "2026-09-25"]
exp = case["expect"]["files"]
out = {}
for p, e in exp.items():
    if "contains" in e:
        out[p] = "\n".join(derived if "derived" in globals() else e["contains"])
print(json.dumps({"files": out}, ensure_ascii=False))
