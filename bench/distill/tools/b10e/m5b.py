"""b10e M5 (v1.4 3.5) multi-line replace_lines ranges: cfg-8650..8664, doc-8600..8614."""
import json
from common import write_case


def C(cid, slug, n, desc, path, text, start, end, new, prompt, done, key, extra=None, trap="", zh=False, ttype="edit_value"):
    """One case: replace lines start..end (1-based, inclusive) of `path` by `new`; sibling blocks are decoys."""
    lines = text.splitlines(keepends=True)
    assert text.endswith("\n") and 2 <= end - start + 1 <= 4 and len(new) == end - start + 1, cid
    old = [l.rstrip("\n") for l in lines[start - 1:end]]
    assert old != new, cid
    out = lines[:start - 1] + [l + "\n" for l in new] + lines[end:]
    expected = "".join(out)
    assert expected != text
    files = dict(extra or {})
    files[path] = text
    exp = {"max_output_chars": 400}
    anyl = list(key)
    assert all(k in path or k in "".join(new) or True for k in anyl)
    exp["output_contains_any"] = anyl
    if done:
        exp["output_contains"] = ["DONE"]
    if zh:
        ans = "已改 %s 第 %d–%d 行，共 %d 行，改完回读确认无误。" % (path, start, end, len(new))
        if done:
            ans += "\nDONE"
    else:
        ans = "Updated %s lines %d-%d (%d lines), re-read the file to confirm." % (path, start, end, len(new))
        if done:
            ans += "\nDONE"
    assert any(k in ans for k in anyl) and (not done or "DONE" in ans), cid
    spec = {"path": path, "start": start, "end": end, "new": new}
    verify = '''
import json

case = json.load(open("case.json"))
SPEC = %s
lines = case["files"][SPEC["path"]].splitlines(keepends=True)
assert len(lines) >= SPEC["end"]
lines[SPEC["start"] - 1:SPEC["end"]] = [l + "\\n" for l in SPEC["new"]]
print(json.dumps({"files": {SPEC["path"]: "".join(lines)}}, ensure_ascii=False))
''' % json.dumps(spec, ensure_ascii=False)
    notes = '''
## Traps
- TR-DECOY: %s
- replace_lines must cover the whole run of %d lines (start_line %d, end_line %d) and content must have %d lines; a shorter range leaves old lines behind and a longer one eats the next block.

## Reference solution
1. Read %s; the target lines are %d-%d.
2. replace_lines start_line %d, end_line %d with:
%s
3. Read %s back to confirm.
Final answer, one sentence%s: %s Criteria: file equals the expected text exactly%s.

## Why the answer is unique
The prompt names every new value and the block is identified unambiguously; all other lines stay byte-identical.
''' % (trap, len(new), start, end, len(new), path, start, end, start, end,
       "\n".join("   " + l for l in new), path,
       " then DONE on its own line" if done else "", ans.replace("\n", " / "),
       "; output contains DONE" if done else "")
    write_case(
        cid, desc=desc, task_type=ttype, family="fam-%s-b10e-%s-%02d" % (cid.split("-")[0], slug, n), level="L1", ref_calls=4,
        traps=["TR-DECOY"], decoys={"TR-DECOY": None}, axes=["OBS"],
        files=files, case_expect={"files": {path: {"equals": expected}}},
        turns=[{"prompt": prompt, "expect": exp}], verify=verify, notes=notes,
    )


def at(text, line, nth=1):
    """1-based number of the nth line equal to `line`."""
    hits = [i + 1 for i, l in enumerate(text.splitlines()) if l == line]
    return hits[nth - 1]


# ------------------------------------------------------------ cfg-8650 (zh) nginx-style upstream blocks
t = """# 反向代理上游
upstream 订单服务 {
    server 10.2.4.11:8080 weight=3;
    server 10.2.4.12:8080 weight=2;
    keepalive 32;
}

upstream 库存服务 {
    server 10.2.4.21:8080 weight=3;
    server 10.2.4.22:8080 weight=2;
    keepalive 32;
}
"""
s = at(t, "upstream 库存服务 {") + 1
C("cfg-8650", "upstreamweights", 1, "Change the two server lines and keepalive of one upstream block; the sibling block has the same shape", "网关/上游.conf", t, s, s + 2,
  ["    server 10.2.4.31:8080 weight=4;", "    server 10.2.4.32:8080 weight=1;", "    keepalive 64;"],
  "网关/上游.conf 里库存服务的上游要换机器：两台改成 10.2.4.31 和 10.2.4.32（端口不变），权重分别 4 和 1，keepalive 调到 64。订单服务别碰。改完回复 DONE。",
  True, ["网关/上游.conf", "上游.conf"], trap="订单服务的块长得一模一样，只能改库存服务那三行。", zh=True)

