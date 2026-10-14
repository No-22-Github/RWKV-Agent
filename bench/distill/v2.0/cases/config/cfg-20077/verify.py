# DISTILL-CANARY-08dac222 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '57b424ef92785134fafd2e8c21df36e449d1833ccd8943e985f62799324145fa', "fixture changed"
m = re.search('(ERR-4410)', case["files"]['incident.log'])
assert m and m.group(1) == 'ERR-4410'
m = re.search('\\((eu-west)\\)', case["files"]['incident.log'])
assert m and m.group(1) == 'eu-west'
draft = 'Subject: Gateway timeout ERR-4410\nRegion: eu-west\nChecks failing since 09:41.\n'
assert all(s in draft for s in ['ERR-4410', 'eu-west'])
print(json.dumps({"files": {'ticket.md': draft}}, ensure_ascii=False))
