"""logs locate_error 33754-33761."""
from common import *
from lg import *

B = []


def reg(f):
    B.append(f)
    return f


def lineno(text, marker):
    ls = text.splitlines()
    hits = [i + 1 for i, l in enumerate(ls) if marker in l]
    assert len(hits) == 1, (marker, hits)
    return hits[0]


LV = ("INFO", "INFO", "INFO", "INFO", "DEBUG", "WARN")


@reg
def e1():
    r = rng("e1"); d = "2026-09-13"
    ev = noise(r, "06:00:00", "09:00:00", 170, ["task {n} scheduled", "task {n} completed in {ms}ms", "cache refresh ok", "heartbeat from node{n}"], LV)
    ev += [("06:42:11", "INFO", "stats: errors=0 warnings=2"), ("07:10:30", "INFO", "retry policy: error budget ok (budget=5)"), ("07:55:02", "INFO", "metrics ERROR_RATE=0.0"),
           ("08:21:47", "ERROR", "export task 81 failed: cannot open /data/out/rep.csv (permission denied)"), ("08:30:12", "ERROR", "export task 83 failed: permission denied")]
    text = render(ev, fmt_iso(d, "svc"))
    n = lineno(text, "export task 81 failed")
    make("log-33754", sub="locate", task_type="locate_error", desc="First ERROR-level line after harmless lines that contain the word error",
         files={"svc.log": text}, turns=[T("svc.log 里第一次真正报错（级别为 ERROR 的那一行）在第几行？是几点？", [str(n), "08:21"], token=True, req=["bash"]),
                                         T("报的是什么错？", ["permission denied"], any_=[], token=False)],
         truth="ls=files['svc.log'].splitlines()\ni=[k for k,l in enumerate(ls,1) if ' ERROR ' in l][0]\nanswers=[str(i)]",
         ref=[("grep -n ' ERROR ' svc.log | head -1", "%d:" % n)],
         notes={"traps": "errors=0, error budget, ERROR_RATE lines contain 'error' but are INFO.", "steps": "grep -n ' ERROR '.", "unique": "line %d at 08:21:47" % n},
         traps=("TR-EARLYHIT", "TR-DECOY"), axes=("STP", "OBS"), rc=4)


@reg
def e2():
    r = rng("e2"); d = "2026-09-08"
    ev = noise(r, "13:00:00", "16:00:00", 165, ["request {n} handled in {ms}ms", "pool size stable", "gc pause {ms}ms"], LV)
    ev += [("13:48:20", "WARN", "caught java.net.SocketTimeoutException, retrying (1/3)"), ("14:03:05", "WARN", "caught java.net.SocketTimeoutException, retrying (2/3)"),
           ("14:19:40", "ERROR", "request 7781 failed: java.net.SocketTimeoutException: connect timed out"), ("14:25:00", "ERROR", "request 7790 failed: connect timed out")]
    text = render(ev, fmt_iso(d, "http"))
    n = lineno(text, "request 7781 failed")
    make("log-33755", sub="locate", task_type="locate_error", desc="Exceptions inside WARN lines come first; the first ERROR line is later",
         files={"http.log": text}, turns=[T("What is the line number and time of the first ERROR in http.log? (Warnings don't count.)", [str(n), "14:19"], token=True, req=["bash"])],
         truth="ls=files['http.log'].splitlines()\nanswers=[str([k for k,l in enumerate(ls,1) if ' ERROR ' in l][0])]",
         ref=[("grep -n ' ERROR ' http.log | head -1", "%d:" % n)],
         notes={"traps": "Two WARN lines carry an exception name.", "steps": "grep -n ' ERROR '.", "unique": "line %d at 14:19:40" % n},
         traps=("TR-EARLYHIT", "TR-DECOY"), axes=("STP", "OBS"), rc=4)


@reg
def e3():
    r = rng("e3"); d1, d2 = "2026-09-06", "2026-09-07"
    old = noise(r, "21:00:00", "23:59:00", 90, ["job {n} queued", "job {n} ok", "disk check ok"], LV) + [("23:12:40", "ERROR", "job 912 aborted: lock timeout")]
    new = noise(r, "00:00:00", "03:00:00", 90, ["job {n} queued", "job {n} ok", "disk check ok"], LV) + [("01:05:10", "ERROR", "job 940 aborted: lock timeout")]
    f = {"batch.log": render(new, fmt_iso(d2, "b")), "batch.log.1": render(old, fmt_iso(d1, "b"))}
    nn = lineno(f["batch.log.1"], "job 912 aborted")
    make("log-33756", sub="locate", task_type="locate_error", desc="The earliest error is in the rotated file batch.log.1, not the current one",
         files=f, turns=[T("batch.log 是当前日志，batch.log.1 是上一份（轮转出去的旧日志）。从头算起，整个任务第一次 ERROR 出现在哪个文件、第几行、什么时间？", ["batch.log.1", str(nn), "23:12"], token=False, req=["bash"]),
                         T("当前那个 batch.log 里的第一条 ERROR 是几点？", ["01:05"], token=True)],
         truth="answers=['batch.log.1','01:05']" if False else "answers=['batch.log.1','01:05']",
         ref=[("grep -n ' ERROR ' batch.log.1 | head -1", "%d:" % nn)],
         notes={"traps": "Rotated file holds the older events.", "steps": "check both files' first ERROR.", "unique": "batch.log.1 line %d 23:12:40" % nn},
         traps=("TR-MULTISRC", "TR-DECOY"), axes=("CHN", "OBS"), rc=5)


