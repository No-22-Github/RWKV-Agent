# DISTILL-CANARY-0588aaa9 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 1274
assert case["files"]["server/access/README.md"].startswith("# Access logs")
assert case["files"]["server/last-deploy.txt"].splitlines()[-1] == "2026-10-08 09:00 deploy 4.12.3 ok"
n = 0
for path, text in case["files"].items():
    if path.startswith("server/access/web-"):
        for r in text.splitlines():
            f = r.split()
            assert len(f) == 6, r
            n += f[3] == "/checkout" and int(f[4]) >= 500
print(json.dumps({"expected_number": n}))
