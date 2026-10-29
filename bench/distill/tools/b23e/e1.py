"""E1: multi-line or line-shifting edits, then read back (35301-35325)."""
from common import (make, L, lineno, apply_ops, N, P_RR, P_RW, P_SRR, P_RRC, P_RRD)

B = []


def reg(f):
    B.append(f)
    return f


REQ = ["read_file"]


def one(cid, *, sub="E1", tt, desc, files, ops, turns, notes, policy=P_RR, ref=4, scen=None, **kw):
    make(cid, sub=sub, task_type=tt, desc=desc, files=files, ops=ops, turns=turns, notes=notes, policy=policy,
         ref_calls=ref, **kw)


@reg
def c01():
    p = "deploy/harbor-gateway.yaml"
    f = {p: L("# harbor-gateway: edge routing for the Harbor storefront", "version: 3", "listen:", "  host: 0.0.0.0", "  port: 8443",
              "  tls: true", "upstreams:", "  - name: catalog", "    url: http://catalog.harbor.internal:7001", "  - name: cart",
              "    url: http://cart.harbor.internal:7002", "timeouts:", "  connect_ms: 800", "  read_ms: 4000", "logging:",
              "  level: info", "  format: json")}
    ops = [("sub", p, "  tls: true\n", "  tls: true\nrate_limit:\n  requests_per_minute: 600\n  burst: 120\n  key: client_ip\n"),
           ("sub", p, "connect_ms: 800", "connect_ms: 500")]
    one("cfg-35301", tt="edit_value", desc="Insert a rate_limit block, then a second tweak", files=f, ops=ops,
        turns=[{"p": "Add a rate_limit block to deploy/harbor-gateway.yaml right after the listen block: requests_per_minute 600, burst 120, key client_ip. Once it's in, tell me which line upstreams: is on now.",
                "inc": [str(lineno(apply_ops(f, ops[:1]), p, "upstreams:"))], "req": REQ},
               {"p": "Also drop the connect timeout to 500 ms.", "review": "accept"}],
        notes=N("TR-DECOY: connect_ms appears once; line numbers shift by 4 after the insert.", "read; insert 4 lines after tls; read back; second turn single-line edit.", "upstreams: moves from line 7 to 11."))


@reg
def c02():
    p = "配置/汇率服务.toml"
    f = {p: L("# 汇率服务配置", "[service]", "name = \"fx-rates\"", "port = 7410", "", "[legacy]", "# 旧版接口，已于 8 月下线", "endpoint = \"/v1/rates\"",
              "sunset = \"2026-08-31\"", "fallback = true", "", "[cache]", "ttl_seconds = 300", "max_entries = 5000", "", "[upstream]",
              "provider = \"nordbank\"", "refresh_minutes = 15")}
    ops = [("sub", p, "[legacy]\n# 旧版接口，已于 8 月下线\nendpoint = \"/v1/rates\"\nsunset = \"2026-08-31\"\nfallback = true\n\n", "")]
    end = apply_ops(f, ops)
    one("cfg-35302", tt="edit_value", desc="Delete the whole [legacy] section", files=f, ops=ops,
        turns=[{"p": "汇率服务配置里的 legacy 那一段已经下线了，整段删掉（包括它上面那行注释和后面的空行），其他保持原样。删完告诉我 [cache] 现在在第几行。",
                "inc": [str(lineno(end, p, "[cache]"))], "req": REQ}],
        notes=N("TR-DECOY: [cache] and [upstream] directly follow; removing one blank line too many or too few is visible.", "read; delete lines 6-11; read back.", "[cache] moves from 12 to 6."))


@reg
def c03():
    p = "conf/lumen-scheduler.ini"
    f = {p: L("; lumen scheduler tuning", "[pool]", "workers = 8", "queue_depth = 200", "", "[retry]", "max_attempts = 3", "backoff = linear",
              "", "[alerts]", "channel = ops-lumen", "threshold = 0.85", "", "[paths]", "spool = /var/spool/lumen")}
    ops = [("sub", p, "workers = 8\n", "workers = 12\nprefetch = 4\n"), ("sub", p, "max_attempts = 3\nbackoff = linear\n", "max_attempts = 5\nbackoff = exponential\n"),
           ("sub", p, "threshold = 0.85\n", "threshold = 0.9\nquiet_hours = 22-06\n")]
    end = apply_ops(f, ops)
    one("cfg-35303", tt="edit_value", desc="Three edits in one ini file, two of them add lines", files=f, ops=ops,
        turns=[{"p": "In conf/lumen-scheduler.ini: raise workers to 12 and add prefetch = 4 under it; set max_attempts to 5 and backoff to exponential; set the alert threshold to 0.9 and add quiet_hours = 22-06 below it. Check the file afterwards and tell me what line spool is on.",
                "inc": [str(lineno(end, p, "spool"))], "req": REQ}],
        notes=N("TR-DECOY: three scattered edits; each insert shifts later line numbers, a stale-line-number edit hits the wrong line.", "read; edit bottom-up or re-read; read back.", "spool ends on line 19."), policy=P_RW)


