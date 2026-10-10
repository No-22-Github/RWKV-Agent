# DISTILL-CANARY-dcf11a8f : distillation case
import json

case = json.load(open("case.json"))
entries = {w["url"]: w for w in case["web_fixture"]}
official = entries['https://www.bh-diving.org.cn/fees/permit']
stale = entries['https://bbs.qianyou.club/thread-8823']
assert official.get("error") and official["error"].startswith('HTTP 503')
assert '1280' in stale["content"]
assert stale["published_at"].startswith('2024')
print(json.dumps({"expected_string": '2024'}))
