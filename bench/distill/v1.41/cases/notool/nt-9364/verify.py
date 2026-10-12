# DISTILL-CANARY-45389ced : distillation case
import json
case = json.load(open("case.json"))
LINES = {'logs/access.log': 4}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
assert case["files"] == {"logs/access.log": "10.0.0.1 - - [12/Oct/2026:10:00:01 +0000] \"GET /index.html HTTP/1.1\" 200 512\n10.0.0.2 - - [12/Oct/2026:10:00:02 +0000] \"GET /old-page HTTP/1.1\" 404 128\n10.0.0.3 - - [12/Oct/2026:10:00:03 +0000] \"GET /api/v1/items HTTP/1.1\" 200 2048\n10.0.0.2 - - [12/Oct/2026:10:00:04 +0000] \"GET /missing.png HTTP/1.1\" 404 128\n"}
print(json.dumps({"expected_contains_any": ["$9"]}, ensure_ascii=False))
