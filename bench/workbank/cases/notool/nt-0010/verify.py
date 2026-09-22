# WORKBANK-CANARY-7b19d4e2 : bank artifact, excluded from training corpora
import json

# Two independent halves. The first turn's request never identifies a pipeline,
# so the workspace must actually hold more than one candidate: the fixture is
# checked for that. The second turn names the attribution pipeline and states
# the standard's inputs, so the figure is its retry_limit times its stage count,
# taken from the workspace extract and cross-checked against the request.
case = json.load(open("case.json"))
first, second = case["turns"][0]["prompt"], case["turns"][1]["prompt"]

extract = case["files"]["standards/retry_inputs.txt"]
inputs = {}
for line in extract.splitlines():
    if not line.strip():
        continue
    name, fields = line.split(None, 1)
    values = dict(part.split("=", 1) for part in fields.split())
    inputs[name] = (int(values["retry_limit"]), int(values["stages"]))

if set(inputs) != {"session_rollup", "attribution", "export_sync"}:
    raise SystemExit("standards extract does not cover the three pipelines")
if len(inputs) < 2 or any(name in first for name in inputs):
    raise SystemExit("the first turn identifies its pipeline after all; the case carries no ambiguity")

limit, stages = inputs["attribution"]
if "retry_limit: %d" % limit not in second or "%d stages" % stages not in second:
    raise SystemExit("the clarifying turn and the workspace extract disagree")
if "jobs/attribution.yaml" not in second:
    raise SystemExit("the clarifying turn does not name the attribution pipeline")

print(json.dumps({"expected_number": limit * stages}))
