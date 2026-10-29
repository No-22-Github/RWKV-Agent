"""G1 logs: log-35509..35516."""
import random

import fill
from common import make, T

B = []


def reg(f):
    B.append(f)
    return f


def R(k):
    return random.Random("b23g-log-" + k)


@reg
def l01():
    r = R("01")
    pl = [(70, lambda ts: "%s WARN  jobs: job=nightly-rollup retry exit_code=2" % ts),
          (390, lambda ts: "%s ERROR jobs: job=nightly-compaction failed exit_code=137" % ts)]
    lines = fill.log_with_plants(r, 520, pl, day=(2026, 9, 14))
    make("log-35509", sub="G1", task_type="locate_error", desc="Worker log, failed job exit code deep in the file",
         path="logs/ingest-worker-0914.log", lines=lines,
         turns=[T("In logs/ingest-worker-0914.log, what exit code did the nightly-compaction job fail with?", "137", "job=nightly-compaction failed",
                  "job=nightly-rollup retry", excl=["exit_code=2", "exit code 2"])],
         notes=("The first screen has a retry of a different job with exit_code=2.", "read_file -> search_text 'nightly-compaction' -> 137.",
                "One failure line for that job."))


@reg
def l02():
    r = R("02")
    pl = [(80, lambda ts: "%s INFO  net: certificate renewal scheduled host=edge-ams-02" % ts),
          (420, lambda ts: "%s ERROR net: certificate expired host=edge-fra-07 peer p31" % ts)]
    lines = fill.log_with_plants(r, 600, pl, day=(2026, 9, 21), start_sec=3600)
    make("log-35510", sub="G1", task_type="locate_error", desc="Gateway cluster log, first certificate-expired error on a later screen",
         path="logs/gateway-cluster-0921.log", lines=lines,
         turns=[T("Which host first reported a 'certificate expired' error in logs/gateway-cluster-0921.log?", "edge-fra-07", "certificate expired host",
                  "certificate renewal scheduled", excl=["edge-ams-02"])],
         notes=("The first screen mentions a certificate renewal on another host.", "read_file -> search_text 'expired' -> edge-fra-07.",
                "Only one expired line."))


@reg
def l03():
    r = R("03")
    pl = [(75, lambda ts: "%s db01 kernel: oom_adj changed for process 4411 (postgres)" % ts),
          (450, lambda ts: "%s db01 kernel: Out of memory: Killed process 28817 (java) total-vm:6291456kB" % ts)]
    lines = fill.log_with_plants(r, 640, pl, fmt="syslog", day=(2026, 9, 7))
    make("log-35511", sub="G1", task_type="locate_error", desc="Syslog, OOM kill PID deep in the file",
         path="logs/syslog-dbhost-0907.log", lines=lines,
         turns=[T("Which PID did the OOM killer terminate according to logs/syslog-dbhost-0907.log?", "28817", "Killed process 28817",
                  "oom_adj changed for process 4411", excl=["4411"])],
         notes=("The first screen has a related oom_adj line for another PID.", "read_file -> search_text 'Killed process' -> 28817.", "One kill line."))


@reg
def l04():
    r = R("04")
    pl = [(65, lambda ts: "%s INFO  batch: summary job=invoice-preview rows_written=1204 duration=38s" % ts),
          (410, lambda ts: "%s INFO  batch: summary job=invoice-export rows_written=48213 duration=412s" % ts)]
    lines = fill.log_with_plants(r, 560, pl, day=(2026, 8, 30))
    make("log-35512", sub="G1", task_type="lookup_value", desc="Batch log final summary, rows written and duration",
         path="logs/billing-batch-0830.log", lines=lines,
         turns=[T("How many rows did the invoice-export batch write according to logs/billing-batch-0830.log?", 48213, "summary job=invoice-export",
                  "summary job=invoice-preview", excl=["1204", "1,204"]),
                T("And how long did that batch take?", ("any", ["412s", "412 s", "412 sec"]), "duration=412s", "duration=38s", excl=["38s"])],
         notes=("The first screen shows the summary of a preview job (1204 rows, 38s).", "read_file -> search_text 'invoice-export' -> 48213 and 412s.",
                "Single summary line for invoice-export."))


