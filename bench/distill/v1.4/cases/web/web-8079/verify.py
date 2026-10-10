# DISTILL-CANARY-0f3d2a76 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'github.com/larkspur-go/router/releases' in w["url"]][0]["content"]
assert 'v1.12.0' in off and 'v2.0.0-beta.2' in off and 'v1.11.4' in off
line = [l for l in off.splitlines() if 'v1.12.0' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": 'v1.12.0'}, ensure_ascii=False))
