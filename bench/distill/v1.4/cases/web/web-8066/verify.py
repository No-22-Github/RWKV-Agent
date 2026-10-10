# DISTILL-CANARY-c1a48fb3 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'yz.hubin-univ.edu.cn/plan' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'kaoyan-circle.cn/hubin-plan' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '320' in sec["content"]

print(json.dumps({"expected_string": '320'}, ensure_ascii=False))
