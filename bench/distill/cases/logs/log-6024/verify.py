# DISTILL-CANARY-b04fa8b3 : distillation case
import json
import re

case = json.load(open("case.json"))
err_re = re.compile(r"^(\S+) oven=(\S+) ERROR code=\S+ msg=")
info_re = re.compile(r"^\S+ oven=\S+ INFO chamber_c=\d+ belt_m_min=\d+$")
warn_re = re.compile(r"^\S+ oven=\S+ WARN code=\S+ msg=\"[^\"]+\"$")
first = None
for name in sorted(case["files"]):
    if not name.endswith(".log"):
        continue
    lines = [l for l in case["files"][name].splitlines() if l.strip()]
    close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
    assert close, name + ": closing record absent"
    assert len(lines) - 1 == int(close.group(1)), name + ": line count does not match the closing record"
    for line in lines[:-1]:
        m = err_re.fullmatch(line + " ")
        m = err_re.match(line)
        if m:
            stamp = m.group(1)
            if first is None or stamp < first[0]:
                first = (stamp, m.group(2))
        else:
            assert info_re.fullmatch(line) or warn_re.fullmatch(line), name + ": unreadable line"
assert first is not None, "no ERROR lines in the journals"
print(json.dumps({"expected": first[1]}))
