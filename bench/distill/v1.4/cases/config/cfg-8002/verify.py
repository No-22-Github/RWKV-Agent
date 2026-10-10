# DISTILL-CANARY-18c2ad2e : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("ledger-sync: consumes ledger events")
doc = files["docs/worker-config.md"].splitlines()
assert doc[0] == "# ledger-sync worker settings"
lib = [l for l in doc if l.startswith("- retry_backoff_ms:")][0].split("built into the ")[1].split(" ")[0]
for path in ("config/ledger-sync.toml", "config/env/production.toml"):
    assert "retry_backoff_ms" not in files[path]
print(json.dumps({"expected_string": lib}))
