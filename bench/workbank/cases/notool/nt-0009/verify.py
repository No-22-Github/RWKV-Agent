# WORKBANK-CANARY-2f6c81ad : bank artifact, excluded from training corpora
import json

# The retry budget is derived from the workspace's own extract of the standard's
# inputs (notes/freeze_inputs.txt, mirrored in profiles/dispatch.yaml) and
# cross-checked against the figures the request states. Never copied from the
# expect block.
case = json.load(open("case.json"))
prompt = case["turns"][-1]["prompt"]

extract = case["files"]["notes/freeze_inputs.txt"]
inputs = {}
for line in extract.splitlines():
    if not line.strip():
        continue
    name, fields = line.split(None, 1)
    values = dict(part.split("=", 1) for part in fields.split())
    inputs[name] = (int(values["retry_limit"]), int(values["upstreams"]))

if set(inputs) != {"dispatch", "warehouse", "returns"}:
    raise SystemExit("freeze extract does not cover the three carrier profiles")

limit, upstreams = inputs["dispatch"]
if "retry_limit: %d" % limit not in prompt or "%d upstreams" % upstreams not in prompt:
    raise SystemExit("request and workspace extract disagree")

profile = case["files"]["profiles/dispatch.yaml"]
if "retry_limit: %d" % limit not in profile:
    raise SystemExit("dispatch profile does not carry the extract's retry_limit")

print(json.dumps({"expected_number": limit * upstreams}))
