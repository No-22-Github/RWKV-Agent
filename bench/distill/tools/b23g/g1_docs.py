"""G1 docs: doc-35501..35508."""
import random

import fill
from common import make, T

B = []


def reg(f):
    B.append(f)
    return f


def R(k):
    return random.Random("b23g-doc-" + k)


def clean(blocks, words):
    flat = "\n".join(l for b in blocks for l in b).lower()
    for w in words:
        assert w.lower() not in flat, w


@reg
def d01():
    r = R("01")
    bl = fill.changelog_blocks(r, top=(2, 9, 4), n_blocks=120)
    k = 44
    ver = bl[k][1].split()[1]
    bl[k].append("- Raised the default request timeout from 15s to 45s for all client calls.")
    header = ["# Lumengate release notes", "", "All notable changes to the gateway are listed here, newest first.", "",
              "## Unreleased", "", "- Streaming endpoints will default to a 20s idle timeout (planned, not shipped yet)."]
    lines = fill.compose(bl, [], header=header, n=520)
    make("doc-35501", sub="G1", task_type="lookup_value", desc="Changelog, timeout bullet in an old release deep in the file",
         path="docs/relnotes-lumengate.md", lines=lines,
         turns=[T("In docs/relnotes-lumengate.md, what default request timeout did release %s introduce?" % ver,
                  ("any", ["45s", "45 s", "45-second", "45 sec"]), "Raised the default request timeout", "20s idle timeout",
                  excl=["20s"])],
         notes=("The first screen shows the Unreleased 20s idle timeout (a different feature, not shipped).",
                "read_file (first screen) -> search_text 'request timeout' or read_file start_line near the release -> answer 45s.",
                "Only release %s carries the 45s bullet." % ver))


@reg
def d02():
    r = R("02")
    bl = fill.en_doc_blocks(r, 160)
    clean(bl, ["escalat", "minutes", "p1", "p2"])
    header = ["# On-call handbook", "", "This handbook describes how the platform group covers incidents outside office hours.", ""]
    p_top = (45, ["", "## 2.3 Ticket handling", "", "P2 tickets escalate to the secondary after 25 minutes without acknowledgement.", ""])
    p_deep = (330, ["", "### Amendment 6 (effective 2026-05-01)", "",
                    "P1 pages escalate to the secondary after 7 minutes without acknowledgement.", ""])
    lines = fill.compose(bl, [p_top, p_deep], header=header, n=480)
    make("doc-35502", sub="G1", task_type="policy_lookup", desc="Handbook amendment deep in the file, different severity on the first screen",
         path="docs/oncall-escalation-handbook.md", lines=lines,
         turns=[T("According to docs/oncall-escalation-handbook.md, after how many minutes does an unacknowledged P1 page escalate to the secondary?",
                  "7", "P1 pages escalate to the secondary", "P2 tickets escalate", excl=["25 minutes"])],
         notes=("First screen has the P2 rule (25 minutes), a different severity.", "read_file -> search_text 'P1' or start_line jump -> 7.",
                "Only Amendment 6 states the P1 rule."))


@reg
def d03():
    r = R("03")
    bl = fill.en_doc_blocks(r, 170)
    clean(bl, ["interest", "notice", "terminat", "discount", "amend"])
    header = ["# Norvale supply terms (internal summary)", "", "Working summary of the signed agreement with Norvale Components Ltd.", ""]
    ps = [(40, ["", "## 3. Invoicing", "", "3.2 Early-payment discount: 2% if the invoice is paid within 10 days.", ""]),
          (60, ["", "## 5. Changes", "", "5.1 Either party may amend the delivery schedule with 14 days' notice.", ""]),
          (320, ["", "## 14. Late payment", "", "14.3 Overdue amounts bear interest at 1.5% per month until settled.", ""]),
          (420, ["", "## 19. Termination", "", "19.1 Termination requires 90 days' written notice by either party.", ""])]
    lines = fill.compose(bl, ps, header=header, n=560)
    make("doc-35503", sub="G1", task_type="policy_lookup", desc="Contract summary, two clauses deep in the file, two multi-turn questions",
         path="contracts/norvale-supply-terms.md", lines=lines,
         turns=[T("What interest rate does contracts/norvale-supply-terms.md say applies to late payments?",
                  ("any", ["1.5%", "1.5 %", "1.5 percent"]), "bear interest at 1.5%", "Early-payment discount", excl=["2%"]),
                T("And how much written notice is needed to terminate?", "90", "90 days' written notice", "14 days' notice", excl=["14 days"])],
         notes=("The first screen shows a 2% early-payment discount and a 14-day amendment notice, both look like the answer.",
                "read_file -> search_text 'interest' -> read near line; second turn search_text 'notice' or start_line.",
                "14.3 and 19.1 are single clauses."))


