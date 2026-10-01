# DISTILL-CANARY-f0cc3f67 : distillation case
import json, re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "help.yunfan.example/limits" in e.get("url", ""))
m = re.search(r"单张出库单最多可添加\s*(\d+)\s*行", page["content"])
assert m, "上限行缺失"
print(json.dumps({"expected_number": int(m.group(1))}))
