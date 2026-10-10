# DISTILL-CANARY-05cdbd62 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]['报名/秋季船宿报名.csv'])))
picked = [r for r in rows if r['状态'] == '已确认']
assert len(picked) > 1
total = len(picked)
official = [w for w in case["web_fixture"] if 'deepblue-liveaboard.cn' in w["url"]][0]
stale = [w for w in case["web_fixture"] if 'chuanzhang.blog' in w["url"]][0]
assert official.get("error") and official["error"].startswith('fetch failed')
assert stale.get("content") and stale["published_at"].startswith('2024')
assert '2850' in stale["content"]
print(json.dumps({"expected_number": total}))
