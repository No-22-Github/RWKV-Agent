# DISTILL-CANARY-b9ab2b6f : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["docs/pgbouncer.md"].startswith("pgbouncer runs on each app host and listens on 6432")
assert files["README.md"].startswith("Orders service")
src = files["app/settings.py"]
old = '"PORT": 5432,  # direct to postgres'
assert src.count(old) == 1
print(json.dumps({"files": {"app/settings.py": src.replace(old, '"PORT": 6432,  # pgbouncer')}}))