@reg
def c04():
    p = "infra/nginx-edge-upstream.conf"
    f = {p: L("# edge upstream pool for the invoice service", "upstream invoice_pool {", "    least_conn;", "    server 10.20.4.11:9100 max_fails=2;",
              "    server 10.20.4.12:9100 max_fails=2;", "    server 10.20.4.13:9100 backup;", "    keepalive 32;", "}", "",
              "server {", "    listen 443 ssl;", "    server_name invoice.northgate.internal;", "    location / {", "        proxy_pass http://invoice_pool;", "    }", "}")}
    ops = [("sub", p, "    server 10.20.4.11:9100 max_fails=2;\n    server 10.20.4.12:9100 max_fails=2;\n    server 10.20.4.13:9100 backup;\n",
            "    server 10.20.7.21:9100 max_fails=3;\n    server 10.20.7.22:9100 max_fails=3;\n    server 10.20.7.23:9100 max_fails=3;\n    server 10.20.7.24:9100 backup;\n")]
    end = apply_ops(f, ops)
    one("cfg-35304", tt="edit_value", desc="Replace three server lines with four", files=f, ops=ops,
        turns=[{"p": "发票服务搬到了新网段。把 infra/nginx-edge-upstream.conf 里 upstream 池的三台旧机器换成 10.20.7.21、10.20.7.22、10.20.7.23（端口不变，max_fails 改成 3），再加一台 10.20.7.24 当 backup。别动其他行，改完读一下确认，告诉我 keepalive 现在在第几行。",
                "inc": [str(lineno(end, p, "keepalive"))], "req": REQ}],
        notes=N("TR-DECOY: keepalive and the second server block must stay untouched.", "read; replace lines 4-6 with 4 lines; read back.", "keepalive moves from 7 to 8."))


@reg
def c05():
    p = "services/ledger-api.json"
    f = {p: L("{", "  \"service\": \"ledger-api\",", "  \"version\": \"1.4.0\",", "  \"endpoints\": [", "    {", "      \"path\": \"/entries\",",
              "      \"method\": \"GET\"", "    },", "    {", "      \"path\": \"/entries\",", "      \"method\": \"POST\"", "    },", "    {",
              "      \"path\": \"/balance\",", "      \"method\": \"GET\"", "    }", "  ]", "}")}
    ops = [("sub", p, "      \"method\": \"GET\"\n    }\n  ]", "      \"method\": \"GET\"\n    },\n    {\n      \"path\": \"/entries/export\",\n      \"method\": \"GET\"\n    }\n  ]"),
           ("sub", p, "\"version\": \"1.4.0\"", "\"version\": \"1.5.0\"")]
    end = apply_ops(f, ops)
    one("cfg-35305", tt="edit_value", desc="Add a JSON array element and bump the version", files=f, ops=ops,
        turns=[{"p": "In services/ledger-api.json add one more endpoint, GET /entries/export, as the last item of the endpoints list, and bump the version to 1.5.0. The file has to stay valid JSON, so check the commas when you read it back.",
                "req": REQ},
               {"p": "Which line does the new endpoint's path sit on?", "inc": [str(lineno(end, p, "/entries/export"))], "token": True}],
        notes=N("TR-DECOY: the missing comma after the old last object is the classic mistake.", "read; edit the tail; read back.", "path at line %d." % lineno(end, p, "/entries/export")))


@reg
def c06():
    p = "settings/alerts-oncall.yaml"
    f = {p: L("# 值班告警规则", "rules:", "  - name: disk-usage", "    severity: warn", "    page: false", "  - name: payment-5xx", "    severity: critical",
              "    page: true", "  - name: queue-lag", "    severity: warn", "    page: false")}
    ops = [("sub", p, "  - name: disk-usage\n    severity: warn\n    page: false\n  - name: payment-5xx\n    severity: critical\n    page: true\n",
            "  - name: payment-5xx\n    severity: critical\n    page: true\n  - name: disk-usage\n    severity: warn\n    page: false\n")]
    one("cfg-35306", tt="edit_value", desc="Move one rule block below another", files=f, ops=ops,
        turns=[{"p": "把 settings/alerts-oncall.yaml 里的 payment-5xx 规则整块移到 disk-usage 前面，内容一个字都不要变。改完读回来核对一下顺序。", "req": REQ,
                "inc": ["payment-5xx"]}],
        notes=N("TR-DECOY: a block move changes six lines; a wrong replace range duplicates or drops a line.", "read; replace lines 3-8 with swapped order; read back.", "equals is exact."))


