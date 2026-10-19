# DISTILL-CANARY-1f21b453 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '993ab4f644090eede17e9a44b919dadf00e56dfcda55e279b079beeb7d28b9d4', "fixture changed"
import csv, io, collections
rows = list(csv.DictReader(io.StringIO(files['readings.csv']), delimiter=';'))
cents = lambda x: round(float(x) * 100)
m = max(rows, key=lambda x: float(x['temp_c']))
answers = [[m['sensor']], [m['ts']]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
