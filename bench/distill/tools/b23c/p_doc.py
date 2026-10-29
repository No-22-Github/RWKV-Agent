"""35117-35130 (C1) and 35157-35161 (C0): documents."""
from common import c1, c0

BUILDERS = []


def reg(f):
    BUILDERS.append(f)
    return f


@reg
def doc_35117():
    files = {"templates/周报模板-0908.md": "# 周报（{周次}）\n## 本周完成\n- \n## 下周计划\n- \n",
             "templates/周报模板-0910.md": "# {周次} 周报\n## 进展\n## 风险\n## 需要的支持\n",
             "reports/本周要点.txt": "上线了订单导出；修复支付超时；下周做权限评审。\n"}
    c1("doc-35117", tt="draft_document", files=files, p1="按上周的模板写这周的周报，放到 reports 里。", stem="0908",
       desc="Asks for this week's report from last week's template when two templates date from last week", ref="两个模板都是上周的，追问用哪一个。")


@reg
def doc_35118():
    files = {"invoices/INV-2291-draft.md": "# Invoice INV-2291\nBill to: ______\nAmount: 4,200.00\n",
             "addresses/brightwell-hq.txt": "Brightwell Foods, 14 Calder Street, Leeds LS2 7HY\n",
             "addresses/brightwell-warehouse.txt": "Brightwell Foods Distribution, Unit 9 Marsh Lane, Doncaster DN4 5PL\n"}
    c1("doc-35118", tt="draft_document", files=files, p1="Fill in the Bill to line on the Brightwell invoice.", stem="warehouse",
       desc="Asks to fill an invoice header when the customer has two addresses on file", ref="read the invoice and both addresses, ask which one is the billing address.")


@reg
def doc_35119():
    files = {"docs/供应商联系人.md": "# 供应商联系人\n- 姓名：陈立\n- 公司：衡泰物流\n- 电话：021-5550-1183\n- 邮箱：chenli@hengtai-logistics.cn\n"}
    c1("doc-35119", tt="write_structured", files=files, p1="把联系人电话改成新号码。", stem="021-5550-1183",
       desc="Asks to change a phone number without giving the new one", ref="读文件，新号码不在工作区，追问。")


@reg
def doc_35120():
    files = {"docs/travel-policy.md": "# Travel policy\n- Hotel limit: 120 per night\n- Meal limit: 60 per day\n- Taxi: receipts required above 25\n"}
    c1("doc-35120", tt="write_structured", files=files, p1="Update the policy doc with the new reimbursement limit.", stem="hotel",
       desc="Asks to update an unspecified limit to an unstated new value", ref="read policy; ask which limit and the new amount.")


@reg
def doc_35121():
    files = {"docs/release-notes.md": "# 发布说明\n\n## v3.4.0 (2026-08-28)\n- 新增批量导出\n", "package.json": "{\"name\": \"portal\", \"version\": \"3.5.0-rc.1\"}\n"}
    c1("doc-35121", tt="write_structured", files=files, p1="在发布说明里加上这次的版本号和日期。", stem="3.5.0",
       desc="Asks to add this release's version and date when only an RC version exists", ref="package.json 只有 3.5.0-rc.1，日期未知，追问正式版本号和发布日期。")


@reg
def doc_35122():
    files = {"meetings/q4-planning-agenda.md": "# Q4 Planning\nDate: 2026-09-29\n1. Review roadmap\n2. Staffing\n"}
    c1("doc-35122", tt="write_structured", files=files, p1="Change the title of the agenda to the new meeting name.", stem="q4-planning",
       desc="Asks to retitle an agenda to a name nobody gave", ref="read agenda; ask for the new name.")


@reg
def doc_35123():
    files = {"proposal/方案-v3.md": "# 迁移方案 v3\n采用方案：待定\n", "review/评审意见-张工.md": "# 张工评审\n结论：采用方案 A（分阶段迁移），预算 80 万。\n",
             "review/评审意见-李工.md": "# 李工评审\n结论：采用方案 B（一次切换），预算 50 万。\n"}
    c1("doc-35123", tt="write_structured", files=files, p1="请按评审意见修改方案文档。", stem="李工",
       desc="Asks to apply review comments that contradict each other", ref="读两份评审，结论冲突，追问采纳哪位的意见。")


