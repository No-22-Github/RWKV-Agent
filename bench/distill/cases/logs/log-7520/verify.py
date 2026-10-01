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
forms = [fail_step, fail_ts, fail_ts[:5],
         "%d items" % released, "%d payouts" % released,
         over, grouped,
         "%d items" % pending, "%d pending" % pending]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
