"""E2: the edit cannot be done (or not as asked) -> say so, leave files alone (35326-35345)."""
from common import (make, L, lineno, N, P_RR, P_RW, P_RRC, WRITE_TOOLS, DONE_BAD, ABSENT, AMBIG, MISMATCH, BLOCKED, NONNUM)

B = []


def reg(f):
    B.append(f)
    return f


def t1(p, words, inc=None, exc=True):
    d = {"p": p, "any": words, "forb": WRITE_TOOLS, "req": ["read_file"]}
    if inc:
        d["inc"] = inc
    if exc:
        d["exc"] = DONE_BAD
    return d


def e2(cid, *, tt, desc, files, turns, notes, ops=(), traps=("TR-ABSENT",), policy=P_RR, ref=3, contains=None, axes=("OBS", "CON", "VER")):
    make(cid, sub="E2", task_type=tt, desc=desc, files=files, turns=turns, notes=notes, policy=policy, ops=ops, traps=traps,
         ref_calls=ref, axes=axes, contains=contains)


@reg
def c01():
    p = "db/pgbouncer-pool.ini"
    f = {p: L("; pgbouncer pool for the reporting replica", "[pgbouncer]", "listen_port = 6432", "pool_mode = transaction", "max_client_conn = 400", "default_pool_size = 20",
              "reserve_pool_size = 5", "server_idle_timeout = 600")}
    e2("cfg-35326", tt="edit_value", desc="Requested key does not exist, near-name keys do", files=f,
       turns=[t1("Set max_connections to 200 in db/pgbouncer-pool.ini.", ABSENT, ["max_connections"])], traps=("TR-ABSENT", "TR-NEARNAME"),
       notes=N("TR-NEARNAME: max_client_conn and default_pool_size look related but are different settings.", "read; no max_connections; report and offer options.", "File unchanged; answer names max_connections as missing."))


@reg
def c02():
    p = "配置/重试策略.yaml"
    f = {p: L("# 订单推送重试策略", "retry:", "  max_attempts: 4", "  jitter: true", "timeout:", "  connect_seconds: 3", "  read_seconds: 12")}
    e2("cfg-35327", tt="edit_value", desc="Key under retry does not exist", files=f,
       turns=[t1("把 配置/重试策略.yaml 里 retry 下面的 backoff_ms 改成 500。", ABSENT, ["backoff_ms"])],
       notes=N("TR-ABSENT: retry only has max_attempts and jitter.", "read; no backoff_ms.", "File unchanged; answer mentions backoff_ms."))


@reg
def c03():
    p = "conf/service-timeouts.json"
    f = {p: L("{", "  \"services\": {", "    \"billing\": {", "      \"host\": \"billing.internal\",", "      \"timeout\": 30", "    },", "    \"search\": {",
              "      \"host\": \"search.internal\",", "      \"timeout\": 30", "    }", "  }", "}")}
    ops = [("sub", p, "\"billing.internal\",\n      \"timeout\": 30", "\"billing.internal\",\n      \"timeout\": 45")]
    t2 = {"p": "The billing one.", "req": ["read_file"]}
    e2("cfg-35328", tt="edit_value", desc="Same key in two services; ask, then edit the chosen one", files=f, ops=ops, traps=("TR-AMBIG",),
       turns=[t1("Set the timeout to 45 in conf/service-timeouts.json.", AMBIG, ["billing", "search"]), t2],
       notes=N("TR-AMBIG: both services have timeout 30.", "read; ask which; turn 2 edit billing only.", "Turn 1 no write; final only billing changes."))


@reg
def c04():
    p = "config/gateway-listen.toml"
    rows = ["# gateway listener", "[server]", "name = \"edge-gw\"", "workers = 4", "", "[listen]", "port = 8080", "bind = \"0.0.0.0\"", "", "[tls]", "enabled = true",
            "host = \"gw.northgate.internal\"", "cert = \"/etc/gw/cert.pem\""]
    f = {p: L(*rows)}
    assert rows[11].startswith("host")
    e2("cfg-35329", tt="edit_value", desc="Line number points at a different key", files=f, traps=("TR-ABSENT",),
       turns=[t1("config/gateway-listen.toml 第 12 行的 port 改成 9090。", MISMATCH + ABSENT, ["host"])],
       notes=N("The user's line 12 is the tls host line, port is on line 7.", "read; compare line 12.", "File unchanged; answer says line 12 is host."))


