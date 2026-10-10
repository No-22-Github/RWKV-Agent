# DISTILL-CANARY-5235a0f7 : distillation case
import json

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if 'qingyu-ferry.gov.cn/fares' in w["url"]][0]
sec = [w for w in case["web_fixture"] if 'islandlife.cn/forum/ferry-pass' in w["url"]][0]
assert off.get("error") and not off.get("content")
assert '468' in sec["content"]

print(json.dumps({"expected_string": '468'}, ensure_ascii=False))
