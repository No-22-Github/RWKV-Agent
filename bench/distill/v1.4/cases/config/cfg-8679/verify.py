# DISTILL-CANARY-043abee3 : distillation case
import json
import re

case = json.load(open("case.json"))
files = case["files"]
basis = files['tickets/CHG-4410.txt']
assert files["README.md"].startswith('Access swi')
assert basis.startswith('Change: move')
m = re.search('to VLAN (\\d+) \\(guest wifi AP\\)', basis, re.M)
val = m.group(1)
src = files['switch/access-ports.cfg']
old = 'description AP-lobby\n switchport access vlan 20'
assert src.count(old) == 1
new = src.replace(old, 'description AP-lobby\n switchport access vlan {V}'.replace("{V}", val))
print(json.dumps({"files": {'switch/access-ports.cfg': new}}, ensure_ascii=False))