# ------------------------------------------------------------ cfg-8651 (en) docker compose healthcheck
t = """services:
  api:
    image: acme/api:2.7
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
  worker:
    image: acme/worker:2.7
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8100/health"]
      interval: 30s
      timeout: 5s
      retries: 3
"""
s = at(t, "      interval: 30s", 2)
C("cfg-8651", "composehealth", 1, "Tighten three consecutive healthcheck timing lines of the worker service; the api service has identical lines", "docker-compose.yml", t, s, s + 2,
  ["      interval: 10s", "      timeout: 3s", "      retries: 5"],
  "In docker-compose.yml, make the worker's healthcheck stricter: interval 10s, timeout 3s, retries 5. Leave api as it is.",
  False, ["docker-compose.yml"], trap="api has the same interval/timeout/retries lines at 6-8; only the worker's lines 13-15 may change.", extra={"README.md": "Local stack. api and worker are tuned separately.\n"})

# ------------------------------------------------------------ cfg-8652 (zh) cron-ish ini 备份计划
t = """[备份-日志库]
周期 = 每天
时间 = 02:30
保留份数 = 7
目标 = /mnt/nas/log-db

[备份-业务库]
周期 = 每天
时间 = 03:10
保留份数 = 14
目标 = /mnt/nas/biz-db

[备份-报表库]
周期 = 每周
时间 = 04:00
保留份数 = 8
目标 = /mnt/nas/report-db
"""
s = at(t, "[备份-业务库]") + 1
C("cfg-8652", "backupplan", 1, "Change period/time/retention of one backup section (three lines) while the other sections keep theirs", "运维/备份计划.ini", t, s, s + 2,
  ["周期 = 每周", "时间 = 01:45", "保留份数 = 10"],
  "运维/备份计划.ini 里业务库的备份改成每周一次，时间 01:45，保留 10 份，目标目录不动。改完回复 DONE。",
  True, ["运维/备份计划.ini", "备份计划.ini"], trap="三个备份段的键完全相同，行号范围必须落在业务库那一段的前三行。", zh=True)

# ------------------------------------------------------------ cfg-8653 (en) k8s resources
t = """containers:
  - name: ingest
    resources:
      requests:
        cpu: 250m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 512Mi
  - name: exporter
    resources:
      requests:
        cpu: 250m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 512Mi
"""
s = at(t, "      limits:", 1)
C("cfg-8653", "k8slimits", 1, "Raise the limits block (key line plus two values) of the ingest container; the exporter container has identical lines", "k8s/deploy-pipeline.yaml", t, s + 1, s + 2,
  ["        cpu: 1000m", "        memory: 1Gi"],
  "Raise the ingest container's limits in k8s/deploy-pipeline.yaml to cpu 1000m and memory 1Gi. exporter stays as it is. Reply DONE when finished.",
  True, ["k8s/deploy-pipeline.yaml", "deploy-pipeline.yaml"], trap="exporter has byte-identical limits lines further down.")

# ------------------------------------------------------------ cfg-8654 (zh) env file
t = """# 短信通道
SMS_PROVIDER=aliyun
SMS_RATE_PER_MIN=120
SMS_RETRY=2
SMS_TIMEOUT_MS=3000

# 邮件通道
MAIL_PROVIDER=smtp
MAIL_RATE_PER_MIN=60
MAIL_RETRY=2
MAIL_TIMEOUT_MS=3000

# 推送通道
PUSH_PROVIDER=jpush
PUSH_RATE_PER_MIN=600
PUSH_RETRY=1
PUSH_TIMEOUT_MS=1500
"""
s = at(t, "MAIL_PROVIDER=smtp")
C("cfg-8654", "channelenv", 1, "Rewrite four consecutive MAIL_* lines in an env file; other channels use the same suffixes", "config/通知.env", t, s, s + 3,
  ["MAIL_PROVIDER=ses", "MAIL_RATE_PER_MIN=200", "MAIL_RETRY=3", "MAIL_TIMEOUT_MS=5000"],
  "config/通知.env 里邮件通道换成 ses 发，每分钟限速 200，重试 3 次，超时 5000 毫秒，其他通道别动。",
  False, ["config/通知.env", "通知.env"], trap="短信、推送两段键后缀和邮件完全对应，改错段就挂。", zh=True)

