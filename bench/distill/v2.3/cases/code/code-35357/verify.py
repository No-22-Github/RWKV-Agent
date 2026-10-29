# DISTILL-CANARY-b312eabd : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '404e334764f32f0b67cdf43109be46cac4eb6da96e144ce018aca2950b759369', "fixture changed"
OPS = json.loads('[["set", "deploy/env-staging.sample", "API_URL=https://staging.hengtai-logistics.cn\\nLOG_LEVEL=debug\\n"], ["append", "deploy/env-staging.sample", "CACHE_TTL=120\\n"]]')
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
