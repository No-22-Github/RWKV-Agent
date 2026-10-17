"""draft_document 33211-33219."""
from common import mk, WEBOFF
from s1a import T


def c11():
    f = {"门店/促销.txt": "中秋促销（门店通知用）\n活动时间：9月24日至9月27日\n月饼礼盒满300减50，仅限线下门店\n会员额外9折，不与满减叠加\n每店每日限量礼盒120盒\n店长：郭涛（东区）、白雪（西区）\n",
         "门店/历史/国庆促销.md": "# 国庆促销\n\n满200减30，会员8折可叠加。\n"}
    mk("doc-33211", sub="draft", ttype="draft_document", files=f,
       turns=[T("根据 门店/促销.txt 写一份给店长的中秋促销执行通知，保存到 门店/中秋通知.md，规则要写准，历史里的国庆规则不适用。")],
       rules={"门店/中秋通知.md": ["9月24日", "9月27日", "满300减50", "9折", "120盒", "郭涛", "白雪"]},
       facts=["9月24日", "9月27日", "满300减50", "9折", "120盒", "郭涛", "白雪"], traps=("TR-SUPERSEDE",),
       ref_calls=3, level="L1", gist="Promotion notice with this year's rules, not the old rules.", steps="read; write.",
       why="Rules from promo file only.")


def c12():
    f = {"hr/offer-info.txt": "Candidate: Priya Raman\nRole: Data Analyst\nStart date: 2026-10-12\nBase salary: 14,500 per month\nProbation: 3 months\nReports to: Marcus Hale\nBenefits: health insurance from day one, 18 days annual leave\n",
         "hr/style.md": "Keep offer letters under 200 words. Friendly but formal.\n"}
    mk("doc-33212", sub="draft", ttype="draft_document", files=f,
       turns=[T("Draft an offer letter for the candidate using hr/offer-info.txt, save it as hr/offer-letter.md, and follow hr/style.md."),
              T("Marcus is on leave that week, so change the line manager to Elena Park and keep everything else.")],
       rules={"hr/offer-letter.md": ["Priya Raman", "Data Analyst", "2026-10-12", "14,500", "3 months", "Elena Park", "18 days"]},
       facts=["Priya Raman", "Data Analyst", "2026-10-12", "14,500", "3 months", "Elena Park", "18 days"], traps=("TR-MULTISRC",),
       ref_calls=5, never=WEBOFF, gist="Offer letter from facts then change the manager.", steps="read both; write; edit.",
       why="Final letter names Elena Park with the other facts.")


def c13():
    f = {"食堂/菜单.txt": "下周食堂菜单（9月21日起）\n周一 红烧排骨、清炒时蔬\n周二 咖喱鸡、凉拌黄瓜\n周三 清蒸鲈鱼、蒜蓉西兰花\n周四 宫保鸡丁、紫菜蛋汤\n周五 披萨日（价格 12 元/份）\n过敏提示：周三含鱼类，周四含花生\n",
         "食堂/公告/上周.md": "# 上周菜单\n\n周五 炸鸡日\n"}
    mk("doc-33213", sub="draft", ttype="draft_document", files=f,
       turns=[T("把 食堂/菜单.txt 写成一份员工公告，存到 食堂/公告/下周菜单.md，标题“# 下周食堂菜单”，过敏提示要醒目地放在最后。")],
       rules={"食堂/公告/下周菜单.md": ["# 下周食堂菜单", "红烧排骨", "咖喱鸡", "清蒸鲈鱼", "宫保鸡丁", "12 元", "鱼类", "花生"]},
       facts=["# 下周食堂菜单", "红烧排骨", "咖喱鸡", "清蒸鲈鱼", "宫保鸡丁", "12 元", "鱼类", "花生"], traps=(), ref_calls=3, level="L0",
       gist="Cafeteria menu announcement with allergy note last.", steps="read; write.", why="Menu items come from the file.")


def c14():
    f = {"项目/进度.csv": "任务,负责人,状态,截止\n接口文档,方宇,完成,9月10日\n数据迁移,康乐,进行中,9月30日\n压测,方宇,未开始,10月8日\n验收,魏然,未开始,10月20日\n",
         "项目/备注.txt": "数据迁移卡在旧库权限，需运维开通，康乐已提单 OPS-771。\n"}
    mk("doc-33214", sub="draft", ttype="draft_document", files=f,
       turns=[T("根据 项目/进度.csv 和 项目/备注.txt 写一份项目周报，保存到 项目/周报-0916.md，分“已完成”“进行中”“未开始”三节，卡点也要写。"),
              T("不对，验收其实已经提前到 10月15日，改一下周报里的日期。")],
       rules={"项目/周报-0916.md": ["已完成", "进行中", "未开始", "接口文档", "数据迁移", "OPS-771", "压测", "10月8日", "验收", "10月15日"]},
       facts=["已完成", "进行中", "未开始", "接口文档", "数据迁移", "OPS-771", "压测", "10月8日", "验收", "10月15日"],
       traps=("TR-MULTISRC",), ref_calls=5, gist="Project report from csv plus a note, then correct a date.", steps="read both; write; edit.",
       why="The final date is 10月15日.")