@reg
def doc_35124():
    files = {"faq/refunds-answer.md": "Refunds are accepted within 14 days of delivery.\n", "faq/returns-answer.md": "Returns are accepted within 30 days of delivery.\n",
             "faq/combined-answer.md": "(empty)\n"}
    c1("doc-35124", tt="write_structured", files=files, p1="Merge the two FAQ answers about refunds into one.", stem="refunds-answer",
       desc="Asks to merge two FAQ answers that give different windows", ref="read both, notice 14 vs 30 days, ask which applies.")


@reg
def doc_35125():
    files = {"minutes/纪要-0912.md": "# 产品周会 0912\n出席：吴静、郑凯、Ravi\n行动项：\n1. 更新定价页（负责人：）\n2. 回访三家客户（负责人：）\n"}
    c1("doc-35125", tt="write_structured", files=files, p1="把会议纪要里的行动项负责人补上。", stem="纪要-0912",
       desc="Asks to fill action-item owners that the minutes never assigned", ref="读纪要，没有分配信息，追问每项由谁负责。")


@reg
def doc_35126():
    files = {"templates/notice-formal.md": "Dear customer,\nWe regret to inform you of a service interruption on {date}.\nSincerely,\nThe Support Team\n",
             "templates/notice-friendly.md": "Hi there!\nHeads up: we'll be down on {date}. Thanks for bearing with us.\n- Support\n",
             "notices/outage-0918-ref.md": "# Outage 2026-09-18, 01:00-03:00 UTC\n"}
    c1("doc-35126", tt="draft_document", files=files, p1="Draft the customer notice for the outage using our standard template.", p2="The friendly one. Save it as notices/outage-0918-notice.md.",
       stem="friendly", new={"notices/outage-0918-notice.md": {"contains": ["2026-09-18"]}},
       desc="Asks for an outage notice when there are two equally standard templates", ref="ask formal or friendly; write the notice with the date.")


@reg
def doc_35127():
    files = {"price/retail-list.csv": "item,price\nBolt M6,1.00\nNut M6,0.50\nWasher M6,0.20\n", "price/wholesale-list.csv": "item,price\nBolt M6,0.70\nNut M6,0.35\nWasher M6,0.12\n"}
    c1("doc-35127", tt="write_structured", files=files, p1="把价格表里的单价调整一下。", p2="零售价表，所有单价上调 10%。", stem="wholesale",
       rules={"price/retail-list.csv": ("has", ["item,price", "Bolt M6,1.10", "Nut M6,0.55", "Washer M6,0.22"])},
       desc="Asks for a price adjustment with two price lists and no percentage", ref="追问哪张表、调多少；答复后零售表整体 +10%。")


@reg
def doc_35128():
    files = {"rota/oncall-sep.md": "# On-call, September\n- Sep 14: Alana (open until noon)\n- Sep 21: (open)\n- Sep 28: Kofi\n"}
    c1("doc-35128", tt="write_structured", files=files, p1="Add me to the on-call rota for next week.", p2="I'm Rahul Mehta. Replace (open) with my name on the Sep 21 line.", stem="Sep 21",
       rules={"rota/oncall-sep.md": ("sub", "Sep 21: (open)", "Sep 21: Rahul Mehta")},
       desc="Asks to add 'me' to a rota without saying who that is", ref="ask for the name (and the slot); then edit one line.")


@reg
def doc_35129():
    files = {"通知/放假通知.md": "# 放假通知\n国庆放假 10 月 1 日至 7 日。\n\n落款：行政部\n", "通知/停电通知.md": "# 停电通知\n9 月 20 日 8:00-12:00 机房停电。\n\n落款：行政部\n"}
    c1("doc-35129", tt="write_structured", files=files, p1="把通知的落款改成新的。", p2="放假通知的，落款改成 人事行政部。", stem="停电通知",
       rules={"通知/放假通知.md": ("sub", "落款：行政部", "落款：人事行政部")},
       desc="Asks to change a signature on notices without saying which notice or the new text", ref="追问哪份通知、新落款；答复后改放假通知。")


