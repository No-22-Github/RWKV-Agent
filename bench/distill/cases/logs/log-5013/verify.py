# DISTILL-CANARY-93a2d357 : distillation case
import json
import re

case = json.load(open("case.json"))
LINE = re.compile(r"(\S+) (OUT|IN) +vehicle=(\S+)")


def movements(path):
    lines = [line for line in case["files"][path].splitlines() if line.strip()]
    trailer = re.fullmatch(r"\S+ CLOSE movements=(\d+)", lines[-1])
    assert trailer is not None, path + ": closing record missing"
    rows = [LINE.fullmatch(line) for line in lines[:-1]]
    assert all(rows), path + ": unreadable movement line"
    assert len(rows) == int(trailer.group(1)), path + ": the journal does not list every movement"
    return [(row.group(1), row.group(2)) for row in rows]


def departures(rows, low, high):
    return sum(1 for stamp, kind in rows
               if kind == "OUT" and low <= stamp.split("T")[1] < high)


# The north barrier stamps the depot clock, eight hours ahead of UTC, so the
# 06:00-08:00 UTC window is 14:00-16:00 there; the south barrier stamps in UTC.
north = movements("logs/north-gate.log")
south = movements("logs/south-gate.log")
total = departures(north, "14:00:00", "16:00:00") + departures(south, "06:00:00", "08:00:00")
print(json.dumps({"expected_number": total}))
