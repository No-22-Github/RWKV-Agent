# DISTILL-CANARY-f469cc05 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '05327b3c403ed934f990487c4d7e2cc74a170be7efa35774f5c77c601f47b1d9', "fixture changed"
OPS = json.loads('[["sub", "services/ledger-api.json", "      \\"method\\": \\"GET\\"\\n    }\\n  ]", "      \\"method\\": \\"GET\\"\\n    },\\n    {\\n      \\"path\\": \\"/entries/export\\",\\n      \\"method\\": \\"GET\\"\\n    }\\n  ]"], ["sub", "services/ledger-api.json", "\\"version\\": \\"1.4.0\\"", "\\"version\\": \\"1.5.0\\""]]')
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
