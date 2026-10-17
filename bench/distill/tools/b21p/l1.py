"""logs root_cause 33736-33744."""
from common import *
from lg import *

B = []


def reg(f):
    B.append(f)
    return f


def rc_case(cid, desc, files, turns, truth, notes, traps=("TR-MULTISRC", "TR-DECOY"), ref=(), policy=BASH):
    make(cid, sub="rootcause", task_type="root_cause", desc=desc, files=files, turns=turns, truth=truth, notes=notes,
         traps=traps, axes=("CHN", "OBS"), rc=6, ref=ref, policy=policy)


@reg
def r1():
    r = rng("r1"); d = "2026-09-15"
    sysl = noise(r, "01:00:00", "04:00:00", 45, ["cron: job {n} finished", "kernel: eth0 link ok", "sshd: session {n} closed", "ntpd: offset {ms}us"])
    sysl += [("02:41:12", "WARN", "monitor: filesystem /var/lib/postgresql usage 100% (0 bytes free)"), ("03:05:40", "INFO", "cleanup: removed 41 wal archives, /var/lib/postgresql usage 61%")]
    db = noise(r, "01:00:00", "04:00:00", 45, ["checkpoint complete: wrote {n} buffers", "autovacuum: table orders done", "connection authorized: user=app"])
    db += [("02:10:05", "WARN", "slow query {n} ms: select * from audit"), ("02:43:09", "FATAL", "could not write to file \"pg_wal/0000000100000A\": No space left on device"),
           ("03:06:02", "INFO", "database system is ready to accept connections")]
    api = noise(r, "01:00:00", "04:00:00", 50, ["GET /v1/items 200 {ms}ms", "POST /v1/cart 200 {ms}ms", "GET /health 200 1ms"])
    api += [("02:43:15", "ERROR", "POST /v1/orders 500 db write failed"), ("02:43:40", "ERROR", "GET /v1/items 500 db unavailable"), ("02:50:00", "ERROR", "GET /health 503 db unavailable"),
            ("03:06:30", "INFO", "GET /health 200 3ms")]
    f = {"logs/system.log": render(sysl, fmt_iso(d, "sys")), "logs/postgres.log": render(db, fmt_iso(d, "pg")), "logs/api.log": render(api, fmt_iso(d, "api"))}
    rc_case("log-33736", "Disk full on the database volume causes api 500s; api recovery time asked next", f,
            [T("昨晚 API 出现一阵 500 错误。看 logs 目录里的三份日志，根本原因是什么？最早的异常信号是几点？",
               ["02:41"], any_=["磁盘", "空间", "disk", "No space", "no space", "100%", "存储"], token=True
               , exc=["慢查询是根本", "慢查询导致"], syn=True),
             T("API 是几点恢复正常的？", ["03:06"], token=True)],
            "answers=['02:41','03:06']",
            {"traps": "Slow query WARN at 02:10 is a decoy; api errors are a symptom; the first signal is the filesystem 100% line in system.log at 02:41, db FATAL at 02:43.", "steps": "grep ERROR/FATAL/WARN across logs, order by time.", "unique": "Disk full from 02:41; API healthy 03:06."},
            ref=[("grep -h -E 'WARN|FATAL|ERROR' logs/*.log | sort | head -3", "02:10:05")])


