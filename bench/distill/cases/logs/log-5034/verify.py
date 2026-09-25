# DISTILL-CANARY-60d7af3e : distillation case
import json

case = json.load(open("case.json"))
rows = [json.loads(line) for line in
        case["files"]["logs/dispatch.jsonl"].splitlines() if line.strip()]
assert len({row["ts"][:10] for row in rows}) == 1, "the journal covers more than one day"
assert {row["bay"] for row in rows} == {"B1", "B2"}, "the journal does not name both bays"
assert all(row["gross_kg"] > row["net_kg"] for row in rows), \
    "a record does not show the pallets weighed off"
print(json.dumps({"expected_number": sum(row["net_kg"] for row in rows)}))