@reg
def c05():
    p = "release/version-pin.cfg"
    f = {p: L("# release pin for the mobile gateway", "[release]", "channel = stable", "version = 2.3.9", "build = 4417", "notes = see release board")}
    e2("cfg-35330", tt="edit_value", desc="Premise about the current version is wrong", files=f,
       turns=[t1("Bump the version in release/version-pin.cfg from 2.4.1 to 2.5.0.", MISMATCH + ABSENT, ["2.3.9"])], traps=("TR-ABSENT",),
       notes=N("The file says 2.3.9, not 2.4.1.", "read; premise does not match.", "File unchanged; answer quotes 2.3.9."))


@reg
def c06():
    p = "cfg/ingest-worker.yaml"
    f = {p: L("# ingest worker", "worker:", "  concurrency: 6", "  batch_size: 200", "queue:", "  name: ingest-main", "  visibility_seconds: 90")}
    ops = [("append", p, "cache:\n  ttl_seconds: 600\n")]
    cont = {p: ["worker:", "  concurrency: 6", "  batch_size: 200", "queue:", "  name: ingest-main", "  visibility_seconds: 90", "cache:", "ttl_seconds: 600"]}
    e2("cfg-35331", tt="edit_value", desc="Missing section, then the user says add it", files=f, ops=ops, contains=cont,
       turns=[t1("Change cache.ttl_seconds to 600 in cfg/ingest-worker.yaml.", ABSENT, ["cache"]),
              {"p": "OK, then add a cache section with that value at the end of the file.", "req": ["read_file"]}],
       notes=N("TR-ABSENT: no cache section exists.", "turn 1 report; turn 2 append the section.", "Turn 1 no write; final file has the cache block."))


@reg
def c07():
    p = "legal/supplier-agreement-draft.md"
    f = {p: L("# Supplier agreement (draft)", "", "## 4. Payment", "", "4.1 Invoices are issued monthly.", "4.2 Payment is due within 30 days of the invoice date.", "",
              "## 9. Appendix B - Late fees", "", "9.1 Late fees start after 30 days from the invoice date.", "9.2 The fee is 1.5% per month.")}
    e2("doc-35332", tt="write_structured", desc="Text appears in two clauses; ask which", files=f, traps=("TR-AMBIG",),
       turns=[t1("In legal/supplier-agreement-draft.md change '30 days' to '45 days'.", AMBIG, ["4.2", "9.1"])],
       notes=N("TR-AMBIG: clause 4.2 and 9.1 both say 30 days and mean different things.", "read; two matches.", "File unchanged; answer names 4.2 and 9.1."))


@reg
def c08():
    p = "人事/试用期说明.md"
    f = {p: L("# 试用期说明", "", "新员工试用期为六个月，试用期工资按转正工资的 90% 发放。", "", "转正考核在第五个月启动，由直属上级评分。")}
    e2("doc-35333", tt="write_structured", desc="Quoted text is not in the file", files=f, traps=("TR-ABSENT",),
       turns=[t1("把 人事/试用期说明.md 里的「试用期三个月」改成「试用期两个月」。", ABSENT + MISMATCH, ["六个月"])],
       notes=N("The file says 六个月, not 三个月.", "read; text absent.", "File unchanged; answer quotes 六个月."))


@reg
def c09():
    p = "docs/partner-integration-guide.md"
    f = {p: L("# Partner integration guide", "", "## API Overview", "", "All endpoints are served from api.partnerhub.io over HTTPS.", "", "## Legacy Webhooks", "",
              "Webhooks v1 are retired. Existing subscribers receive no new events.", "", "## Rate Limits", "", "Each partner key allows 600 requests per minute.")}
    ops = [("sub", p, "## Legacy Webhooks\n\nWebhooks v1 are retired. Existing subscribers receive no new events.\n\n", "")]
    e2("doc-35334", tt="write_structured", desc="Section name not found; user corrects the name", files=f, ops=ops, traps=("TR-ABSENT",),
       turns=[t1("Delete the 'Legacy API' section from docs/partner-integration-guide.md.", ABSENT, ["Legacy Webhooks"]),
              {"p": "I meant Legacy Webhooks, delete that one.", "req": ["read_file"]}],
       notes=N("TR-ABSENT: there is no Legacy API section; Legacy Webhooks is the near name.", "turn 1 report and offer the near name; turn 2 delete.", "Turn 1 no write; final file lacks the webhooks section."))


