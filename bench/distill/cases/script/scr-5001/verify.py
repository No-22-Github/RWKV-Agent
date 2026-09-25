# DISTILL-CANARY-8bad58ab : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
shipped = case["files"]
hidden = case["expect"]["run"]["hidden_files"]

log_path = "firings/2026-09.csv"
rows = list(csv.DictReader(io.StringIO(shipped[log_path])))
rows += list(csv.DictReader(io.StringIO(hidden["firings/2026-10.csv"])))


def pounds(pence):
    return "%d.%02d" % (pence // 100, pence % 100)


loads = {}
amounts = {}
for row in rows:
    if row["status"] != "billed":
        continue
    client = row["client"]
    loads[client] = loads.get(client, 0) + 1
    amounts[client] = amounts.get(client, 0) + int(row["charge_pence"])

statement = ["%s,%d,%s" % (client, loads[client], pounds(amounts[client]))
             for client in sorted(loads)]
statement.append("TOTAL,%d,%s" % (sum(loads.values()), pounds(sum(amounts.values()))))

print(json.dumps({
    "expected_stdout": "\n".join(statement),
    "files": {log_path: shipped[log_path]},
}))
