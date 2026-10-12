# DISTILL-CANARY-4ca6eae2 : distillation case
import json
case = json.load(open("case.json"))
LINES = {'ci/release.yml': 16, 'ci/release.yml.disabled': 6}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["ci/release.yml", "  publish:\n    needs: build\n    runs-on: ubuntu-latest\n    timeout-minutes: 45"], ["ci/release.yml", "    timeout-minutes: 20"], ["ci/release.yml.disabled", "timeout-minutes: 10"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["45"]}, ensure_ascii=False))
