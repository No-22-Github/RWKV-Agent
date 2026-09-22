# WORKBANK-CANARY-2f6a90d3 : bank artifact, excluded from training corpora
import csv
import io
import json
import re

MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}
ISO_RE = re.compile(r"(\d{4})/(\d{2})/(\d{2})")
DMY_RE = re.compile(r"(\d{2})-(\d{2})-(\d{4})")
TXT_RE = re.compile(r"([A-Za-z]{3}) (\d{1,2}) (\d{4})")


def month_of(text):
    text = text.strip()
    m = ISO_RE.fullmatch(text)
    if m:
        return "%s-%s" % (m.group(1), m.group(2))
    m = DMY_RE.fullmatch(text)
    if m:
        return "%s-%s" % (m.group(3), m.group(2))
    m = TXT_RE.fullmatch(text)
    if m:
        return "%s-%02d" % (m.group(3), MONTHS[m.group(1)])
    raise ValueError("unrecognised date %r" % text)


case = json.load(open("case.json", encoding="utf-8"))
blobs = dict(case["files"])
blobs.update(case["expect"]["run"].get("hidden_files") or {})
totals = {}
seen = set()
for name in sorted(blobs):
    base = name.rsplit("/", 1)[-1]
    if not base.startswith("events-") or not base.endswith(".csv"):
        continue
    for row in csv.DictReader(io.StringIO(blobs[name])):
        event = row["event_id"]
        if event in seen:
            continue
        seen.add(event)
        month = month_of(row["occurred"])
        totals[month] = totals.get(month, 0) + int(row["amount_cents"])
lines = ["month,amount_cents"]
for month in sorted(totals):
    lines.append("%s,%d" % (month, totals[month]))
lines.append("total,%d" % sum(totals.values()))
print(json.dumps({"expected_stdout": "\n".join(lines)}))
