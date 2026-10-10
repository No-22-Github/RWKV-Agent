# DISTILL-CANARY-dae5a06a : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'embercache.io/download' in w["url"]][0]["content"]
assert '8.0.6' in off and '8.1.0-beta.1' in off and '8.0.5' in off
line = [l for l in off.splitlines() if '8.0.6' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))
files = case["files"]
assert files['compose/images.csv'].splitlines()[0] == 'service,image,version'
assert 'sessions,ember-cache,7.2.9' in files['compose/images.csv'].splitlines()

print(json.dumps({"expected_string": '8.0.6'}, ensure_ascii=False))
