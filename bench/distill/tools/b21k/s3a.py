"""policy_lookup 33239-33248."""
from common import mk, WEBOFF
from s1a import T


def c39():
    f = {"制度/差旅管理办法.md": "# 差旅管理办法（2026）\n\n1. 出差须提前一个工作日在系统提交申请。\n2. 住宿标准按城市等级和职级分档：\n   - 一线城市（北京、上海、广州、深圳）：普通员工每晚 650 元，经理及以上每晚 900 元。\n   - 二线城市（杭州、成都、武汉等省会及计划单列市）：普通员工每晚 480 元，经理及以上每晚 650 元。\n   - 其他城市：普通员工每晚 350 元，经理及以上每晚 480 元。\n3. 超出标准的部分由个人承担，特殊情况须总监书面批准。\n4. 市内交通凭票报销，打车每单不超过 80 元。\n5. 餐补：出差期间每天 100 元，不凭票。\n6. 回程后 10 个工作日内提交报销，逾期需说明原因。\n"}

    def answer(files):
        import re
        return re.search(r"二线城市.*?普通员工每晚 (\d+) 元", files["制度/差旅管理办法.md"]).group(1)
    mk("doc-33239", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我是普通员工，下周去成都出差，公司规定我每晚住宿最多报销多少钱？", inc=["480"])],
       gist="Tiered lodging cap: ordinary staff, second-tier city.", steps="read; answer 480.", why="成都 is second-tier; ordinary staff 480.")


def c40():
    f = {"制度/假期制度.md": "# 假期制度\n\n## 事假\n- 1 天以内：提前 1 个工作日向直属经理申请。\n- 超过 1 天、不超过 3 天：提前 3 个工作日申请，经理批准。\n- 超过 3 天：提前 5 个工作日申请，需经理和部门总监共同批准。\n- 事假期间不发工资，按日扣减。\n\n## 病假\n- 需提供医院证明，3 天以内可事后 2 日内补交。\n- 病假工资按基本工资的 80% 发放。\n\n## 婚假\n- 法定婚假 3 天，公司另加 7 天，共 10 天，需在领证后 1 年内休完。\n"}

    def answer(files):
        import re
        return re.search(r"\n- 超过 3 天：提前 (\d) 个工作日", files["制度/假期制度.md"]).group(1)
    mk("doc-33240", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=3,
       turns=[T("我想请 4 天事假，得提前几个工作日申请？还需要谁批准？", inc=["5"]),
              T("那病假的话工资发多少？", inc=["80%"])],
       gist="Long personal leave lead time then sick pay.", steps="read; answer 5 / 80%.", why="over 3 days -> 5 working days.")


def c41():
    f = {"library/loan-rules.md": "# Library loan rules\n\n- Undergraduates: books 21 days, 5 items at a time; DVDs 3 days.\n- Postgraduates: books 42 days, 10 items at a time; DVDs 7 days.\n- Staff: books 56 days, 15 items at a time; DVDs 14 days.\n- Renewals: up to 2 times if nobody has reserved the item; each renewal adds the original loan period.\n- Overdue fines: 0.30 per day for books, 1.00 per day for DVDs; capped at 20.00 per item.\n- Reference-only items cannot leave the building.\n"}

    def answer(files):
        import re
        return re.search(r"Postgraduates: books (\d+) days", files["library/loan-rules.md"]).group(1)
    mk("doc-33241", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), never=WEBOFF, ref_calls=2,
       turns=[T("I'm a postgraduate student. How many days is my loan period for a book?", inc=["42"])],
       gist="Loan period for postgraduates.", steps="read; 42.", why="Postgraduate books 42 days.")


def c42():
    f = {"安保/访客规定.md": "# 访客管理规定\n\n第一条 访客须由被访员工提前在系统登记，未登记的访客一律不得入内。\n第二条 访客证当日有效，当天 18:00 前须归还。\n第三条 普通访客停留不超过 4 小时；施工、维修类访客不超过 8 小时。\n第四条 访客不得进入机房和财务室；需进入研发区域的，须由部门负责人书面同意。\n第五条 访客车辆停放在 B2 层访客区，每次免费 2 小时，超出后每小时 5 元。\n第六条 夜间（22:00 后）访客一律不接待，紧急维修除外。\n"}

    def answer(files):
        import re
        return re.search(r"施工、维修类访客不超过 (\d+) 小时", files["安保/访客规定.md"]).group(1)
    mk("doc-33242", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("空调维修师傅明天来我们办公室修机器，他最长可以在楼里待多久？", inc=["8"])],
       gist="Max stay for repair visitors vs ordinary visitors.", steps="read; 8.", why="Repair visitors 8 hours.")


def c43():
    f = {"it/security-policy.md": "# Account security policy\n\n1. Standard accounts: change the password every 90 days.\n2. Administrator accounts: change the password every 60 days and use a hardware key.\n3. Service accounts: rotate the secret every 180 days; no interactive login allowed.\n4. Passwords must have at least 12 characters (administrators: 16).\n5. After 5 failed sign-ins the account locks for 15 minutes; administrator accounts lock for 60 minutes.\n6. Reused passwords: the last 10 passwords cannot be reused.\n7. Contractors get standard accounts that expire after 30 days unless renewed by their sponsor.\n"}

    def answer(files):
        import re
        return re.search(r"Administrator accounts: change the password every (\d+) days", files["it/security-policy.md"]).group(1)
    mk("doc-33243", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), never=WEBOFF, ref_calls=2,
       turns=[T("How often does an administrator account have to change its password?", inc=["60"]),
              T("And how long is an administrator locked out after too many failed sign-ins?", inc=["60"])],
       gist="Admin password rotation then admin lockout.", steps="read; 60; 60.", why="Both are 60 for admins (days, minutes).")


