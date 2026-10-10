# DISTILL-CANARY-c0e12811 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'luwei-sdk.org/releases' in w["url"]][0]["content"]
assert '3.11.5' in off and '3.12.0-alpha.2' in off and '3.11.4' in off
line = [l for l in off.splitlines() if '3.11.5' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))
files = case["files"]
assert files['app/依赖.csv'].splitlines()[0] == '依赖,版本,用途'
assert '芦苇 SDK,3.9.0,数据同步' in files['app/依赖.csv'].splitlines()

print(json.dumps({"expected_string": '3.11.5'}, ensure_ascii=False))
