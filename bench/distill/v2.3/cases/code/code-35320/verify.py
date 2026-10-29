# DISTILL-CANARY-36ac1441 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'dcb33401f2e993751cc62680b93a78b4df485de951eb9a844b2f320183978320', "fixture changed"
OPS = json.loads('[["sub", ".ci/pipeline-build.yml", "        run: npm ci\\n", "        run: npm ci\\n      - name: Lint\\n        run: npm run lint\\n        env:\\n          CI: true\\n"], ["sub", ".ci/pipeline-build.yml", "name: build\\non:", "name: build-and-pack\\non:"]]')
end = dict(files)
for op in OPS:
    kind, path = op[0], op[1]
    if kind == "sub":
        assert end[path].count(op[2]) == 1, (path, op[2])
        end[path] = end[path].replace(op[2], op[3])
    elif kind == "set":
        end[path] = op[2]
    else:
        t = end[path]
        end[path] = (t if t.endswith("\n") or not t else t + "\n") + op[2]
print(json.dumps({"files": {p: t for p, t in end.items() if files.get(p) != t}}, ensure_ascii=False))
