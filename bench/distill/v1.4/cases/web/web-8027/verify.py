# DISTILL-CANARY-9646aebb : distillation case
import json

case = json.load(open("case.json"))
entries = {w["url"]: w for w in case["web_fixture"]}
official = entries['https://www.chenzhou-club.cn/card']
stale = entries['https://diverhub.cn/t-2201']
assert official.get("error") and official["error"].startswith('HTTP 503')
assert '1680' in stale["content"]
assert stale["published_at"].startswith('2023')
print(json.dumps({"expected_string": '2023'}))
