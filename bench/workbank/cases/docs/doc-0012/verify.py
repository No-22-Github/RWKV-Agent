# WORKBANK-CANARY-82a5e3b7 : bank artifact, excluded from training corpora
"""Recompute the Northgate depot shuttle permit interval for doc-0012.

The airside operations handbook holds the general validity in clause 6.1.1;
appendix D, whose heading is located through handbook/section-index.json,
carries the variation for depot-based service-road vehicles. The expected file
content is derived here from the handbook, independently of the expect block.
"""
import json
import re

case = json.load(open("case.json"))
files = case["files"]
handbook = files["handbook/airside-operations-handbook.md"]
index = json.loads(files["handbook/section-index.json"])

headings = {entry["id"]: entry["heading"] for entry in index["sections"]}
for needed in ("6", "D"):
    if needed not in headings:
        raise SystemExit("section index does not list section %s" % needed)

order = [entry["heading"] for entry in index["sections"]]
if not handbook.startswith("# Meridian Airport Services"):
    raise SystemExit("handbook front matter is missing")


def section_body(heading):
    """Text of one indexed section, up to the next indexed heading."""
    start = handbook.find(heading)
    if start < 0:
        raise SystemExit("handbook does not carry the heading %r" % heading)
    start += len(heading)
    ends = [
        handbook.find(other, start)
        for other in order
        if other != heading and handbook.find(other, start) >= 0
    ]
    end = min(ends) if ends else len(handbook)
    return handbook[start:end]


permits = section_body(headings["6"])
general = re.search(r"valid for a period of (\d+)\s+months", permits)
if not general:
    raise SystemExit("clause 6.1.1 does not state the standard validity")

variations = section_body(headings["D"])
depot = re.search(
    r"class P7\s+vehicle based at the Northgate depot and used only on the landside service\s+"
    r"roads holds a permit valid for (\d+)\s+months",
    variations,
)
if not depot:
    raise SystemExit("appendix D does not state the Northgate depot variation")

if int(depot.group(1)) == int(general.group(1)):
    raise SystemExit("appendix D carries no variation for these vehicles")

content = "# Northgate shuttle fleet - permit renewal\n%s months\n" % depot.group(1)
print(json.dumps({"files": {"notes/northgate-shuttle-permits.md": content}}))
