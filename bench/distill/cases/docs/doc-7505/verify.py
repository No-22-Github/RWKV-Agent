# DISTILL-CANARY-e3a05b28 : distillation case
import json

case = json.load(open("case.json"))
files = case["files"]
import re
plan = files["docs/plan.txt"]
readme_first = files["README.md"].splitlines()[0]
facts = [re.search(r"[a-z][a-z0-9-]+", readme_first).group(0)]
milestone = [line for line in plan.splitlines() if "里程碑" in line][0]
facts.append(re.search(r"M\d+", milestone).group(0))
facts.append(re.search(r"里程碑 M\d+：(.*?)，", milestone).group(1))
shelved = [line for line in plan.splitlines() if "搁置" in line][0]
facts.append(re.search(r"搁置：(.*?)报价", shelved).group(1))
facts = sorted(set(facts))
print(json.dumps({"expected_contains_any": facts}))