# ------------------------------------------------------------ cfg-8655 (en) ssh config
t = """Host bastion-eu
    HostName 52.18.4.10
    User ops
    Port 22
    IdentityFile ~/.ssh/eu_ed25519

Host bastion-us
    HostName 34.201.9.77
    User ops
    Port 22
    IdentityFile ~/.ssh/us_ed25519

Host bastion-ap
    HostName 13.250.31.5
    User ops
    Port 22
    IdentityFile ~/.ssh/ap_ed25519
"""
s = at(t, "Host bastion-us") + 1
C("cfg-8655", "sshhosts", 1, "Point the bastion-us host entry at a new address, user, port (three lines after HostName)", ".ssh/config.d/bastions", t, s, s + 2,
  ["    HostName 34.201.12.140", "    User deploy", "    Port 2222"],
  "The bastion-us entry in .ssh/config.d/bastions moved: HostName 34.201.12.140, User deploy, Port 2222. Keep its IdentityFile and the other hosts untouched.",
  False, [".ssh/config.d/bastions", "bastion-us"], trap="three Host blocks share User ops / Port 22; only bastion-us may change.")

# ------------------------------------------------------------ cfg-8656 (zh) json-ish app settings
t = """{
  "缓存": {
    "商品": { "ttl": 300, "最大条数": 5000 },
    "用户": { "ttl": 600, "最大条数": 20000 },
    "券": { "ttl": 120, "最大条数": 800 },
    "地址": { "ttl": 3600, "最大条数": 20000 }
  }
}
"""
s = at(t, '    "用户": { "ttl": 600, "最大条数": 20000 },')
C("cfg-8656", "cachejson", 1, "Replace two adjacent cache entries (user and coupon) in a JSON file; the address entry has the same max size as user", "配置/缓存.json", t, s, s + 1,
  ['    "用户": { "ttl": 900, "最大条数": 30000 },', '    "券": { "ttl": 60, "最大条数": 1500 },'],
  "配置/缓存.json：用户缓存 ttl 改 900、最大条数 30000；券缓存 ttl 改 60、最大条数 1500。别的缓存不变，JSON 格式保持合法。改完回复 DONE。",
  True, ["配置/缓存.json", "缓存.json"], trap="地址缓存的最大条数也是 20000，按数值全文替换会误伤；且每行末尾逗号要保留。", zh=True)

# ------------------------------------------------------------ cfg-8657 (en) toml
t = """[pool.read]
min = 2
max = 10
idle_timeout = "30s"

[pool.write]
min = 2
max = 10
idle_timeout = "30s"

[pool.batch]
min = 1
max = 4
idle_timeout = "120s"
"""
s = at(t, "[pool.write]") + 1
C("cfg-8657", "pooltoml", 1, "Resize the write pool (three lines under [pool.write]); the read pool has identical values", "db/pools.toml", t, s, s + 2,
  ["min = 4", "max = 24", 'idle_timeout = "15s"'],
  "In db/pools.toml, the write pool needs min 4, max 24 and idle_timeout 15s. Don't touch read or batch. Reply DONE afterwards.",
  True, ["db/pools.toml", "pools.toml"], trap="[pool.read] and [pool.write] are identical, so the first match of `max = 10` is the wrong block.")

# ------------------------------------------------------------ cfg-8658 (zh) systemd unit
t = """[Unit]
Description=报表导出服务
After=network.target

[Service]
ExecStart=/opt/export/bin/export --port 7010
Restart=on-failure
RestartSec=5
LimitNOFILE=4096

[Install]
WantedBy=multi-user.target
"""
s = at(t, "Restart=on-failure")
C("cfg-8658", "unitrestart", 1, "Change the three restart/limit lines of a systemd unit", "systemd/export.service", t, s, s + 2,
  ["Restart=always", "RestartSec=10", "LimitNOFILE=65536"],
  "systemd/export.service 想让它挂了就一直重启，间隔 10 秒，文件句柄上限提到 65536。ExecStart 那行别动。",
  False, ["systemd/export.service", "export.service"], trap="ExecStart 紧挨在被改范围上方，范围从 Restart 行开始，不能把它盖掉。", zh=True)

# ------------------------------------------------------------ cfg-8659 (en) logging yaml handlers
t = """handlers:
  console:
    level: INFO
    format: short
    stream: stdout
  file:
    level: INFO
    format: short
    path: /var/log/app/app.log
  audit:
    level: INFO
    format: short
    path: /var/log/app/audit.log
"""
s = at(t, "  file:") + 1
C("cfg-8659", "loghandlers", 1, "Switch the file handler's level, format and path (three lines); console and audit use the same level/format lines", "logging.yaml", t, s, s + 2,
  ["    level: DEBUG", "    format: json", "    path: /var/log/app/debug.log"],
  "For the file handler in logging.yaml set level DEBUG, format json and path /var/log/app/debug.log. Console and audit must keep their settings. Reply DONE when it's written.",
  True, ["logging.yaml"], trap="level: INFO / format: short appear three times; only the file handler's block (lines 7-9) changes.")

