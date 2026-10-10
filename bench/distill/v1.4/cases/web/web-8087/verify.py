# DISTILL-CANARY-1c4728fc : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'basalt-lint.org/changelog' in w["url"]][0]["content"]
assert '0.42.3' in off and '0.43.0-rc.1' in off and '0.42.2' in off
line = [l for l in off.splitlines() if '0.42.3' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '0.42.3'}, ensure_ascii=False))
