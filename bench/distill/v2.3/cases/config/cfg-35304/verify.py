# DISTILL-CANARY-d88ca7b1 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'bf51f4771a849beec7f7f5009049efe3d5d25df5366178cfcd2a83ac28630edb', "fixture changed"
OPS = json.loads('[["sub", "infra/nginx-edge-upstream.conf", "    server 10.20.4.11:9100 max_fails=2;\\n    server 10.20.4.12:9100 max_fails=2;\\n    server 10.20.4.13:9100 backup;\\n", "    server 10.20.7.21:9100 max_fails=3;\\n    server 10.20.7.22:9100 max_fails=3;\\n    server 10.20.7.23:9100 max_fails=3;\\n    server 10.20.7.24:9100 backup;\\n"]]')
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
