# DISTILL-CANARY-e386bfb0 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '18fdc56d224f8b630312fb11b756c5f0f5039d5cb814f791e7bfa84fbc20f0a5', "fixture changed"
OPS = json.loads('[["sub", "docs/partner-integration-guide.md", "## Legacy Webhooks\\n\\nWebhooks v1 are retired. Existing subscribers receive no new events.\\n\\n", ""]]')
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
