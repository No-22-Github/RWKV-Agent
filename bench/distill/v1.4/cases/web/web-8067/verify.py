# DISTILL-CANARY-45ee183a : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'alderlibrary.org/membership' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'riverside-parents.org/alder-library-guide' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '112' in sec["content"]

print(json.dumps({"expected_string": '112'}, ensure_ascii=False))
