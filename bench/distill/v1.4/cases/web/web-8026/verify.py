# DISTILL-CANARY-45d9955b : distillation case
import json

case = json.load(open("case.json"))
entries = {w["url"]: w for w in case["web_fixture"]}
official = entries['https://www.shanwan-dive.cn/photo']
stale = entries['https://haifengnotes.cn/shanwan-photo']
assert official.get("error") and official["error"].startswith('Connection timed out')
assert '1580' in stale["content"]
assert stale["published_at"].startswith('2025')
print(json.dumps({"expected_string": '2025'}))
