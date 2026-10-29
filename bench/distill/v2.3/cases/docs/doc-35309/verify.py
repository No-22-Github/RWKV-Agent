# DISTILL-CANARY-e7aac704 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9131359151b2e298383a0ea15dfb947a2aca00b35efb8f6c8e4cdd5af44bbe49', "fixture changed"
OPS = json.loads('[["sub", "docs/policies/remote-work-policy.md", "Last reviewed: 2025-11-04", "Last reviewed: 2026-09-16"], ["sub", "docs/policies/remote-work-policy.md", "Employees who have completed their first 90 days may work remotely\\nup to two days per week. Managers approve exceptions\\nin writing. Roles that require on-site equipment are excluded.\\n", "Employees who have completed their first 60 days may work remotely\\nup to three days per week. Team leads approve exceptions\\nin writing, and HR is copied on every approval.\\nRoles that require on-site equipment are excluded.\\n"]]')
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
