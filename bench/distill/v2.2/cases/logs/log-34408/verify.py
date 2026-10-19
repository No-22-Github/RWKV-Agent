# DISTILL-CANARY-a802d6bf : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '29be0da49340b7df2747a6e57cb30352274c9480b7096e20d69c88262b68ab68', "fixture changed"
import re
best = max(((int(re.search(r'duration=(\d+)ms', l).group(1)), re.search(r'query=(q-\d+)', l).group(1)) for l in files['slowquery.log'].split('\n') if l))
answers = [[best[1], str(best[0])]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
