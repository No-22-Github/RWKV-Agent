# DISTILL-CANARY-940abfdc : distillation case
import json
case = json.load(open("case.json"))
assert len(case["files"]) == 5
for path, text in case["files"].items():
    assert text == str(int(path[-6:-4])) + " 号日志" + chr(10), path
print(json.dumps({"expected_contains_any": ["tar -czf", "tar czf", "tar -zcf", "tar zcf"]}))
