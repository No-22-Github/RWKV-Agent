# DISTILL-CANARY-756ff276 : distillation case
import json

case = json.load(open("case.json"))
SPEC = {"path": "config/通知.env", "start": 8, "end": 11, "new": ["MAIL_PROVIDER=ses", "MAIL_RATE_PER_MIN=200", "MAIL_RETRY=3", "MAIL_TIMEOUT_MS=5000"]}
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
