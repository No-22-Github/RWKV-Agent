# DISTILL-CANARY-7db9a21d : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'xingguiplot.org/releases' in w["url"]][0]["content"]
assert '0.19.2' in off and '0.20.0-rc.1' in off and '0.19.1' in off
line = [l for l in off.splitlines() if '0.19.2' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '0.19.2'}, ensure_ascii=False))