@reg
def r2():
    r = rng("r2"); d = "2026-03-02"
    gw = noise(r, "08:00:00", "12:00:00", 55, ["GET /api/v2/users 200 {ms}ms", "GET /static/app.js 200 {ms}ms", "POST /api/v2/login 200 {ms}ms"])
    gw += [("10:00:03", "ERROR", "tls handshake failed: peer reports certificate expired (cn=api.example.test)"), ("10:00:09", "ERROR", "tls handshake failed: certificate expired"),
           ("10:20:44", "INFO", "reloaded certificate cn=api.example.test notAfter=2027-03-02")]
    cm = noise(r, "08:00:00", "12:00:00", 40, ["scan: {n} certificates checked", "ocsp stapling refreshed", "inventory sync ok"])
    cm += [("07:55:00", "WARN", "certificate cn=api.example.test expires in 5 minutes (notAfter=2026-03-02T10:00:00Z)"), ("10:15:30", "INFO", "renewal request accepted for cn=api.example.test"),
           ("09:00:00", "WARN", "certificate cn=old-admin.example.test expires in 29 days")]
    cl = noise(r, "08:00:00", "12:00:00", 40, ["client {n} connected", "retry budget ok", "poll cycle {n} done"])
    cl += [("10:00:12", "ERROR", "request to api.example.test failed: SSL routines: certificate verify failed"), ("10:00:30", "ERROR", "retry 3/3 failed, giving up"), ("10:21:00", "INFO", "request to api.example.test ok")]
    f = {"gateway.log": render(gw, fmt_iso(d, "gw")), "certmon.log": render(cm, fmt_iso(d, "certmon")), "client.log": render(cl, fmt_iso(d, "cli"))}
    rc_case("log-33737", "Expired TLS certificate seen in three logs; the earliest warning and the recovery time", f,
            [T("Clients were unable to reach the API this morning. Using the three logs here, what was the root cause, and at what time did the failures start?", ["10:00"], any_=["certificate", "cert", "TLS", "SSL", "expired", "证书"], token=True, syn=True),
             T("When was it fixed?", ["10:20"], any_=[], token=True)],
            "answers=['10:00','10:20']",
            {"traps": "Another certificate warning (old-admin) is unrelated; client sees a generic verify failure.", "steps": "grep ERROR/WARN across logs, sort by time.", "unique": "api cert expired at 10:00; reloaded 10:20:44."},
            ref=[("grep -h ERROR gateway.log | head -1", "10:00:03")])


@reg
def r3():
    r = rng("r3"); d = "2026-09-11"
    dep = noise(r, "13:00:00", "17:00:00", 30, ["deploy {n} started for svc billing", "deploy {n} finished"], lvls=("INFO",))
    dep += [("14:32:10", "INFO", "applied config change #5521: pool.max_connections 200 -> 20 (service=orders)"), ("14:32:30", "INFO", "orders restarted"),
            ("15:10:00", "INFO", "applied config change #5522: log.level debug -> info (service=billing)")]
    app = noise(r, "13:00:00", "17:00:00", 55, ["order {n} created", "order {n} paid", "cache hit ratio 0.9{ms}"])
    app += [("14:41:07", "WARN", "connection pool wait time 1200ms"), ("14:47:55", "ERROR", "timeout waiting for a database connection after 5000ms"),
            ("14:48:20", "ERROR", "timeout waiting for a database connection after 5000ms"), ("16:02:00", "INFO", "pool.max_connections now 200, pool healthy")]
    mon = noise(r, "13:00:00", "17:00:00", 40, ["cpu {n}%", "mem {n}MB", "disk ok"])
    mon += [("14:48:00", "ALERT", "orders error rate 38% (threshold 5%)"), ("16:03:00", "INFO", "orders error rate 0.4%")]
    f = {"deploy.log": render(dep, fmt_br(d, "")), "orders.log": render(app, fmt_br(d, "orders")), "monitor.log": render(mon, fmt_br(d, "mon"))}
    rc_case("log-33738", "Pool size reduced by a config change causes timeouts later; asks which change and when", f,
            [T("下午订单服务一直超时。三份日志里能看出是哪次变更引起的吗？说出是哪个配置、改成了多少，还有变更是几点。", ["14:32"], any_=["max_connections", "连接数", "连接池", "pool"], token=True, syn=True),
             T("那个变更是什么时候撤销的、问题是几点恢复的？", ["16:02"], token=True)],
            "answers=['14:32','16:02']",
            {"traps": "Another config change (log.level) at 15:10 is unrelated; errors start 15 minutes after the change.", "steps": "read deploy.log, grep ERROR orders.log.", "unique": "#5521 at 14:32 caused timeouts."},
            ref=[("grep -h 'config change' deploy.log", "5521")])


