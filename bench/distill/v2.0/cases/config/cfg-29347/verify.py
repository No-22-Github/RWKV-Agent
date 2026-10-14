# DISTILL-CANARY-7034b7bc : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 38
def solve(files):
    keys = [r.split("=")[0] for r in files["deploy/.env.example"].splitlines()]
    final = dict(files)
    n = 0
    for env in ("prod", "staging", "dev"):
        p = "deploy/env/%s.env" % env
        have = {r.split("=")[0] for r in files[p].splitlines()}
        miss = [k for k in keys if k not in have]
        n += len(miss)
        final[p] = files[p] + "".join(k + "=CHANGE_ME" + chr(10) for k in miss)
    for env in ("staging", "dev"):
        p = "deploy/env/%s.env" % env
        final[p] = final[p].replace("SENTRY_DSN=CHANGE_ME" + chr(10), "")
    return [{"any": [str(n)]}, None, None], final, {"n": n}
files = case["files"]
answers, final, info = solve(files)
for turn, ans in zip(case["turns"], answers):
    if ans is None:
        continue
    if "any" in ans:
        assert turn["expect"]["output_contains_any"] == ans["any"], (turn["expect"], ans)
    else:
        assert turn["expect"]["output_contains"] == ans["all"], (turn["expect"], ans)
out = {p: t for p, t in final.items() if files.get(p) != t}
print(json.dumps({"files": out}, ensure_ascii=False))
