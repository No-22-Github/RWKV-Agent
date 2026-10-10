# DISTILL-CANARY-35c97c52 : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'import glob\n\nsums = {}\ncounts = {}\nfor path in glob.glob("sensors/*.csv"):\n    with open(path, encoding="utf-8") as f:\n        next(f)\n        for line in f:\n            room, fahrenheit = line.strip().split(",")\n            celsius = (int(fahrenheit) - 32) * 5 / 9\n            sums[room] = sums.get(room, 0) + celsius\n            counts[room] = counts.get(room, 0) + 1\nfor room in sorted(sums):\n    print(f"{room} {sums[room] / counts[room]:.1f}")\n'
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
