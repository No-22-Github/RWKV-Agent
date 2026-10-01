# DISTILL-CANARY-cb17f62b : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["logs/payout-batch.csv"])))

fail_step = ""
fail_ts = ""
gross = 0.0
limit = 0.0
released = pending = 0
for row in rows:
    msg = row["message"]
    if row["level"] == "ERROR" and "limit exceeded" in msg:
        fail_step = row["unit"].split(":")[1]
        fail_ts = row["ts"].split()[1]
        gross = float(re.search(r"gross ([\d,]+\.\d+)", msg).group(1).replace(",", ""))
        limit = float(re.search(r"limit ([\d,]+\.\d+)", msg).group(1).replace(",", ""))
    m = re.search(r"released (\d+) items, (\d+) items pending", msg)
    if m:
        released, pending = int(m.group(1)), int(m.group(2))

over = "%.2f" % (gross - limit)
grouped = "{:,.2f}".format(gross - limit)

_cg = case["files"].get('logs/payout-batch.csv', "")
if '2026-09-26 02:14:08,step:fund-release,INFO,"released 118 items, 42 items pending, batch aborted"' not in _cg:
    raise SystemExit(1)
print(json.dumps({"expected_number": released}))
