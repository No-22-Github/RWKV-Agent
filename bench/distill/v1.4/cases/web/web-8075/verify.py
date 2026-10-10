# DISTILL-CANARY-7ed6ea8a : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'corvidnet.com/r7/specs' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'homelab-wiki.org/Corvid_R7' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '128' in sec["content"]

print(json.dumps({"expected_string": '128'}, ensure_ascii=False))
