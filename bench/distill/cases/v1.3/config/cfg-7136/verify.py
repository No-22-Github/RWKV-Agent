# DISTILL-CANARY-61a5dda7 : distillation case
import json

case = json.load(open("case.json"))
base = json.loads(case["files"]["config/farm-base.json"])
fragment = json.loads(case["files"]["config/queue-fragment.json"])

# Premise: both layers carry a retry object and the fragment names only part of
# it, so the nested-object rule decides the asked key.
for layer, name in ((base, "base"), (fragment, "fragment")):
    if not isinstance(layer.get("retry"), dict):
        raise SystemExit("fixture guard failed: retry missing in " + name)
if "max_attempts" in fragment["retry"]:
    raise SystemExit("fixture guard failed: fragment now defines max_attempts")
if fragment["retry"].get("backoff_s") == base["retry"].get("backoff_s"):
    raise SystemExit("fixture guard failed: backoff no longer conflicts")

# queue-merge.txt rule one: nested objects merge key by key; sub-keys the
# fragment does not write keep the baseline value.
merged_retry = dict(base["retry"])
merged_retry.update(fragment["retry"])
print(json.dumps({"expected_number": merged_retry["max_attempts"]}))