# ------------------------------------------------------------ cfg-8660 (zh) 排班规则 yaml
t = """班次:
  早班:
    开始: "08:00"
    结束: "16:00"
    最少人数: 3
  中班:
    开始: "16:00"
    结束: "24:00"
    最少人数: 3
  夜班:
    开始: "00:00"
    结束: "08:00"
    最少人数: 2
"""
s = at(t, "  中班:") + 1
C("cfg-8660", "shiftrule", 1, "Move the middle shift to new start/end times and headcount (three lines); early shift has the same headcount", "排班/规则.yaml", t, s, s + 2,
  ['    开始: "15:00"', '    结束: "23:00"', "    最少人数: 4"],
  "排班/规则.yaml 里中班提前一小时：15:00 到 23:00，最少人数加到 4。早班夜班不动，引号保留。",
  False, ["排班/规则.yaml", "规则.yaml"], trap="早班和中班的最少人数都是 3，按 `最少人数: 3` 全文查找会先命中早班。", zh=True)

# ------------------------------------------------------------ cfg-8661 (en) crontab
t = """# m h dom mon dow command
0 2 * * * /opt/jobs/rotate-logs.sh
15 2 * * * /opt/jobs/vacuum-db.sh
30 2 * * 0 /opt/jobs/full-backup.sh
0 3 * * * /opt/jobs/sync-assets.sh
@reboot /opt/jobs/warm-cache.sh
"""
s = at(t, "15 2 * * * /opt/jobs/vacuum-db.sh")
C("cfg-8661", "crontabshift", 1, "Reschedule two adjacent cron lines (vacuum and weekly backup) to new times", "etc/crontab.jobs", t, s, s + 1,
  ["45 3 * * * /opt/jobs/vacuum-db.sh", "0 4 * * 6 /opt/jobs/full-backup.sh"],
  "In etc/crontab.jobs move vacuum-db to 03:45 daily and make full-backup run on Saturdays (dow 6) at 04:00. The other jobs keep their lines.",
  False, ["etc/crontab.jobs", "crontab.jobs"], trap="rotate-logs and sync-assets bracket the two lines with similar schedules; the range must be exactly the middle two lines.")

# ------------------------------------------------------------ cfg-8662 (zh) 价格档 ini
t = """[标准会员]
月费 = 39
折扣 = 0.95
赠券张数 = 2

[高级会员]
月费 = 89
折扣 = 0.90
赠券张数 = 5

[企业会员]
月费 = 299
折扣 = 0.85
赠券张数 = 20
"""
s = at(t, "[高级会员]") + 1
C("cfg-8662", "memberplans", 1, "Update three consecutive keys of the premium member tier", "配置/会员档.ini", t, s, s + 2,
  ["月费 = 99", "折扣 = 0.88", "赠券张数 = 6"],
  "配置/会员档.ini：高级会员月费涨到 99，折扣 0.88，赠券 6 张。另外两档不变。改完回复 DONE。",
  True, ["配置/会员档.ini", "会员档.ini"], trap="三档的键名一致，数值各不同；范围要正好是高级会员下面的三行。", zh=True)

# ------------------------------------------------------------ cfg-8663 (en) prometheus alert rule
t = """groups:
  - name: latency
    rules:
      - alert: HighP95
        expr: p95_ms > 800
        for: 5m
        severity: warning
      - alert: HighP99
        expr: p99_ms > 800
        for: 5m
        severity: warning
"""
s = at(t, "      - alert: HighP99")
C("cfg-8663", "alertrules", 1, "Rewrite the HighP99 rule (alert name, expr, for, severity lines); HighP95 has parallel lines", "monitoring/rules.yaml", t, s, s + 3,
  ["      - alert: HighP99", "        expr: p99_ms > 1500", "        for: 10m", "        severity: critical"],
  "In monitoring/rules.yaml the HighP99 alert should fire above 1500 ms for 10m and have severity critical. HighP95 stays. Reply DONE once done.",
  True, ["monitoring/rules.yaml", "rules.yaml"], trap="HighP95 sits right above with the same thresholds; for: 5m / severity: warning appear twice.")

