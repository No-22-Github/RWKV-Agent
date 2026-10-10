# DISTILL-CANARY-079b433c : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'bijinotes.com/pricing' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'sspai-like.cn/biji-review' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '250' in sec["content"]

print(json.dumps({"expected_string": '250'}, ensure_ascii=False))
