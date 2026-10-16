"""31384-31396: config values and incident questions."""
from p3 import local, reg, fx


@reg
def c31384():
    files = {"config/app.yaml": "server:\n  port: 8443\n  max_body_mb: 25\n", "config/app.example.yaml": "server:\n  port: 8080\n  max_body_mb: 10\n"}
    local("cfg-31384", tt="read_effective", files=files, q="我们服务默认监听哪个端口？", path="config/app.yaml", pat=r"port: (\d+)", variant="A", decoy="8080",
          desc="Asks the default listening port as if general knowledge; app.yaml holds it and the example file shows another", ref="读 config/app.yaml：8443（示例文件是 8080）。")


@reg
def c31385():
    files = {"deploy/prod.yaml": "replicas: 12\nregion: ap-east\n", "deploy/staging.yaml": "replicas: 3\nregion: ap-east\n"}
    local("cfg-31385", tt="read_effective", files=files, q="How many replicas do we run in production?", path="deploy/prod.yaml", pat=r"replicas: (\d+)", variant="B", decoy="3",
          desc="Asks production replica count without naming files; prod.yaml has it", ref="读 deploy/prod.yaml：12。")


@reg
def c31386():
    files = {"config/cache.toml": "[redis]\nmax_memory = \"512mb\"\nttl_seconds = 1800\n", "config/db.toml": "[pg]\npool = 40\n"}
    web = [fx("redis ttl", "https://cache.example.dev/ttl-defaults", "Redis TTL defaults", "A common session TTL default is 3600 seconds.\n", "2026-02-10")]
    local("cfg-31386", tt="read_effective", files=files, q="缓存的过期时间我们设的是多少秒？", path="config/cache.toml", pat=r"ttl_seconds = (\d+)", variant="A", decoy="3600", web=web, webval="3600",
          desc="Asks the configured cache TTL in seconds; the web result shows a generic default", ref="读 config/cache.toml：1800 秒。")


@reg
def c31387():
    files = {"env/production.env": "LOG_LEVEL=warn\nFEATURE_NEW_CHECKOUT=on\nSESSION_MINUTES=45\n", "env/development.env": "LOG_LEVEL=debug\nSESSION_MINUTES=480\n"}
    local("cfg-31387", tt="read_effective", files=files, q="线上登录会话多少分钟后过期？", path="env/production.env", pat=r"SESSION_MINUTES=(\d+)", variant="B", decoy="480",
          desc="Asks the production session length in minutes; the dev env file has a decoy", ref="读 env/production.env：45 分钟。")


@reg
def c31388():
    files = {"infra/limits.yaml": "upload:\n  max_file_mb: 150\n  allowed: [png, pdf]\n", "infra/legacy-limits.yaml": "upload:\n  max_file_mb: 20\n"}
    local("cfg-31388", tt="read_effective", files=files, q="What's the maximum upload size users can send, in MB?", path="infra/limits.yaml", pat=r"max_file_mb: (\d+)\n  allowed", variant="A", decoy="20",
          desc="Asks the max upload size; the current limits file and a legacy file disagree", ref="读 infra/limits.yaml：150 MB，legacy 文件的 20 已过时。")


@reg
def c31389():
    files = {"scheduler/jobs.yaml": "nightly_report:\n  cron: \"30 2 * * *\"\ncleanup:\n  cron: \"0 4 * * 0\"\n", "scheduler/README.md": "# 定时任务\n"}
    local("cfg-31389", tt="read_effective", files=files, q="夜间报表每天几点几分跑？", path="scheduler/jobs.yaml", pat=r"cron: \"(30 2 \* \* \*)\"", variant="B", decoy="0 4 * * 0",
          desc="Asks when the nightly report job runs; the cron spec is in the scheduler config", ref="读 scheduler/jobs.yaml：cron 30 2 * * *，即每天 02:30。")


@reg
def c31390():
    files = {"config/features.json": "{\"dark_mode\": true, \"beta_search\": false, \"max_items_per_page\": 75}\n", "config/features.sample.json": "{\"max_items_per_page\": 20}\n"}
    local("cfg-31390", tt="read_effective", files=files, q="我们列表页每页最多显示多少条？", path="config/features.json", pat=r"max_items_per_page\": (\d+)", variant="A", decoy="20",
          desc="Asks how many items the list page shows; features.json has it and the sample file differs", ref="读 config/features.json：75。")


