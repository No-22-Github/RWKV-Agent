# DISTILL-CANARY-77bb17b3 : distillation case
import json

case = json.load(open("case.json"))
lines = case["files"]["logs/payments-0925.jsonl"].splitlines()

total = 0.0
if_count = 0
gateways = {}
for line in lines:
    if not line.strip():
        continue
    row = json.loads(line)
    if row.get("result") == "settled":
        total += float(row["amount"].replace(",", ""))
    if row.get("result") == "declined" and row.get("code") == "insufficient_funds":
        if_count += 1
        gateways[row["gateway"]] = gateways.get(row["gateway"], 0) + 1

plain = "%.2f" % total
grouped = "{:,.2f}".format(total)
top = sorted(gateways.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
forms = [plain, grouped,
         "%d declined" % if_count, "%d transactions" % if_count, "%d declines" % if_count,
         top]
print(json.dumps({"expected_contains_any": sorted(set(forms))}))
