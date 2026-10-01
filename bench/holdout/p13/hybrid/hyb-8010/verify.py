# DISTILL-CANARY-347214d4 : p13 holdout eval case (eval-only, never for training)
import csv
import io
import json
import re
import sys

case = json.load(open("case.json"))

def to_iso(s):
    s = s.strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        return s
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", s)
    if m:
        d, mo, y = m.groups()
        return f"{y}-{mo}-{d}"
    sys.exit(1)

def active(r, y, m):
    start = to_iso(r["start_date"])
    end = to_iso(r["end_date"]) if r["end_date"].strip() else ""
    ms = f"{y:04d}-{m:02d}-01"
    me = f"{y:04d}-{m:02d}-31"
    return start <= me and (end == "" or end >= ms)

rows = list(csv.DictReader(io.StringIO(case["files"]["subs-export.csv"])))
aug = [r for r in rows if active(r, 2026, 8)]
print(json.dumps({"expected_number": len(aug)}))
