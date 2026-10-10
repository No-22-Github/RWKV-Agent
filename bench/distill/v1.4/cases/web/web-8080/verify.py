# DISTILL-CANARY-96931636 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'weidu-mq.io/download' in w["url"]][0]["content"]
assert '5.4.1' in off and '5.5.0-beta.1' in off and '5.4.0' in off
line = [l for l in off.splitlines() if '5.4.1' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '5.4.1'}, ensure_ascii=False))
