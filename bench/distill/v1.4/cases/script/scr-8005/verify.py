# DISTILL-CANARY-9fc036ec : distillation case
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = 'import glob\n\ntotals = {}\nfor path in sorted(glob.glob("jobs/*/**/words.csv", recursive=True)):\n    lang = path.split("/")[1]\n    with open(path, encoding="utf-8") as f:\n        for line in f.read().splitlines()[1:]:\n            words = int(line.split(",")[1])\n            totals[lang] = totals.get(lang, 0) + words\nfor lang in sorted(totals):\n    print(lang, totals[lang])\n'
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
