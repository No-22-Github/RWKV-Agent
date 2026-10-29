# DISTILL-CANARY-9f408265 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '394dabae51b9874db7c3a205976b9401bab95c758386dd075077e5e45549d0de', "fixture changed"
OPS = json.loads('[["sub", "release/checklist-v7.md", "- [ ] Freeze main branch", "- [x] Freeze main branch"], ["sub", "release/checklist-v7.md", "- [ ] Run full regression", "- [x] Run full regression"], ["sub", "release/checklist-v7.md", "- [ ] Tag the release\\n", "- [ ] Tag the release\\n- [ ] Publish the release notes\\n"], ["append", "release/checklist-v7.md", "\\nNote: regression passed on 2026-09-16.\\n"]]')
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
