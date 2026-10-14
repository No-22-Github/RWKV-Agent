# DISTILL-CANARY-de43855e : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'import os\nfrom collections import Counter\n\ncounts = Counter()\nfor root, _dirs, names in os.walk("logs"):\n    for name in names:\n        if not name.endswith(".log"):\n            continue\n        for line in open(os.path.join(root, name), encoding="utf-8"):\n            parts = line.split()\n            if len(parts) > 3 and parts[3] == "ERROR":\n                counts[parts[2]] += 1\nfor svc in sorted(counts):\n    print(f"{svc}: {counts[svc]}")\n'
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