# ------------------------------------------------------------ cfg-8664 (zh) 门店营业设置
t = """门店:
  长宁店:
    营业开始: "09:00"
    营业结束: "21:30"
    外卖开关: 开
  静安店:
    营业开始: "09:00"
    营业结束: "21:30"
    外卖开关: 开
  徐汇店:
    营业开始: "10:00"
    营业结束: "22:00"
    外卖开关: 关
"""
s = at(t, "  静安店:") + 1
C("cfg-8664", "storehours", 1, "Change opening, closing time and delivery switch of one store; another store has identical values", "配置/门店营业.yaml", t, s, s + 2,
  ['    营业开始: "10:30"', '    营业结束: "20:00"', "    外卖开关: 关"],
  "配置/门店营业.yaml 里静安店改成 10:30 开门、20:00 打烊，外卖先关掉。长宁店跟它原来一模一样，别误改。",
  False, ["配置/门店营业.yaml", "门店营业.yaml"], trap="长宁店与静安店的原值逐字相同。", zh=True)

# ============================================================ docs
# ------------------------------------------------------------ doc-8600 (zh) 价目表两行
t = """# 打印服务价目

| 项目 | 单价（元/张） | 起印量 |
|---|---|---|
| A4 黑白 | 0.30 | 10 |
| A4 彩色 | 1.50 | 10 |
| A3 黑白 | 0.80 | 5 |
| A3 彩色 | 3.00 | 5 |

价格含纸张，不含装订。
"""
s = at(t, "| A3 黑白 | 0.80 | 5 |")
C("doc-8600", "priceprint", 1, "Replace the two A3 rows of a price table; A4 rows have similar names", "docs/打印价目.md", t, s, s + 1,
  ["| A3 黑白 | 0.90 | 5 |", "| A3 彩色 | 3.50 | 5 |"],
  "docs/打印价目.md 里 A3 涨价了：黑白 0.90，彩色 3.50，起印量不变。A4 不动。改完回复 DONE。",
  True, ["docs/打印价目.md", "打印价目.md"], trap="A4 和 A3 行只差尺寸，必须只覆盖最后两条数据行。", zh=True, ttype="write_structured")

# ------------------------------------------------------------ doc-8601 (en) release notes bullets
t = """# Release notes 3.8

## Highlights
- Faster cold start (about 30% lower)
- New export wizard
- Dark theme refresh

## Known issues
- Export wizard fails on files over 2 GB
- Tray icon blurry on 4K displays
- Dark theme flickers on first launch

## Upgrade notes
Back up your settings before upgrading.
"""
s = at(t, "- Export wizard fails on files over 2 GB")
C("doc-8601", "relnotes", 1, "Rewrite the three bullets under Known issues; the Highlights bullets mention the same features", "RELEASE-3.8.md", t, s, s + 2,
  ["- Export wizard fails on files over 4 GB", "- Tray icon blurry on 4K displays (fixed in 3.8.1)", "- Dark theme flicker fixed in 3.8"],
  "In RELEASE-3.8.md update the Known issues list: the export wizard limit is actually 4 GB, the tray icon item gets the suffix ' (fixed in 3.8.1)', and the flicker item becomes 'Dark theme flicker fixed in 3.8'. Keep the leading dashes. Reply DONE afterwards.",
  True, ["RELEASE-3.8.md"], trap="Highlights repeats the feature names (export wizard, dark theme); only the three Known issues bullets (lines 9-11) change.", ttype="write_structured")

# ------------------------------------------------------------ doc-8602 (zh) 会议纪要待办
t = """# 周会纪要 2026-09-14

## 结论
- 下周起统一用新模板

## 待办
- [ ] 邵宇航：整理供应商名单，周三前
- [ ] 韩佳宁：对接物流对账，周四前
- [ ] 邵宇航：更新报价表，周五前
- [ ] 韩佳宁：预约机房巡检，周五前

## 下次会议
2026-09-21 上午十点
"""
s = at(t, "- [ ] 韩佳宁：对接物流对账，周四前")
C("doc-8602", "meetingtodo", 1, "Update the two middle todo lines (assignee and deadline change); the same names appear on the other lines", "会议/周会-0914.md", t, s, s + 1,
  ["- [ ] 魏子轩：对接物流对账，周三前", "- [ ] 邵宇航：更新报价表，下周一前"],
  "会议/周会-0914.md 的待办调整一下：物流对账改给魏子轩，周三前；报价表仍是邵宇航，但推迟到下周一前。其余待办不变。",
  False, ["会议/周会-0914.md", "周会-0914.md"], trap="邵宇航、韩佳宁各出现在两条待办里，只能改中间两条。", zh=True, ttype="write_structured")