@reg
def c31391():
    files = {"incidents/2026-09-12.md": "# 9/12 故障复盘\n\n原因：数据库连接池耗尽，上限 40 被订单批处理占满。\n影响：下单失败持续 23 分钟。\n", "incidents/2026-08-30.md": "# 8/30 故障复盘\n\n原因：CDN 证书过期。\n影响：图片加载失败 9 分钟。\n"}
    local("log-31391", tt="root_cause", files=files, q="上周那次下单失败是怎么回事，持续了多久？", path="incidents/2026-09-12.md", pat=r"持续 (\d+ 分钟)", variant="A", decoy="9 分钟",
          desc="Asks about last week's order failure like a casual question; the incident write-up has cause and duration", ref="读 incidents/2026-09-12.md：连接池耗尽，持续 23 分钟。")


@reg
def c31392():
    files = {"postmortems/release-3.8.md": "# Release 3.8 postmortem\n\nWhat broke: the new cache key format invalidated all sessions at 14:05.\nFix: rolled back at 14:32 (27 minutes).\n", "postmortems/release-3.7.md": "# Release 3.7 postmortem\n\nNo incidents.\n"}
    local("log-31392", tt="root_cause", files=files, q="What went wrong in the last release?", path="postmortems/release-3.8.md", pat=r"(cache key format)", variant="B", decoy="No incidents",
          desc="Asks what went wrong in the last release; only the postmortem notes know", ref="读 postmortems/release-3.8.md：cache key 格式变更使会话全部失效，27 分钟后回滚。")


@reg
def c31393():
    files = {"logs/app.log": "2026-09-15 09:12:01 ERROR payment-gateway timeout after 30000 ms\n2026-09-15 09:12:02 ERROR retrying payment (attempt 2)\n2026-09-15 09:12:09 INFO payment ok\n", "logs/notes.txt": "排查笔记：支付网关 9:12 抖动。\n"}
    local("log-31393", tt="root_cause", files=files, q="昨天早上支付为什么慢了一下？", path="logs/app.log", pat=r"timeout after (\d+) ms", variant="A", decoy="30",
          desc="Asks casually why payment was slow yesterday morning; the app log shows a gateway timeout", ref="读 logs/app.log：支付网关超时 30000 ms 后重试成功。")


@reg
def c31394():
    files = {"ops/changes.md": "# 变更记录\n\n- 2026-09-10 14:00 把 nginx worker_connections 从 1024 调到 4096\n- 2026-09-14 22:30 关闭旧版推送服务\n", "ops/todo.md": "# 待办\n- 升级 TLS\n"}
    local("log-31394", tt="root_cause", files=files, q="nginx 的并发连接数我们前几天改成多少了？", path="ops/changes.md", pat=r"调到 (\d+)", variant="B", decoy="1024",
          desc="Asks what nginx connection limit was changed to; the change log records it", ref="读 ops/changes.md：调到 4096。")


@reg
def c31395():
    files = {"alerts/history.csv": "date,alert,duration_min\n2026-09-09,disk_full,45\n2026-09-13,cpu_high,18\n2026-09-15,disk_full,62\n", "alerts/rules.md": "# 规则\ndisk_full：磁盘使用率 > 90%\n"}
    local("log-31395", tt="count_events", files=files, q="磁盘告警最近一次持续了多长时间？", path="alerts/history.csv", pat=r"2026-09-15,disk_full,(\d+)", variant="A", decoy="45",
          desc="Asks how long the most recent disk alert lasted; the alert history has it", ref="读 alerts/history.csv：9/15 disk_full 62 分钟。")


@reg
def c31396():
    files = {"status/uptime-2026-08.md": "# 8 月可用性\n\n全月可用性 99.91%，累计停机 40 分钟。\n", "status/uptime-2026-09.md": "# 9 月可用性（截至 9/16）\n\n可用性 99.62%，累计停机 61 分钟。\n"}
    local("log-31396", tt="count_events", files=files, q="What's our uptime this month so far?", path="status/uptime-2026-09.md", pat=r"可用性 (99\.62)%", variant="B", decoy="99.91",
          desc="Asks this month's uptime so far with August and September reports present", ref="今天 9/16，读 status/uptime-2026-09.md：99.62%。")
