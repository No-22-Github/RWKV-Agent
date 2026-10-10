# DISTILL-CANARY-0acb728e : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'brindleair.com/baggage-fees' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'frequentflyer-forum.net/brindle-bag' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '145' in sec["content"]

print(json.dumps({"expected_string": '145'}, ensure_ascii=False))
