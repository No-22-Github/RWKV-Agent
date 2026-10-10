# DISTILL-CANARY-54159337 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'lighthouse-monitor.cn/changelog' in w["url"]][0]["content"]
assert '2.18.3' in off and '2.19.0-preview.2' in off and '2.18.2' in off
line = [l for l in off.splitlines() if '2.18.3' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '2.18.3'}, ensure_ascii=False))
