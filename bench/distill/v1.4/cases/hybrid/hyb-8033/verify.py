# DISTILL-CANARY-45cf23c2 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'chengguang-av.com/support/x30' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'avfans.cn/thread/x30-lamp' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert 'LP-7740' in sec["content"]
files = case["files"]
assert files['采购/2026-09.csv'].splitlines()[0] == '品名,型号,数量,单价'
assert '澄光投影仪,X30,4,5980' in files['采购/2026-09.csv'].splitlines()

print(json.dumps({"expected_string": 'LP-7740'}, ensure_ascii=False))
