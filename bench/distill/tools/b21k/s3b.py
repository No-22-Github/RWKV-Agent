"""policy_lookup 33249-33257."""
from common import mk, WEBOFF
from s1a import T


def c49():
    f = {"制度/加班与调休.md": "# 加班与调休\n\n1. 加班须事前在系统申请，经理批准后方有效；事后补申请不予认可。\n2. 工作日加班：按小时工资的 150% 计算，或按 1:1 调休。\n3. 周末加班：按小时工资的 200% 计算，也可在 30 天内调休。\n4. 法定节假日加班：按小时工资的 300% 计算，不可调休。\n5. 调休有效期 90 天，过期作废；工作日加班产生的调休有效期同为 90 天。\n6. 每月加班总时长不超过 36 小时。\n"}

    def answer(files):
        import re
        return re.search(r"周末加班：按小时工资的 (\d+)%", files["制度/加班与调休.md"]).group(1)
    mk("doc-33249", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("周六我去公司加班（已经批准了），工资按小时工资的百分之多少算？如果想调休，多久内要休完？", inc=["200", "30"])],
       gist="Weekend overtime rate and comp-time window.", steps="read; 200 and 30.", why="clause 3.")


def c50():
    f = {"it/数据保留规定.md": "# 数据保留规定\n\n| 数据类型 | 保留期限 | 到期处理 |\n|---|---|---|\n| 应用运行日志 | 90 天 | 自动删除 |\n| 访问审计日志 | 365 天 | 归档后再保留 2 年 |\n| 数据库备份 | 35 天 | 自动覆盖 |\n| 财务凭证电子档 | 10 年 | 人工审核后销毁 |\n| 客服录音 | 180 天 | 自动删除 |\n\n补充：涉及诉讼保全的数据不受上述期限限制，须由法务书面通知后方可处理。\n"}

    def answer(files):
        import re
        return re.search(r"客服录音 \| (\d+) 天", files["it/数据保留规定.md"]).group(1)
    mk("doc-33250", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("客服录音要保留多少天？", inc=["180"]),
              T("访问审计日志呢？到期之后是直接删掉吗？", inc=["365", "2"])],
       gist="Retention for call recordings then audit logs.", steps="read; 180; 365 then archived 2 years.", why="table rows.")


def c51():
    f = {"行政/公车管理.md": "# 公务用车管理\n\n- 公车仅限公务使用，使用须提前 1 天在系统申请，当天紧急用车可电话申请。\n- 一般员工申请需经理批准；跨城市用车需部门总监批准。\n- 私车公用：按 0.8 元/公里补贴，每月上限 600 元。\n- 公车每日 18:30 前归还并加满油；过夜停放须停在公司车库。\n- 违章罚款由当事司机承担；因公违章经批准可报销，但扣分不予报销。\n"}

    def answer(files):
        import re
        return str(round(120 * float(re.search(r"按 ([\d.]+) 元/公里", files["行政/公车管理.md"]).group(1))))
    mk("doc-33251", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我开自己的车去客户那儿，来回 120 公里，能补贴多少钱？", inc=["96"])],
       gist="Private car allowance computed from per-km rate (120*0.8=96, below the 600 monthly cap).", steps="read; 0.8*120=96.", why="")
    return


def c52():
    f = {"office/laptop-loan.md": "# Laptop loan scheme\n\n- Short loan (up to 5 working days): approved by the IT desk the same day.\n- Standard loan (6-30 days): needs line manager approval; deposit 200.\n- Long loan (31-90 days): needs department head approval; deposit 500.\n- Loans over 90 days are not available; request a permanent device instead.\n- Late return: 15 per day after the due date, charged against the deposit.\n- Damage: repair costs above 100 are deducted from the deposit.\n"}

    def answer(files):
        return "500"
    mk("doc-33252", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), never=WEBOFF, ref_calls=2,
       turns=[T("I need a laptop for 45 days for a field project. Who has to approve it and how much deposit do I pay?", inc=["500", "department head"])],
       gist="Laptop loan tier for 45 days.", steps="read; 500, department head.", why="31-90 days tier.")


def c53():
    f = {"hr/培训经费.md": "# 培训经费管理\n\n1. 每人每年培训额度：初级员工 3000 元，中级员工 5000 元，高级及以上 8000 元。\n2. 外部课程须提前 15 天提交申请并附课程大纲。\n3. 课程费用超出额度的部分，经部门总监批准后可使用部门公共经费，每部门每年公共经费 20000 元。\n4. 报销凭证须在课程结束后 30 天内提交。\n5. 获得公司报销的证书类培训，员工须在公司服务满 12 个月，否则按比例返还费用。\n6. 额度不能跨年结转。\n"}

    def answer(files):
        import re
        return re.search(r"中级员工 (\d+) 元", files["hr/培训经费.md"]).group(1)
    mk("doc-33253", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我是中级员工，今年培训额度有多少？没用完能带到明年吗？", inc=["5000", "不能"]),
              T("那我想报一门外部课程，要提前多少天申请？", inc=["15"])],
       gist="Mid-level training budget and carry-over, then lead time.", steps="read; 5000/不能; 15.", why="clauses 1,6,2.")