@reg
def c07():
    p = "docs/runbooks/db-failover-runbook.md"
    f = {p: L("# DB failover runbook (orders cluster)", "", "Owner: platform-data", "", "## Steps", "", "1. Confirm the primary is unreachable from two probes.",
              "2. Freeze deploys in the release channel.", "3. Promote the replica with `orders-ctl promote`.", "4. Repoint the connection alias.",
              "5. Verify writes land on the new primary.", "6. Post the incident summary.", "", "## Rollback", "", "See the failback checklist.")}
    ops = [("sub", p, "4. Repoint the connection alias.\n5. Verify writes land on the new primary.\n6. Post the incident summary.\n",
            "4. Drain in-flight batch jobs.\n5. Repoint the connection alias.\n6. Verify writes land on the new primary.\n7. Post the incident summary.\n")]
    one("doc-35307", tt="write_structured", desc="Insert a numbered step and renumber the rest", files=f, ops=ops,
        turns=[{"p": "In docs/runbooks/db-failover-runbook.md, add a new step 4 'Drain in-flight batch jobs.' and renumber the steps after it so the list still runs 1 to 7. When it's saved, read the list back and tell me what step 6 says.",
                "inc": ["Verify writes"], "req": REQ}],
        notes=N("TR-DECOY: renumbering touches three lines.", "read; replace lines 10-12; read back.", "step 6 is 'Verify writes land on the new primary.'"), policy=P_RW)


@reg
def c08():
    p = "纪要/产品周会-0911.md"
    f = {p: L("# 产品周会 9 月 11 日", "", "## 决议", "- 新版引导流程下周灰度", "- 价格页文案由运营确认", "", "## 待定", "- 是否上线深色模式",
              "- 海外站点的支付渠道", "- 会员体系是否并入", "", "## 行动项", "- 张岚：整理灰度名单")}
    ops = [("sub", p, "## 待定\n- 是否上线深色模式\n- 海外站点的支付渠道\n- 会员体系是否并入\n\n## 行动项\n- 张岚：整理灰度名单\n",
            "## 行动项\n- 张岚：整理灰度名单\n- 周屿：跟进深色模式排期\n- 陈默：确认海外支付渠道清单\n")]
    end = apply_ops(f, ops)
    one("doc-35308", tt="write_structured", desc="Remove the pending section, add two action items", files=f, ops=ops,
        turns=[{"p": "产品周会-0911 那份纪要里，「待定」这一节的三条都已经定了，把整节删掉，再往行动项里加两条：周屿跟进深色模式排期，陈默确认海外支付渠道清单（格式照已有那条）。弄完读回来看一眼，告诉我现在文件一共多少行。",
                "inc": [str(len(end.get(p).split("\n")) - 1)], "req": REQ}],
        notes=N("TR-DECOY: removing the section plus its blank line while keeping 行动项 intact.", "read; replace lines 7-13; read back.", "file has %d lines." % (len(end[p].split("\n")) - 1)), policy=P_RW)


@reg
def c09():
    p = "docs/policies/remote-work-policy.md"
    f = {p: L("# Remote work policy", "", "Last reviewed: 2025-11-04", "", "## Eligibility", "",
              "Employees who have completed their first 90 days may work remotely", "up to two days per week. Managers approve exceptions",
              "in writing. Roles that require on-site equipment are excluded.", "", "## Equipment", "", "The company provides one laptop and one monitor.")}
    ops = [("sub", p, "Last reviewed: 2025-11-04", "Last reviewed: 2026-09-16"),
           ("sub", p, "Employees who have completed their first 90 days may work remotely\nup to two days per week. Managers approve exceptions\nin writing. Roles that require on-site equipment are excluded.\n",
            "Employees who have completed their first 60 days may work remotely\nup to three days per week. Team leads approve exceptions\nin writing, and HR is copied on every approval.\nRoles that require on-site equipment are excluded.\n")]
    end = apply_ops(f, ops)
    one("doc-35309", tt="write_structured", desc="Rewrite a paragraph and bump the review date", files=f, ops=ops,
        turns=[{"p": "Update docs/policies/remote-work-policy.md: eligibility drops to 60 days and the limit goes to three days a week, team leads (not managers) approve exceptions in writing and HR is copied on every approval. Keep the excluded-roles sentence. Set 'Last reviewed' to today. Then read it back and tell me which line '## Equipment' is on.",
                "inc": [str(lineno(end, p, "## Equipment"))], "req": REQ}],
        notes=N("TR-DECOY: the paragraph grows by one line, so '## Equipment' shifts; date must be the fixed clock date 2026-09-16.", "read; two edits; read back.", "## Equipment at line %d." % lineno(end, p, "## Equipment")), policy=P_RRD, ref=5)


