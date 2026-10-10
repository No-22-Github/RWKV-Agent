# DISTILL-CANARY-adfc1c68 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]['会员/名单.csv'])))
picked = [r for r in rows if r['状态'] == '待注册']
assert len(picked) > 1
total = len(picked)
official = [w for w in case["web_fixture"] if 'canglan-diving.org.cn' in w["url"]][0]
stale = [w for w in case["web_fixture"] if 'divego.cn' in w["url"]][0]
assert official.get("error") and official["error"].startswith('HTTP 503')
assert stale.get("content") and stale["published_at"].startswith('2024')
assert '120' in stale["content"]
print(json.dumps({"expected_number": total}))
