# DISTILL-CANARY-832c946a : distillation case
import json

case = json.load(open("case.json"))
entries = {w["url"]: w for w in case["web_fixture"]}
official = entries['https://www.moorfoot.com/night-ski']
stale = entries['https://carvedturns.blog/moorfoot-nights']
assert official.get("error") and official["error"].startswith('Connection timed out')
assert '1,250' in stale["content"]
assert stale["published_at"].startswith('2025')
print(json.dumps({"expected_string": '2025'}))
