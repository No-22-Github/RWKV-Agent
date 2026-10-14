# DISTILL-CANARY-31722e21 : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '36ec9682d1c37cbc7b32af1f5477b96ed2bfb84ee72595bb4116c558475f3e07', "fixture changed"
m = re.search('(Thursday 10:30)', case["files"]['call-notes.md'])
assert m and m.group(1) == 'Thursday 10:30'
draft = 'Reminder: call with Meridian on Thursday 10:30.\n'
assert all(s in draft for s in ['Thursday', '10:30', 'Meridian'])
print(json.dumps({"files": {'reminder.md': draft}}, ensure_ascii=False))
