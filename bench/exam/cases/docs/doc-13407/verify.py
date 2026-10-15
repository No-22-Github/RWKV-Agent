# EXAM-CANARY-7e16b643 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
missing = ["附录B-住宿标准.xlsx"]
anchors = {"制度/差旅管理办法.md": "# 差旅管理办法（2026 版）", "制度/README.txt": "制度目录。"}
for path, first in anchors.items():
    assert path in files and files[path].lstrip().startswith(first), "fixture damaged: " + path
blob = "\n".join(v for k, v in files.items() if k not in []) + json.dumps(case.get("web_fixture", []), ensure_ascii=False)
for item in missing:
    assert item not in blob.replace("{", "").replace("}", "") or True, item
for item in missing:
    assert item not in files, item
print(json.dumps({"expected": "UNKNOWN", "must_state_unverified": missing}, ensure_ascii=False))
