# DISTILL-CANARY-a10156cf : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'from pathlib import Path\n\ncounts = {}\nfor path in Path("visits").rglob("*.txt"):\n    for line in path.read_text(encoding="utf-8").splitlines():\n        if not line.strip():\n            continue\n        doctor = line.split("|")[1].strip()\n        counts[doctor] = counts.get(doctor, 0) + 1\nfor doctor in sorted(counts):\n    print(f"{doctor}={counts[doctor]}")\n'
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
