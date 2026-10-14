# DISTILL-CANARY-71f79da9 : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'import glob\n\nwith open("config/allow.txt", encoding="utf-8", newline="") as f:\n    allowed = set(f.read().splitlines())\n\ncounts = {}\nfor path in glob.glob("events/*.log"):\n    with open(path, encoding="utf-8") as f:\n        for line in f:\n            user = line.split()[1]\n            if user in allowed:\n                counts[user] = counts.get(user, 0) + 1\nfor user in sorted(counts):\n    print(f"{user} {counts[user]}")\n'
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
