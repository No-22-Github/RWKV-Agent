# DISTILL-CANARY-343526d1 : distillation case
import json

case = json.load(open("case.json"))
entries = {w["url"]: w for w in case["web_fixture"]}
official = entries['https://www.kellasvale.com/shuttle-pass']
stale = entries['https://powderchat.net/t/55871']
assert official.get("error") and official["error"].startswith('fetch failed')
assert '1,080' in stale["content"]
assert stale["published_at"].startswith('2023')
print(json.dumps({"expected_string": '2023'}))