@reg
def e4():
    r = rng("e4"); import json
    base = 1789002000
    rows = []
    for i in range(175):
        t = base + i * 17 + r.randint(0, 9)
        rows.append({"ts": t, "level": r.choice(["info", "info", "info", "debug"]), "msg": r.choice(["tick %d" % i, "sync ok", "lease renewed", "queue drained"])})
    rows[60] = {"ts": rows[60]["ts"], "level": "warn", "msg": "error budget exhausted for tenant 7"}
    rows[88] = {"ts": rows[88]["ts"], "level": "info", "msg": "no error detected in scan %d" % 3}
    rows[121] = {"ts": rows[121]["ts"], "level": "error", "msg": "replica r2 diverged: checksum mismatch"}
    rows[140] = {"ts": rows[140]["ts"], "level": "error", "msg": "replica r2 still diverged"}
    text = "".join(json.dumps(x, separators=(",", ":")) + "\n" for x in rows)
    f = {"events.jsonl": text}
    n = 122
    make("log-33757", sub="locate", task_type="locate_error", desc="JSON-lines log with lowercase levels and decoy messages mentioning error",
         files=f, turns=[T("events.jsonl 每行是一个 JSON。level 为 error 的第一条在第几行？消息是什么？", [str(n), "checksum mismatch"], token=False, req=["bash"])],
         truth="import json\nrows=[json.loads(l) for l in files['events.jsonl'].splitlines()]\nanswers=[str([i for i,x in enumerate(rows,1) if x['level']=='error'][0])]",
         ref=[("grep -n '\"level\":\"error\"' events.jsonl | head -1", "%d:" % n)],
         notes={"traps": "A warn-level and an info-level message contain 'error'; level case is lowercase so a case-sensitive grep for ERROR finds nothing.", "steps": "grep -n level error.", "unique": "line 122"},
         traps=("TR-DECOY", "TR-DEFN"), axes=("OBS",), rc=4)


@reg
def e5():
    r = rng("e5"); d = "2026-09-02"
    ev = noise(r, "10:00:00", "12:00:00", 175, ["worker {n} idle", "worker {n} picked job {n}", "flush {n} rows", "ping ok"], LV)
    ev += [("10:31:14", "ERROR", "job 55 failed: upstream returned 503"), ("10:19:30", "FATAL", "config reload aborted: invalid section [limits]"), ("11:40:00", "ERROR", "job 61 failed: upstream returned 503")]
    text = render(ev, fmt_iso(d, "w"))
    n = lineno(text, "config reload aborted")
    make("log-33758", sub="locate", task_type="locate_error", desc="A FATAL line precedes the first ERROR line; the user asks for the first line at ERROR severity or worse",
         files={"worker.log": text}, turns=[T("worker.log 里最先出现的严重问题（ERROR 或 FATAL 都算）在第几行？那是什么问题？", [str(n), "limits"], token=False, req=["bash"]),
                                           T("只算 ERROR 的话，第一条是第几行？", [str(lineno(text, "job 55 failed"))], token=True)],
         truth="ls=files['worker.log'].splitlines()\nanswers=[str([k for k,l in enumerate(ls,1) if ' ERROR ' in l or ' FATAL ' in l][0]), str([k for k,l in enumerate(ls,1) if ' ERROR ' in l][0])]",
         ref=[("grep -n -E ' (ERROR|FATAL) ' worker.log | head -1", "%d:" % n)],
         notes={"traps": "FATAL is not ERROR; the first ERROR is a different, later line.", "steps": "grep -n -E.", "unique": "FATAL line %d, ERROR line %d" % (n, lineno(text, 'job 55 failed'))},
         traps=("TR-DEFN", "TR-DECOY"), axes=("OBS",), rc=5)


