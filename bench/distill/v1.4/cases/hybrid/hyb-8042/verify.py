# DISTILL-CANARY-a4f4c2b5 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'tidewater-db.org/channels' in w["url"]][0]["content"]
assert '11.4.2' in off and '11.5.0-rc.2' in off and '11.4.1' in off
line = [l for l in off.splitlines() if '11.4.2' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))
files = case["files"]
assert files['runbook/clusters.csv'].splitlines()[0] == 'cluster,engine,version,owner'
assert 'prod-east,Tidewater DB,11.3.0,platform' in files['runbook/clusters.csv'].splitlines()

print(json.dumps({"expected_string": '11.4.2'}, ensure_ascii=False))
