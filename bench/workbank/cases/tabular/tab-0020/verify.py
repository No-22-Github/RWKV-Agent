# WORKBANK-CANARY-52d9f0a4 : bank artifact, excluded from training corpora
"""Expected answer for tab-0020: June 2026 subscription total in Singapore time.

invoices_utc.csv stamps are UTC; metering_sgt.csv stamps are already at
UTC+08:00. Each stamp is shifted to Singapore time, kept when the resulting
local date falls in June 2026, and the kept amounts are summed. Computed from
case.json, independent of the expect block.
"""
import csv
import io
import json
from datetime import datetime, timedelta

STYLES = [
    "%d/%m/%Y %H:%M",
    "%d-%m-%Y %H:%M",
    "%b %d, %Y %H:%M",
    "%Y/%m/%d %H:%M",
]
SINGAPORE = timedelta(hours=8)

case = json.load(open("case.json"))


def parse(text):
    for style in STYLES:
        try:
            return datetime.strptime(text.strip(), style)
        except ValueError:
            continue
    raise SystemExit("unparsed stamp: " + repr(text))


def in_june_singapore(stamp, source_offset):
    local = stamp + (SINGAPORE - source_offset)
    return local.year == 2026 and local.month == 6


total = 0.0
ledgers = [
    ("invoices_utc.csv", "issued_at", timedelta(0)),
    ("metering_sgt.csv", "recorded_at", SINGAPORE),
]
for path, column, offset in ledgers:
    for row in csv.DictReader(io.StringIO(case["files"][path])):
        if in_june_singapore(parse(row[column]), offset):
            total += float(row["amount"])
print(json.dumps({"expected_number": round(total, 2)}))
