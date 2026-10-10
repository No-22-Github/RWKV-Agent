# DISTILL-CANARY-bd9c4002 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]['充气/9月充气台账.csv'])))
picked = [r for r in rows if r['通道'] == '俱乐部气瓶']
assert len(picked) > 1
total = sum(int(r['瓶数']) for r in picked)
official = [w for w in case["web_fixture"] if 'lanjiao-dive.cn' in w["url"]][0]
stale = [w for w in case["web_fixture"] if 'bbs.haiyu.cn' in w["url"]][0]
assert official.get("error") and official["error"].startswith('Connection timed out')
assert stale.get("content") and stale["published_at"].startswith('2025')
assert '18' in stale["content"]
print(json.dumps({"expected_number": total}))
