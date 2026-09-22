# WORKBANK-CANARY-5be2d84f : bank artifact, excluded from training corpora
import json

case = json.load(open("case.json"))
rows = [
    json.loads(line)
    for line in case["files"]["telemetry/transcode-jobs.jsonl"].splitlines()
    if line.strip()
]
times = [
    r["render_ms"]
    for r in rows
    if isinstance(r.get("render_ms"), (int, float)) and not isinstance(r.get("render_ms"), bool)
]
print(json.dumps({"expected_number": sum(times) / len(times)}))