@reg
def c10():
    p = "发布/更新说明.md"
    f = {p: L("# 更新说明", "", "## v3.2.0（2026-08-20）", "- 新增批量导出", "- 修复登录页闪退", "", "## v3.1.0（2026-07-02）", "- 新增暗色主题")}
    ops = [("sub", p, "# 更新说明\n\n", "# 更新说明\n\n## v3.3.0（2026-09-16）\n- 新增离线草稿\n- 导出支持 CSV 与 JSON\n- 修复通知角标不清零\n\n"),
           ("sub", p, "- 修复通知角标不清零\n", "- 修复通知角标不清零\n- 优化冷启动速度\n")]
    end = apply_ops(f, ops)
    one("doc-35310", tt="write_structured", desc="Prepend a release section", files=f, ops=ops,
        turns=[{"p": "在 发布/更新说明.md 最上面（标题下面）加一节 v3.3.0，日期写今天的，三条：新增离线草稿、导出支持 CSV 与 JSON、修复通知角标不清零。写完读回来，告诉我 v3.2.0 那一节现在从第几行开始。",
                "inc": [str(lineno(apply_ops(f, ops[:1]), p, "v3.2.0"))], "req": REQ},
               {"p": "再往 v3.3.0 这一节的最后补一条：- 优化冷启动速度。", "review": "accept"}],
        notes=N("TR-DECOY: older sections must stay in order.", "read; insert after line 2; read back.", "v3.2.0 starts at line %d." % lineno(end, p, "v3.2.0")), policy=P_RRD, ref=5)


@reg
def c11():
    p = "finance/vendor-spend-q3.md"
    f = {p: L("# Vendor spend, Q3", "", "| Vendor | Amount (USD) |", "|---|---:|", "| Brightwave | 4,200 |", "| Corvin Labs | 7,900 |", "| Zephyr Cloud | 12,300 |",
              "| **Total** | **24,400** |", "", "Source: AP ledger export.")}
    ops = [("sub", p, "| Zephyr Cloud | 12,300 |\n| **Total** | **24,400** |\n", "| Delmar Print | 1,500 |\n| Ostrand Freight | 2,600 |\n| Zephyr Cloud | 12,300 |\n| **Total** | **28,500** |\n")]
    one("doc-35311", tt="write_structured", desc="Insert two table rows and fix the total", files=f, ops=ops,
        turns=[{"p": "In finance/vendor-spend-q3.md add Delmar Print at 1,500 and Ostrand Freight at 2,600, keeping the vendors in the order of the table's existing alphabetical sort, and fix the Total row. Read the table back to confirm and tell me the new total.",
                "inc": ["28,500"], "req": REQ}],
        notes=N("TR-DECOY: the total must be recomputed (24,400 + 1,500 + 2,600).", "read; insert two rows; fix total; read back.", "28,500; rows sorted Brightwave, Corvin, Delmar, Ostrand, Zephyr."), policy=P_RRC, ref=5)


@reg
def c12():
    p = "客服/常见问题.md"
    f = {p: L("# 常见问题", "", "**Q1：如何修改绑定手机？**", "A：在「账号安全」里选择换绑。", "", "**Q2：发票多久能开？**", "A：申请后 3 个工作日内。", "",
              "**Q3：旧积分会过期吗？**", "A：自 2026 年 1 月起已取消积分过期。", "", "**Q4：怎么联系人工客服？**", "A：工作日 9:00–18:00，应用内「帮助」页。")}
    ops = [("sub", p, "**Q3：旧积分会过期吗？**\nA：自 2026 年 1 月起已取消积分过期。\n\n**Q4：怎么联系人工客服？**", "**Q3：怎么联系人工客服？**")]
    one("doc-35312", tt="write_structured", desc="Remove a Q&A block and renumber the next", files=f, ops=ops,
        turns=[{"p": "客服/常见问题.md 里「旧积分会过期吗」那一问已经没人问了，把这一问连答案一起删掉，后面那一问的编号顺延成 Q3。改完读回来确认，告诉我最后一问现在是第几行。",
                "inc": [str(lineno(apply_ops(f, ops), p, "Q3：怎么联系"))], "req": REQ}],
        notes=N("TR-DECOY: delete block + renumber in one pass.", "read; replace lines 9-13; read back.", "last Q is Q3 at line %d." % lineno(apply_ops(f, ops), p, "Q3：怎么联系")), policy=P_RW)


