# DISTILL-CANARY-a2d7c53a : distillation case
import json

case = json.load(open("case.json"))
entries = {w["url"]: w for w in case["web_fixture"]}
official = entries['https://www.graysummit.com/pass-renewals']
stale = entries['https://liftline.net/t/90412']
assert official.get("error") and official["error"].startswith('HTTP 503')
assert '1,150' in stale["content"]
assert stale["published_at"].startswith('2024')
print(json.dumps({"expected_string": '2024'}))