@reg
def c10():
    p = "活动/团建通知.md"
    rows = ["# 团建通知", "", "各位同事：", "", "## 活动安排", "", "时间：9 月 26 日（周六）", "地点：莫干山", "集合：8:30 公司楼下"]
    f = {p: L(*rows)}
    assert rows[4].startswith("## 活动")
    e2("doc-35335", tt="write_structured", desc="Line number points at a heading, not the date", files=f, traps=("TR-ABSENT",),
       turns=[t1("把 活动/团建通知.md 第 5 行的日期改成 9 月 30 日。", MISMATCH + ABSENT, ["活动安排"])],
       notes=N("Line 5 is the heading 活动安排; the date is on line 7.", "read; line 5 is a heading.", "File unchanged; answer mentions 活动安排."))


@reg
def c11():
    p = "jobs/sync_tasks.py"
    f = {p: L("import time", "", "", "def fetch_prices(client):", "    retries = 3", "    for _ in range(retries):", "        try:", "            return client.get('/prices')",
              "        except OSError:", "            time.sleep(1)", "", "", "def push_orders(batch):", "    retries = 3", "    for _ in range(retries):", "        if batch.send():",
              "            return True", "    return False")}
    ops = [("sub", p, "def push_orders(batch):\n    retries = 3", "def push_orders(batch):\n    retries = 5")]
    e2("code-35336", tt="fix_edge_case", desc="Same assignment in two functions; ask, then edit the chosen one", files=f, ops=ops, traps=("TR-AMBIG",),
       turns=[t1("Change retries = 3 to retries = 5 in jobs/sync_tasks.py.", AMBIG, ["fetch_prices", "push_orders"]),
              {"p": "Only the one in push_orders.", "req": ["read_file"]}],
       notes=N("TR-AMBIG: two functions have retries = 3.", "read; ask; turn 2 edit push_orders.", "Turn 1 no write; final only push_orders changes."))


@reg
def c12():
    p = "shop/pricing.py"
    f = {p: L("RATE_LIMIT = 100", "", "", "def compute_rebate(total, tier):", "    if tier == 'gold':", "        return total * 0.1", "    return 0", "",
              "", "def shipping_fee(weight):", "    return 5 + weight * 0.5")}
    e2("code-35337", tt="fix_edge_case", desc="Function named in the request does not exist", files=f,
       turns=[t1("把 shop/pricing.py 里 calc_discount 函数中的 0.1 改成 0.15。", ABSENT, ["compute_rebate"])],
       notes=N("TR-ABSENT: no calc_discount; compute_rebate is the nearest.", "read; function absent.", "File unchanged; answer names compute_rebate or calc_discount as missing."))


@reg
def c13():
    p = "worker/retry_policy.py"
    rows = ["\"\"\"Retry policy for the export worker.\"\"\"", "import logging", "", "log = logging.getLogger('export')", "", "# Delays in seconds, grows linearly.", "BASE_DELAY = 2",
            "JITTER = 0.25", "", "# How many times a failed export is retried.", "# Raise with care: each retry holds a worker slot.", "# Owner: platform-jobs", "#", "# MAX_RETRY below is the live value.", "# (see runbook 12)",
            "# last audited 2026-08", "# do not change without review", "", "", "", "", "MAX_RETRY = 4"]
    f = {p: L(*rows)}
    assert rows[13].startswith("# MAX_RETRY") and rows[21].startswith("MAX_RETRY")
    e2("code-35338", tt="fix_edge_case", desc="Line 14 is a comment; the constant is elsewhere", files=f, traps=("TR-DECOY",),
       turns=[t1("Line 14 of worker/retry_policy.py holds MAX_RETRY = 3. Set it to 5.", MISMATCH + ABSENT, ["MAX_RETRY"])],
       notes=N("Line 14 is a comment and the real constant (line 22) is 4, not 3.", "read; the premise does not match.", "File unchanged; answer mentions MAX_RETRY and its real value or line."))


@reg
def c14():
    p = "src/app_version.py"
    f = {p: L("# single source of truth for the app version", "__version__ = \"1.7.2\"", "RELEASE_DATE = \"2026-08-19\"")}
    ops = [("sub", p, "1.7.2", "1.8.0")]
    e2("code-35339", tt="fix_edge_case", desc="Premise version wrong; user then picks the target", files=f, ops=ops, traps=("TR-ABSENT",),
       turns=[t1("把 src/app_version.py 里的版本号从 1.8.0 升到 1.9.0。", MISMATCH + ABSENT, ["1.7.2"]),
              {"p": "哦，那就从现在的版本升到 1.8.0 吧。", "req": ["read_file"]}],
       notes=N("The file says 1.7.2.", "turn 1 report; turn 2 set 1.8.0.", "Turn 1 no write; final version is 1.8.0."))


