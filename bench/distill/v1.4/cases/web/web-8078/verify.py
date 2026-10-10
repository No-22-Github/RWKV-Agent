# DISTILL-CANARY-605d99cd : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'yantaidb.org/releases' in w["url"]][0]["content"]
assert '3.7.2' in off and '4.0.0-rc.3' in off and '3.7.1' in off
line = [l for l in off.splitlines() if '3.7.2' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))

print(json.dumps({"expected_string": '3.7.2'}, ensure_ascii=False))
