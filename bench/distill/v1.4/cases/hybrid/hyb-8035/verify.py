# DISTILL-CANARY-f814d7b2 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'github.com/yanchi-search/yanchi/blob/main/LICENSE' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'oss-compliance.cn/wiki/yanchi' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert 'MPL-2.0' in sec["content"]
files = case["files"]
assert files['部署/组件清单.csv'].splitlines()[0] == '组件,版本,用途'
assert '砚池搜索,1.9.3,站内检索' in files['部署/组件清单.csv'].splitlines()

print(json.dumps({"expected_string": 'MPL-2.0'}, ensure_ascii=False))
