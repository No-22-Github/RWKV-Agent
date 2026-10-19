# DISTILL-CANARY-26824ed3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '705eaac19c34e170177c50c8fc5c8770f097e9aaf4bbdebb9aa2f5b16eb2de27', "fixture changed"
import collections
ls = [l for l in files['logs/mesh-sidecar-0911.log'].split('\n') if ' ERROR ' in l]
c = collections.Counter(l.split(': ', 1)[1] for l in ls)
m, k = c.most_common(1)[0]
answers = [[m, str(k)]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
