# DISTILL-CANARY-c91ef3f4 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a899e8a3756abe648fa0a44bcedf4a1b8e1c3771256e31adfdecc96c5a0121f5', "fixture changed"
OPS = json.loads('[["sub", "docs/runbooks/db-failover-runbook.md", "4. Repoint the connection alias.\\n5. Verify writes land on the new primary.\\n6. Post the incident summary.\\n", "4. Drain in-flight batch jobs.\\n5. Repoint the connection alias.\\n6. Verify writes land on the new primary.\\n7. Post the incident summary.\\n"]]')
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
