# DISTILL-CANARY-d44cb860 : distillation case
import json

case = json.load(open("case.json"))


def errs(text):
    out = []
    for line in text.splitlines():
        if not line.strip() or "cache=ERR" not in line:
            continue
        f = line.split()
        ts = f[0] + " " + f[1]
        origin = f[6].split("=")[1]
        out.append((ts, origin))
    return out


hq_text = case["files"]["logs/cdn-edge-hq.log"]
bj_text = case["files"]["logs/cdn-edge-bj.log"]
hq = [e for e in errs(hq_text) if "2026-09-23 12:00:00" <= e[0] < "2026-09-23 18:00:00"]
bj = [e for e in errs(bj_text) if "2026-09-23 12:00:00" <= e[0] < "2026-09-23 18:00:00"]

total = len(hq) + len(bj)
fifties = sum(1 for _, o in hq + bj if o == "503")
hq_kept = [e for e in hq if not ("2026-09-23 15:00:00" <= e[0] < "2026-09-23 15:30:00")]

forms = [
    "%d 次" % total,
    "%d 次" % fifties,
    "%d 次" % len(hq),
    "%d 次" % len(hq_kept),
]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