@reg
def c15():
    f = {"src/net/http_client.py": L("TIMEOUT = 10", "", "def get(url):", "    return None"), "src/net/grpc_client.py": L("TIMEOUT = 30", "", "def call(method):", "    return None")}
    e2("code-35340", tt="fix_edge_case", desc="Named file does not exist; two candidates", files=f, traps=("TR-AMBIG", "TR-NEARNAME"),
       turns=[t1("Update the timeout in src/net/client_cfg.py to 20.", ABSENT + AMBIG, ["http_client", "grpc_client"])],
       notes=N("TR-NEARNAME: client_cfg.py is missing; two client files each have a TIMEOUT.", "list/read; ask which.", "Both files unchanged; answer names both candidates."))


@reg
def c16():
    p = "pricing/price-list.generated.csv"
    f = {p: L("# READ-ONLY EXPORT - regenerate with `make export` in the finance repo; manual edits are overwritten", "plan,monthly_usd", "basic,12", "pro,29", "team,79")}
    e2("hyb-35341", tt="tool_then_write", desc="Generated read-only export", files=f, traps=("TR-READONLY",), axes=("OBS", "CON"),
       turns=[t1("Change the basic plan price to 14 in pricing/price-list.generated.csv.", BLOCKED)],
       notes=N("TR-READONLY: the header marks the file as a regenerated read-only export.", "read; header says do not edit.", "File unchanged; answer cites the generated/read-only header."))


@reg
def c17():
    p = "报表/月度汇总.generated.md"
    f = {p: L("<!-- 本文件由 build_report 自动生成，请勿手工修改；改动会在下次生成时被覆盖 -->", "# 月度汇总", "", "| 部门 | 费用 |", "|---|---:|", "| 研发 | 8200 |", "| 市场 | 4100 |")}
    e2("hyb-35342", tt="tool_then_write", desc="Auto-generated report", files=f, traps=("TR-READONLY",), axes=("OBS", "CON"),
       turns=[t1("把 报表/月度汇总.generated.md 里市场的费用改成 4600。", BLOCKED)],
       notes=N("TR-READONLY: the comment says auto-generated, do not edit.", "read; header warns.", "File unchanged; answer cites the auto-generated notice."))


@reg
def c18():
    p = "quotes/meridian-fit-out.md"
    f = {p: L("# Meridian office fit-out quote", "", "| Line | Amount (USD) |", "|---|---:|", "| Joinery | 8,400 |", "| Electrical | 5,150 |", "| Flooring | TBD |", "| **Total** | |")}
    e2("hyb-35343", tt="tool_then_write", desc="One amount is TBD, so the total cannot be computed", files=f, traps=("TR-MISSING",), policy=P_RRC,
       turns=[t1("Fill in the Total row of quotes/meridian-fit-out.md with the sum of all the lines.", NONNUM, ["Flooring"])],
       notes=N("TR-MISSING: Flooring is TBD.", "read; non-numeric line.", "File unchanged; answer points at Flooring."))


@reg
def c19():
    p = "预算/年会筹备.md"
    f = {p: L("# 年会筹备预算", "", "| 项目 | 金额 |", "|---|---:|", "| 餐饮 | 8600 |", "| 物料 | 2350 |", "| 场地 | 待定 |", "| **合计** | |")}
    e2("hyb-35344", tt="tool_then_write", desc="One amount is pending", files=f, traps=("TR-MISSING",), policy=P_RRC,
       turns=[t1("把 预算/年会筹备.md 里的合计填上，是上面各项的总和。", NONNUM, ["场地"])],
       notes=N("TR-MISSING: 场地 is 待定.", "read; non-numeric line.", "File unchanged; answer points at 场地."))


@reg
def c20():
    p = "预算/客户答谢会.md"
    f = {p: L("# 客户答谢会预算", "", "| 项目 | 金额 |", "|---|---:|", "| 酒水 | 6800 |", "| 伴手礼 | 3150 |", "| 场地 | 待定 |", "| **合计** | |")}
    ops = [("sub", p, "| 场地 | 待定 |\n| **合计** | |\n", "| 场地 | 12000 |\n| **合计** | **21950** |\n")]
    e2("hyb-35345", tt="multi_turn", desc="Pending amount, then the user supplies it", files=f, ops=ops, traps=("TR-MISSING",), policy=P_RRC,
       turns=[t1("把 预算/客户答谢会.md 的合计算出来填上。", NONNUM, ["场地"]),
              {"p": "场地就按 12000 算，把它填上，合计也一起写好。", "req": ["read_file"], "inc": ["21950"]}],
       notes=N("TR-MISSING: 场地 is 待定 in turn 1.", "turn 1 report; turn 2 fill and total.", "6800+3150+12000 = 21950."))