@reg
def r4():
    r = rng("r4"); d = "2026-06-20"
    res = noise(r, "21:00:00", "23:59:00", 45, ["dns: cache hit for host{n}", "dns: query a.example.test ok {ms}ms", "dns: refreshed zone"], lvls=("INFO", "DEBUG"))
    res += [("22:14:00", "WARN", "dns: upstream 10.8.0.2 not responding, failing over to 10.8.0.3"), ("22:14:30", "ERROR", "dns: all upstreams failed for payments.internal.test (SERVFAIL)"),
            ("22:44:10", "INFO", "dns: upstream 10.8.0.2 responding again")]
    pay = noise(r, "21:00:00", "23:59:00", 50, ["charge {n} ok", "refund {n} ok", "ledger sync ok"])
    pay += [("22:14:35", "ERROR", "charge failed: could not resolve ledger.internal.test"), ("22:20:00", "ERROR", "charge failed: could not resolve ledger.internal.test"),
            ("22:44:20", "INFO", "charge ok after resolver recovery")]
    net = noise(r, "21:00:00", "23:59:00", 35, ["link up eth0", "bgp session established", "packet loss 0.{n}%"])
    net += [("22:13:40", "WARN", "switch sw-3 port 12 flapping, upstream resolver subnet unreachable"), ("22:43:50", "INFO", "switch sw-3 port 12 stable after cable replacement")]
    f = {"resolver.log": render(res, fmt_iso(d, "")), "payments.log": render(pay, fmt_iso(d, "")), "network.log": render(net, fmt_iso(d, ""))}
    rc_case("log-33739", "Payment failures trace back to a flapping switch port, upstream of DNS errors", f,
            [T("The payment service could not resolve ledger.internal.test for half an hour last night. Digging through resolver.log, payments.log and network.log, what is the underlying cause and when did the trouble first show up?", ["22:13"], any_=["switch", "port", "flapping", "cable", "network"], token=True, syn=True)],
            "answers=['22:13']",
            {"traps": "DNS and payment errors are symptoms; network.log has the earliest signal 22:13:40.", "steps": "merge logs by time.", "unique": "sw-3 port 12 flapping at 22:13."},
            ref=[("grep -h -E 'WARN|ERROR' *.log | sort -k2 | head -2", "22:13:40")], traps=("TR-MULTISRC", "TR-DECOY"))


@reg
def r5():
    r = rng("r5"); d = "2026-09-09"
    w = noise(r, "05:00:00", "08:00:00", 60, ["worker{n} job {n} done", "heartbeat ok", "queue depth {n}"])
    w += [("05:30:00", "INFO", "rss=1.1GB"), ("06:00:00", "INFO", "rss=2.0GB"), ("06:30:00", "INFO", "rss=3.1GB"), ("06:50:00", "WARN", "rss=3.9GB, limit 4.0GB"),
          ("07:02:11", "ERROR", "worker exited: signal 9"), ("07:02:40", "INFO", "worker restarted pid=4412"), ("07:03:30", "ERROR", "worker exited: signal 9")]
    k = noise(r, "05:00:00", "08:00:00", 40, ["usb: device {n}", "eth0: link ok", "audit: syscall {n}"])
    k += [("07:02:10", "ERR", "oom-killer: killed process 4301 (worker) total-vm 5.2GB"), ("07:03:29", "ERR", "oom-killer: killed process 4412 (worker)")]
    sv = noise(r, "05:00:00", "08:00:00", 40, ["supervisor: tick", "supervisor: health ok"])
    sv += [("07:02:40", "WARN", "supervisor: worker died, restart 1/5"), ("07:03:31", "WARN", "supervisor: worker died, restart 2/5"), ("07:10:00", "INFO", "supervisor: deployed hotfix 'cap batch size', worker stable")]
    f = {"worker.log": render(w, fmt_iso(d, "")), "kernel.log": render(k, fmt_iso(d, "")), "supervisor.log": render(sv, fmt_iso(d, ""))}
    rc_case("log-33740", "Worker memory climbs until the kernel kills it; asks cause and when the first kill happened", f,
            [T("早上 worker 老是重启。三份日志里，它为什么挂的？第一次被杀是几点？", ["07:02"], any_=["内存", "OOM", "oom", "memory", "rss", "泄漏", "泄露"], token=True, syn=True),
             T("worker 的 rss 是几点第一次超过 3GB 的？", ["06:30"], token=True)],
            "answers=['07:02','06:30']",
            {"traps": "Worker log says only 'signal 9'; the reason is in kernel.log; rss lines reveal the trend.", "steps": "grep rss, grep oom.", "unique": "OOM at 07:02:10."},
            ref=[("grep -h oom-killer kernel.log | head -1", "07:02:10")])


