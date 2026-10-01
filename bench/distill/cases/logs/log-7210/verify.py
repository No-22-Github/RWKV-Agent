# DISTILL-CANARY-9adb38c9 : distillation case
import json
import re

case = json.load(open("case.json"))
close_re = re.compile(r"^# 日志收播 记录数=(\d+) 采集器=\S+$")
line_re = re.compile(r"^(\S+) (\S+) (INFO|WARN|ERROR) (\S+) 订单=(\S+) (.+)$")

def scan(path, service):
    lines = case["files"][path].splitlines()
    closes = [i for i, l in enumerate(lines) if close_re.match(l)]
    if closes != [len(lines) - 1]:
        raise SystemExit("fixture guard failed: 收播行必须是最后一行: " + path)
    if int(close_re.match(lines[-1]).group(1)) != len(lines) - 2:
        raise SystemExit("fixture guard failed: 记录数与收播行不符: " + path)
    errs, warns = set(), set()
    for line in lines[1:-1]:
        if line.startswith("#"):
            continue
        m = line_re.match(line)
        if not m:
            raise SystemExit("无法解析的日志行 in %s: %s" % (path, line))
        ts, tm, level, svc, oid, msg = m.groups()
        if svc != service:
            raise SystemExit("fixture guard failed: 混入其他服务的行: " + path)
        if level == "ERROR":
            errs.add(oid)
        elif level == "WARN":
            warns.add(oid)
    return errs, warns

q_err, q_warn = scan("logs/qiandan-2026-08-12.log", "下单服务")
c_err, c_warn = scan("logs/cangku-2026-08-12.log", "仓储调度")
both = q_err & c_err
if len(both) != 1:
    raise SystemExit("fixture guard failed: 两边都报错的订单应恰好一个")
if len(q_err) < 4 or len(c_err) < 4:
    raise SystemExit("fixture guard failed: 单侧 decoy 不足")
if not (q_warn & c_err):
    raise SystemExit("fixture guard failed: WARN/ERROR 近似对缺失")
value = both.pop()
print(json.dumps({"expected": value}))