# WORKBANK-CANARY-e18b5d26 : bank artifact, excluded from training corpora
"""Expected answer for tab-0019: events inside the 1-15 March 2026 window.

Dates in the export are written in three styles; the README fixes the day-first
convention for the bare-number styles. Each row's date is parsed, then filtered
to the inclusive window. Computed from case.json, independent of expect.
"""
import csv
import io
import json
from datetime import date, datetime

STYLES = ["%d/%m/%Y", "%d-%m-%Y", "%b %d, %Y", "%Y/%m/%d"]
WINDOW_START = date(2026, 3, 1)
WINDOW_END = date(2026, 3, 15)

case = json.load(open("case.json"))


def parse(text):
    for style in STYLES:
        try:
            return datetime.strptime(text.strip(), style).date()
        except ValueError:
            continue
    raise SystemExit("unparsed event date: " + repr(text))


count = 0
rows = csv.DictReader(io.StringIO(case["files"]["contract_events.csv"]))
for row in rows:
    when = parse(row["event_date"])
    if WINDOW_START <= when <= WINDOW_END:
        count += 1
print(json.dumps({"expected_number": count}))
