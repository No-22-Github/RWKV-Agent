# DISTILL-CANARY-98dc5e4c : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'PAGE = 2\nPAGE_SIZE = 10\n\nwith open("catalog.txt", encoding="utf-8") as f:\n    items = f.read().splitlines()\nstart = (PAGE - 1) * PAGE_SIZE\nfor item in items[start:start + PAGE_SIZE]:\n    print(item)\n'
files = dict(case["files"])
files.update(run.get("hidden_files", {}))
files[run["path"]] = FIXED
with tempfile.TemporaryDirectory() as d:
    for p, c in files.items():
        t = os.path.join(d, p)
        os.makedirs(os.path.dirname(t), exist_ok=True)
        with open(t, "w", encoding="utf-8", newline="") as f:
            f.write(c)
    r = subprocess.run(["python3", "-I", "-S", os.path.join(d, run["path"])], cwd=d, capture_output=True,
                       text=True, encoding="utf-8", timeout=10)
    if r.returncode != 0:
        raise SystemExit(r.stderr)
print(json.dumps({"expected_stdout": r.stdout.rstrip("\n")}, ensure_ascii=False))
