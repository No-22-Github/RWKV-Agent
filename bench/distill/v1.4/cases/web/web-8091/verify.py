# DISTILL-CANARY-6fb64cdc : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'heron-auth.dev/changelog' in w["url"]][0]["content"]
assert '6.0.4' in off and '6.1.0-beta.1' in off and '6.0.3' in off
line = [l for l in off.splitlines() if '6.0.4' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '6.0.4'}, ensure_ascii=False))
