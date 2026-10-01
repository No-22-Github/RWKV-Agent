# DISTILL-CANARY-8c4ce690 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/purge-executed.log"].splitlines()

sent = []
for line in lines:
    if " SENT " not in line:
        continue
    f = line.split()
    sent.append((f[0] + " " + f[1], f[2], f[4]))

ids = {p for _, p, _ in sent}
covers = {p for _, p, path in sent if path.startswith("path=/assets/covers/")}
kept = {p for _, p, path in sent
        if path.startswith("path=/assets/covers/") or not path.startswith("path=/assets/marketing/")}
kept = {p for p in ids if p not in {q for _, q, path in sent if path.startswith("path=/assets/marketing/")}}
minutes = {}
for ts, _, _ in sent:
    m = ts.split(" ")[1][:5]
    minutes[m] = minutes.get(m, 0) + 1
peak = sorted(minutes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

forms = ["%d purge" % len(ids), "%d purge" % len(covers), "%d purge" % len(kept), peak]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
