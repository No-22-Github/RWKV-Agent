# DISTILL-CANARY-1d1ccb97 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'请求/api-0912.log': 103, '请求/api-0913.log': 120, '请求/api-0914.log': 117, 'tools/slowest_get.pl': 11}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
script = case["files"]["tools/slowest_get.pl"]
assert "next unless $f[1] eq 'GET';" in script
best = (0, None)
tie = False
logs = 0
for path, text in case["files"].items():
    if not path.startswith("请求/"):
        continue
    logs += 1
    for row in text.splitlines():
        t, method, p, ms = row.split(" ")
        if method == "GET":
            if int(ms) == best[0]:
                tie = True
            if int(ms) > best[0]:
                best, tie = (int(ms), p), False
assert logs == 3 and not tie
print(json.dumps({"expected_string": best[1]}))
