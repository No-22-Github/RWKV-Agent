# DISTILL-CANARY-5fa811f0 : distillation case
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["README.md"].startswith("Shared defaults live in config/database.yaml")
sizes = {}
for env in ("staging", "dr"):
    sizes[env] = int(re.search(r"pool_size: (\d+)", f["config/env/%s.yaml" % env]).group(1))
print(json.dumps({"expected_number": sizes["staging"]}))
