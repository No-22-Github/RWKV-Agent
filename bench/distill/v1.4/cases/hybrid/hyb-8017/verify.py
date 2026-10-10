# DISTILL-CANARY-3396ead7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]['lockers/assignments.csv'])))
picked = [r for r in rows if r['Status'] == 'occupied']
assert len(picked) > 1
total = len(picked)
official = [w for w in case["web_fixture"] if 'brantfell.com' in w["url"]][0]
stale = [w for w in case["web_fixture"] if 'snowhomejournal.com' in w["url"]][0]
assert official.get("error") and official["error"].startswith('Connection timed out')
assert stale.get("content") and stale["published_at"].startswith('2025')
assert '85' in stale["content"]
print(json.dumps({"expected_number": total}))
