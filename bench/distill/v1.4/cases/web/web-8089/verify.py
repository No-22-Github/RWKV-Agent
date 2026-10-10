# DISTILL-CANARY-8cd2832e : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'cinder-queue.dev/download' in w["url"]][0]["content"]
assert '3.2.6' in off and '3.3.0-preview.1' in off and '3.2.5' in off
line = [l for l in off.splitlines() if '3.2.6' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '3.2.6'}, ensure_ascii=False))