@reg
def e6():
    r = rng("e6"); d = "2026-09-04"
    ev = noise(r, "15:00:00", "17:00:00", 150, ["handled request {n}", "cache hit {n}", "session {n} ok"], LV)
    base = render(ev, fmt_iso(d, "app")).splitlines()
    err = ["2026-09-04 15:58:21 ERROR app: unhandled exception in handler render_page", "Traceback (most recent call last):", "  File \"app/views.py\", line 88, in render_page",
           "    return tpl.render(ctx)", "KeyError: 'user_name'"]
    pos = 100
    lines = base[:pos] + err + base[pos:]
    # make timestamps monotone-neutral: acceptable, only line numbers matter
    text = "\n".join(lines) + "\n"
    n = pos + 1
    kline = pos + 5
    make("log-33759", sub="locate", task_type="locate_error", desc="Python traceback spans several lines; asks the line of the first error and the last line of its traceback",
         files={"app.log": text}, turns=[T("app.log 里第一次 ERROR 从第几行开始？", [str(n)], token=True, req=["bash"]),
                                         T("它那段 traceback 最后一行（真正的异常）是什么？在第几行？", ["KeyError", str(kline)], token=False)],
         truth="ls=files['app.log'].splitlines()\nanswers=[str([k for k,l in enumerate(ls,1) if ' ERROR ' in l][0])]",
         ref=[("grep -n ' ERROR ' app.log | head -1", "%d:" % n), ("sed -n '%d,%dp' app.log" % (n, kline), "KeyError")],
         notes={"traps": "The traceback continues on following lines that have no level.", "steps": "grep -n then sed -n range.", "unique": "ERROR at %d, KeyError at %d" % (n, kline)},
         traps=("TR-EARLYHIT",), axes=("STP",), rc=4)


@reg
def e7():
    r = rng("e7"); d = "2026-09-10"
    a = noise(r, "18:00:00", "20:00:00", 85, ["a: request {n} ok", "a: lease renew", "a: tick"], LV) + [("19:12:50", "ERROR", "a: write conflict on key k91")]
    b = noise(r, "18:00:00", "20:00:00", 85, ["b: request {n} ok", "b: lease renew", "b: tick"], LV) + [("18:47:03", "ERROR", "b: replica lag 42s exceeds limit")]
    f = {"svc-a.log": render(a, fmt_iso(d, "a")), "svc-b.log": render(b, fmt_iso(d, "b"))}
    make("log-33760", sub="locate", task_type="locate_error", desc="Which of two services logged an error first",
         files=f, turns=[T("svc-a.log 和 svc-b.log 是同一个晚上两个服务的日志。哪个服务先出的错？第一条错误是几点？", ["svc-b", "18:47"], token=False, req=["bash"]),
                         T("另一个服务的第一条错误呢？", ["19:12"], token=True)],
         truth="answers=['svc-b','19:12']" if False else "answers=['svc-b','19:12']",
         ref=[("grep -h ' ERROR ' svc-a.log svc-b.log | sort | head -1", "18:47:03")],
         notes={"traps": "File a is listed first and its error is notable; b errs earlier.", "steps": "grep ERROR each, compare time.", "unique": "b at 18:47:03; a at 19:12:50"},
         traps=("TR-MULTISRC", "TR-DECOY"), axes=("CHN", "OBS"), rc=5)


@reg
def e8():
    r = rng("e8"); d = "2026-09-14"
    ev = noise(r, "08:00:00", "10:00:00", 170, ["conn {n} opened", "conn {n} closed", "query {n} took {ms}ms"], LV)
    ev += [("08:20:00", "INFO", "operator note: simulated ERROR drill started (not a real incident)"), ("08:55:31", "ERROR", "conn 4402 reset by peer while sending response"), ("09:30:10", "ERROR", "conn 4471 reset by peer")]
    text = render(ev, fmt_iso(d, "net"))
    n = lineno(text, "conn 4402 reset")
    make("log-33761", sub="locate", task_type="locate_error", desc="A drill note mentions ERROR in an INFO line before the real first error",
         files={"net.log": text}, turns=[T("Find the first line in net.log whose level is ERROR. Give the line number and the time.", [str(n), "08:55"], token=True, req=["bash"]),
                                         T("What does that line say went wrong?", ["reset by peer"])],
         truth="ls=files['net.log'].splitlines()\nanswers=[str([k for k,l in enumerate(ls,1) if l.split()[2]=='ERROR'][0])]",
         ref=[("grep -n 'ERROR net:' net.log | head -1", "%d:" % n)],
         notes={"traps": "'ERROR' appears inside an INFO message earlier.", "steps": "the INFO note contains ERROR as a word; match the level column instead (grep -n 'ERROR net:').", "unique": "line %d" % n},
         traps=("TR-EARLYHIT", "TR-DECOY"), axes=("STP", "OBS"), rc=5)
