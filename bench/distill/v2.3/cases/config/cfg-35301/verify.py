# DISTILL-CANARY-7f558e69 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '93706cd0b3663b6539572d016c14c4f61815a61b0f6f85ed9552131a4f377f11', "fixture changed"
OPS = json.loads('[["sub", "deploy/harbor-gateway.yaml", "  tls: true\\n", "  tls: true\\nrate_limit:\\n  requests_per_minute: 600\\n  burst: 120\\n  key: client_ip\\n"], ["sub", "deploy/harbor-gateway.yaml", "connect_ms: 800", "connect_ms: 500"]]')
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
