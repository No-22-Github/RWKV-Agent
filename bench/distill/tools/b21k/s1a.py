"""draft_document 33201-33210: draft a document from workspace material and write it to a named file."""
from common import mk, WEBOFF


def T(p, **kw):
    d = {"p": p}
    d.update(kw)
    return d


def c01():
    f = {"行政/放假安排.txt": "国庆节放假安排（行政部提供）\n放假时间：10月1日至10月7日，共7天。\n10月8日正常上班。\n节日期间值班电话：8802，值班负责人：李静。\n返程提醒：各部门10月8日上午9:30前完成考勤打卡。\n",
         "行政/去年通知.md": "# 关于2025年国庆放假的通知\n\n放假时间：10月1日至10月6日。\n10月7日正常上班。\n值班电话：8610。\n"}
    mk("doc-33201", sub="draft", ttype="draft_document", files=f,
       turns=[T("根据 行政/放假安排.txt 起草一份国庆放假通知，写到 行政/通知-国庆.md，第一行用一级标题。去年的通知只当格式参考，日期和电话不要沿用。")],
       rules={"行政/通知-国庆.md": ["10月1日", "10月7日", "10月8日", "8802", "李静"]},
       facts=["10月1日", "10月7日", "10月8日", "8802", "李静"], traps=("TR-DECOY",), must=("read_file", "write_file"),
       gist="Draft a holiday notice from this year's schedule, not last year's.", steps="read both, write notice.",
       why="Facts come from the 2026 schedule file; the 2025 notice has different dates and phone.")


def c02():
    f = {"周报/素材.txt": "本周完成：\n- 登录页改版上线（负责人：周朗）\n- 修复订单导出乱码，涉及 3 个接口\n- 压测报告出稿，峰值 1200 QPS\n下周计划：\n- 接入新支付渠道，预计周四联调\n- 梳理告警规则\n风险：测试环境 2 号机磁盘占用 91%\n",
         "周报/上周.md": "# 第37周周报\n\n## 完成\n- 完成预发环境迁移\n\n## 计划\n- 登录页改版\n"}
    mk("doc-33202", sub="draft", ttype="draft_document", files=f,
       turns=[T("用 周报/素材.txt 帮我写本周周报，存成 周报/第38周.md。分“本周完成”“下周计划”“风险”三节，格式照 周报/上周.md。"),
              T("标题改成“# 第38周周报（后端组）”，再在最后加一节“## 需要的支持”，写一条：申请扩容测试环境磁盘。")],
       rules={"周报/第38周.md": ["# 第38周周报（后端组）", "周朗", "1200 QPS", "91%", "## 需要的支持", "扩容测试环境磁盘"]},
       facts=["# 第38周周报（后端组）", "周朗", "1200 QPS", "91%", "## 需要的支持", "扩容测试环境磁盘"], traps=("TR-DECOY",),
       ref_calls=5, gist="Weekly report from notes, then retitle and add a section.", steps="read; write; edit title; append section.",
       why="Final file carries the new title, facts and the added section.")


def c03():
    f = {"会议/速记.txt": "9月12日 产品评审会 14:00-15:30 会议室B座302\n到场：陈曦、吴昊、孙悦、郑凯\n议题1：搜索改版——结论：先做灰度，灰度比例10%，负责人吴昊\n议题2：会员价格——结论：暂不调价，孙悦下周三前出竞品对比\n议题3：埋点规范——结论：沿用旧规范，郑凯整理文档\n",
         "会议/模板.md": "# 会议纪要\n\n时间：\n地点：\n参会人：\n\n## 结论\n\n## 待办\n"}
    mk("doc-33203", sub="draft", ttype="draft_document", files=f,
       turns=[T("把 会议/速记.txt 整理成会议纪要，写到 会议/纪要-0912.md，按 会议/模板.md 的结构，待办里写清楚谁做什么。")],
       rules={"会议/纪要-0912.md": ["14:00-15:30", "B座302", "陈曦", "郑凯", "10%", "吴昊", "孙悦", "竞品对比", "埋点规范"]},
       facts=["14:00-15:30", "B座302", "陈曦", "郑凯", "10%", "吴昊", "孙悦", "竞品对比", "埋点规范"], traps=(),
       ref_calls=3, level="L0", gist="Meeting minutes from shorthand using a template.", steps="read both; write.",
       why="All names, times and decisions are in the shorthand.")


