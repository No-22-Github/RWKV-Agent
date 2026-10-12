# DISTILL-CANARY-ff448428 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": ["cp -a", "cp -p", "cp -rp", "cp -pr", "cp -r", "rsync", "-a"]}, ensure_ascii=False))
