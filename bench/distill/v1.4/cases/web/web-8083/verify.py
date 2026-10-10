# DISTILL-CANARY-9ec553fa : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'quartzite.dev/versions' in w["url"]][0]["content"]
assert '4.9.2' in off and '5.0.0-alpha.4' in off and '4.9.1' in off
line = [l for l in off.splitlines() if '4.9.2' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '4.9.2'}, ensure_ascii=False))
