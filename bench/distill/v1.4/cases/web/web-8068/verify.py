# DISTILL-CANARY-e086b3a1 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'docs.yunzhou-ci.com/quota' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'devtalk.cn/t/yunzhou-ci-free' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '750' in sec["content"]

print(json.dumps({"expected_string": '750'}, ensure_ascii=False))
