# DISTILL-CANARY-421b5442 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'zhandao.io/download' in w["url"]][0]["content"]
assert '2.9.4' in off and '3.0.0-rc.1' in off and '2.9.3' in off
line = [l for l in off.splitlines() if '2.9.4' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))
files = case["files"]
assert files['部署/客户A.csv'].splitlines()[0] == '组件,版本,环境'
assert '栈道网关,2.8.0,生产' in files['部署/客户A.csv'].splitlines()

print(json.dumps({"expected_string": '2.9.4'}, ensure_ascii=False))
