"""Filler policy-document generator for the G4 long-document cases (deterministic given the rng)."""

EN_TOPICS = ["Meeting rooms", "Visitor badges", "Printing and supplies", "Parking allocation", "Remote work equipment",
             "Onboarding checklist", "Mail and parcels", "Fire drills", "Shared kitchen", "Laptop refresh", "Conference attendance",
             "Training budget", "Software requests", "Customer gifts", "Translation requests", "Cleaning schedule",
             "Bicycle storage", "Phone allowances", "Emergency contacts", "Archive boxes", "Accessibility requests",
             "Photography on site", "Lost property", "Vendor invoices", "Intern programme", "Wellness room", "Quarterly town halls",
             "Facility bookings", "Security cameras", "Plant care", "Courier pickups", "Language courses"]
EN_SUBJ = ["Employees", "Team leads", "The facilities team", "Contractors", "The finance office", "Each department",
           "The front desk", "New joiners", "The IT service desk", "Managers"]
EN_VERB = ["must submit", "should confirm", "may request", "are expected to log", "need to coordinate", "have to report",
           "can escalate", "will be asked to document", "are encouraged to review", "must keep a record of"]
EN_OBJ = ["the booking in the shared calendar", "any change to the arrangement", "the form to the responsible office",
          "equipment that was borrowed", "the relevant ticket in the service portal", "visitors before they arrive",
          "the outcome of the last review", "a short note for the file", "the schedule for the following month", "unused items"]
EN_COND = ["within {n} working days", "at least {n} days in advance", "no later than {n}:00 on the day", "once per quarter",
           "when more than {n} people are involved", "unless the office manager agrees otherwise", "whenever the plan changes",
           "if the cost is above {n} euros", "during the first {n} weeks of the year", "before the end of each month"]

ZH_TOPICS = ["会议室预定", "访客登记", "办公用品领用", "停车位分配", "远程办公设备", "新员工入职清单", "快递收发", "消防演练",
             "茶水间使用", "电脑更换", "外部培训", "软件采购申请", "客户礼品", "保洁安排", "自行车存放", "通讯补贴",
             "紧急联系人", "档案归档", "无障碍需求", "现场拍摄", "失物招领", "供应商发票", "实习生管理", "健康小屋",
             "季度全员会", "场地借用", "监控管理", "绿植养护", "快递代收", "语言课程", "内部打印", "门禁卡管理"]
ZH_SUBJ = ["员工", "部门负责人", "行政部", "外包人员", "财务部", "各部门", "前台", "新入职同事", "信息服务台", "直属上级"]
ZH_VERB = ["应当提交", "需要确认", "可以申请", "须在系统中登记", "应与相关部门协调", "必须上报", "可以逐级上报", "需要留档记录", "建议定期检查", "应保存"]
ZH_OBJ = ["共享日历里的预定信息", "安排上的任何变动", "对应的申请表", "借用的设备", "服务台系统里的工单", "来访人员的信息",
          "上一次检查的结果", "一份简短的说明", "下个月的计划", "闲置的物品"]
ZH_COND = ["在{n}个工作日内", "至少提前{n}天", "最迟当天{n}点前", "每季度一次", "涉及{n}人以上时", "除非行政主管另行同意", "计划发生变化时",
           "费用超过{n}元时", "每年前{n}周内", "每月底之前"]


def filler(rng, lang, n_sections, start_no=1):
    topics, subj, verb, obj, cond = ((EN_TOPICS, EN_SUBJ, EN_VERB, EN_OBJ, EN_COND) if lang == "en"
                                     else (ZH_TOPICS, ZH_SUBJ, ZH_VERB, ZH_OBJ, ZH_COND))
    order = list(topics)
    rng.shuffle(order)
    out = []
    for i in range(n_sections):
        no = start_no + i
        title = order[i % len(order)]
        if lang == "en":
            out.append("## %d. %s" % (no, title) + ("" if i < len(order) else " (continued)"))
        else:
            out.append("## 第%d章 %s" % (no, title) + ("" if i < len(order) else "（续）"))
        out.append("")
        for k in range(rng.randrange(5, 9)):
            c = cond[rng.randrange(len(cond))].replace("{n}", str(rng.choice([2, 3, 5, 7, 10, 14, 20, 45, 60, 150, 300])))
            s, v, o = subj[rng.randrange(len(subj))], verb[rng.randrange(len(verb))], obj[rng.randrange(len(obj))]
            if lang == "en":
                out.append("%d.%d %s %s %s %s." % (no, k + 1, s, v, o, c))
            else:
                out.append("%d.%d %s%s%s，%s。" % (no, k + 1, s, v, o, c))
        out.append("")
    return out


def make_doc(rng, lang, title, total_sections, blocks):
    """blocks: {section_slot: [lines]} inserted before filler section number slot. Returns text."""
    lines = ["# " + title, ""]
    chunks = {}
    for slot, block in blocks.items():
        chunks[slot] = block
    slots = sorted(chunks)
    prev = 0
    for slot in slots:
        lines += filler(rng, lang, slot - prev, prev + 1)
        lines += chunks[slot] + [""]
        prev = slot
    lines += filler(rng, lang, total_sections - prev, prev + 1)
    return "\n".join(lines) + "\n"
