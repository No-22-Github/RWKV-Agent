"""F3 several long registers -> one summary file, cases 34559-34565."""
from f3 import F3

ZH = dict(level="级别：", status="状态：", owner="负责人：", due="截止：", note="说明：", hi="高", mids=["中", "低"], open="未关闭", closed="已关闭")


def build():
    F3("doc-34559", "zh", [("巡检/一号厂区-巡检问题.md", "XJ", 150, 2, "一号厂区巡检问题记录"),
                           ("巡检/二号厂区-巡检问题.md", "EJ", 160, 3, "二号厂区巡检问题记录"),
                           ("巡检/物流园-巡检问题.md", "WL", 140, 2, "物流园巡检问题记录")],
       ["消防通道", "配电柜", "叉车", "仓储货架", "监控设备", "危化品存放"],
       dict(ZH, level="严重程度：", hi="严重", mids=["较重", "一般"], status="整改情况：", open="未整改", closed="已整改", due="整改期限："),
       "安监部要出季度通报。三个厂区的巡检问题记录在巡检目录下，帮我找出严重程度为严重、到现在还没整改的问题，按厂区分组，把编号、标题和负责人写到 严重问题未整改通报.md。",
       "严重问题未整改通报.md")
    F3("doc-34560", "en", [("vendor-audits/northwind-findings.md", "NW", 80, 2, "Northwind audit findings"),
                           ("vendor-audits/pelican-logistics-findings.md", "PL", 96, 2, "Pelican Logistics audit findings"),
                           ("vendor-audits/quarry-cloud-findings.md", "QC", 110, 3, "Quarry Cloud audit findings"),
                           ("vendor-audits/redfern-print-findings.md", "RP", 70, 1, "Redfern Print audit findings")],
       ["access control", "subcontractors", "data retention", "incident drills", "encryption", "contract terms"],
       dict(level="Rating: ", status="Remediation: ", owner="Owner: ", due="Due: ", note="Finding: ", hi="Critical", mids=["Major", "Minor"], open="Pending", closed="Completed"),
       "Procurement needs a one-pager on supplier audits. Go through the four findings files in vendor-audits and list the Critical findings whose remediation is still Pending, with id, title and owner, saved as critical-pending-findings.md.",
       "critical-pending-findings.md")
    F3("doc-34561", "zh", [("实验室/材料楼-设备报修.md", "CL", 100, 2, "材料楼设备报修记录"),
                           ("实验室/生物楼-设备报修.md", "SW", 118, 2, "生物楼设备报修记录"),
                           ("实验室/信息楼-设备报修.md", "XX", 90, 2, "信息楼设备报修记录")],
       ["离心机", "质谱仪", "超净台", "空调机组", "服务器机柜", "示波器"],
       dict(ZH, level="故障等级：", hi="一级", mids=["二级", "三级"], status="维修状态：", open="未修复", closed="已修复", owner="报修人：", due="期望修复："),
       "后勤处在清理积压报修。实验室目录下有三栋楼的设备报修记录，帮我找出故障等级为一级、还没修复、并且报修人是 周杰 的记录，把编号和标题写到 周杰-一级未修复.md。",
       "周杰-一级未修复.md", owner_filter="周杰")
    F3("doc-34562", "en", [("support/emea-escalations.md", "EM", 90, 2, "EMEA support escalations"),
                           ("support/apac-escalations.md", "AP", 104, 3, "APAC support escalations"),
                           ("support/americas-escalations.md", "AM", 120, 2, "Americas support escalations"),
                           ("support/partner-escalations.md", "PA", 66, 1, "Partner support escalations")],
       ["billing disputes", "sync failures", "login lockouts", "data exports", "api quotas", "invoice errors"],
       dict(level="Tier: ", status="Ticket state: ", owner="Assignee: ", due="Reply by: ", note="Summary: ", hi="Escalated", mids=["Standard", "Basic"], open="Waiting", closed="Resolved"),
       "Customer success wants Lena Ortiz's backlog. In the four escalation files under support, find tickets that are Tier Escalated, still Waiting, and assigned to Lena Ortiz, and save their ids and titles to lena-escalated-waiting.md.",
       "lena-escalated-waiting.md", owner_filter="Lena Ortiz")
    F3("doc-34563", "zh", [("评审意见/数据结构课-评审意见.md", "SJ", 70, 1, "数据结构课程评审意见"),
                           ("评审意见/操作系统课-评审意见.md", "CZ", 82, 2, "操作系统课程评审意见"),
                           ("评审意见/编译原理课-评审意见.md", "BY", 76, 2, "编译原理课程评审意见"),
                           ("评审意见/数据库课-评审意见.md", "SK", 90, 2, "数据库课程评审意见"),
                           ("评审意见/计算机网络课-评审意见.md", "WL", 64, 1, "计算机网络课程评审意见")],
       ["教学大纲", "实验指导书", "考核方式", "课件", "习题库", "课程思政"],
       dict(ZH, level="意见类型：", hi="必改", mids=["建议", "提示"], status="落实情况：", open="未落实", closed="已落实", owner="责任教师：", due="落实期限："),
       "教学评估要交材料。五门课程的评审意见在评审意见目录下，帮我整理出意见类型是必改、但至今未落实的条目，按课程分组写到 必改未落实汇总.md，带上编号、标题和责任教师。",
       "必改未落实汇总.md")
    F3("doc-34564", "en", [("change-board/platform-change-requests.md", "PF", 95, 2, "Platform change requests"),
                           ("change-board/data-change-requests.md", "DC", 110, 3, "Data team change requests"),
                           ("change-board/mobile-change-requests.md", "MB", 85, 2, "Mobile change requests")],
       ["config rollout", "schema change", "feature flag", "library upgrade", "network rule", "cron schedule"],
       dict(level="Impact: ", status="Approval: ", owner="Requester: ", due="Planned: ", note="Reason: ", hi="Major", mids=["Moderate", "Minor"], open="Pending", closed="Approved"),
       "I'm preparing the change advisory board agenda. Looking through the three change-request files in change-board, list the Major-impact requests that are still Pending approval, with id, title and requester, and save them to cab-agenda-major.md.",
       "cab-agenda-major.md")
    F3("doc-34565", "zh", [("合同审查/采购合同-条款清单.md", "CH", 88, 2, "采购合同条款审查清单"),
                           ("合同审查/外包合同-条款清单.md", "WB", 104, 2, "外包合同条款审查清单"),
                           ("合同审查/租赁合同-条款清单.md", "ZL", 72, 1, "租赁合同条款审查清单"),
                           ("合同审查/合作协议-条款清单.md", "HZ", 98, 2, "合作协议条款审查清单")],
       ["违约金", "付款节点", "保密义务", "知识产权", "管辖约定", "解除条件"],
       dict(ZH, level="风险等级：", hi="高", mids=["中", "低"], status="法务确认：", open="待确认", closed="已确认", owner="经办人：", due="确认期限："),
       "法务部让我把吴婷经办的合同里，风险等级为高、法务还没确认的条款挑出来。四类合同的条款清单都在合同审查目录下，结果写到 吴婷-高风险待确认条款.md，要编号和标题。",
       "吴婷-高风险待确认条款.md", owner_filter="吴婷")
