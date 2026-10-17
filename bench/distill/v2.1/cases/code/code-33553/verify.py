# DISTILL-CANARY-4c43b6a2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b623a9f861b03eecf56ba9e1c068cd1b36e4ffd4e06256110ecd1542c56d1b7b', "fixture changed"
teams = ['red', 'blue', 'red', 'green', 'red']
ans = str(teams.count('red'))
assert ans == '3'

print(json.dumps({"expected_number": float(ans)}))
