"""31371-31383: policy and internal-doc questions."""
from p3 import local, reg, fx


@reg
def c31371():
    files = {"docs/api.md": "# API 使用说明\n\n限流：每个 API key 每分钟最多 600 次请求，超出返回 429。\n", "docs/legacy-api.md": "# 旧版 API\n\n限流：每分钟最多 120 次。该版本已下线。\n", "README.md": "# 接口文档\n"}
    web = [fx("限流", "https://blog.example.org/rate-limits", "常见 API 限流策略", "多数公共 API 默认每分钟 100 次请求。\n", "2026-03-02")]
    local("doc-31371", tt="policy_lookup", files=files, q="我们的 API 限流是多少？", path="docs/api.md", pat=r"每分钟最多 (\d+) 次请求", variant="A", decoy="120", web=web, webval="100",
          desc="Asks 'what is our API rate limit' with no mention of files; only docs/api.md holds it", ref="list_files 找到 docs/api.md，读出 600 次/分钟；不搜网页。")


@reg
def c31372():
    files = {"hr/leave-policy.md": "# 请假制度\n\n年假：入职满一年 10 天，满五年 15 天。病假需提供医院证明。\n", "hr/old-leave-2023.md": "# 2023 请假制度（作废）\n\n年假：入职满一年 5 天。\n"}
    local("doc-31372", tt="policy_lookup", files=files, q="入职满一年能休几天年假？", path="hr/leave-policy.md", pat=r"满一年 (\d+) 天", variant="B", decoy="5",
          desc="Asks about annual leave days as if it were general knowledge; the company policy file answers it", ref="搜索/读取 hr/leave-policy.md，满一年 10 天（旧版 5 天已作废）。")


@reg
def c31373():
    files = {"ops/oncall.md": "# 值班手册\n\n夜间告警先打电话给值班人，5 分钟内无人响应再升级给 SRE 主管。\n升级响应时限：15 分钟。\n", "ops/runbook-db.md": "# 数据库手册\n\n主库故障切换时限 30 分钟。\n"}
    local("doc-31373", tt="policy_lookup", files=files, q="告警升级后多少分钟内必须响应？", path="ops/oncall.md", pat=r"响应时限：(\d+) 分钟", variant="A", decoy="30",
          desc="Asks for the escalation response limit without naming a document", ref="读 ops/oncall.md，升级响应时限 15 分钟；runbook-db 的 30 分钟是另一回事。")


@reg
def c31374():
    files = {"policies/expense.md": "# Expense policy\n\nMeals are reimbursed up to 85 per day. Hotel cap is 220 per night.\n", "policies/travel.md": "# Travel policy\n\nBook economy for flights under 6 hours.\n"}
    web = [fx("meal allowance", "https://travel.example.net/per-diem", "Typical business per diem", "Typical per diem for meals is 60 per day.\n", "2026-05-12")]
    local("doc-31374", tt="policy_lookup", files=files, q="What's the daily meal allowance for business trips?", path="policies/expense.md", pat=r"up to (\d+) per day", variant="A", decoy="60", web=web, webval="60",
          desc="Asks for the daily meal allowance as a general question; the expense policy file gives the company figure", ref="读 policies/expense.md：每日 85；公网通用值 60 不是公司标准。")


@reg
def c31375():
    files = {"it/security.md": "# 信息安全规范\n\n密码最短长度：14 位；每 90 天更换；连续输错 5 次锁定账号。\n", "it/vpn.md": "# VPN 使用\n\n空闲 30 分钟自动断开。\n"}
    local("doc-31375", tt="policy_lookup", files=files, q="公司要求密码至少多少位？", path="it/security.md", pat=r"最短长度：(\d+) 位", variant="B", decoy="8",
          desc="Asks the minimum password length as general advice; the internal security rule answers it", ref="读 it/security.md：14 位。")


@reg
def c31376():
    files = {"legal/retention.md": "# Data retention\n\nCustomer invoices are kept for 7 years. Support chats are kept for 18 months.\n", "legal/privacy.md": "# Privacy\n\nUsers may request deletion within 30 days.\n"}
    local("doc-31376", tt="policy_lookup", files=files, q="How long do we keep support chats?", path="legal/retention.md", pat=r"chats are kept for (\d+) months", variant="A", decoy="30",
          desc="Asks how long support chats are retained without naming a file", ref="读 legal/retention.md：18 个月。")