def c04():
    f = {"setup/notes.txt": "Printer onboarding notes\n- Printer name: PR-HALL-3, IP 10.20.4.37\n- Driver: download 'HP Universal 7.2' from the IT share \\\\fileserver\\drivers\n- Default paper: A4; double-sided is off by default\n- Badge release: tap badge within 8 hours or the job is deleted\n- Help: ext. 4471 (IT desk), weekdays 08:30-17:30\n",
         "setup/old-guide.md": "# Printer guide (retired)\n\nPrinter: PR-HALL-1, IP 10.20.4.12\nHelp: ext. 4120\n"}
    mk("doc-33204", sub="draft", ttype="draft_document", files=f,
       turns=[T("Write a short how-to for new staff based on setup/notes.txt and save it to setup/printer-howto.md. Use numbered steps and a title line starting with '# '. The old guide is retired, so don't reuse its details."),
              T("Add a final line at the end that says: Last reviewed: 2026-09-16.")],
       rules={"setup/printer-howto.md": ["PR-HALL-3", "10.20.4.37", "HP Universal 7.2", "8 hours", "4471", "08:30-17:30", "Last reviewed: 2026-09-16."]},
       facts=["PR-HALL-3", "10.20.4.37", "HP Universal 7.2", "8 hours", "4471", "08:30-17:30", "Last reviewed: 2026-09-16."],
       traps=("TR-DECOY",), ref_calls=4, never=WEBOFF, gist="Printer how-to from notes, retired guide is a decoy, then append a line.",
       steps="read; write; append.", why="Details come from the notes; old guide has PR-HALL-1.")


def c05():
    f = {"财务/报销单汇总.txt": "9月差旅报销汇总\n张宇 北京出差 机票 1480 住宿 960 合计 2440\n王璐 上海出差 高铁 553 住宿 820 合计 1373\n赵铭 广州出差 机票 1260 住宿 700 合计 1960\n以上均已审核，付款日期 9月25日。\n",
         "财务/说明.md": "付款通知需写明付款日期和每人金额，不要写银行卡号。\n"}
    mk("doc-33205", sub="draft", ttype="draft_document", files=f,
       turns=[T("根据 财务/报销单汇总.txt 起草一份给员工的付款通知，写到 财务/付款通知-9月.md，要求看 财务/说明.md。"),
              T("再加一段：请在 9月22日 前确认金额，有异议联系财务小陈。")],
       rules={"财务/付款通知-9月.md": ["9月25日", "张宇", "2440", "王璐", "1373", "赵铭", "1960", "9月22日", "财务小陈"]},
       facts=["9月25日", "张宇", "2440", "王璐", "1373", "赵铭", "1960", "9月22日", "财务小陈"], traps=("TR-MULTISRC",),
       ref_calls=5, gist="Payment notice from two files, then add a confirmation paragraph.", steps="read both; write; append.",
       why="Per-person totals are in the summary; the style rule is in the note.")


def c06():
    f = {"客服/反馈.txt": "客户来信摘要：订单 A20931 的耳机左耳无声，7天内申请退换。\n处理方案：换新，运费由我们承担，换货单号 EX-5528，预计 9月19日发出。\n客户姓名：沈琳\n",
         "客服/话术.md": "# 回复话术\n\n- 先道歉，再说方案\n- 不超过 150 字\n"}
    mk("doc-33206", sub="draft", ttype="draft_document", files=f,
       turns=[T("按 客服/话术.md 的要求，给客户写一封回复，内容根据 客服/反馈.txt，保存为 客服/回复-A20931.md。")],
       rules={"客服/回复-A20931.md": ["沈琳", "A20931", "EX-5528", "9月19日", "运费"]},
       facts=["沈琳", "A20931", "EX-5528", "9月19日", "运费"], traps=(), ref_calls=3, level="L0", never=WEBOFF,
       gist="Customer reply drafted from a feedback summary and a style note.", steps="read; write.",
       why="Order id, exchange id and date come from the feedback file.")


def c07():
    f = {"培训/安排.txt": "新员工培训\n日期：9月28日、9月29日\n地点：三楼培训室\n讲师：9月28日 钱峰（制度与安全），9月29日 蒋云（系统操作）\n自带：笔记本电脑、工牌\n午餐：公司统一提供，12:00 开始\n",
         "培训/往期.md": "# 往期通知（8月）\n\n日期：8月24日\n地点：二楼会议室\n"}
    mk("doc-33207", sub="draft", ttype="draft_document", files=f,
       turns=[T("起草一份新员工培训通知，信息在 培训/安排.txt，写入 培训/通知.md。往期的不要参考。"),
              T("改一下：标题用“# 新员工入职培训通知”；另外把“自带”那条单独拎出来，放在最后一节“## 温馨提示”里。")],
       rules={"培训/通知.md": ["# 新员工入职培训通知", "9月28日", "9月29日", "三楼培训室", "钱峰", "蒋云", "## 温馨提示", "笔记本电脑", "12:00"]},
       facts=["# 新员工入职培训通知", "9月28日", "9月29日", "三楼培训室", "钱峰", "蒋云", "## 温馨提示", "笔记本电脑", "12:00"],
       traps=("TR-DECOY",), ref_calls=5, gist="Training notice then retitle and move a part into a tips section.", steps="read; write; rewrite.",
       why="Final file has new title, tips section and all schedule facts.")


