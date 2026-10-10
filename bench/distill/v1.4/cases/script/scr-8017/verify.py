# DISTILL-CANARY-53d74b42 : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'import glob\n\ncounts = {}\nfor path in glob.glob("deliveries/*.csv"):\n    with open(path, encoding="utf-8", newline="") as f:\n        lines = f.read().splitlines()[1:]\n    for line in lines:\n        if not line:\n            continue\n        region, status = line.split(",")\n        if status == "OK":\n            counts[region] = counts.get(region, 0) + 1\nfor region in sorted(counts):\n    print(f"{region} {counts[region]}")\n'
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
