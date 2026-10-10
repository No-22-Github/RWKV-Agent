# DISTILL-CANARY-710c25ef : distillation case

import json


def load_yaml_layer(text):
    data = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        data[key.strip()] = value.strip()
    return data


case = json.load(open("case.json"))
instance = load_yaml_layer(case["files"]["config/tile-cache.yaml"])
base = load_yaml_layer(case["files"]["config/tile-base.yaml"])

KEY = "tile_refresh_s"

# README.md: the instance config overrides the platform baseline and a key in
# neither layer has no effective value. Recompute the effective map.
effective = dict(base)
effective.update(instance)
if KEY in effective:
    raise SystemExit("fixture defines " + KEY + "; the absent-key case is broken")

# Positive controls: the first key of each layer anchors the recomputation
# above, and the commented-out bait line must still be present.
if effective.get("service") != "tile-cache":
    raise SystemExit("fixture guard failed: instance layer anchor is broken")
if effective.get("tenant_tier") != "professional":
    raise SystemExit("fixture guard failed: baseline layer anchor is broken")
bait = [l for l in case["files"]["config/tile-cache.yaml"].splitlines()
        if l.strip().startswith("#") and KEY in l]
if not bait:
    raise SystemExit("fixture lost the commented " + KEY + " bait line")

accepted = [
    "tile_refresh_s",
    "tile refresh",
    "瓦片刷新",
]
print(json.dumps({"expected_contains_any": accepted}))
