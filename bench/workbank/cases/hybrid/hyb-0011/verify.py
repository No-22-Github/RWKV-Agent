# WORKBANK-CANARY-6ad08f23 : bank artifact, excluded from training corpora
import csv
import io
import json

case = json.load(open("case.json"))
# The period is supplied by the second turn of the conversation; the ledger and
# the published rate come from the fixture.
period = "2026-Q1"
page = next(e for e in case["web_fixture"] if "tarnbrookwater.example" in e.get("url", ""))
row = next(l for l in page["content"].splitlines() if "| Meadowford |" in l)
rate = float([c.strip() for c in row.split("|") if c.strip()][1])
rows = csv.DictReader(io.StringIO(case["files"]["usage/consumption.csv"]))
volume = next(int(r["volume_m3"]) for r in rows if r["period"] == period)
print(json.dumps({"expected_number": round(volume * rate, 2)}))