@reg
def d04():
    r = R("04")
    bl = fill.en_doc_blocks(r, 150)
    clean(bl, ["req/min", "rate limit", "/v2"])
    header = ["# Harbor API reference v2", "", "Base URL: https://api.harborstack.io/v2", ""]
    p1 = (50, ["", "## 2. Rate limits (standard)", "", "| Endpoint | Limit |", "|---|---|", "| GET /v2/reports | 600 req/min |",
               "| POST /v2/imports | 120 req/min |", "| GET /v2/items | 900 req/min |", ""])
    p2 = (310, ["", "## 9. Rate limits (restricted)", "", "| Endpoint | Limit |", "|---|---|", "| POST /v2/exports | 40 req/min |",
                "| POST /v2/webhooks | 60 req/min |", ""])
    p3 = (400, ["", "### 9.2 Report generation", "", "| Endpoint | Limit |", "|---|---|", "| POST /v2/reports | 25 req/min |", ""])
    lines = fill.compose(bl, [p1, p2, p3], header=header, n=520)
    make("doc-35504", sub="G1", task_type="lookup_value", desc="API reference with rate-limit tables, restricted table deep in the file",
         path="docs/api-reference-harbor-v2.md", lines=lines,
         turns=[T("What is the rate limit for POST /v2/exports in docs/api-reference-harbor-v2.md?", "40", "POST /v2/exports", "POST /v2/imports",
                  excl=["120 req"]),
                T("And for POST /v2/reports?", "25", "POST /v2/reports", "GET /v2/reports", excl=["600 req"])],
         notes=("The standard table on the first screen lists similar endpoints (imports, GET reports) with larger limits.",
                "read_file -> search_text 'exports' -> 40; then 'POST /v2/reports' -> 25.", "Each endpoint appears once with its verb."))


@reg
def d05():
    r = R("05")
    bl = fill.minutes_blocks(r, 70)
    flat = "\n".join(l for b in bl for l in b)
    assert "cutover" not in flat.lower() and "rollback" not in flat.lower()
    header = ["# Platform sync minutes, first half of 2026", "", "Tentative cutover for the queue cluster: 2026-10-03 (to be confirmed)."]
    p1 = (330, ["", "## Sync of 2026-04-02 (decision)", "", "- Decision: cutover to the new queue cluster is set for 2026-11-14.", ""])
    p2 = (60, ["", "## Sync of 2026-01-02 (actions)", "", "- Action: Tomasz Kowal owns the capacity plan.", ""])
    p3 = (420, ["", "## Sync of 2026-05-07 (actions)", "", "- Action: Priya Venkataraman owns the rollback plan.", ""])
    lines = fill.compose(bl, [p1, p2, p3], header=header, n=560)
    make("doc-35505", sub="G1", task_type="lookup_value", desc="Meeting minutes, final decision and action owner deep in the file",
         path="meetings/platform-sync-2026H1.md", lines=lines,
         turns=[T("What cutover date did the group finally agree on in meetings/platform-sync-2026H1.md?", "2026-11-14", "cutover to the new queue cluster is set",
                  "Tentative cutover", excl=["2026-10-03"]),
                T("Who owns the rollback plan?", ("any", ["Priya Venkataraman", "Venkataraman", "Priya"]), "owns the rollback plan",
                  "owns the capacity plan", excl=["Tomasz"])],
         notes=("The file starts with a tentative date; an earlier action line names the owner of a different plan.",
                "read_file -> search_text 'cutover' -> 2026-11-14; search_text 'rollback' -> Priya.", "Decision line and rollback action are unique."))


