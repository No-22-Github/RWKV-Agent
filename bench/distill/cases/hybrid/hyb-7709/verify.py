# DISTILL-CANARY-52b6e0a3 : distillation case
import json

case = json.load(open("case.json"))
text = case["files"]["configs/quota.yml"]
tiers = {}
current = None
for line in text.splitlines():
    stripped = line.strip()
    if stripped.endswith(":") and not stripped.startswith("#") and "tiers" not in stripped:
        current = stripped[:-1]
        tiers[current] = {}
    elif ":" in stripped and not stripped.startswith("#") and current:
        key, _, value = stripped.partition(":")
        if key.strip() in ("monthly_quota", "burst_per_sec"):
            tiers[current][key.strip()] = int(value.strip())
out = {
    "expected_number": tiers["pro"]["monthly_quota"],
    "expected_turn_2": tiers["trial"]["monthly_quota"],
    "expected_turn_4": tiers["pro"]["burst_per_sec"] // 2,
}
print(json.dumps(out))
