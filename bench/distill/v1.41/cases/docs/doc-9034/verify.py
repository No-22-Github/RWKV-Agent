# DISTILL-CANARY-ea78ed41 : distillation case
import json, re
case = json.load(open("case.json"))
text = case["files"]["docs/CHANGELOG.md"]
assert text.startswith("# Changelog")
m = re.search(r"## (\d+\.\d+\.\d+)" + chr(10) + r"- Removed: the `--legacy-auth` flag", text)
print(json.dumps({"expected_string": m.group(1)}))