@reg
def c13():
    p = "pricing/plan-sheet-2026.md"
    f = {p: L("# Plan sheet 2026", "", "| Plan | Seats | Monthly |", "|---|---:|---:|", "| Starter | 3 | 29 |", "| Team | 15 | 119 |", "| Business | 60 | 399 |", "",
              "Prices in USD, billed monthly.")}
    ops = [("sub", p, "| Team | 15 | 119 |\n", "| Team | 15 | 129 |\n"), ("sub", p, "| Business | 60 | 399 |\n", "| Business | 60 | 399 |\n| Enterprise | 250 | 1,490 |\n"),
           ("append", p, "Enterprise pricing includes a dedicated support contact.\n")]
    one("doc-35313", tt="write_structured", desc="Table edits over two turns", files=f, ops=ops,
        turns=[{"p": "Raise Team to 129 a month in pricing/plan-sheet-2026.md and add an Enterprise row after Business: 250 seats, 1,490. Read the table back when you're done.",
                "req": REQ, "inc": ["129"]},
               {"p": "Now put one more line at the very end of that file: 'Enterprise pricing includes a dedicated support contact.'", "review": "accept"}],
        notes=N("TR-DECOY: only the Team row changes, not Starter or Business.", "turn 1 two edits + read back; turn 2 append.", "final file equals."), policy=P_RR)


@reg
def c14():
    p = "billing/proration.py"
    f = {p: L("\"\"\"Proration helpers for mid-cycle plan changes.\"\"\"", "", "", "def prorate(amount_cents, days_used, days_in_cycle):",
              "    ratio = days_used / days_in_cycle", "    value = amount_cents * ratio", "    value = round(value)", "    if value < 0:", "        value = 0",
              "    return value", "", "", "def refund_due(paid_cents, days_used, days_in_cycle):", "    return paid_cents - prorate(paid_cents, days_used, days_in_cycle)")}
    ops = [("sub", p, "    ratio = days_used / days_in_cycle\n    value = amount_cents * ratio\n    value = round(value)\n    if value < 0:\n        value = 0\n    return value\n",
            "    if days_in_cycle <= 0:\n        return 0\n    return max(0, round(amount_cents * days_used / days_in_cycle))\n")]
    end = apply_ops(f, ops)
    one("code-35314", tt="fix_edge_case", desc="Replace a six-line body with a guarded three-liner", files=f, ops=ops,
        turns=[{"p": "prorate() in billing/proration.py blows up with a ZeroDivisionError when days_in_cycle is 0. Replace its body so it returns 0 in that case and otherwise returns the rounded, non-negative prorated amount, in as few lines as is still readable. Leave refund_due alone. Read the file back and tell me which line refund_due now starts on.",
                "inc": [str(lineno(end, p, "def refund_due"))], "req": REQ}],
        notes=N("TR-DECOY: refund_due calls prorate and must not change.", "read; replace lines 5-10; read back.", "refund_due at line %d." % lineno(end, p, "def refund_due")), policy=P_RR)


@reg
def c15():
    p = "web/src/format-money.js"
    f = {p: L("export function formatMoney(cents, currency) {", "  const amount = (cents / 100).toFixed(2);", "  return currency + ' ' + amount;", "}", "",
              "export function formatPercent(ratio) {", "  return (ratio * 100).toFixed(1) + '%';", "}")}
    f["web/src/text-utils.js"] = L("export function pad(s, n) {", "  return s.padStart(n, ' ');", "}")
    ops = [("sub", p, "export function formatMoney", "import { pad } from './text-utils.js';\n\nexport function formatMoney"),
           ("append", p, "\nexport function formatCount(n) {\n  return pad(String(n), 6);\n}\n"),
           ("sub", p, "export function formatCount", "// right-aligned counter\nexport function formatCount")]
    end = apply_ops(f, ops)
    one("code-35315", tt="fix_edge_case", desc="Add an import at the top and a function at the bottom", files=f, ops=ops,
        turns=[{"p": "在 web/src/format-money.js 顶上加一行从 ./text-utils.js 引入 pad，文件最后再加一个 formatCount(n)，返回 pad(String(n), 6)。两处都弄完后读回来，告诉我 formatPercent 现在在第几行。",
                "inc": [str(lineno(end, p, "export function formatPercent"))], "req": REQ},
               {"p": "再给 formatCount 上面加一行注释：// right-aligned counter", "review": "accept"}],
        notes=N("TR-DECOY: text-utils.js already exports pad.", "read; insert top; append; read back.", "formatPercent at line %d." % lineno(end, p, "export function formatPercent")), policy=P_RW, traps=("TR-DECOY",))


