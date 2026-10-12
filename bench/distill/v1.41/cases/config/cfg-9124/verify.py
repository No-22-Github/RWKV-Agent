# DISTILL-CANARY-ebd4b20c : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 24
assert case["files"]["envs/README.md"].startswith("# Environment files")
assert "REPLICA_HOST moves next month" in case["files"]["envs/README.md"]
want = {"prod": "db-new.internal", "qa": "db-new.internal", "staging": "db-old.internal", "dev": "db-dev.internal"}
out = {}
for e, host in want.items():
    path = "envs/%s/db.env" % e
    rows = case["files"][path].splitlines()
    assert rows[0] == "DB_HOST=db-old.internal" and rows[2] == "REPLICA_HOST=db-old.internal", path
    out[path] = case["files"][path].replace("DB_HOST=db-old.internal", "DB_HOST=" + host)
assert case["files"]["envs/_template/db.env"].splitlines()[0] == "DB_HOST=db-old.internal"
print(json.dumps({"files": out}))