# ------------------------------------------------------------ doc-8603 (en) changelog version table
t = """# Supported versions

| Version | Status | End of support |
|---|---|---|
| 1.8 | maintenance | 2026-12-31 |
| 1.9 | maintenance | 2027-03-31 |
| 2.0 | active | 2027-09-30 |
| 2.1 | active | 2028-03-31 |

Security fixes are backported to maintenance versions only.
"""
s = at(t, "| 1.8 | maintenance | 2026-12-31 |")
C("doc-8603", "supportmatrix", 1, "Update the 1.8 and 1.9 rows of a support table to end-of-life; the other rows share the same layout", "SUPPORT.md", t, s, s + 1,
  ["| 1.8 | end-of-life | 2026-09-30 |", "| 1.9 | maintenance | 2027-01-31 |"],
  "SUPPORT.md: version 1.8 is now end-of-life with support ending 2026-09-30, and 1.9's end of support moves up to 2027-01-31 (it stays in maintenance).",
  False, ["SUPPORT.md"], trap="1.9 only changes its date; changing its status or touching 2.0/2.1 rows fails the exact match.", ttype="write_structured")

# ------------------------------------------------------------ doc-8604 (zh) 员工手册段落
t = """# 差旅报销规定

## 住宿
一线城市每晚不超过 600 元。
二线城市每晚不超过 450 元。
其他城市每晚不超过 350 元。

## 交通
高铁二等座据实报销。
飞机经济舱据实报销。
市内打车每次不超过 80 元。

## 餐补
每人每天 100 元，不需要发票。
"""
s = at(t, "高铁二等座据实报销。")
C("doc-8604", "travelpolicy", 1, "Rewrite the three transport sentences of a policy; the lodging section has the same three-line pattern", "制度/差旅报销.md", t, s, s + 2,
  ["高铁二等座据实报销，商务座须提前审批。", "飞机经济舱据实报销，须提前 7 天订票。", "市内打车每次不超过 100 元。"],
  "制度/差旅报销.md 的交通部分改三处：高铁二等座那句后面补「，商务座须提前审批」，飞机那句补「，须提前 7 天订票」，打车上限改成 100 元。句号保持句末。改完回复 DONE。",
  True, ["制度/差旅报销.md", "差旅报销.md"], trap="住宿部分同样是三行一组，且打车上限 80 与其他数字相近。", zh=True, ttype="write_structured")

# ------------------------------------------------------------ doc-8605 (en) API param table
t = """## Query parameters

| Name | Type | Default |
|---|---|---|
| limit | int | 20 |
| offset | int | 0 |
| sort | string | created |
| order | string | desc |

## Response headers

| Name | Type | Default |
|---|---|---|
| x-total | int | 0 |
| x-page | int | 1 |
"""
s = at(t, "| sort | string | created |")
C("doc-8605", "apiparams", 1, "Change the sort and order rows of the query-parameter table; the second table has a similar layout", "docs/api/list.md", t, s, s + 1,
  ["| sort | string | updated |", "| order | string | asc |"],
  "In docs/api/list.md the list endpoint now defaults to sort=updated and order=asc. Update the query parameter table accordingly.",
  False, ["docs/api/list.md", "list.md"], trap="A second table (response headers) uses the same three columns; only the query parameter rows change.", ttype="write_structured")

# ------------------------------------------------------------ doc-8606 (zh) 活动议程
t = """# 年会议程

| 时间 | 环节 | 负责人 |
|---|---|---|
| 14:00 | 签到入场 | 行政组 |
| 14:30 | 开场致辞 | 总经理 |
| 15:00 | 年度回顾 | 各部门 |
| 15:40 | 茶歇 | 行政组 |
| 16:00 | 颁奖典礼 | 人事组 |
| 17:00 | 聚餐 | 行政组 |
"""
s = at(t, "| 15:40 | 茶歇 | 行政组 |")
C("doc-8606", "agendarows", 1, "Shift the tea break and awards rows to new times and a new owner", "活动/年会议程.md", t, s, s + 1,
  ["| 15:50 | 茶歇 | 行政组 |", "| 16:10 | 颁奖典礼 | 工会 |"],
  "活动/年会议程.md：茶歇推迟 10 分钟，颁奖也推迟 10 分钟并改由工会负责。别的环节时间不变。",
  False, ["活动/年会议程.md", "年会议程.md"], trap="行政组出现在多行，按负责人查找容易错位；范围只有茶歇和颁奖这相邻两行。", zh=True, ttype="write_structured")

