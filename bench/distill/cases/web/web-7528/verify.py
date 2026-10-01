# DISTILL-CANARY-910ba5f4 : distillation case
import json, re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "www.baize.example/fanyi/changelog" in e.get("url", ""))
versions = re.findall(r"^##\s+(\d+\.\d+\.\d+)", page["content"], re.M)
assert versions, "更新日志缺版本标题"
latest = max(versions, key=lambda v: [int(x) for x in v.split(".")])
print(json.dumps({"expected_contains_any": [latest]}, ensure_ascii=False))
