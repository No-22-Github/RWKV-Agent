# DISTILL-CANARY-b04a92f6 : distillation case
import json
import re

case = json.load(open("case.json"))
alarm_re = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2}) ALARM unit=\S+ code=\S+ msg=\"[^\"]+\"$")
boiler_info = re.compile(r"^\S+ INFO (boiler_steam_t=[\d.]+ drum_pressure_bar=[\d.]+|drum_level_mm=\d+ feedwater_flow_t_h=[\d.]+)$")
turbine_info = re.compile(r"^\S+ INFO (generator_mw=[\d.]+ speed_rpm=\d+|casing_pressure_bar=[\d.]+ lubrication_ok=true)$")
alarms = 0
for name in sorted(case["files"]):
    if not name.endswith(".log"):
        continue
    lines = [l for l in case["files"][name].splitlines() if l.strip()]
    close = re.search(r"JOURNAL CLOSE lines=(\d+)$", lines[-1])
    assert close, name + ": closing record absent"
    assert len(lines) - 1 == int(close.group(1)), name + ": line count does not match the closing record"
    for line in lines[:-1]:
        m = alarm_re.fullmatch(line)
        if m:
            if m.group(1) == "2026-07-16" and "09:00:00" <= m.group(2) < "10:00:00":
                alarms += 1
        elif boiler_info.fullmatch(line) or turbine_info.fullmatch(line):
            pass
        else:
            raise AssertionError(name + ": unreadable line: " + line)
print(json.dumps({"expected_number": alarms}))
