# DISTILL-CANARY-a559f079 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '430e4dc7ec556b80d4e685d65fc6a07171c5eb910592ec51497b03576a765cf0', "fixture changed"
ls = files['store.log'].split('\n')
i = [k for k, l in enumerate(ls) if 'No space left' in l][0]
j = [k for k in range(i, i + 6) if 'removed' in ls[k]][0]
answers = [[ls[j].split(' from ')[1].split(' ')[0].rsplit('/', 1)[1]]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
