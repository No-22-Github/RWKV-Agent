# DISTILL-CANARY-ecebea7e : distillation case
import json
case = json.load(open("case.json"))
LINES = {'ci/pipeline.toml': 8, 'ci/pipeline.toml.sample': 5}
for _p, _n in LINES.items():
    assert len(case["files"][_p].splitlines()) == _n, _p
NEEDLES = [["ci/pipeline.toml", "[nightly]\ntest_shards = 8"], ["ci/pipeline.toml", "[pr]\ntest_shards = 4"], ["ci/pipeline.toml.sample", "test_shards = 3"]]
for _p, _s in NEEDLES:
    assert _s in case["files"][_p], (_p, _s)
print(json.dumps({"expected_contains_any": ["8", "eight"]}, ensure_ascii=False))
