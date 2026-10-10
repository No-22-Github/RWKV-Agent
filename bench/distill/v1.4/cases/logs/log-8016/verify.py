# DISTILL-CANARY-01308158 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
# sabotage guard: bank verify deletes the first non-empty line of this file first
assert files["logs/新风压差-手术室-2026-10.csv"].splitlines()[0] == "日期,机组,滤网状态,压差Pa,备注"

surg = {r["日期"]: r for r in csv.DictReader(io.StringIO(files["logs/新风压差-手术室-2026-10.csv"]))}
# No pressure reading on Oct 7-8: the gauge was disconnected for the filter change.
assert surg["2026-10-07"]["压差Pa"] == "" and surg["2026-10-08"]["压差Pa"] == ""
assert "断开" in surg["2026-10-07"]["备注"] and "未接回" in surg["2026-10-08"]["备注"]
assert surg["2026-10-09"]["压差Pa"] == "41"
# Decoys: pre-change readings of the same unit and the kennel unit's Oct 8 value.
assert surg["2026-10-06"]["压差Pa"] == "92"
kennel = {r["日期"]: r for r in csv.DictReader(io.StringIO(files["logs/新风压差-犬舍-2026-10.csv"]))}
assert kennel["2026-10-08"]["压差Pa"] == "69"
doc = files["运维/机组维护记录.md"]
assert "断开" in doc and "重新接回" in doc
words = ["断开", "未接回", "没接回", "重新接回", "无读数", "没有读数", "没有记录", "无记录", "缺失", "没有数据", "无数据", "10-09", "10 月 9 日"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
