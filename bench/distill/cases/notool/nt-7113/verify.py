# DISTILL-CANARY-b83d4a98 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["courses/videos_2026-10.csv"]))
minutes = next(float(r["时长分钟"]) for r in rows if r["视频"] == "开班导学")
value = minutes * 60
print(json.dumps({"expected_number": value}))