@reg
def doc_35130():
    files = {"docs/install-guide.md": "# Install\nRequires Node 18.\nRun `npm ci`.\n", "docs/contributing-setup.md": "# Dev setup\nUse Node 18 LTS locally.\n"}
    c1("doc-35130", tt="write_structured", files=files, p1="Update the docs for the new Node version.", p2="Node 22, in both files.", stem="install-guide",
       rules={"docs/install-guide.md": ("sub", "Node 18", "Node 22"), "docs/contributing-setup.md": ("sub", "Node 18 LTS", "Node 22")},
       desc="Asks to update docs for an unstated Node version", ref="ask which version; then update both mentions.")


# ---- C0 ----
@reg
def doc_35157():
    files = {"templates/周报模板-0908.md": "# 周报（{周次}）\n## 本周完成\n- \n## 下周计划\n- \n", "templates/周报模板-0910.md": "# {周次} 周报\n## 进展\n## 风险\n",
             "reports/本周要点.txt": "上线了订单导出；修复支付超时；下周做权限评审。\n", "reports/历史-0909.md": "# 上周周报\n略\n"}
    c0("doc-35157", tt="draft_document", files=files, decoy=True,
       prompts=["按 templates/周报模板-0908.md 这个模板，用 reports/本周要点.txt 的内容写这周的周报，保存成 reports/周报-0916.md。", "再把标题里的周次写成 第 38 周。"],
       new={"reports/周报-0916.md": {"contains": ["订单导出", "第 38 周"]}},
       desc="Names the template and output file explicitly, then a follow-up tweak", ref="读模板和要点，写周报，第二轮改标题周次。")


@reg
def doc_35158():
    files = {"invoices/INV-2300-draft.md": "# Invoice INV-2300\nBill to: ______\nAmount: 880.00\n", "addresses/brightwell-hq.txt": "Brightwell Foods, 14 Calder Street, Leeds LS2 7HY\n",
             "addresses/brightwell-warehouse.txt": "Brightwell Foods Distribution, Unit 9 Marsh Lane, Doncaster DN4 5PL\n"}
    c0("doc-35158", tt="draft_document", files=files, decoy=True,
       prompts=["Fill in the Bill to line on INV-2300 with the head office address from the Brightwell HQ file."],
       rules={"invoices/INV-2300-draft.md": ("sub", "Bill to: ______", "Bill to: Brightwell Foods, 14 Calder Street, Leeds LS2 7HY")},
       desc="Names the head-office address file explicitly", ref="read the HQ file, fill the line.")


@reg
def doc_35159():
    files = {"docs/供应商联系人.md": "# 供应商联系人\n- 姓名：陈立\n- 公司：衡泰物流\n- 电话：021-5550-1183\n"}
    c0("doc-35159", tt="write_structured", files=files, prompts=["把联系人电话改成 021-5550-2290。"],
       rules={"docs/供应商联系人.md": ("sub", "021-5550-1183", "021-5550-2290")}, desc="Gives the new phone number", ref="替换电话。")


@reg
def doc_35160():
    files = {"docs/travel-policy.md": "# Travel policy\n- Hotel limit: 120 per night\n- Meal limit: 60 per day\n- Taxi: receipts required above 25\n"}
    c0("doc-35160", tt="write_structured", files=files, prompts=["Set the hotel limit in the travel policy to 140 per night."],
       rules={"docs/travel-policy.md": ("sub", "Hotel limit: 120 per night", "Hotel limit: 140 per night")}, desc="Names the limit and the value", ref="edit the hotel line.")


@reg
def doc_35161():
    files = {"docs/release-notes.md": "# Release notes\n\n## v3.4.0 (2026-08-28)\n- Bulk export\n", "package.json": "{\"name\": \"portal\", \"version\": \"3.5.0\"}\n"}
    c0("doc-35161", tt="write_structured", files=files, prompts=["Add an entry for v3.5.0 dated 2026-09-18 to the release notes with the line 'Faster search'."], decoy=True,
       rules={"docs/release-notes.md": ("has", ["# Release notes", "v3.5.0 (2026-09-18)", "Faster search", "v3.4.0 (2026-08-28)"])},
       desc="Gives version, date and content for the release entry", ref="add an entry above v3.4.0.")