@reg
def c31377():
    files = {"release/process.md": "# 发布流程\n\n每周四 14:00 冻结代码，周五 10:00 发布。紧急修复走热修通道，需两人审批。\n", "release/changelog.md": "# 变更\n- 3.8.1 热修\n"}
    local("doc-31377", tt="policy_lookup", files=files, q="我们每周几发布？", path="release/process.md", pat=r"(周五) 10:00 发布", variant="B", decoy="周四",
          desc="Asks which weekday releases go out; the release process file answers", ref="读 release/process.md：周五 10:00 发布（周四只是冻结）。")


@reg
def c31378():
    files = {"onboarding/checklist.md": "# Onboarding checklist\n\nDay 1: laptop and accounts. Day 3: security training. Day 10: first code review.\n", "onboarding/faq.md": "# FAQ\n\nWhere is the canteen? Floor 2.\n"}
    local("doc-31378", tt="policy_lookup", files=files, q="On which day does a new hire do their first code review?", path="onboarding/checklist.md", pat=r"Day (\d+): first code review", variant="A", decoy="3",
          desc="Asks about the first code review day for new hires; the onboarding checklist has it", ref="读 onboarding/checklist.md：第 10 天。")


@reg
def c31379():
    files = {"finance/approval.md": "# 审批权限\n\n单笔 5000 元以内部门经理审批；5000 至 50000 元需财务总监；超过 50000 元需 CEO。\n", "finance/faq.md": "# 报销常见问题\n\n发票抬头必须与公司全称一致。\n"}
    local("doc-31379", tt="policy_lookup", files=files, q="超过多少钱的采购要 CEO 批准？", path="finance/approval.md", pat=r"超过 (\d+) 元需 CEO", variant="B", decoy="5000",
          desc="Asks the purchase amount above which CEO approval is needed", ref="读 finance/approval.md：超过 50000 元。")


@reg
def c31380():
    files = {"support/sla.md": "# SLA\n\nP1 incidents: first response within 20 minutes. P2: 4 hours. P3: next business day.\n", "support/contacts.md": "# Contacts\nsupport@internal.example\n"}
    web = [fx("sla response time", "https://saas.example.com/sla-guide", "SLA guide", "A typical P1 first response target is 60 minutes.\n", "2026-04-01")]
    local("doc-31380", tt="policy_lookup", files=files, q="What's our first response target for a P1 incident?", path="support/sla.md", pat=r"P1 incidents: first response within (\d+) minutes", variant="A", decoy="60", web=web, webval="60",
          desc="Asks the P1 first response target; only the SLA file has our number while a public guide shows another", ref="读 support/sla.md：20 分钟，不用公网的 60。")


@reg
def c31381():
    files = {"team/working-hours.md": "# 工作时间\n\n核心协作时段 10:00-16:00，每周三下午为无会议时间。\n", "team/holidays.md": "# 节假日\n国庆放假 7 天。\n"}
    local("doc-31381", tt="policy_lookup", files=files, q="咱们每周哪天下午不开会？", path="team/working-hours.md", pat=r"每(周三下午)为无会议时间", variant="B", decoy="周五下午",
          desc="Asks which afternoon of the week has no meetings", ref="读 team/working-hours.md：周三下午。")


@reg
def c31382():
    files = {"standards/code-style.md": "# 代码规范\n\n单行最大长度 100 个字符；函数不超过 60 行；提交信息用中文。\n", "standards/readme.md": "# 规范目录\n"}
    local("doc-31382", tt="policy_lookup", files=files, q="我们代码规范里函数最多可以有多少行？", path="standards/code-style.md", pat=r"函数不超过 (\d+) 行", variant="A", decoy="100",
          desc="Asks the function length limit in our code standard; line length 100 is a near-miss", ref="读 code-style.md：函数 60 行（100 是单行字符数）。")


@reg
def c31383():
    files = {"vendor/terms.md": "# Vendor terms\n\nPayment is due 45 days after invoice. Late fee: 2% per month.\n", "vendor/contacts.md": "# Contacts\nbilling@vendor.example\n"}
    local("doc-31383", tt="policy_lookup", files=files, q="What are the payment terms with our vendor, in days?", path="vendor/terms.md", pat=r"due (\d+) days", variant="B", decoy="30",
          desc="Asks vendor payment terms in days with no file hint", ref="读 vendor/terms.md：45 天。")
