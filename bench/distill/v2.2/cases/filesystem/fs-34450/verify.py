# DISTILL-CANARY-e8d1a29a : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '35259ccf6d0a4f0b87c8e406494e2e73251c6fd5206368c69a77c4fcd21799e8', "fixture changed"
import collections
h = [p for p in files if 'TODO' in files[p]]
c = collections.Counter(p.split('/')[1] for p in h)
assert c.most_common(2)[1][1] < c.most_common(1)[0][1] - 3
answers = [len(h), [c.most_common(1)[0][0]]]

print(json.dumps({"expected_string": answers[1][0]}, ensure_ascii=False))