@reg
def c16():
    p = "internal/queue/worker.go"
    f = {p: L("package queue", "", "type Worker struct {", "\tID   int", "\tName string", "}", "", "func NewWorker(id int, name string) *Worker {",
              "\treturn &Worker{ID: id, Name: name}", "}", "", "func (w *Worker) Label() string {", "\treturn w.Name", "}")}
    ops = [("sub", p, "\tName string\n}", "\tName string\n\tRetries int\n\tPaused  bool\n}"),
           ("sub", p, "\treturn &Worker{ID: id, Name: name}", "\treturn &Worker{ID: id, Name: name, Retries: 3}")]
    end = apply_ops(f, ops)
    one("code-35316", tt="fix_edge_case", desc="Struct gets two fields, constructor changes below", files=f, ops=ops,
        turns=[{"p": "Add two fields to the Worker struct in internal/queue/worker.go: Retries (int) and Paused (bool). NewWorker should start every worker with Retries set to 3. After editing, read the file back and tell me which line Label() is on.",
                "inc": [str(lineno(end, p, "func (w *Worker) Label"))], "req": REQ}],
        notes=N("TR-DECOY: the constructor line number shifts by two after the struct edit.", "read; edit struct; edit constructor with the shifted line; read back.", "Label at line %d." % lineno(end, p, "func (w *Worker) Label")))


@reg
def c17():
    p = "scripts/打包发布.sh"
    f = {p: L("#!/usr/bin/env bash", "set -e", "VERSION=$(cat VERSION)", "", "if [ -d dist ]; then", "  echo \"cleaning dist\"", "  rm -rf dist", "  mkdir dist", "fi", "",
              "tar czf \"dist/app-$VERSION.tgz\" src", "echo \"packed $VERSION\"")}
    ops = [("sub", p, "if [ -d dist ]; then\n  echo \"cleaning dist\"\n  rm -rf dist\n  mkdir dist\nfi\n\n", "mkdir -p dist\n\n")]
    end = apply_ops(f, ops)
    ops = ops + [("append", p, "echo \"done\"\n")]
    one("code-35317", tt="fix_edge_case", desc="Replace a five-line if-block with one line", files=f, ops=ops,
        turns=[{"p": "scripts/打包发布.sh 里清理 dist 的那个 if 块（五行）太啰嗦了，换成一行 mkdir -p dist，后面的空行保留一个就行。改完读回来看一眼，说一下 tar 那行现在是第几行。",
                "inc": [str(lineno(end, p, "tar czf"))], "req": REQ},
               {"p": "最后再加一行 echo \"done\"。", "review": "accept"}],
        notes=N("TR-DECOY: tar line must be untouched.", "read; replace lines 5-10; read back.", "tar at line %d." % lineno(end, p, "tar czf")))


@reg
def c18():
    p = "src/checkout/totals.ts"
    f = {p: L("export function calcTotal(items: Item[]): number {", "  return items.reduce((s, i) => s + i.price * i.qty, 0);", "}", "",
              "export function summary(items: Item[]) {", "  const t = calcTotal(items);", "  return { total: t, label: `Total: ${calcTotal(items)}` };", "}", "",
              "export function isFree(items: Item[]) {", "  return calcTotal(items) === 0;", "}")}
    ops = [("sub", p, "export function calcTotal", "export function computeTotal"), ("sub", p, "const t = calcTotal(items);", "const t = computeTotal(items);"),
           ("sub", p, "`Total: ${calcTotal(items)}`", "`Total: ${computeTotal(items)}`"), ("sub", p, "return calcTotal(items) === 0;", "return computeTotal(items) === 0;")]
    one("code-35318", tt="fix_edge_case", desc="Rename a function in four places", files=f, ops=ops,
        turns=[{"p": "Rename calcTotal to computeTotal in src/checkout/totals.ts — the definition and every place it's called in that file. Afterwards search or read the file back to make sure no calcTotal is left, and tell me how many places you changed.",
                "inc": ["4"], "req": REQ}],
        notes=N("TR-DECOY: the template string call is easy to miss.", "read; four single-line edits; read back.", "4 places."), policy=P_SRR, ref=6)