def c44():
    f = {"财务/采购审批流程.md": "# 采购审批流程\n\n- 1000 元以下：部门经理审批即可，无需比价。\n- 1000 元至 1 万元（含 1 万）：部门经理审批，须附两家报价。\n- 1 万元以上至 10 万元（含 10 万）：部门经理 + 财务总监审批，须三家比价。\n- 10 万元以上：以上两级加总经理审批，并须走招标流程。\n- 固定资产（单价 5000 元以上的设备）不论总价，都需财务总监备案。\n- 紧急采购可先购后补，但须在 3 个工作日内补办手续。\n"}

    def answer(files):
        return "财务总监"
    mk("doc-33244", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我要采购一批总价 8 万元的培训服务，除了部门经理外还要谁审批，需要几家比价？", inc=["财务总监", "三家"])],
       gist="Approval tiers for an 80k purchase.", steps="read; 财务总监 + 三家.", why="1万–10万 tier.")


def c45():
    f = {"商城/退换货政策.md": "# 退换货政策\n\n1. 普通商品：签收后 7 天内可无理由退货，商品需保持原包装。\n2. 电子产品：签收后 15 天内出现质量问题可换货；超过 15 天至 1 年内走保修。\n3. 定制商品：除质量问题外不支持退换。\n4. 生鲜食品：签收后 24 小时内反馈质量问题，拍照为证。\n5. 退货运费：质量问题由商家承担；无理由退货由买家承担。\n6. 退款到账：商家收到退货后 3 个工作日内原路退回。\n"}

    def answer(files):
        import re
        return re.search(r"电子产品：签收后 (\d+) 天内", files["商城/退换货政策.md"]).group(1)
    mk("doc-33245", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我买的耳机用了 10 天发现左耳没声音，还能换货吗？换货窗口是多少天？", inc=["15"]),
              T("如果是无理由退货，运费谁出？退款几个工作日到账？", inc=["买家", "3"])],
       gist="Electronics exchange window, then no-reason return shipping and refund time.", steps="read; 15; 买家/3.", why="clauses 2,5,6.")


def c46():
    f = {"实验室/安全守则.md": "# 实验室安全守则\n\n1. 进入实验室必须穿实验服、戴护目镜。\n2. 易燃溶剂（乙醇、丙酮等）单瓶不超过 500 mL，每个操作台总存放量不超过 2 L。\n3. 强酸强碱单瓶不超过 1 L，须放在专用防泄漏柜中。\n4. 剧毒品由两人双锁保管，领用须两人在场并登记。\n5. 实验废液按类别收集，不得倒入下水道，每周五 16:00 统一交接。\n6. 离开实验室前须检查水、电、气，最后离开者在登记表签字。\n7. 发生泄漏须立即报告实验室负责人，不得自行处理超过 100 mL 的泄漏。\n"}

    def answer(files):
        import re
        return re.search(r"总存放量不超过 (\d) L", files["实验室/安全守则.md"]).group(1)
    mk("doc-33246", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我这个操作台最多一共能放多少升易燃溶剂？单瓶最大多大？", inc=["2", "500"])],
       gist="Flammable solvent storage limits.", steps="read; 2 L total, 500 mL per bottle.", why="clause 2.")


def c47():
    f = {"finance/per-diem.md": "# Travel per diem (2026)\n\n| Country | Meals per day | Incidentals per day |\n|---|---|---|\n| Germany | 48 | 12 |\n| France | 44 | 10 |\n| Japan | 52 | 14 |\n| Singapore | 46 | 11 |\n\nNotes:\n- Rates are in USD and apply from the second day of a trip.\n- On the first and last day only 75% of the meal rate is paid.\n- Meals provided by the host are deducted: breakfast 20%, lunch 30%, dinner 50% of the meal rate.\n"}

    def answer(files):
        import re
        return re.search(r"\| Japan \| (\d+) \|", files["finance/per-diem.md"]).group(1)
    mk("doc-33247", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), never=WEBOFF, ref_calls=2,
       turns=[T("What is the daily meal allowance in Japan, and what percentage of it do I get on the first day of the trip?", inc=["52", "75%"])],
       gist="Per-diem lookup with first-day percentage.", steps="read; 52 and 75%.", why="table row Japan; notes.")


def c48():
    f = {"行政/会议室预订.md": "# 会议室预订规则\n\n- 大会议室（A厅）：最多提前 14 天预订，单次最长 3 小时，须审批。\n- 中会议室（B座201、B座202）：最多提前 7 天预订，单次最长 2 小时。\n- 小会议室（面试间1-4）：当天可订，单次最长 1 小时。\n- 取消须在开始前 2 小时内取消完成，否则记一次违约；一个月内 3 次违约暂停预订权 2 周。\n- 开始 15 分钟仍无人到场，系统自动释放。\n- 会后须恢复桌椅并关闭设备。\n"}

    def answer(files):
        import re
        return re.search(r"B座202）：最多提前 (\d+) 天", files["行政/会议室预订.md"]).group(1)
    mk("doc-33248", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我想订 B座202，最多能提前多少天订？", inc=["7"]),
              T("那如果我一个月内违约三次，会怎样？", any=["2周", "两周", "2 周", "两个星期", "2个星期", "14天", "14 天", "二周"])],
       gist="Advance booking window then penalty (second turn answer restated).", steps="read; 7; suspension 2 weeks.", why="")


BUILDERS = [c39, c40, c41, c42, c43, c44, c45, c46, c47, c48]
