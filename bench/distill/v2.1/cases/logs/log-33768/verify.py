# DISTILL-CANARY-b46983e7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8f0c8bcb5b9432118a18da69b7c0cbe333ff4b246b576a51e0b331fd859b2b9f', "fixture changed"
import csv,io
rows=list(csv.DictReader(io.StringIO(files['activity.csv'])))
answers=[str(sum(1 for x in rows if x['user']=='ben' and x['action']=='download')), str(len({x['user'] for x in rows if x['action']=='download'}))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
