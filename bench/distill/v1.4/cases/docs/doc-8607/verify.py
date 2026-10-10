# DISTILL-CANARY-40f662c3 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "INSTALL.md", "start": 9, "end": 11, "new": ["1. wget https://get.example.test/acme.tar.gz", "2. tar xzf acme.tar.gz -C /usr/local/bin", "3. acme --version"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
