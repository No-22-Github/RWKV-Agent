# DISTILL-CANARY-23253587 : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'import glob\n\ntotals = {}\nfor path in glob.glob("sales/**/*.csv", recursive=True):\n    with open(path, encoding="utf-8") as f:\n        next(f)\n        for line in f:\n            dish, qty = line.strip().split(",")\n            totals[dish] = totals.get(dish, 0) + int(qty)\nfor dish in sorted(totals):\n    print(dish, totals[dish])\n'
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
