# DISTILL-CANARY-d267337f : distillation case
import json, re

case = json.load(open("case.json"))
page = next(e for e in case["web_fixture"] if "help.zhenliu.example/read-later" in e.get("url", ""))
m = re.search(r"最多可保存\s*(\d+)\s*条内容", page["content"])
assert m, "保存上限行缺失"
print(json.dumps({"expected_number": int(m.group(1))}))
