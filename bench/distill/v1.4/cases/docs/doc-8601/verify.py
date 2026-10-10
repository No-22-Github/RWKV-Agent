# DISTILL-CANARY-3df37905 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "RELEASE-3.8.md", "start": 9, "end": 11, "new": ["- Export wizard fails on files over 4 GB", "- Tray icon blurry on 4K displays (fixed in 3.8.1)", "- Dark theme flicker fixed in 3.8"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
