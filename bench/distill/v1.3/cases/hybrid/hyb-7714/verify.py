# DISTILL-CANARY-f35c6b90 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["workshop/varnish-2026-09.log"].splitlines()
if not lines or not lines[0].startswith("#"):
    raise SystemExit("fixture shape changed: log header line missing")
def faults(prefix):
    n = 0
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 4 and parts[2] == "fault" and parts[1].startswith(prefix):
            n += 1
    return n
def clouding_batches(prefix):
    out = set()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 4 and parts[2] == "fault" and parts[3] == "clouding" and parts[1].startswith(prefix):
            out.add(parts[1])
    return out
out = {
    "expected_number": faults("V-3"),
    "expected_turn_3": len(clouding_batches("V-3")),
    "expected_turn_4": sum(1 for line in lines[1:]
                           for p in [line.split()]
                           if len(p) >= 4 and p[2] == "fault" and p[3] == "clouding"
                           and p[1].startswith("V-2")),
}
print(json.dumps(out))
