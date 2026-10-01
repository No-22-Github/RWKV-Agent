# DISTILL-CANARY-43713d58 : distillation case
import json
import re

case = json.load(open("case.json"))
close_re = re.compile(r"^=== JOURNAL CLOSE records=(\d+) writer=\S+ ===$")
head_re = re.compile(r"^=== JOURNAL OPEN host=\S+ date=\S+ writers=\d+ ===$")
line_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) shipment=(\S+) stage=(\S+) (.+)$")

def scan(path, service):
    lines = case["files"][path].splitlines()
    if not head_re.match(lines[0]) or any(head_re.match(l) for l in lines[1:]):
        raise SystemExit("fixture guard failed: journal head must be line 1 and unique in " + path)
    closes = [i for i, l in enumerate(lines) if close_re.match(l)]
    if closes != [len(lines) - 1]:
        raise SystemExit("fixture guard failed: journal close must be the last line in " + path)
    if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
        raise SystemExit("fixture guard failed: record count mismatch in " + path)
    errs, warns = set(), set()
    for line in lines[1:-1]:
        if line.startswith("==="):
            continue
        m = line_re.match(line)
        if not m:
            raise SystemExit("unreadable journal line in %s: %s" % (path, line))
        ts, tm, level, svc, shp, stage, msg = m.groups()
        if svc != service:
            raise SystemExit("fixture guard failed: foreign service line in " + path)
        if level == "ERROR":
            errs.add(shp)
        elif level == "WARN":
            warns.add(shp)
    return errs, warns

book_err, book_warn = scan("logs/booking-2026-05-19.log", "booking-api")
disp_err, disp_warn = scan("logs/dispatch-2026-05-19.log", "dispatch-relay")
both = book_err & disp_err
if len(both) != 1:
    raise SystemExit("fixture guard failed: exactly one shipment must fail in the two stages")
if len(book_err) < 4 or len(disp_err) < 4:
    raise SystemExit("fixture guard failed: single-stage decoys missing")
if not (book_warn & disp_err):
    raise SystemExit("fixture guard failed: warn/error decoy pair missing")
value = both.pop()
print(json.dumps({"expected": value}))