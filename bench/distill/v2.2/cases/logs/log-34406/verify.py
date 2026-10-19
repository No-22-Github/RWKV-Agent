# DISTILL-CANARY-84cfa84c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '352a1657a98c46b8e50d9011b21861540f78be773cb931ddbccee3edddc52425', "fixture changed"
import json
ls = [l for l in files['events.jsonl'].split('\n') if l]
i = [k for k, l in enumerate(ls) if json.loads(l)['lvl'] == 'error'][0]
d = json.loads(ls[i])
answers = [[str(i + 1)], [d['svc'], d['msg']]]

print(json.dumps({"expected_number": float(answers[0][0])}))
