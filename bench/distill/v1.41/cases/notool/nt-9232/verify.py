# DISTILL-CANARY-8db232b2 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'data/sales.tsv': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"data/sales.tsv": "date\tregion\tamount\n2026-10-01\teast\t120\n2026-10-01\twest\t95\n2026-10-02\teast\t210\n"}
print(json.dumps({"expected_contains_any": ["awk"]}, ensure_ascii=False))
