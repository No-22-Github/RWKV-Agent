# DISTILL-CANARY-a2386ebd : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'import glob\n\nsums = {}\ncounts = {}\nfor path in glob.glob("latency/*.csv"):\n    with open(path, encoding="utf-8") as f:\n        next(f)\n        for line in f:\n            api, ms = line.strip().split(",")\n            sums[api] = sums.get(api, 0) + int(ms)\n            counts[api] = counts.get(api, 0) + 1\nfor api in sorted(sums):\n    avg_seconds = sums[api] / counts[api] / 1000\n    print(f"{api} {avg_seconds:.2f} 秒")\n'
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
