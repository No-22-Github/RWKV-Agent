# DISTILL-CANARY-4bafeeba : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]['instructors/roster.csv'])))
picked = [r for r in rows if r['Status'] == 'current']
assert len(picked) > 1
total = len(picked)
official = [w for w in case["web_fixture"] if 'fellcraft.org' in w["url"]][0]
stale = [w for w in case["web_fixture"] if 'skiteacherdiaries.com' in w["url"]][0]
assert official.get("error") and official["error"].startswith('HTTP 503')
assert stale.get("content") and stale["published_at"].startswith('2024')
assert '340' in stale["content"]
print(json.dumps({"expected_number": total}))
