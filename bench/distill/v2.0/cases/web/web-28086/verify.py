# DISTILL-CANARY-64d5cea4 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'zhanqiao.dev/releases' in w["url"]][0]["content"]
assert '1.28.4' in off and '1.29.0-next.5' in off and '1.28.3' in off
line = [l for l in off.splitlines() if '1.28.4' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '1.28.4'}, ensure_ascii=False))
