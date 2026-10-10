# DISTILL-CANARY-26a824df : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]['装备/调节器台账.csv'])))
picked = [r for r in rows if r['状态'] == '在用']
assert len(picked) > 1
total = len(picked)
official = [w for w in case["web_fixture"] if 'qingsha-gear.cn' in w["url"]][0]
stale = [w for w in case["web_fixture"] if 'zhuangbeibiji.cn' in w["url"]][0]
assert official.get("error") and official["error"].startswith('HTTP 503')
assert stale.get("content") and stale["published_at"].startswith('2023')
assert '260' in stale["content"]
print(json.dumps({"expected_number": total}))
