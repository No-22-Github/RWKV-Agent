# DISTILL-CANARY-2eedf4b3 : distillation case
import hashlib
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == 'ca0842d7cd92147bf776836e782f36a301334051d2d7b6a43bbc483dfc3f82c4'
ans = int(re.search(r"单车:\n  人数上限: (\d+)", files["课程/团课.yaml"]).group(1))
assert ans == 18
print(json.dumps({"expected_contains_any": ['18 人', '18 位', '18 个人', '18人', '18位', '18个人']}, ensure_ascii=False))
