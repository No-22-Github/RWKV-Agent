# DISTILL-CANARY-f7230c21 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["charts/README.md"].startswith("# Charts")
out = {}
for path, text in case["files"].items():
    if not path.endswith("Chart.yaml") or "/legacy/" in path:
        continue
    rows = text.splitlines()
    assert rows[1] == "version: 2.3.1" and rows[2] == "appVersion: 2.3.1", path
    out[path] = text.replace(chr(10) + "version: 2.3.1" + chr(10), chr(10) + "version: 2.4.0" + chr(10))
print(json.dumps({"files": out}))