@reg
def c19():
    p = "tools/sync_inventory.py"
    f = {p: L("import json", "", "", "def load_stock(path):", "    with open(path) as fh:", "        data = json.load(fh)", "    return {row['sku']: row['qty'] for row in data}",
              "", "", "def main():", "    stock = load_stock('stock.json')", "    print(len(stock))")}
    ops = [("sub", p, "    with open(path) as fh:\n        data = json.load(fh)\n    return {row['sku']: row['qty'] for row in data}\n",
            "    try:\n        with open(path) as fh:\n            data = json.load(fh)\n    except FileNotFoundError:\n        return {}\n    return {row['sku']: row['qty'] for row in data}\n")]
    end = apply_ops(f, ops)
    one("code-35319", tt="fix_edge_case", desc="Wrap the body in try/except, indentation shifts", files=f, ops=ops,
        turns=[{"p": "tools/sync_inventory.py 里 load_stock 在文件不存在时直接崩。让它在 FileNotFoundError 时返回空字典，读文件那部分放进 try 里，其他逻辑不变。改完读回来核对缩进，告诉我 main 现在在第几行。",
                "inc": [str(lineno(end, p, "def main"))], "req": REQ}],
        notes=N("TR-DECOY: indentation of the with-block changes; the return stays at function level.", "read; replace lines 5-7; read back.", "main at line %d." % lineno(end, p, "def main")), policy=P_RW)


@reg
def c20():
    p = ".ci/pipeline-build.yml"
    f = {p: L("name: build", "on: [push]", "jobs:", "  test:", "    runs-on: ubuntu-latest", "    steps:", "      - uses: actions/checkout@v4", "      - name: Install",
              "        run: npm ci", "      - name: Unit tests", "        run: npm test", "  package:", "    needs: test", "    runs-on: ubuntu-latest", "    steps:",
              "      - run: npm pack")}
    ops = [("sub", p, "        run: npm ci\n", "        run: npm ci\n      - name: Lint\n        run: npm run lint\n        env:\n          CI: true\n"),
           ("sub", p, "name: build\non:", "name: build-and-pack\non:")]
    end = apply_ops(f, ops)
    one("code-35320", tt="fix_edge_case", desc="Insert a four-line CI step between two steps", files=f, ops=ops,
        turns=[{"p": "Add a Lint step to the test job in .ci/pipeline-build.yml, between Install and Unit tests. It runs `npm run lint` and sets the env var CI to true. Read the workflow back to make sure the indentation lines up, then tell me which line the package job starts on.",
                "inc": [str(lineno(end, p, "  package:"))], "req": REQ},
               {"p": "Also rename the workflow itself to build-and-pack.", "review": "accept"}],
        notes=N("TR-DECOY: YAML indentation of the nested env block.", "read; insert 4 lines; read back; turn 2 rename.", "package at line %d." % lineno(end, p, "  package:")))


@reg
def c21():
    p = "budget/offsite-2026.md"
    f = {p: L("# Offsite budget", "", "| Item | Cost (USD) |", "|---|---:|", "| Venue | 3200 |", "| Catering | 1850 |", "| **Total** | **5050** |", "", "Approved by finance on 2026-09-02.")}
    ops = [("sub", p, "| Catering | 1850 |\n| **Total** | **5050** |\n", "| Catering | 1850 |\n| Transport | 940 |\n| Team activity | 1275 |\n| **Total** | **7265** |\n")]
    one("hyb-35321", tt="tool_then_write", desc="Add two budget rows and recompute the total", files=f, ops=ops,
        turns=[{"p": "Add Transport at 940 and Team activity at 1275 to budget/offsite-2026.md, above the total, and make the Total row correct. Read the table back and tell me the new total.",
                "inc": ["7265"], "req": REQ}],
        notes=N("TR-DECOY: total must be 3200+1850+940+1275.", "read; insert rows; recompute total; read back.", "7265."), policy=P_RRC, ref=5)


@reg
def c22():
    p = "采购/办公用品清单.md"
    f = {p: L("# 办公用品清单", "", "| 品名 | 数量 | 单价 | 小计 |", "|---|---:|---:|---:|", "| 笔记本 | 40 | 6 | 240 |", "| 白板笔 | 25 | 4 | 100 |", "| **合计** | | | **340** |",
              "", "审批人：吴桐")}
    ops = [("sub", p, "| 白板笔 | 25 | 4 | 100 |\n| **合计** | | | **340** |\n", "| 白板笔 | 25 | 4 | 100 |\n| 订书机 | 12 | 15 | 180 |\n| 文件夹 | 60 | 3 | 180 |\n| 便利贴 | 30 | 5 | 150 |\n| **合计** | | | **850** |\n")]
    one("hyb-35322", tt="tool_then_write", desc="Add three rows with subtotals and a new total", files=f, ops=ops,
        turns=[{"p": "在 采购/办公用品清单.md 里加三行：订书机 12 个每个 15、文件夹 60 个每个 3、便利贴 30 个每个 5，小计算好，合计也改对。读回来确认，告诉我新的合计。",
                "inc": ["850"], "req": REQ}],
        notes=N("TR-DECOY: three subtotals 180/180/150 plus old 340.", "read; insert; fix total; read back.", "850."), policy=P_RRC, ref=5)


