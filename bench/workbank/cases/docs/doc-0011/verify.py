# WORKBANK-CANARY-6f28d1c5 : bank artifact, excluded from training corpora
"""Recompute the opening-critical check list for doc-0011.

The handbook defines an opening-critical check as one whose recorded
consequence of failure is that a building or a service area cannot open. The
register carries the consequence of every check, so the expected file is
derived here from the register, independently of the expect block.
"""
import json
import re

case = json.load(open("case.json"))
register = case["files"]["registers/premises-checks.txt"]
handbook = case["files"]["handbook/premises-handbook.md"]

if "Opening-critical check" not in handbook or "cannot open" not in handbook:
    raise SystemExit("handbook does not carry the opening-critical definition")

lines = [line for line in register.splitlines() if line.strip()]
header = re.match(
    r"# Premises checks register .* exported (\d{4}-\d{2}-\d{2})", lines[0]
)
if not header:
    raise SystemExit("checks register header not found")
export_date = header.group(1)

entries = []
for line in lines[1:]:
    if line.lstrip().startswith("#"):
        continue
    fields = [field.strip() for field in line.split("|")]
    if len(fields) != 3:
        raise SystemExit("register line is not name | interval | consequence: %r" % line)
    name, _interval, consequence = fields
    if "cannot open" in consequence:
        entries.append(name)

if not entries:
    raise SystemExit("no opening-critical check found in the register")

content = "# Opening-critical checks - %s\n\n" % export_date
content += "".join("- %s\n" % name for name in entries)
print(json.dumps({"files": {"reports/opening-critical-checks.md": content}}))
