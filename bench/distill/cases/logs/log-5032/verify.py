# DISTILL-CANARY-7f4c81aa : distillation case
import json

case = json.load(open("case.json"))
rows = [json.loads(line) for line in
        case["files"]["logs/crusher-throughput.jsonl"].splitlines() if line.strip()]
assert sorted({row["day"] for row in rows}) == ["2026-08-03", "2026-08-04"], \
    "the export does not cover the two production days"
assert {row["belt"] for row in rows} == {"B1", "B2"}, "the journal does not name both belts"
print(json.dumps({"expected_number": sum(
    row["tonnes"] for row in rows if row["belt"] == "B1" and row["day"] == "2026-08-03")}))
