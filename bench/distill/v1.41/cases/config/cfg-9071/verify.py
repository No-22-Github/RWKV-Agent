# DISTILL-CANARY-4a83afa8 : distillation case
import json
case = json.load(open("case.json"))
assert case["files"]["deploy/README.md"].startswith("# Deploy configs")
assert "ACCESS_LOG_LEVEL is audited separately" in case["files"]["deploy/README.md"]
out = {}
for path, text in case["files"].items():
    if not path.endswith("app.env") or "/_example/" in path:
        continue
    rows = text.splitlines()
    assert rows[1] == "LOG_LEVEL=debug" and rows[2] == "ACCESS_LOG_LEVEL=debug", path
    out[path] = text.replace(chr(10) + "LOG_LEVEL=debug" + chr(10), chr(10) + "LOG_LEVEL=info" + chr(10))
print(json.dumps({"files": out}))
