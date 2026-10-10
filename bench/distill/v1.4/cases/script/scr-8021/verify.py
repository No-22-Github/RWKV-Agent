# DISTILL-CANARY-6d60c33d : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'import glob\n\nrows = []\nfor path in glob.glob("invoices/*.csv"):\n    with open(path, encoding="utf-8") as f:\n        next(f)\n        for line in f:\n            number, amount = line.strip().split(",")\n            rows.append((number, amount))\nrows.sort(key=lambda row: int(row[1]), reverse=True)\nfor number, amount in rows[:5]:\n    print(number, amount)\n'
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
