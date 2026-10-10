# DISTILL-CANARY-e81a931f : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]['race/entries.csv'])))
picked = [r for r in rows if r['Status'] == 'entered']
assert len(picked) > 1
total = len(picked)
official = [w for w in case["web_fixture"] if 'thornbeckcup.com' in w["url"]][0]
stale = [w for w in case["web_fixture"] if 'gatejumperforum.net' in w["url"]][0]
assert official.get("error") and official["error"].startswith('fetch failed')
assert stale.get("content") and stale["published_at"].startswith('2023')
assert '130' in stale["content"]
print(json.dumps({"expected_number": total}))