@reg
def r6():
    r = rng("r6"); d = "2026-08-27"
    dep = noise(r, "09:00:00", "11:30:00", 25, ["rollout {n}: node web-{n} healthy", "image pull ok"], lvls=("INFO",))
    dep += [("10:05:00", "INFO", "rollout v2.8.1 started (3 nodes)"), ("10:05:40", "INFO", "web-1 updated to v2.8.1"), ("10:12:00", "INFO", "rollback to v2.8.0 started"), ("10:13:30", "INFO", "rollback finished")]
    app = noise(r, "09:00:00", "11:30:00", 55, ["request {n} ok {ms}ms", "session {n} refreshed"])
    app += [("10:05:45", "ERROR", "startup failed: required env var PAYMENT_KEY is not set"), ("10:05:50", "INFO", "process exiting with code 3"),
            ("10:06:20", "ERROR", "startup failed: required env var PAYMENT_KEY is not set"), ("10:13:40", "INFO", "web-1 started v2.8.0 ok")]
    lb = noise(r, "09:00:00", "11:30:00", 45, ["backend web-{n} up", "conn {n} routed", "stats ok"])
    lb += [("10:06:30", "WARN", "backend web-1 health check failed 3/3, removing from pool"), ("10:07:00", "ERROR", "no healthy backend for /checkout (1 of 3 pool slots)") if False else ("10:07:00", "WARN", "pool capacity 2/3"),
           ("10:13:50", "INFO", "backend web-1 up, pool capacity 3/3")]
    f = {"deploy.log": render(dep, fmt_br(d, "")), "web.log": render(app, fmt_br(d, "web")), "lb.log": render(lb, fmt_br(d, "lb"))}
    rc_case("log-33741", "A rollout missing an env var crash-loops one node; load balancer ejects it", f,
            [T("What made web-1 drop out of the load balancer this morning? Check deploy.log, web.log and lb.log, and tell me the version that broke it and the missing setting.", ["v2.8.1", "PAYMENT_KEY"], any_=[]),
             T("What time did the rollback finish?", ["10:13"], token=True)],
            "answers=['v2.8.1','10:13']",
            {"traps": "lb.log only shows health check failures.", "steps": "grep ERROR web.log.", "unique": "v2.8.1 missing PAYMENT_KEY; rollback finished 10:13:30."},
            ref=[("grep -h 'env var' web.log | head -1", "PAYMENT_KEY")])


@reg
def r7():
    r = rng("r7"); d = "2026-09-03"
    bk = noise(r, "01:30:00", "04:30:00", 40, ["backup: copied {n} files", "backup: verified chunk {n}"])
    bk += [("02:00:00", "INFO", "backup: started, acquiring lock /var/lock/data.lock"), ("03:40:00", "INFO", "backup: finished, lock released")]
    cr = noise(r, "01:30:00", "04:30:00", 45, ["cron: tick", "cron: job {n} scheduled"])
    cr += [("02:30:00", "INFO", "cron: start report-export"), ("02:30:05", "WARN", "cron: report-export waiting for /var/lock/data.lock"), ("03:40:05", "INFO", "cron: report-export got lock"),
           ("03:50:00", "INFO", "cron: report-export finished (79 minutes late)")]
    q = noise(r, "01:30:00", "04:30:00", 50, ["queue depth {n}", "consumer {n} ack"])
    q += [("03:00:00", "WARN", "queue depth 5000 (limit 4000)"), ("03:35:00", "ERROR", "producers blocked: queue full"), ("03:52:00", "INFO", "queue depth back to normal")]
    f = {"backup.log": render(bk, fmt_iso(d, "bk")), "cron.log": render(cr, fmt_iso(d, "cron")), "queue.log": render(q, fmt_iso(d, "q"))}
    rc_case("log-33742", "Report export is blocked by the backup's lock; queue overflow is a downstream symptom", f,
            [T("夜里队列堆满、报表导出晚了一个多小时。结合 backup.log、cron.log、queue.log，导出为什么晚？等的是什么，被谁占着？", ["data.lock"], any_=["备份", "backup"], syn=False),
             T("锁是几点释放的？", ["03:40"], token=True)],
            "answers=['data.lock','03:40']",
            {"traps": "Queue overflow looks like the root cause; the lock holder is the backup.", "steps": "read cron WARN, backup lock lines.", "unique": "data.lock held by backup 02:00-03:40."},
            ref=[("grep -h 'lock' backup.log cron.log", "data.lock")])