def c54():
    f = {"宿舍/管理规定.md": "# 员工宿舍管理规定\n\n- 门禁：宿舍楼 23:00 关闭大门，23:00 后归寝须刷卡并登记。\n- 访客：只允许在 8:00-21:00 之间探访，访客须登记并留下证件，不得留宿。\n- 用电：禁止使用 800W 以上的电器（电热水壶除外，限 1500W 以内）。\n- 卫生：每周日 10:00 进行宿舍检查，三次不合格取消住宿资格。\n- 退宿：提前 7 天书面申请，退宿当天交还钥匙并结清水电。\n"}

    def answer(files):
        return "21:00"
    mk("doc-33254", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我朋友想来宿舍看我，最晚几点必须离开？可以留宿吗？", inc=["21:00", "不"])],
       gist="Dorm visitor hours and overnight rule.", steps="read; 21:00, no overnight.", why="")


def c55():
    f = {"support/sla.md": "# Support SLA\n\n| Priority | First response | Resolution target |\n|---|---|---|\n| P1 (service down) | 15 minutes | 4 hours |\n| P2 (major degradation) | 1 hour | 1 business day |\n| P3 (minor issue) | 4 business hours | 5 business days |\n| P4 (question) | 1 business day | best effort |\n\nNotes:\n- P1 is supported 24x7; P2-P4 only 09:00-18:00 on business days.\n- Response clocks pause while we wait for the customer.\n- Customers on the Premium plan get P2 first response of 30 minutes.\n"}

    def answer(files):
        return "30 minutes" if "Premium plan get P2 first response of 30 minutes" in files["support/sla.md"] else ""
    mk("doc-33255", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), never=WEBOFF, ref_calls=2,
       turns=[T("A Premium customer reports a major degradation. What is our first-response time for them?", inc=["30 minutes"]),
              T("And what is the resolution target for that same ticket?", inc=["1 business day"])],
       gist="Premium override of P2 first response then P2 resolution target.", steps="read; 30 minutes; 1 business day.", why="")
    return


def c56():
    f = {"财务/发票与报销.md": "# 发票与报销规则\n\n1. 发票抬头须为公司全称，税号错误的发票不予报销。\n2. 发票开具日期超过 90 天的，不予报销；因特殊原因逾期的，须总监书面说明。\n3. 单张发票金额超过 5000 元的，须同时附合同或订单。\n4. 电子发票须打印并签字，同一张电子发票不得重复报销。\n5. 差旅类发票的报销时限为返回后 10 个工作日，不适用第 2 条的 90 天规则。\n6. 餐饮发票每人每餐不超过 150 元。\n"}

    def answer(files):
        import re
        return re.search(r"超过 (\d+) 天的，不予报销", files["财务/发票与报销.md"]).group(1)
    mk("doc-33256", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我手上有一张办公用品的发票，开了 100 天了，还能直接报销吗？按规定超过多少天就不行了？", inc=["90"]),
              T("如果是出差的车票发票呢？时限是多久？", inc=["10"])],
       gist="Overdue office invoice vs travel invoice.", steps="read; not eligible; travel not subject to 90-day rule.", why="")
    return


def c57():
    f = {"法务/保密与竞业.md": "# 保密与竞业\n\n- 保密义务：在职期间及离职后 3 年内，不得披露公司商业秘密。\n- 竞业限制：仅适用于高管和核心技术岗，离职后 12 个月；公司按月支付竞业补偿，标准为离职前 12 个月平均工资的 30%。\n- 普通员工不适用竞业限制，但仍受保密义务约束。\n- 违反保密义务的，须赔偿公司损失，并按情节处以不超过 20 万元的违约金。\n- 离职时须交还所有资料、设备，并在离职交接单上签字。\n"}

    def answer(files):
        import re
        return re.search(r"离职后 (\d+) 年内，不得披露", files["法务/保密与竞业.md"]).group(1)
    mk("doc-33257", sub="policy", ttype="policy_lookup", files=f, ans=answer, traps=("TR-DECOY",), ref_calls=2,
       turns=[T("我是普通工程师，离职后保密义务要持续多久？", inc=["3"]),
              T("我还会被竞业限制吗？补偿是多少？", any=["不适用", "不会", "不受", "没有竞业", "无需", "不需要", "不用"])],
       gist="Confidentiality term then non-compete applicability for ordinary staff.", steps="read; 3 years; not subject.", why="")


BUILDERS = [c49, c50, c51, c52, c53, c54, c55, c56, c57]
