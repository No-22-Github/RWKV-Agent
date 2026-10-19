"""F3 several long registers -> one summary file, cases 34551-34558."""
from f3 import F3

ZH = dict(level="级别：", status="状态：", owner="负责人：", due="截止：", note="说明：", hi="高", mids=["中", "低"], open="未关闭", closed="已关闭")
EN = dict(level="Severity: ", status="Status: ", owner="Owner: ", due="Due: ", note="Note: ", hi="High", mids=["Medium", "Low"], open="Open", closed="Closed")
ZH_BUG = dict(ZH, level="优先级：", hi="P0", mids=["P1", "P2", "P3"], open="待修复", closed="已修复")
EN_BUG = dict(EN, level="Priority: ", hi="P0", mids=["P1", "P2", "P3"], open="Unresolved", closed="Fixed")


def build():
    F3("doc-34551", "zh", [("项目风险/青岚平台-风险登记簿.md", "QL", 72, 2, "青岚平台风险登记簿"),
                           ("项目风险/海豚结算-风险登记簿.md", "HT", 95, 2, "海豚结算风险登记簿"),
                           ("项目风险/远帆门户-风险登记簿.md", "YF", 110, 3, "远帆门户风险登记簿")],
       ["接口联调", "数据迁移", "第三方服务", "上线排期", "测试资源", "权限设计", "性能压测"], ZH,
       "我要给周会准备材料。三个项目的风险登记簿都在项目风险文件夹里，帮我找出所有级别为高、状态还没关闭的风险，按项目分组列出编号、标题和负责人，写到 高风险未关闭清单.md。",
       "高风险未关闭清单.md")
    F3("doc-34552", "en", [("defect-tracker/ledgerline-defects.md", "LL", 85, 2, "Ledgerline defect list"),
                           ("defect-tracker/orchard-mobile-defects.md", "OM", 100, 3, "Orchard Mobile defect list"),
                           ("defect-tracker/tidewater-api-defects.md", "TW", 120, 2, "Tidewater API defect list")],
       ["login flow", "report export", "push notices", "payment retry", "search index", "profile sync", "dark mode"], EN_BUG,
       "Three defect lists live under defect-tracker. Find every P0 defect that is still unresolved, group them by product, and save id, title and owner in p0-open-defects.md.",
       "p0-open-defects.md")
    F3("doc-34553", "zh", [("采购/华北片区-采购申请汇总.md", "CG", 70, 2, "华北片区采购申请汇总"),
                           ("采购/华东片区-采购申请汇总.md", "HD", 88, 2, "华东片区采购申请汇总"),
                           ("采购/华南片区-采购申请汇总.md", "HN", 100, 2, "华南片区采购申请汇总"),
                           ("采购/西部片区-采购申请汇总.md", "XB", 64, 1, "西部片区采购申请汇总")],
       ["办公设备", "服务器", "安防设备", "培训服务", "车辆租赁", "软件授权"],
       dict(level="金额档：", status="审批：", owner="申请人：", due="需求日期：", note="用途：", hi="大额", mids=["中额", "小额"], open="待审批", closed="已审批"),
       "四个片区的采购申请汇总都在采购目录下。帮我挑出金额档为大额、审批还没完成、而且申请人是 孙悦 的申请，把编号和标题整理进 孙悦-待批大额采购.md。",
       "孙悦-待批大额采购.md", owner_filter="孙悦")
    F3("doc-34554", "en", [("programme/atlas-risk-register.md", "AT", 90, 2, "Atlas programme risk register"),
                           ("programme/beacon-risk-register.md", "BC", 105, 2, "Beacon programme risk register"),
                           ("programme/cairn-risk-register.md", "CR", 75, 1, "Cairn programme risk register"),
                           ("programme/dune-risk-register.md", "DN", 118, 2, "Dune programme risk register")],
       ["vendor contract", "data centre move", "regulatory review", "staff turnover", "tooling migration", "pilot rollout"], EN,
       "For the steering group: pull out the high-severity risks that are still open and owned by Priya Nair across the four registers in the programme folder, and write their ids and titles to priya-open-high.md.",
       "priya-open-high.md", owner_filter="Priya Nair")
    F3("doc-34555", "zh", [("缺陷库/云账本-缺陷清单.md", "YZ", 84, 2, "云账本缺陷清单"),
                           ("缺陷库/智巡-缺陷清单.md", "ZX", 96, 3, "智巡缺陷清单"),
                           ("缺陷库/灯塔-缺陷清单.md", "DT", 68, 2, "灯塔缺陷清单")],
       ["登录", "对账", "消息推送", "报表导出", "权限同步", "离线缓存", "扫码"], ZH_BUG,
       "发版前要清一下 P0。三份缺陷清单在缺陷库目录，请把优先级是 P0 且还待修复的缺陷整理出来，写到 发版阻塞项.md，包含编号、标题和负责人。",
       "发版阻塞项.md")
    F3("doc-34556", "en", [("specs/gateway-requirements.md", "GW", 66, 2, "Gateway requirements"),
                           ("specs/ledger-requirements.md", "LG", 90, 2, "Ledger requirements"),
                           ("specs/notifier-requirements.md", "NT", 72, 2, "Notifier requirements"),
                           ("specs/portal-requirements.md", "PT", 100, 2, "Portal requirements"),
                           ("specs/scheduler-requirements.md", "SC", 60, 1, "Scheduler requirements")],
       ["rate limiting", "audit trail", "retry policy", "tenant isolation", "export format", "timeouts"],
       dict(EN, level="Level: ", hi="MUST", mids=["SHOULD", "MAY"], status="Implementation: ", open="Not started", closed="Done"),
       "Release planning needs the gaps. Across the five requirement files in specs, list every requirement at level MUST whose implementation has not started, with id, title and owner, in must-gaps.md.",
       "must-gaps.md")
    F3("doc-34557", "zh", [("客服/华中大区-客诉工单.md", "KF", 78, 2, "华中大区客诉工单"),
                           ("客服/西南大区-客诉工单.md", "XN", 92, 3, "西南大区客诉工单"),
                           ("客服/东北大区-客诉工单.md", "DB", 64, 1, "东北大区客诉工单"),
                           ("客服/海外-客诉工单.md", "HW", 105, 2, "海外客诉工单"),
                           ("客服/线上商城-客诉工单.md", "SC", 80, 2, "线上商城客诉工单")],
       ["退款", "物流延误", "质量问题", "发票", "会员权益", "售后维修"],
       dict(level="紧急程度：", status="处理状态：", owner="跟进人：", due="答复期限：", note="摘要：", hi="紧急", mids=["一般", "普通"], open="处理中", closed="已办结"),
       "年底要复盘客诉。五个大区的工单文件在客服目录，找出紧急程度为紧急、仍在处理中的工单，按文件分组写到 紧急未办结工单.md，每条要编号、标题、跟进人。",
       "紧急未办结工单.md")
    F3("doc-34558", "en", [("followups/q1-incident-actions.md", "A1", 88, 2, "Q1 incident follow-up actions"),
                           ("followups/q2-incident-actions.md", "A2", 102, 3, "Q2 incident follow-up actions"),
                           ("followups/q3-incident-actions.md", "A3", 96, 2, "Q3 incident follow-up actions")],
       ["alerting", "failover", "capacity", "runbooks", "on-call handoff", "backups", "certificates"], EN,
       "Ahead of the postmortem review, gather the high-severity follow-up actions from the three quarterly files in followups that are still open and put id, title and owner in open-actions-review.md.",
       "open-actions-review.md")
