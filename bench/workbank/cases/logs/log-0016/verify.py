# WORKBANK-CANARY-2d68b3f1 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
rows = [
    json.loads(line)
    for line in case["files"]["telemetry/edge-requests.jsonl"].splitlines()
    if line.strip()
]


def to_ms(value):
    value = value.strip()
    if value.endswith("ms"):
        return float(value[:-2])
    if value.endswith("s"):
        return float(value[:-1]) * 1000.0
    raise ValueError("unrecognized elapsed value: %r" % value)


count = 0
for record in rows:
    elapsed = record.get("elapsed")
    if elapsed is None or elapsed == "":
        # No elapsed value: the request ran past the collector window.
        count += 1
    elif to_ms(elapsed) > 1000.0:
        count += 1
print(json.dumps({"expected_number": count}))
