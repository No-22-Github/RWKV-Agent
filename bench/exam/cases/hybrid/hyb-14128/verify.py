# EXAM-CANARY-b12c1ea4 : exam gap-fill case
import json

case = json.load(open("case.json", encoding="utf-8"))
pkg = case["files"]["package.json"].replace("2.7.4", "2.8.0")
chg = case["files"]["CHANGELOG.md"].replace("# Changelog\n\n", "# Changelog\n\n## 2.8.0 - minor release\n\n")
print(json.dumps({"files": {"package.json": pkg, "CHANGELOG.md": chg}}))
