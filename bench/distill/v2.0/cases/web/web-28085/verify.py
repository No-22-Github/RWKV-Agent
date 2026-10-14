# DISTILL-CANARY-cc494c16 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'vellum-pdf.io/channels' in w["url"]][0]["content"]
assert '9.1.1' in off and '9.2.0-beta.3' in off and '9.1.0' in off
line = [l for l in off.splitlines() if '9.1.1' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '9.1.1'}, ensure_ascii=False))
