# DISTILL-CANARY-714298ec : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 24
assert case["files"]['app/README.md'].startswith('# app')
assert 'old_logger_test_helper is an unrelated test helper' in case["files"]['app/README.md']
FINAL = json.loads(r'''{"app/api/handlers.py": "from app.logging import new_logger\n\nnew_logger.info(\"api start\")\n", "app/db/session.py": "from app.logging import new_logger\n\nnew_logger.info(\"db start\")\nfrom app.testing import old_logger_test_helper\n", "app/cache/redis.py": "from app.logging import new_logger\n\nnew_logger.info(\"cache start\")\n"}''')
for path, text in FINAL.items():
    assert case["expect"]["files"][path]["equals"] == text, path
for path, rule in {"app/jobs/nightly.py": 1, "app/jobs/weekly.py": 1, "app/compat/shim.py": 1, "app/README.md": 1}.items():
    assert case["expect"]["files"][path] == {"unchanged": True}, path
state = dict(case["files"])
state.update(FINAL)
print(json.dumps({"files": FINAL}, ensure_ascii=False))
