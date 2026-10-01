# DISTILL-CANARY-d92b605e : p13 holdout (eval-only)
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
files = dict(case["files"])
files.update(case["expect"]["run"]["hidden_files"])
names = sorted(n for n in files if re.search(r"floor[1-9]\.csv$", n))
out = []
for name in names:
    seen = set()
    total = 0
    for line in files[name].splitlines():
        line = line.strip()
        if not line or line in seen:
            continue
        seen.add(line)
        total += int(line.rsplit(",", 1)[1])
    out.append("%s: %d" % (name.rsplit("/", 1)[1], total))
print(json.dumps({"expected_stdout": "\n".join(out)}))
