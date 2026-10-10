# DISTILL-CANARY-b67e09c3 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import re
text = files["notices/notice-0618.txt"]
facts = [re.search(r"NC-\d+", text).group(0),
         re.search(r"自 (\d{4}-\d{2}-\d{2}) 起", text).group(1),
         re.search(r"上限调整为 (\d+) 行", text).group(1)]
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
