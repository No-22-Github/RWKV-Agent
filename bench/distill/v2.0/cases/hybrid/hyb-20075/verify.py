# DISTILL-CANARY-08e3504a : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '94cd75b44427c63ba83ccf75ee8f5a770d37b151ff0a8e0750970639381201e6', "fixture changed"
m = re.search('(2026-09-24 14:00)', case["files"]['meeting.md'])
assert m and m.group(1) == '2026-09-24 14:00'
draft = '日程邀请\n时间：2026-09-24 14:00\n地点：3 号会议室\n事项：下次评审\n'
assert all(s in draft for s in ['2026-09-24 14:00', '3 号会议室'])
print(json.dumps({"files": {'invite.txt': draft}}, ensure_ascii=False))
