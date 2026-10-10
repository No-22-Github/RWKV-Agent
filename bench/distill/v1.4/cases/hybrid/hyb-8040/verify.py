# DISTILL-CANARY-1b17d49a : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'pebblestream.io/changelog' in w["url"]][0]["content"]
assert '5.6.2' in off and '5.7.0-beta.2' in off and '5.6.1' in off
line = [l for l in off.splitlines() if '5.6.2' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))
files = case["files"]
assert files['inventory/hosts.csv'].splitlines()[0] == 'host,package,version'
assert 'web-01,pebblestream-agent,5.4.3' in files['inventory/hosts.csv'].splitlines()

print(json.dumps({"expected_string": '5.6.2'}, ensure_ascii=False))
