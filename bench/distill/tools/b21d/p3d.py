"""31410-31420: questions where an older note and a newer one disagree, plus more internal lookups."""
from p3 import local, reg, fx

S = "TR-SUPERSEDE"


@reg
def c31410():
    files = {"office/address-2024.md": "# 办公地址（2024）\n\n北京市海淀区中关村南大街 18 号 6 层。\n", "office/address-2026.md": "# 办公地址（2026-07 起）\n\n自 2026 年 7 月起搬迁至 上海市浦东新区张江路 88 号。2024 年的地址作废。\n"}
    local("doc-31410", tt="policy_lookup", files=files, q="我们公司现在的办公地址在哪？", path="office/address-2026.md", pat=r"搬迁至 (上海市浦东新区张江路 88 号)", variant="A", decoy="中关村南大街 18 号",
          trap=S, desc="Asks the company's office address now; a 2024 note and a 2026 relocation note disagree", ref="读两份地址文件，2026-07 起搬到张江路 88 号。")


@reg
def c31411():
    files = {"pricing/plans-2025.md": "# Plans (2025)\n\nPro plan: 29 per month.\n", "pricing/plans-2026.md": "# Plans (effective 2026-06-01)\n\nPro plan: 39 per month. Replaces the 2025 price list.\n"}
    web = [fx("pro plan price", "https://compare.example.com/saas-pricing", "SaaS pricing roundup", "Pro tiers across the market cost about 25 per month.\n", "2026-02-03")]
    local("doc-31411", tt="policy_lookup", files=files, q="How much does our Pro plan cost per month?", path="pricing/plans-2026.md", pat=r"Pro plan: (39) per month", variant="B", decoy="29",
          trap=S, web=web, webval="25", desc="Asks the Pro plan monthly price; the 2026 list replaces the 2025 one and a web roundup shows another figure", ref="读 plans-2026.md：39；2025 的 29 已被替换。")


@reg
def c31412():
    files = {"hr/benefits-v1.md": "# 福利 v1\n\n每年体检预算 800 元。\n", "hr/benefits-v2.md": "# 福利 v2（2026-01 生效）\n\n每年体检预算 1500 元，取代 v1。\n"}
    local("doc-31412", tt="policy_lookup", files=files, q="公司每年给多少体检预算？", path="hr/benefits-v2.md", pat=r"体检预算 (\d+) 元，取代", variant="A", decoy="800",
          trap=S, desc="Asks the yearly health-check budget with a v1 and a v2 benefits file", ref="v2 取代 v1：1500 元。")


@reg
def c31413():
    files = {"api/changelog.md": "# Changelog\n\n## 4.2.0 (2026-09-01)\n- default page size 100 (was 50)\n\n## 4.1.0\n- default page size 50\n", "api/overview.md": "# Overview\nsee changelog\n"}
    local("code-31413", tt="locate_definition", files=files, q="接口默认每页返回多少条？", path="api/changelog.md", pat=r"default page size (100) \(was", variant="B", decoy="50",
          trap=S, desc="Asks the default page size; the changelog shows it changed in the newest release", ref="读 api/changelog.md：4.2.0 起 100。")


@reg
def c31414():
    files = {"ops/rotation-2026-08.md": "# 8 月值班\n\n周末值班：Chen\n", "ops/rotation-2026-09.md": "# 9 月值班\n\n周末值班：Dara\n"}
    local("doc-31414", tt="policy_lookup", files=files, q="Who is on call this weekend?", path="ops/rotation-2026-09.md", pat=r"周末值班：(Dara)", variant="A", decoy="Chen",
          trap=S, desc="Asks who is on call this weekend; August and September rotations exist and today is mid September", ref="今天 9/16，读 9 月排班：Dara。")


@reg
def c31415():
    files = {"vendor/contact-old.md": "供应商联系人：王强，电话 021-5550-1100\n", "vendor/contact.md": "供应商联系人变更：自 2026-08 起由 李娜 负责，电话 021-5550-2368。\n"}
    local("doc-31415", tt="policy_lookup", files=files, q="供应商现在找谁对接，电话多少？", path="vendor/contact.md", pat=r"电话 (021-5550-2368)", variant="B", decoy="021-5550-1100",
          trap=S, desc="Asks who handles the vendor now and the phone; an old and a changed contact note exist", ref="读 vendor/contact.md：李娜 021-5550-2368。")


@reg
def c31416():
    files = {"security/keys.md": "# 密钥轮换\n\n数据库主密钥每 60 天轮换一次，上次轮换 2026-08-28。\n", "security/certs.md": "# 证书\n\n证书有效期 365 天。\n"}
    local("doc-31416", tt="policy_lookup", files=files, q="数据库密钥多久换一次？", path="security/keys.md", pat=r"每 (60) 天轮换", variant="A", decoy="365",
          desc="Asks the database key rotation interval; keys.md has it, certs.md a near-miss", ref="读 security/keys.md：60 天。")


@reg
def c31417():
    files = {"data/glossary.md": "# 术语表\n\n活跃用户（DAU）：当日至少完成一次登录的去重用户数。\n留存率：新增用户 7 天后仍活跃的比例。\n", "data/metrics.md": "# 指标\nDAU 看板见 BI\n"}
    local("doc-31417", tt="policy_lookup", files=files, q="我们说的“留存率”具体怎么算的？", path="data/glossary.md", pat=r"留存率：新增用户 (7 天后仍活跃)的比例", variant="B", decoy="当日至少完成一次登录",
          desc="Asks how our retention rate is defined; the glossary has the company's definition", ref="读 data/glossary.md：新增用户 7 天后仍活跃的比例。")


@reg
def c31418():
    files = {"budget/2026.csv": "dept,q4_budget\nmarketing,240000\nrnd,910000\nops,330000\n", "budget/2025.csv": "dept,q4_budget\nrnd,780000\n"}
    local("tab-31418", tt="aggregate", files=files, q="研发部 Q4 预算是多少？", path="budget/2026.csv", pat=r"rnd,(\d+)", variant="A", decoy="780000",
          trap=S, desc="Asks R&D's Q4 budget with 2025 and 2026 budget tables", ref="今年读 budget/2026.csv：910000。")


@reg
def c31419():
    files = {"notes/meeting-0915.md": "# 9/15 站会\n\n决定：数据库迁移推到 10 月 12 日，原因是压测未通过。\n", "notes/meeting-0908.md": "# 9/8 站会\n\n决定：数据库迁移定在 9 月 28 日。\n"}
    local("log-31419", tt="root_cause", files=files, q="When is the database migration happening, and why did it move?", path="notes/meeting-0915.md", pat=r"迁移推到 (10 月 12 日)", variant="B", decoy="9 月 28 日",
          trap=S, desc="Asks when the migration happens and why it moved; the 9/15 meeting overrides the 9/8 plan", ref="9/15 站会：推到 10 月 12 日，压测未通过。")


@reg
def c31420():
    files = {"service/ports.md": "# 端口表\n\n| 服务 | 端口 |\n|---|---|\n| gateway | 8000 |\n| billing | 8731 |\n| search | 9200 |\n", "service/readme.md": "# 服务\n"}
    web = [fx("9200 端口", "https://ports.example.net/9200", "Port 9200", "TCP 9200 is commonly used by Elasticsearch.\n", "2025-11-05")]
    local("cfg-31420", tt="read_effective", files=files, q="计费服务用哪个端口？", path="service/ports.md", pat=r"\| billing \| (\d+) \|", variant="A", decoy="9200", web=web, webval="Elasticsearch",
          desc="Asks which port the billing service uses; the internal port table has it", ref="读 service/ports.md：8731。")