@reg
def d06():
    r = R("06")
    bl = fill.zh_doc_blocks(r, 170)
    clean(bl, ["年假", "工作日"])
    header = ["# 员工手册（2026 年修订）", "", "本手册适用于全体在编员工，条款自 2026-01-01 起执行。", ""]
    p1 = (45, ["", "## 4.1 年假（入门档）", "", "工作满 1 年不满 5 年的，每年享受 5 个工作日带薪年假。", ""])
    p2 = (340, ["", "## 4.4 年假（资深档）", "", "工作满 5 年不满 10 年的，每年享受 10 个工作日带薪年假。", ""])
    lines = fill.compose(bl, [p1, p2], header=header, n=500)
    make("doc-35506", sub="G1", task_type="policy_lookup", desc="员工手册年假分档，目标档位在第二屏之后",
         path="制度/员工手册-2026修订.md", lines=lines,
         turns=[T("按 制度/员工手册-2026修订.md，工作满 5 年不满 10 年的员工，每年有多少个工作日的年假？", "10", "不满 10 年的，每年享受", "不满 5 年的，每年享受",
                  excl=["5 个工作日", "5个工作日"])],
         notes=("第一屏是入门档（5 个工作日），档位不同。", "read_file -> search_text '年假' 或 start_line 跳读 -> 10。", "资深档只有 4.4 一处。"))


@reg
def d07():
    r = R("07")
    bl = fill.zh_doc_blocks(r, 170)
    clean(bl, ["住宿", "报销", "上限", "元"])
    header = ["# 差旅报销办法（汇编）", "", "适用于公司全体员工的境内出差，标准按城市等级划分。", ""]
    p1 = (50, ["", "## 2.1 二线城市标准", "", "二线城市住宿，每晚报销上限为 420 元。", ""])
    p2 = (350, ["", "## 6.2 一线城市标准", "", "一线城市住宿，每晚报销上限为 650 元。", ""])
    lines = fill.compose(bl, [p1, p2], header=header, n=500)
    make("doc-35507", sub="G1", task_type="lookup_value", desc="差旅标准，一线城市条款在后部",
         path="财务/差旅报销办法-汇编.md", lines=lines,
         turns=[T("财务/差旅报销办法-汇编.md 里，一线城市出差住宿每晚最高能报多少元？", "650", "一线城市住宿，每晚报销上限", "二线城市住宿，每晚报销上限",
                  excl=["420"])],
         notes=("第一屏是二线城市标准 420 元。", "read_file -> search_text '一线城市' -> 650。", "一线城市标准唯一。"))


@reg
def d08():
    r = R("08")
    bl = fill.zh_doc_blocks(r, 170)
    clean(bl, ["影响时长", "分钟", "INC-"])
    header = ["# 故障复盘汇编 2026 上半年", "", "每次事故一节，记录影响时长与根因。", ""]
    ps = [(45, ["", "## INC-0107 订单服务磁盘告警", "", "- 影响时长：19 分钟", "- 根因：日志未轮转"]),
          (70, ["", "## INC-0121 缓存集群扩容", "", "- 影响时长：8 分钟", "- 根因：扩容期间重新分片"]),
          (330, ["", "## INC-0412 支付网关证书过期", "", "- 影响时长：83 分钟", "- 根因：证书续期任务未纳入监控"]),
          (430, ["", "## INC-0466 数据库主从切换", "", "- 影响时长：36 分钟", "- 根因：复制延迟导致切换回退"])]
    lines = fill.compose(bl, ps, header=header, n=560)
    make("doc-35508", sub="G1", task_type="lookup_value", desc="事故复盘汇编，两次事故在第二屏之后，两轮追问",
         path="运维/故障复盘汇编-2026上半年.md", lines=lines,
         turns=[T("运维/故障复盘汇编-2026上半年.md 里，支付网关证书过期那次事故影响了多少分钟？", "83", "影响时长：83 分钟", "影响时长：19 分钟", excl=["19 分钟"]),
                T("那次数据库主从切换的事故呢？", "36", "影响时长：36 分钟", "影响时长：8 分钟", excl=["8 分钟"])],
         notes=("第一屏有另外两次事故（19、8 分钟），格式相同。", "read_file -> search_text '证书' -> 83；再 search_text '主从' -> 36。", "两个事故标题唯一。"))
