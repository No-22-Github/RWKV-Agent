# EXAM-CANARY-a8f0c936 : sol pilot case
import csv,io,json
case=json.load(open("case.json",encoding="utf-8"))
config=json.loads(case["files"]["box_sources.json"])
counts={}
for row in csv.DictReader(io.StringIO(case["files"]["pallets.csv"])):
    chosen=next((int(row[key]) for key in config["priority"] if row[key] not in config["unset"]),0)
    counts[row["dock"]]=counts.get(row["dock"],0)+chosen
lines=["dock,boxes"]+[f"{dock},{counts[dock]}" for dock in sorted(counts)]
print(json.dumps({"expected_stdout":"\n".join(lines)},ensure_ascii=False))
