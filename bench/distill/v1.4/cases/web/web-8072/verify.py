# DISTILL-CANARY-772092c0 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'qixialing-scenic.cn/ticket' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'travelnotes.cn/qixialing-winter' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '240' in sec["content"]

print(json.dumps({"expected_string": '240'}, ensure_ascii=False))
