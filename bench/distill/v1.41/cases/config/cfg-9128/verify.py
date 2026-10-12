# DISTILL-CANARY-82c72215 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 32
assert case["files"]["features/README.md"].startswith("# Feature flags")
assert "new_ui_v2 is an experiment" in case["files"]["features/README.md"]
out = {}
for n in ["web", "mobile", "admin", "billing", "payments", "search"]:
    path = "features/%s.toml" % n
    rows = case["files"][path].splitlines()
    assert rows == ["[flags]", "new_ui = false", "new_ui_v2 = false", "beta_search = false"], path
    on = n not in ("billing", "payments")
    rows[1] = "new_ui = true" if on else "new_ui = false"
    if n == "search":
        rows[3] = "beta_search = true"
    out[path] = chr(10).join(rows) + chr(10)
assert case["files"]["features/frozen/legacy.toml"].splitlines()[1] == "new_ui = false"
print(json.dumps({"files": out}))
