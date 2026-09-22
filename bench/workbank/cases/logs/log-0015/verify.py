# WORKBANK-CANARY-c7104ea2 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
rows = [
    json.loads(line)
    for line in case["files"]["telemetry/label-print-jobs.jsonl"].splitlines()
    if line.strip()
]


def to_ms(value):
    value = value.strip()
    if value.endswith("ms"):
        return float(value[:-2])
    if value.endswith("s"):
        return float(value[:-1]) * 1000.0
    raise ValueError("unrecognized elapsed value: %r" % value)


print(json.dumps({"expected_number": sum(to_ms(r["elapsed"]) for r in rows)}))
