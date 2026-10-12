# DISTILL-CANARY-267e8743 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'conf/site.conf': 7}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"conf/site.conf": "# main site\nserver {\n    listen 80;\n\n    # static files\n    root /srv/www;\n}\n"}
print(json.dumps({"expected_contains_any": ["sed"]}, ensure_ascii=False))