@reg
def l05():
    r = R("05")
    pl = [(85, lambda ts: "%s INFO  deploy: ROLLBACK build=7688 environment=staging" % ts),
          (470, lambda ts: "%s WARN  deploy: ROLLBACK build=7731 environment=production reason=health-check" % ts)]
    lines = fill.log_with_plants(r, 680, pl, day=(2026, 11, 3))
    make("log-35513", sub="G1", task_type="locate_error", desc="Deploy pipeline log, production rollback build number",
         path="logs/deploy-pipeline-1103.log", lines=lines,
         turns=[T("Which build was rolled back in production, per logs/deploy-pipeline-1103.log?", "7731", "build=7731", "build=7688", excl=["7688"])],
         notes=("The first screen has a staging rollback with another build number.", "read_file -> search_text 'production' -> 7731.", "One production rollback."))


@reg
def l06():
    r = R("06")
    pl = [(70, lambda ts: "%s WARN  db: 连接池使用率 85%%，接近上限" % ts),
          (420, lambda ts: "%s ERROR db: 连接池耗尽，新请求被拒绝 active=64" % ts)]
    lines = fill.log_with_plants(r, 600, pl, lang="zh", day=(2026, 9, 12))
    lines = [l for l in lines]
    ts_line = [l for l in lines if "连接池耗尽" in l][0]
    when = ts_line.split()[0]
    make("log-35514", sub="G1", task_type="locate_error", desc="订单服务日志，连接池耗尽出现在后部",
         path="logs/订单服务-0912.log", lines=lines,
         turns=[T("logs/订单服务-0912.log 里，数据库连接池第一次耗尽是在几点几分几秒？", when, "连接池耗尽", "连接池使用率", excl=[])],
         notes=("第一屏有同一连接池的使用率告警，但不是耗尽。", "read_file -> search_text '耗尽' -> 时间戳。", "耗尽只出现一行。"))
    # excl: the decoy time must not be required away; the decoy line time is a different time anyway.


@reg
def l07():
    r = R("07")
    pl = [(60, lambda ts: "%s INFO  风控: 汇总（预跑）拦截=57 放行=3120" % ts),
          (440, lambda ts: "%s INFO  风控: 汇总（正式）拦截=342 放行=18755" % ts)]
    lines = fill.log_with_plants(r, 580, pl, lang="zh", day=(2026, 9, 20))
    make("log-35515", sub="G1", task_type="lookup_value", desc="风控批处理日志，正式汇总在后部",
         path="logs/风控批处理-0920.log", lines=lines,
         turns=[T("logs/风控批处理-0920.log 里，正式汇总一共拦截了多少笔交易？", "342", "汇总（正式）", "汇总（预跑）", excl=["拦截=57", "拦截 57"])],
         notes=("第一屏是预跑汇总（拦截 57）。", "read_file -> search_text '汇总' -> 342。", "正式汇总只有一行。"))


@reg
def l08():
    r = R("08")
    pl = [(75, lambda ts: "%s WARN  备份: 增量备份重试 错误码=E2031" % ts),
          (400, lambda ts: "%s ERROR 备份: 全量备份失败 错误码=E4017" % ts)]
    lines = fill.log_with_plants(r, 540, pl, lang="zh", day=(2026, 10, 15))
    make("log-35516", sub="G1", task_type="locate_error", desc="备份任务日志，全量备份失败错误码",
         path="logs/备份任务-1015.log", lines=lines,
         turns=[T("logs/备份任务-1015.log 里全量备份失败时报的错误码是什么？", "E4017", "全量备份失败", "增量备份重试", excl=["E2031"])],
         notes=("第一屏有增量备份的另一个错误码。", "read_file -> search_text '全量' -> E4017。", "全量失败只有一行。"))
