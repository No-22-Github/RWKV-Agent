# DISTILL-CANARY-07ab51ca : distillation case
import json

case = json.load(open("case.json"))
entries = {w["url"]: w for w in case["web_fixture"]}
official = entries['https://www.branholm.com/tubing']
stale = entries['https://snowdaysblog.com/branholm-tubing']
assert official.get("error") and official["error"].startswith('HTTP 503')
assert '1,290' in stale["content"]
assert stale["published_at"].startswith('2024')
print(json.dumps({"expected_string": '2024'}))
