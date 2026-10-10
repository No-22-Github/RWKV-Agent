# DISTILL-CANARY-428539b3 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'mosaic-cms.org/channels' in w["url"]][0]["content"]
assert '7.3.5' in off and '7.4.0-rc.1' in off and '7.3.4' in off
line = [l for l in off.splitlines() if '7.3.5' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '7.3.5'}, ensure_ascii=False))
