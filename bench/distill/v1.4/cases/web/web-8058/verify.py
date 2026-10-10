# DISTILL-CANARY-75949bcb : distillation case
import json
import re

case = json.load(open("case.json"))
off = [w for w in case["web_fixture"] if w["url"] == 'https://quillmark.example/releases'][0]["content"]
m = re.search('\\| (\\d\\.\\d) \\| LTS \\|', off)
assert m and m.group(1) == '6.0'
print(json.dumps({"expected_contains_any": ["Quillmark 6.0", "6.0 is the LTS", "6.0 LTS", "version 6.0", "6.0 (LTS)", "6.0"]}, ensure_ascii=False))
