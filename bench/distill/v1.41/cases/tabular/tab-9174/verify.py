# DISTILL-CANARY-a500f991 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'data/visits.csv': 521, 'queries/top_city.sql': 3}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
sql = case["files"]["queries/top_city.sql"]
assert sql.splitlines()[0] == ".mode csv"
assert "WHERE status = 'completed' GROUP BY city ORDER BY n DESC LIMIT 1;" in sql
rows = case["files"]["data/visits.csv"].splitlines()
assert rows[0] == "visit_id,city,status"
counts = {}
for row in rows[1:]:
    vid, city, status = row.split(",")
    if status == "completed":
        counts[city] = counts.get(city, 0) + 1
ranked = sorted(counts.items(), key=lambda kv: -kv[1])
assert ranked[0][1] - ranked[1][1] >= 5
print(json.dumps({"expected_string": ranked[0][0]}))
