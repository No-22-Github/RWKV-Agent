# DISTILL-CANARY-40f95586 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'songzhen-ui.cn/channels' in w["url"]][0]["content"]
assert '8.6.0' in off and '9.0.0-beta.4' in off and '8.5.2' in off
line = [l for l in off.splitlines() if '8.6.0' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '8.6.0'}, ensure_ascii=False))
