# DISTILL-CANARY-51c7e3a9 : p13 holdout (eval-only)
import json

case = json.load(open("case.json", encoding="utf-8"))
files = dict(case["files"])
files.update(case["expect"]["run"]["hidden_files"])
names = sorted(
    n for n in files
    if n.startswith("returns/") and n.endswith(".jsonl") and n.count("/") == 1
)
out = []
for name in names:
    count = sum(1 for line in files[name].splitlines() if line.strip())
    out.append("%s: %d" % (name.rsplit("/", 1)[1], count))
snapshot = {
    path: case["files"][path]
    for path in (
        "README.md",
        "returns/week-1.jsonl",
        "returns/week-2.jsonl",
        "returns/archive/2026-08-w4.jsonl",
    )
}
print(json.dumps({"expected_stdout": "\n".join(out), "files": snapshot}))