def c15():
    f = {"docs/faq-source.txt": "Q: How do I reset my password?\nA: Open Settings > Security > Reset password. A link is valid for 30 minutes.\nQ: Can I change my username?\nA: Only once, within the first 14 days after sign-up.\nQ: Where is my invoice?\nA: Billing > Invoices, PDFs are kept for 24 months.\n",
         "docs/faq/index.md": "# FAQ\n\n(empty)\n"}
    mk("doc-33215", sub="draft", ttype="draft_document", files=f,
       turns=[T("Turn docs/faq-source.txt into a tidy FAQ page and write it to docs/faq/account.md. Each question should be a '## ' heading with the answer under it.")],
       rules={"docs/faq/account.md": ["How do I reset my password?", "30 minutes", "Can I change my username?", "14 days", "Where is my invoice?", "24 months"]},
       facts=["How do I reset my password?", "30 minutes", "Can I change my username?", "14 days", "Where is my invoice?", "24 months"],
       traps=("TR-HEADER",), ref_calls=3, never=WEBOFF, gist="FAQ page from Q/A source.", steps="read; write.", why="Questions and numbers in source.")


def c16():
    f = {"社区/志愿活动.txt": "周末社区清洁日\n集合：10月11日 08:00 小区东门\n人数上限：40人，已报名 27人\n物资：手套和垃圾袋由物业提供，请自带水杯\n联系人：林婉 13800000042\n雨天顺延到 10月18日\n"}
    mk("doc-33216", sub="draft", ttype="draft_document", files=f,
       turns=[T("写一个招募志愿者的公告，素材在 社区/志愿活动.txt，输出到 社区/招募.md。公告里要写清还剩几个名额，写完告诉我剩几个。", inc=["13"])],
       rules={"社区/招募.md": ["10月11日", "08:00", "东门", "水杯", "林婉", "13800000042", "10月18日"]},
       facts=["10月11日", "08:00", "东门", "水杯", "林婉", "13800000042", "10月18日"], traps=("TR-DEFN",), ref_calls=3, level="L1",
       gist="Volunteer call that must state the remaining quota (40-27=13).", steps="read; compute 13; write.",
       why="40 minus 27 gives 13 remaining places.")


def c17():
    f = {"采购/申请.txt": "采购申请单\n申请人：马俊\n物品：显示器 24 寸 x6\n单价：890\n用途：新工位\n预算科目：办公设备\n期望到货：10月9日前\n",
         "采购/审批规则.md": "金额 5000 元以上需部门总监审批；5000 元以下经理审批。\n"}
    mk("doc-33217", sub="draft", ttype="draft_document", files=f,
       turns=[T("根据 采购/申请.txt 和 采购/审批规则.md 写一份提交给审批人的请示，存为 采购/请示.md。要写出总金额（直接写数字，不要加千分位）和该谁审批。"),
              T("申请人姓名后面括号补上部门：研发部。")],
       rules={"采购/请示.md": ["马俊（研发部）", "显示器", "5340", "总监", "10月9日"]},
       facts=["马俊（研发部）", "显示器", "5340", "总监", "10月9日"], free=["马俊（研发部）", "5340"], traps=("TR-RULEFILE",), ref_calls=5,
       gist="Approval request needing total 6*890=5340 and the director per the rule, then add a dept.", steps="read both; compute; write; edit.",
       why="5340 is above 5000, so the director approves.")


def c18():
    f = {"notes/trip.txt": "Team offsite plan\nDate: 2026-11-06 (Friday)\nVenue: Lakeside Lodge, 2 hours by coach\nCoach leaves HQ at 08:15 sharp\nBudget cap: 85 per person\nDietary forms due to Rosa Ibarra by 2026-10-23\n",
         "notes/older-plan.txt": "Offsite draft (cancelled)\nDate: 2026-10-30\nVenue: Pine Hill\n"}
    mk("doc-33218", sub="draft", ttype="draft_document", files=f,
       turns=[T("Write an invitation email draft for the offsite and save it to notes/invite.md. The older plan was cancelled, so use only the current one."),
              T("Add a line at the end asking people to reply with their t-shirt size by 2026-10-27.")],
       rules={"notes/invite.md": ["2026-11-06", "Lakeside Lodge", "08:15", "85", "Rosa Ibarra", "2026-10-23", "t-shirt size", "2026-10-27"]},
       facts=["2026-11-06", "Lakeside Lodge", "08:15", "85", "Rosa Ibarra", "2026-10-23", "t-shirt size", "2026-10-27"],
       traps=("TR-SUPERSEDE",), ref_calls=5, never=WEBOFF, gist="Invitation draft from the current plan then add a request line.", steps="read; write; append.",
       why="Current plan is 2026-11-06; cancelled plan has other date.")


def c19():
    f = {"新闻/稿源.txt": "基本信息：公司获评“2026年度最佳雇主”。\n颁奖地点：深圳，颁奖日期：9月12日。\n公司代表：副总裁 谭晓。\n评选机构：华南人力资源协会，共 218 家企业参评。\n致辞要点：感谢员工，下一步将设立员工成长基金。\n",
         "新闻/发布规范.md": "对外稿件控制在 300 字以内，不得出现未公开的金额。\n"}
    mk("doc-33219", sub="draft", ttype="draft_document", files=f,
       turns=[T("按 新闻/发布规范.md 的要求，把 新闻/稿源.txt 写成一篇对外新闻稿，保存到 新闻/稿件.md。")],
       rules={"新闻/稿件.md": ["2026年度最佳雇主", "深圳", "9月12日", "谭晓", "华南人力资源协会", "218", "员工成长基金"]},
       facts=["2026年度最佳雇主", "深圳", "9月12日", "谭晓", "华南人力资源协会", "218", "员工成长基金"], traps=("TR-RULEFILE",),
       ref_calls=3, level="L1", gist="Press release following a style rule file.", steps="read both; write.", why="All facts in the source.")


BUILDERS = [c11, c12, c13, c14, c15, c16, c17, c18, c19]
