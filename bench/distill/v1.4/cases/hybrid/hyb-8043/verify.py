# DISTILL-CANARY-55b13f5b : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'yunshan-ui.cn/changelog' in w["url"]][0]["content"]
assert '4.2.7' in off and '4.3.0-preview.3' in off and '4.2.6' in off
line = [l for l in off.splitlines() if '4.2.7' in l][0]
assert any(k in line for k in ("stable", "latest", "推荐"))
files = case["files"]
assert files['前端/package清单.csv'].splitlines()[0] == '包名,版本,类型'
assert '云杉前端框架,4.0.2,运行时' in files['前端/package清单.csv'].splitlines()

print(json.dumps({"expected_string": '4.2.7'}, ensure_ascii=False))
