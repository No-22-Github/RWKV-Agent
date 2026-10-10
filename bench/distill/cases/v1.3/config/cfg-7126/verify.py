# DISTILL-CANARY-80a6a8a5 : distillation case
import json

case = json.load(open("case.json"))
site_text = case["files"]["config/pump-station.yaml"]
region = json.loads(case["files"]["config/region-baseline.json"])

site = {}
for line in site_text.splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    key, sep, value = line.partition(":")
    if not sep:
        raise SystemExit("fixture guard failed: unparsable site line " + repr(line))
    site[key.strip()] = value.strip()

for key in ("station", "alert_delay_s"):
    if key not in site:
        raise SystemExit("fixture guard failed: site key " + key + " is missing")
if "alert_delay_s" not in region:
    raise SystemExit("fixture guard failed: region baseline is broken")
# Positive control: the stale commented value the decoy comes from.
if "120" not in site_text:
    raise SystemExit("fixture guard failed: stale comment is gone")

# README.md: the site config overrides the region baseline.
effective = dict(region)
effective.update(site)

print(json.dumps({"expected_number": int(effective["alert_delay_s"])}))