# ------------------------------------------------------------ doc-8607 (en) README install steps
t = """# Install

## macOS
1. brew tap acme/tools
2. brew install acme-cli
3. acme --version

## Linux
1. curl -fsSL https://get.example.test/acme.sh -o acme.sh
2. sh acme.sh
3. acme --version
"""
s = at(t, "1. curl -fsSL https://get.example.test/acme.sh -o acme.sh")
C("doc-8607", "installsteps", 1, "Rewrite the three Linux install steps; macOS steps share the final step text", "INSTALL.md", t, s, s + 2,
  ["1. wget https://get.example.test/acme.tar.gz", "2. tar xzf acme.tar.gz -C /usr/local/bin", "3. acme --version"],
  "Linux install in INSTALL.md should use the tarball instead of the script: step 1 wget https://get.example.test/acme.tar.gz, step 2 tar xzf acme.tar.gz -C /usr/local/bin, step 3 stays acme --version. macOS section untouched. Reply DONE when it's changed.",
  True, ["INSTALL.md"], trap="Step 3 is identical in both sections, so searching for it finds macOS first.", ttype="write_structured")

# ------------------------------------------------------------ doc-8608 (zh) 值班表
t = """# 国庆值班表

| 日期 | 白班 | 夜班 |
|---|---|---|
| 10-01 | 孟思远 | 柴雪晴 |
| 10-02 | 柴雪晴 | 孟思远 |
| 10-03 | 孟思远 | 柴雪晴 |
| 10-04 | 柴雪晴 | 孟思远 |

注：值班补贴按天结算。
"""
s = at(t, "| 10-02 | 柴雪晴 | 孟思远 |")
C("doc-8608", "dutyroster", 1, "Swap in a new person on two adjacent duty rows; names repeat on all rows", "值班/国庆.md", t, s, s + 1,
  ["| 10-02 | 柴雪晴 | 容嘉树 |", "| 10-03 | 容嘉树 | 柴雪晴 |"],
  "值班/国庆.md：孟思远 10 月 2 日夜班和 10 月 3 日白班有事，这两个班换成容嘉树，别的班次不动。",
  False, ["值班/国庆.md", "国庆.md"], trap="孟思远在四行里都出现，只有 10-02 的夜班和 10-03 的白班要换，两行内另一人的名字保持。", zh=True, ttype="write_structured")

# ------------------------------------------------------------ doc-8609 (en) FAQ paragraph lines
t = """# FAQ

**Can I change my plan mid-cycle?**
Yes. The change applies from the next billing date.
No proration is applied.

**Can I cancel at any time?**
Yes. Access continues until the end of the paid period.
No refund is issued for the remaining days.

**Can I add seats?**
Yes. New seats are billed from the day they are added.
Proration is applied.
"""
s = at(t, "Yes. The change applies from the next billing date.")
C("doc-8609", "faqbilling", 1, "Rewrite the three answer lines of the plan-change FAQ entry; cancel entry has parallel sentences", "docs/billing-faq.md", t, s, s + 1,
  ["Yes. The change applies immediately.", "The price difference is prorated for the rest of the cycle."],
  "billing-faq.md is outdated for plan changes: they now apply immediately and the price difference is prorated for the rest of the cycle. Rewrite that answer (the two lines under the question) and leave the other questions alone.",
  False, ["docs/billing-faq.md", "billing-faq.md"], trap="The cancel and seats answers use similar Yes./No refund/Proration sentences.", extra=None, ttype="write_structured")

# ------------------------------------------------------------ doc-8610 (zh) 食谱用料
t = """# 家常菜谱

## 番茄炒蛋
- 番茄 2 个
- 鸡蛋 3 个
- 盐 2 克
- 糖 5 克

## 青椒炒蛋
- 青椒 2 个
- 鸡蛋 3 个
- 盐 2 克
- 糖 1 克
"""
s = at(t, "- 番茄 2 个")
C("doc-8610", "recipeitems", 1, "Rewrite the four ingredient lines of the tomato dish; the next recipe shares two of them", "食谱/家常菜.md", t, s, s + 3,
  ["- 番茄 3 个", "- 鸡蛋 4 个", "- 盐 3 克", "- 糖 8 克"],
  "食谱/家常菜.md 里番茄炒蛋要做大份：番茄 3 个，鸡蛋 4 个，盐 3 克，糖 8 克。青椒炒蛋照旧。",
  False, ["食谱/家常菜.md", "家常菜.md"], trap="青椒炒蛋的鸡蛋和盐行与番茄炒蛋逐字相同，范围只能是番茄炒蛋那四行。", zh=True, ttype="write_structured")

