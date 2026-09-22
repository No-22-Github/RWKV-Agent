# WORKBANK-CANARY-e9b3a742 : bank artifact, excluded from training corpora
"""Recompute the Tarnbeck reservoir acknowledgement target for doc-0010.

The general target lives in the body of the operations handbook; appendix C
carries the site-specific override for the three unmanned upland sites. The
answer is the override, derived here from the two fixture documents.
"""
import json
import re

case = json.load(open("case.json"))
files = case["files"]
handbook = files["handbook/field-operations-handbook.md"]
appendix = files["handbook/appendix-c-upland-worksites.md"]

if not handbook.splitlines()[0].startswith("# Field operations handbook"):
    raise SystemExit("operations handbook title line not found")
if not appendix.splitlines()[0].startswith("# Appendix C"):
    raise SystemExit("appendix C title line not found")

general = re.search(r"Priority 2: acknowledge within (\d+) minutes", handbook)
if not general:
    raise SystemExit("general priority 2 target not stated in the handbook")

if "Tarnbeck reservoir" not in appendix:
    raise SystemExit("appendix C does not name the Tarnbeck reservoir site")

override = re.search(
    r"A priority 2 job at any of the three sites above is acknowledged within (\d+)\s+minutes",
    appendix,
)
if not override:
    raise SystemExit("appendix C does not state the site-specific target")

if int(override.group(1)) == int(general.group(1)):
    raise SystemExit("appendix C carries no override for these sites")

print(json.dumps({"expected_number": int(override.group(1))}))