@reg
def c23():
    p = "ops/maintenance-windows.md"
    f = {p: L("# Maintenance windows", "", "| Date | System | Owner |", "|---|---|---|", "| 2026-09-04 | billing-db | Reyes |", "| 2026-09-11 | search-index | Okafor |", "",
              "Windows run 01:00-03:00 UTC.")}
    ops = [("sub", p, "| 2026-09-11 | search-index | Okafor |\n", "| 2026-09-11 | search-index | Okafor |\n| 2026-09-18 | auth-gateway | Lindqvist |\n")]
    one("hyb-35323", tt="tool_then_write", desc="Add a row dated this coming Friday", files=f, ops=ops,
        turns=[{"p": "Schedule an auth-gateway window in ops/maintenance-windows.md for this coming Friday, owner Lindqvist, as a new last row of the table. Check the file afterwards and tell me the date you used.",
                "inc": ["2026-09-18"], "req": REQ}],
        notes=N("TR-DECOY: today is Wednesday 2026-09-16 so the coming Friday is 2026-09-18.", "datetime; read; insert; read back.", "2026-09-18."), policy=P_RRD, ref=5)


@reg
def c24():
    p = "仓库/库存盘点.md"
    f = {p: L("# 库存盘点（9 月）", "", "| 货号 | 名称 | 库存 |", "|---|---|---:|", "| A-101 | 蓝牙耳机 | 48 |", "| A-102 | 充电线 | 130 |", "| A-103 | 手机支架 | 75 |", "| A-104 | 移动电源 | 22 |")}
    ops = [("sub", p, "| 48 |", "| 36 |"), ("sub", p, "| A-104 | 移动电源 | 22 |", "| A-104 | 移动电源 | 60 |"), ("sub", p, "| A-103 | 手机支架 | 75 |\n", "")]
    end = apply_ops(f, ops)
    one("hyb-35324", tt="multi_turn", desc="Update stock counts, then delete a row", files=f, ops=ops,
        turns=[{"p": "盘点结果出来了：A-101 蓝牙耳机剩 36，A-104 移动电源补货后是 60。帮我改到 仓库/库存盘点.md 里，改完读回来确认。", "req": REQ, "inc": ["36", "60"]},
               {"p": "A-103 手机支架下架了，把那一行删掉。删完告诉我表格现在还剩几行商品。", "inc": ["3"], "review": "accept"}],
        notes=N("TR-DECOY: only the two named rows change in turn 1.", "turn 1 two edits + read back; turn 2 delete row.", "3 products left."), policy=P_RR)


@reg
def c25():
    p = "release/checklist-v7.md"
    f = {p: L("# Release checklist v7", "", "- [ ] Freeze main branch", "- [ ] Run full regression", "- [ ] Update the status page", "- [ ] Tag the release", "- [ ] Notify support")}
    ops = [("sub", p, "- [ ] Freeze main branch", "- [x] Freeze main branch"), ("sub", p, "- [ ] Run full regression", "- [x] Run full regression"),
           ("sub", p, "- [ ] Tag the release\n", "- [ ] Tag the release\n- [ ] Publish the release notes\n"), ("append", p, "\nNote: regression passed on 2026-09-16.\n")]
    one("hyb-35325", tt="multi_turn", desc="Tick two boxes and add an item, then add a note", files=f, ops=ops,
        turns=[{"p": "In release/checklist-v7.md tick off 'Freeze main branch' and 'Run full regression', and add a new item 'Publish the release notes' right after 'Tag the release'. Read it back and tell me how many items are still unticked.",
                "inc": ["4"], "req": REQ},
               {"p": "Add a blank line and then 'Note: regression passed on 2026-09-16.' at the bottom.", "review": "accept"}],
        notes=N("TR-DECOY: the new item is unticked, so 4 remain (status page, tag, publish notes, support).", "read; tick two; insert; read back; turn 2 append.", "4 unticked."), policy=P_RR)
