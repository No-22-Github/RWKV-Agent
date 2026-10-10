# DISTILL-CANARY-ea6aadf3 : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'SHELVES = 8\n\ntotal = 0\nfor number in range(1, SHELVES + 1):\n    with open(f"stock/shelf-{number}.txt", encoding="utf-8") as f:\n        total += int(f.read().strip())\nprint(f"total {total}")\n'
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