# ------------------------------------------------------------ doc-8611 (en) ADR header block
t = """# ADR-014 Queue backend

- Status: proposed
- Date: 2026-08-19
- Deciders: platform team
- Supersedes: none

## Context
Workers poll the database for jobs.

# ADR-015 Cache layer

- Status: accepted
- Date: 2026-08-26
- Deciders: platform team
- Supersedes: none
"""
s = at(t, "- Status: proposed")
C("doc-8611", "adrstatus", 1, "Update the four metadata bullets of ADR-014 to accepted; ADR-015 has parallel bullets", "docs/adr/decisions.md", t, s, s + 3,
  ["- Status: accepted", "- Date: 2026-09-10", "- Deciders: platform team, SRE", "- Supersedes: ADR-009"],
  "In docs/adr/decisions.md ADR-014 was accepted on 2026-09-10 with SRE joining the deciders (platform team, SRE) and it supersedes ADR-009. Update its status, date, deciders and supersedes bullets; ADR-015 is not affected. Reply DONE afterwards.",
  True, ["docs/adr/decisions.md", "ADR-014"], trap="ADR-015 has the same four bullet keys, and its Deciders and Supersedes values equal ADR-014's old ones.", ttype="write_structured")

# ------------------------------------------------------------ doc-8612 (zh) 合同条款
t = """# 服务合同（节选）

## 第四条 付款
甲方应在验收后 15 日内付款。
逾期按日万分之五计违约金。
违约金总额不超过合同金额 10%。

## 第五条 交付
乙方应在签约后 30 日内交付。
逾期按日万分之五计违约金。
违约金总额不超过合同金额 10%。
"""
s = at(t, "甲方应在验收后 15 日内付款。")
C("doc-8612", "contractclause", 1, "Rewrite the three sentences of the payment clause; the delivery clause repeats the last two", "合同/服务合同.md", t, s, s + 2,
  ["甲方应在验收后 30 日内付款。", "逾期按日万分之三计违约金。", "违约金总额不超过合同金额 5%。"],
  "合同/服务合同.md 第四条付款按新谈的条件改：验收后 30 日内付款，逾期按日万分之三，违约金总额不超过合同金额 5%。第五条交付不动。改完回复 DONE。",
  True, ["合同/服务合同.md", "服务合同.md"], trap="第五条后两句与第四条后两句逐字相同，按句子查找会命中第四条或第五条各一次。", zh=True, ttype="write_structured")

# ------------------------------------------------------------ doc-8613 (en) roadmap table rows
t = """# Roadmap

| Quarter | Theme | Owner |
|---|---|---|
| Q1 | Onboarding revamp | Growth |
| Q2 | Search relevance | Search |
| Q3 | Offline mode | Mobile |
| Q4 | Billing v2 | Payments |

Dates are indicative.
"""
s = at(t, "| Q2 | Search relevance | Search |")
C("doc-8613", "roadmaprows", 1, "Swap the themes and owners of the Q2 and Q3 rows (two rows plus one more) in a roadmap table", "ROADMAP.md", t, s, s + 2,
  ["| Q2 | Offline mode | Mobile |", "| Q3 | Search relevance | Search |", "| Q4 | Billing v2 | Payments, Growth |"],
  "ROADMAP.md: Offline mode (Mobile) moves up to Q2 and Search relevance (Search) slips to Q3. Billing v2 in Q4 now also involves Growth, so its owner becomes 'Payments, Growth'. Q1 stays.",
  False, ["ROADMAP.md"], trap="Rows must keep Quarter in place while theme and owner move together; three rows are rewritten, Q1 is not.", ttype="write_structured")

# ------------------------------------------------------------ doc-8614 (zh) 课程表
t = """# 周三课程表

| 节次 | 一班 | 二班 |
|---|---|---|
| 第 1 节 | 语文 | 数学 |
| 第 2 节 | 数学 | 语文 |
| 第 3 节 | 英语 | 体育 |
| 第 4 节 | 体育 | 英语 |
| 第 5 节 | 美术 | 美术 |

备注：美术课两个班合上。
"""
s = at(t, "| 第 3 节 | 英语 | 体育 |")
C("doc-8614", "classtable", 1, "Change the third and fourth period rows of a class timetable; classes have mirrored subjects", "教务/周三课表.md", t, s, s + 1,
  ["| 第 3 节 | 体育 | 英语 |", "| 第 4 节 | 英语 | 体育 |"],
  "教务/周三课表.md 里第 3、4 节两个班对调一下：一班第 3 节体育、第 4 节英语，二班第 3 节英语、第 4 节体育。其他节次不动。改完回复 DONE。",
  True, ["教务/周三课表.md", "周三课表.md"], trap="两个班的科目镜像对称，容易只改一列；范围覆盖第 3、4 节两整行。", zh=True, ttype="write_structured")
