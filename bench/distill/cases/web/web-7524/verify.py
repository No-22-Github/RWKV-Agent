# DISTILL-CANARY-6b280d11 : distillation case
import json, re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "geo.yantai.example/docs/track" in e.get("url", ""))
m = re.search(r"最多上传\s*(\d+)\s*个轨迹点", page["content"])
assert m, "轨迹点上限行缺失"
print(json.dumps({"expected_number": int(m.group(1))}))
