# DISTILL-CANARY-fad5e141 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["releases/release-log.csv"])))

# Re-run the retrieval. README.md: a capability that no summary mentions has
# never shipped in a drive release. No summary names SNMPv3 — the log's only
# SNMP entry added SNMPv1 read-only monitoring, a different protocol
# generation — and no other file in the workspace mentions SNMPv3 either.
WANTED = "snmpv3"
match = [r for r in rows if WANTED in r["summary"].strip().lower()]
if match:
    raise SystemExit("release log now lists an SNMPv3 release; the absent-object case is broken")
for path in sorted(files):
    if WANTED in files[path].lower():
        raise SystemExit(path + " now mentions SNMPv3; the absent-object case is broken")
if "no summary mentions" not in files["README.md"]:
    raise SystemExit("README.md no longer states the never-shipped rule")

accepted = [
    "SNMPv3",
    "snmpv3",
    "SNMPv3 polling",
    "SNMP version 3",
]
print(json.dumps({"expected_contains_any": accepted}))
