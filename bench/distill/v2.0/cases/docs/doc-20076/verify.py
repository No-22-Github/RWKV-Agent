# DISTILL-CANARY-c42af0e7 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '85c7c1cb1dc6907aa648e8e018cc8478a450d35863e35192c894f5a7f4eb9dd7', "fixture changed"
m = re.search('2026-09-18,([^\\n,]+)', case["files"]['值班表.csv'])
assert m and m.group(1) == '李想'
draft = '# 值班提醒草稿\n\n李想你好，9 月 18 日你值班，别忘了交接班。\n'
assert all(s in draft for s in ['李想', '交接班'])
print(json.dumps({"files": {'通知草稿.md': draft}}, ensure_ascii=False))
