# WORKBANK-CANARY-a3f91c07 : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
rows = [
    json.loads(line)
    for line in case["files"]["telemetry/api-calls.jsonl"].splitlines()
    if line.strip()
]
print(json.dumps({"expected_number": sum(r["bytes_out"] for r in rows)}))