def c08():
    f = {"release/changes.txt": "v2.6.0 changes\n+ add CSV export for reports (issue #412)\n+ dark mode for the dashboard\n- remove legacy /api/v1/ping endpoint\n! fix crash when the avatar is larger than 5 MB (issue #430)\nUpgrade: run `migrate --to 2.6.0` before restarting. Release date: 2026-09-30.\n",
         "release/TEMPLATE.md": "# Release notes\n\n## New\n\n## Removed\n\n## Fixed\n\n## Upgrade\n"}
    mk("doc-33208", sub="draft", ttype="draft_document", files=f,
       turns=[T("Turn release/changes.txt into release notes in release/notes-2.6.0.md, following release/TEMPLATE.md. Replace the title with '# Release notes 2.6.0'.")],
       rules={"release/notes-2.6.0.md": ["# Release notes 2.6.0", "CSV export", "#412", "dark mode", "/api/v1/ping", "#430", "5 MB", "migrate --to 2.6.0", "2026-09-30"]},
       facts=["# Release notes 2.6.0", "CSV export", "#412", "dark mode", "/api/v1/ping", "#430", "5 MB", "migrate --to 2.6.0", "2026-09-30"],
       traps=("TR-HEADER",), ref_calls=3, never=WEBOFF, gist="Release notes from a change list with a template.", steps="read both; write.",
       why="Every change item and the upgrade command are in changes.txt.")


def c09():
    f = {"活动/信息.txt": "公司秋季运动会\n时间：10月17日 08:30 开始\n地点：滨江体育场\n项目：拔河、接力、跳绳\n报名：向各部门联络员报名，截止 10月10日\n注意：请穿运动鞋；现场有医务点\n",
         "活动/联络员.txt": "研发部 秦岚\n市场部 邓超\n行政部 曾艺\n"}
    mk("doc-33209", sub="draft", ttype="draft_document", files=f,
       turns=[T("写一份运动会通知到 活动/运动会通知.md，材料在 活动 目录里的两个文件，通知里要让大家知道找谁报名。"),
              T("标题改成“# 秋季运动会报名通知”，再加一节“## 奖励”，写：每个项目前三名发奖品。")],
       rules={"活动/运动会通知.md": ["# 秋季运动会报名通知", "10月17日", "滨江体育场", "10月10日", "秦岚", "邓超", "曾艺", "## 奖励", "前三名"]},
       facts=["# 秋季运动会报名通知", "10月17日", "滨江体育场", "10月10日", "秦岚", "邓超", "曾艺", "## 奖励", "前三名"],
       traps=("TR-MULTISRC",), ref_calls=6, must=("list_files", "read_file", "write_file"),
       gist="Sports day notice from two files, then retitle and add a rewards section.", steps="list; read both; write; edit.",
       why="Contacts live in the second file.")


def c10():
    f = {"运维/故障记录.txt": "2026-09-14 故障\n21:05 监控告警：订单库连接数打满\n21:12 值班 许诺 介入，发现慢查询（来自报表任务）\n21:30 暂停报表任务，连接数恢复\n21:45 业务恢复，影响订单 约340单未及时落库，已补写\n后续：报表任务改到凌晨 02:00 执行；加连接数阈值告警\n",
         "运维/事故报告模板.md": "# 事故报告\n\n## 经过\n\n## 影响\n\n## 改进措施\n"}
    mk("doc-33210", sub="draft", ttype="draft_document", files=f,
       turns=[T("按 运维/事故报告模板.md 把 运维/故障记录.txt 写成事故报告，存到 运维/事故报告-0914.md。")],
       rules={"运维/事故报告-0914.md": ["21:05", "许诺", "21:30", "21:45", "340", "02:00", "阈值告警"]},
       facts=["21:05", "许诺", "21:30", "21:45", "340", "02:00", "阈值告警"], traps=("TR-HEADER",), ref_calls=3,
       gist="Incident report from a timeline using a template.", steps="read both; write.", why="Timeline facts are in the record.")


BUILDERS = [c01, c02, c03, c04, c05, c06, c07, c08, c09, c10]
