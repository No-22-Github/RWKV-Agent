# DISTILL-CANARY-0cc299f6 : distillation case
import json, re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.kongqing.example/notes/releases" in e.get("url", ""))
versions = re.findall(r"^##\s+(\d+\.\d+\.\d+)", page["content"], re.M)
assert versions, "发布记录缺版本标题"
latest = max(versions, key=lambda v: [int(x) for x in v.split(".")])
print(json.dumps({"expected_contains_any": [latest]}, ensure_ascii=False))
