# DISTILL-CANARY-bf99705b : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'lanhai-home.com/support/ap880' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'jiadian-blog.cn/lanhai-ap880' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert 'F-2231' in sec["content"]

print(json.dumps({"expected_string": 'F-2231'}, ensure_ascii=False))
