# DISTILL-CANARY-f67ce23b : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'zhujian-doc.com/download' in w["url"]][0]["content"]
assert '6.2.0' in off and '6.3.0-rc.2' in off and '6.1.5' in off
line = [l for l in off.splitlines() if '6.2.0' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '6.2.0'}, ensure_ascii=False))
