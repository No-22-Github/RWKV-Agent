"""31341-31348: read-only log questions with a missing day, file or service."""
from p2 import clarify, reg

R = ("list_files", "read_file", "search_text")
OKS = ["request served", "cache hit", "health check ok", "session refreshed", "job finished", "config reloaded"]
ERRS = ["upstream timeout", "db connection reset", "payment declined by bank", "disk quota warning escalated", "invalid token"]


def mklog(date, errs, oks, tag="ERROR", msgs=ERRS, start=8):
    total = errs + oks
    idx = {(j * total) // errs + 1 for j in range(errs)} if errs else set()
    while len(idx) < errs:
        idx.add(max(set(range(total)) - idx))
    rows = []
    for k in range(total):
        sec = start * 3600 + k * 97
        ts = "%s %02d:%02d:%02d" % (date, sec // 3600 % 24, sec // 60 % 60, sec % 60)
        if k in idx:
            rows.append("%s %s %s" % (ts, tag, msgs[k % len(msgs)]))
        else:
            rows.append("%s INFO %s" % (ts, OKS[k % len(OKS)]))
    return "".join(r + "\n" for r in rows)


COUNT = 'ans = str(sum(1 for l in case["files"][%r].splitlines() if " %s " in l))'


@reg
def c31341():
    files = {"logs/app-0914.log": mklog("2026-09-14", 4, 20), "logs/app-0915.log": mklog("2026-09-15", 12, 18), "logs/app-0916.log": mklog("2026-09-16", 6, 12)}
    clarify("log-31341", scen="log", task_type="count_events", files=files, p1="统计一下报错有多少条。", p2="看 0915 那天的。", stems=["0914", "0915"], must=R,
            edit=False, calc=COUNT % ("logs/app-0915.log", "ERROR"), ans2="12", desc="Asks for an error count with three daily logs and no day named",
            ref="三份按日日志，追问统计哪天（或合计）；用户指 0915 后数 ERROR 行 = 12。")


@reg
def c31342():
    files = {"logs/auth-mon.log": mklog("2026-09-14", 5, 14, "WARN", ["failed login for admin", "failed login for guest"]),
             "logs/auth-tue.log": mklog("2026-09-15", 11, 10, "WARN", ["failed login for admin", "failed login for guest", "failed login for root"])}
    clarify("log-31342", scen="log", task_type="count_events", files=files, p1="How many failed logins were there?", p2="Tuesday.", stems=["auth-mon", "auth-tue"], must=R,
            edit=False, calc=COUNT % ("logs/auth-tue.log", "WARN"), ans2="11", desc="Asks for a failed-login count with Monday and Tuesday logs",
            ref="两天日志，追问哪一天；答 Tuesday 后数 WARN 行 = 11。")


@reg
def c31343():
    files = {"logs/slow-w37.log": mklog("2026-09-09", 7, 15, "SLOW", ["GET /report 4.2s", "POST /export 6.8s"]),
             "logs/slow-w38.log": mklog("2026-09-14", 13, 15, "SLOW", ["GET /report 5.1s", "POST /export 7.3s"])}
    clarify("log-31343", scen="log", task_type="count_events", files=files, p1="上周的慢请求有几条？", stems=["slow-w37", "slow-w38"], must=R, edit=False,
            calc=COUNT % ("logs/slow-w38.log", "SLOW"), desc="Asks for last week's slow-request count; the logs are named by week number and 'last week' is not mapped",
            ref="日志按周号命名，不知道上周对应哪个周号（今天 9/16 在 w38），追问或说明候选后确认。")


@reg
def c31344():
    files = {"logs/gateway.log": "2026-09-16 03:11:09 INFO restarting gateway\n2026-09-16 03:11:12 INFO gateway up\n2026-09-15 22:40:00 INFO restarting gateway\n",
             "logs/worker.log": "2026-09-16 05:02:41 INFO restarting worker\n2026-09-16 05:02:45 INFO worker up\n"}
    clarify("log-31344", scen="log", task_type="time_window", files=files, p1="最近一次重启是几点？", p2="worker 的。", stems=["gateway", "worker"], must=R, edit=False,
            calc='ans = [l for l in case["files"]["logs/worker.log"].splitlines() if "restarting" in l][-1].split()[1][:5]', ans2="05:02",
            desc="Asks for the latest restart time with gateway and worker logs", ref="两个服务各有重启记录，追问哪个服务；worker 最近一次 05:02:41。")


@reg
def c31345():
    files = {"logs/deploy-api.log": "2026-09-12 16:20 deploy api v3.8.0 finished\n2026-09-15 11:05 deploy api v3.8.1 finished\n",
             "logs/deploy-web.log": "2026-09-14 09:30 deploy web v7.2.0 finished\n"}
    clarify("log-31345", scen="log", task_type="time_window", files=files, p1="When did the last deploy happen?", stems=["deploy-api", "deploy-web"], must=R, edit=False,
            desc="Asks when the last deploy happened with separate api and web deploy logs", ref="两个独立的部署日志；追问是哪个系统的部署（或给出两者并确认）。")


@reg
def c31346():
    files = {"logs/pay-a-0910.log": mklog("2026-09-10", 3, 12, "FAIL", ["card declined"]), "logs/pay-a-0912.log": mklog("2026-09-12", 14, 12, "FAIL", ["card declined", "3ds timeout"]),
             "logs/pay-b-0912.log": mklog("2026-09-12", 5, 9, "FAIL", ["card declined"])}
    clarify("log-31346", scen="log", task_type="count_events", files=files, p1="这个月支付失败多少笔？", p2="支付网关 A，9 月 12 日那天。", stems=["pay-a", "pay-b"], must=R, edit=False,
            calc=COUNT % ("logs/pay-a-0912.log", "FAIL"), ans2="14", desc="Asks for a monthly failed-payment count when the logs are per gateway and per day",
            ref="日志按网关和日期拆分，追问网关与日期；A 网关 0912 数 FAIL = 14。")


@reg
def c31347():
    rows_a = "".join("2026-09-15 10:%02d resp_ms=%d\n" % (i, v) for i, v in enumerate([120, 340, 95, 880, 410]))
    rows_b = "".join("2026-09-15 10:%02d resp_ms=%d\n" % (i, v) for i, v in enumerate([210, 150, 1260, 730, 90]))
    files = {"logs/access-a.log": rows_a, "logs/access-b.log": rows_b}
    clarify("log-31347", scen="log", task_type="time_window", files=files, p1="What's the peak response time?", p2="Server b.", stems=["access-a", "access-b"], must=R, edit=False,
            calc='import re\nans = str(max(int(x) for x in re.findall(r"resp_ms=(\\d+)", case["files"]["logs/access-b.log"])))', ans2="1260",
            desc="Asks for peak response time with two servers' access logs", ref="两台服务器各一份日志，追问哪台；b 的峰值 1260 ms。")


@reg
def c31348():
    files = {"logs/web.log": mklog("2026-09-15", 4, 16, "HTTP 502", ["upstream bad gateway"]) .replace("HTTP 502", "502"), "logs/api.log": mklog("2026-09-15", 2, 18, "500", ["internal error"]),
             "logs/cdn.log": mklog("2026-09-15", 0, 12, "503", ["unavailable"])}
    clarify("log-31348", scen="log", task_type="count_events", files=files, p1="昨天有没有 5xx？", stems=["web.log", "api.log"], must=R, edit=False,
            desc="Asks whether yesterday had any 5xx errors with web, api and cdn logs", ref="三份日志，用户没说看哪个服务；追问或列出各自情况并请确认范围。")