@reg
def r8():
    r = rng("r8"); d = "2026-04-12"
    ntp = noise(r, "16:00:00", "18:00:00", 40, ["ntpd: offset +{ms}ms", "ntpd: poll 64s", "ntpd: peer sync ok"])
    ntp += [("16:41:00", "WARN", "ntpd: clock stepped by -420.3s (time source reconfigured)"), ("16:41:02", "INFO", "ntpd: synchronized")]
    au = noise(r, "16:00:00", "18:00:00", 55, ["login ok user{n}", "token issued for user{n}", "refresh ok"])
    au += [("16:41:10", "ERROR", "token rejected: not valid yet (nbf in the future) for user214"), ("16:41:12", "ERROR", "token rejected: not valid yet (nbf in the future) for user221"),
           ("16:48:20", "INFO", "token validation back to normal")]
    gw = noise(r, "16:00:00", "18:00:00", 40, ["GET /me 200 {ms}ms", "GET /feed 200 {ms}ms"])
    gw += [("16:41:15", "ERROR", "GET /me 401"), ("16:41:20", "ERROR", "GET /feed 401"), ("16:48:30", "INFO", "GET /me 200 12ms")]
    f = {"ntp.log": render(ntp, fmt_br(d, "")), "auth.log": render(au, fmt_br(d, "auth")), "gateway.log": render(gw, fmt_br(d, "gw"))}
    rc_case("log-33743", "Clock stepped backwards causes tokens to look not-yet-valid", f,
            [T("Users got a burst of 401s late afternoon. What is the root cause? Use the three log files and give the time of the first event that set it off.", ["16:41"], any_=["clock", "time", "ntp", "NTP", "nbf", "skew"], token=True, syn=True)],
            "answers=['16:41']",
            {"traps": "401 is a symptom; auth says not valid yet; ntp.log shows clock step.", "steps": "grep ERROR/WARN in each, order by time.", "unique": "Clock step 16:41:00."},
            ref=[("grep -h WARN ntp.log", "clock stepped")])


@reg
def r9():
    r = rng("r9"); d = "2026-08-05"
    sec_ = noise(r, "13:30:00", "15:30:00", 35, ["vault: lease {n} renewed", "vault: audit write ok"])
    sec_ += [("14:00:00", "INFO", "vault: rotated API key for partner mapservice, old key revoked"), ("14:00:01", "WARN", "vault: 2 consumers still hold key id k-1187")]
    cl = noise(r, "13:30:00", "15:30:00", 55, ["geocode {n} ok", "tile fetch {n} ok", "cache refreshed"])
    cl += [("14:00:25", "ERROR", "mapservice returned 401 invalid api key"), ("14:00:55", "ERROR", "mapservice returned 401 invalid api key"), ("14:21:10", "INFO", "reloaded credentials from vault, key id k-1202"),
           ("14:21:20", "INFO", "geocode ok")]
    jb = noise(r, "13:30:00", "15:30:00", 40, ["batch {n} started", "batch {n} done"])
    jb += [("14:01:30", "ERROR", "batch 31 failed: dependency mapservice unavailable (401)"), ("14:22:00", "INFO", "batch 31 retried ok")]
    f = {"vault.log": render(sec_, fmt_iso(d, "vault")), "client.log": render(cl, fmt_iso(d, "client")), "jobs.log": render(jb, fmt_iso(d, "jobs"))}
    rc_case("log-33744", "Key rotation revoked the old key; the client kept using it until reload", f,
            [T("下午地图服务一直返回 401，批处理也失败了。看 vault.log、client.log、jobs.log，根因是什么，是几点发生的？", ["14:00"], any_=["轮换", "rotat", "吊销", "revoked", "密钥", "key"], token=True, syn=True),
             T("客户端几点用上了新密钥？", ["14:21"], token=True)],
            "answers=['14:00','14:21']",
            {"traps": "401 looks like a client bug; the rotation line is in vault.log.", "steps": "grep rotated/401.", "unique": "Rotation at 14:00:00; new key at 14:21:10."},
            ref=[("grep -h rotated vault.log", "14:00:00")])
