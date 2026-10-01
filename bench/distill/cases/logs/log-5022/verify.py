# DISTILL-CANARY-d6418e2c : distillation case
import json
import re

case = json.load(open("case.json"))
readme = case["files"]["README.md"]
log = case["files"]["logs/boiler.log"]
assert readme.startswith("# boiler house journal\n"), "README.md does not document the journal"
lines = [line for line in log.splitlines() if line.strip()]
cycle_re = re.compile(r"\S+ CYCLE burner=\S+ load=\d+ minutes=\d+ fuel=\d+")
cycles = [line for line in lines if cycle_re.fullmatch(line)]
summary = re.fullmatch(r"\S+ SUMMARY session=\S+ cycles=(\d+) fuel=(\d+)", lines[-1])
assert summary is not None, "summary line missing"
assert len(cycles) == len(lines) - 1 == int(summary.group(1)), \
    "the summary does not cover every cycle line"

# The journal records what each cycle took in, how long it ran and the gas units
# it drew. No price, tariff or charge is written down anywhere in the workspace,
# so the cost of the session's gas cannot be worked out.
for line in lines[:-1]:
    assert cycle_re.fullmatch(line), "unexpected journal line: " + line
money = re.search(r"price|tariff|charge|pound|GBP|£", readme + log, re.IGNORECASE)
assert money is None, "a money record appeared in the workspace: " + money.group(0)
print(json.dumps({"expected_contains_any": ["tariff", "price", "charge"]}))
