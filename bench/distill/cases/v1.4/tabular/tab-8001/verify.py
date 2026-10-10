# DISTILL-CANARY-943a3125 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
ledger = list(csv.DictReader(io.StringIO(files["出库/2026-09.csv"])))
assert ledger and set(ledger[0]) == {"出库单号", "日期", "仓库", "金额"}
assert not any(r["仓库"] == "华东二仓" for r in ledger)
codes = {r["仓库"]: r for r in csv.DictReader(io.StringIO(files["仓库/编码表.csv"]))}
assert codes["华东二仓"]["状态"] == "停用" and "华东中转仓" in codes["华东二仓"]["说明"]
print(json.dumps({"expected_contains_any": ["停用", "并入", "合并"]}, ensure_ascii=False))
