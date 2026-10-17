# DISTILL-CANARY-9cf69123 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'e09f891599aa0075712265c9d0febc005b76001dec7f614ba59884bd6ed81c1b', "fixture changed"
import collections
g=collections.defaultdict(list)
for p,t in files.items(): g[t].append(p)
d=[v for v in g.values() if len(v)>1]
assert len(d)==1
answers=['IMG_2041.txt']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
