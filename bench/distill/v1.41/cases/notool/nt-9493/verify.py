# DISTILL-CANARY-77e650c4 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["inode", "pointer", "dangling", "broken", "path", "shortcut"]}, ensure_ascii=False))
