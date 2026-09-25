# DISTILL-CANARY-c15ada5d : distillation case
import json

case = json.load(open("case.json"))
suffixes = {}
for line in case["files"]["conventions/export-filenames.txt"].splitlines():
    export, suffix = [part.strip() for part in line.split("=")]
    suffixes[export] = suffix
print(json.dumps({"expected_string": suffixes["account snapshots"]}))
