# DISTILL-CANARY-caad4a18 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'README.txt': 1}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"README.txt": "Photo mirror notes: originals live in ~/photos, the backup disk mounts at /mnt/backup.\n"}
print(json.dumps({"expected_contains_any": ["rsync"]}, ensure_ascii=False))
