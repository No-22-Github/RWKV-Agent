# DISTILL-CANARY-47111f49 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '51bc43c755c6aac2b2394d64b715d093b0079da2c722b498d667e3b25bf5701f', "fixture changed"
import collections
c=collections.Counter(l.split()[2][:2] for l in files['syslog.txt'].splitlines())
h,n=c.most_common(1)[0]
answers=[h+':00', str(n)]
print(json.dumps({"expected_number": float(answers[1])}, ensure_ascii=False))
