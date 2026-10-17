"""link_check 33267-33275."""
from common import mk, WEBOFF
from s1a import T
from s4a import LK


def c67():
    f = {"docs/a-overview.md": "# 概览\n\n见 [部署](b-deploy.md) 与 [监控](c-monitor.md)。\n",
         "docs/b-deploy.md": "# 部署\n\n回到 [概览](a-overview.md)，故障见 [排错](d-debug.md)。\n",
         "docs/c-monitor.md": "# 监控\n\n指标说明：[指标](metrics/list.md)，告警：[告警规则](alerts.md)。\n",
         "docs/metrics/index.md": "# 指标\n", "docs/alerts.md": "# 告警\n"}
    mk("doc-33267", sub="link", ttype="link_check", files=f,
       links=(["docs/a-overview.md", "docs/b-deploy.md", "docs/c-monitor.md"], ["d-debug.md", "metrics/list.md"]), traps=("TR-MULTISRC",),
       must=("list_files", "read_file"), ref_calls=6,
       turns=[T("docs 目录里有三篇互相引用的文档（a、b、c 开头的那三篇）。帮我把三篇里所有失效的相对链接找出来，写出链接目标。", inc=["d-debug.md", "metrics/list.md"])],
       gist="Broken links spread over three docs.", steps="list; read 3; compare.", why="d-debug.md absent; metrics/list.md absent (index.md exists).")


def c68():
    f = {"manual/toc.md": "# Manual\n\n- [Setup](setup.md#requirements)\n- [Operation](operation.md#daily-checks)\n- [Safety](safety.md#warnings)\n- [Spare parts](parts.md#list)\n- [Vendor](https://vendor.example.com/manual#top)\n- [Jump to top](#manual)\n",
         "manual/setup.md": "# Setup\n\n## Requirements\n", "manual/operation.md": "# Operation\n", "manual/safety.md": "# Safety\n"}
    mk("doc-33268", sub="link", ttype="link_check", files=f, links=("manual/toc.md", ["parts.md"]), traps=("TR-DECOY",),
       must=LK, never=WEBOFF, ref_calls=4,
       turns=[T("Check manual/toc.md for links whose target file is missing. Only the files matter; whether a section anchor exists is irrelevant. Give just the missing file name(s).", inc=["parts.md"], exc=["safety.md", "operation.md"])],
       gist="Anchors on existing files and external/self links are fine; one file missing.", steps="list; read; compare.", why="parts.md absent.")


def c69():
    f = {"项目/说明.md": "# 项目说明\n\n负责人名单见 [名单](people/team.md)，预算见 [预算](finance/budget-2026.md)，日程见 [日程](plan/schedule.md)。\n",
         "项目/people/team.md": "# 团队\n", "项目/finance/budget-2025.md": "# 预算2025\n", "项目/plan/schedule.md": "# 日程\n"}
    fixed = "# 项目说明\n\n负责人名单见 [名单](people/team.md)，预算见 [预算](finance/budget-2025.md)，日程见 [日程](plan/schedule.md)。\n"
    mk("doc-33269", sub="link", ttype="link_check", files=f, links=("项目/说明.md", ["finance/budget-2026.md"]), traps=("TR-SUPERSEDE",),
       must=("list_files", "read_file", "write_file"), ref_calls=6,
       turns=[T("检查 项目/说明.md 里哪个链接点不到文件？", inc=["finance/budget-2026.md"]),
              T("2026 的预算表还没做，先让这个链接指向现有的 2025 版，其余内容不要动。")],
       rules={"项目/说明.md": fixed},
       gist="Report a missing 2026 budget link then repoint to the 2025 file.", steps="list; read; report; rewrite.", why="")


def c70():
    f = {"kb/index.md": "# KB\n\n| Topic | Page |\n|---|---|\n| VPN | [vpn](network/vpn.md) |\n| Wi-Fi | [wifi](network/wifi.md) |\n| Printers | [printers](devices/printers.md) |\n| Badges | [badges](facilities/badges.md) |\n",
         "kb/network/vpn.md": "# VPN\n", "kb/network/wi-fi.md": "# Wi-Fi\n", "kb/devices/printers.md": "# Printers\n", "kb/facilities/badge.md": "# Badge\n"}
    mk("doc-33270", sub="link", ttype="link_check", files=f, links=("kb/index.md", ["network/wifi.md", "facilities/badges.md"]), traps=("TR-NEARNAME",),
       must=LK, never=WEBOFF, ref_calls=4,
       turns=[T("The table in kb/index.md links to topic pages. Which of those links are dead? List the targets.", inc=["network/wifi.md", "facilities/badges.md"], exc=["network/vpn.md", "devices/printers.md"])],
       gist="Links inside a table, two near-miss file names.", steps="list; read; compare.", why="wi-fi.md and badge.md exist, not wifi.md/badges.md.")


def c71():
    f = {"社团/章程.md": "# 社团章程\n\n详细条款：[入会](章程/入会.md)、[会费](章程/会费.md)、[退会](章程/退会.md)、[处分](章程/处分.md)。\n",
         "社团/章程/入会.md": "# 入会\n", "社团/章程/会费.md": "# 会费\n"}
    mk("doc-33271", sub="link", ttype="link_check", files=f, links=("社团/章程.md", ["章程/退会.md", "章程/处分.md"]), traps=("TR-DECOY",),
       must=("list_files", "read_file", "write_file"), ref_calls=7,
       turns=[T("社团/章程.md 里的链接有些页面还没写，列出缺的。", inc=["章程/退会.md", "章程/处分.md"]),
              T("每个缺的页面都建一个，文件内容只写标题，比如“# 退会”。")],
       rules={"社团/章程/退会.md": ["# 退会"], "社团/章程/处分.md": ["# 处分"]},
       gist="List missing pages then create a stub for each.", steps="list; read; report; write two stubs.", why="Two stubs.")


def c72():
    f = {"README.md": "# Data Lab\n\nProjects:\n\n1. [Churn model](projects/churn/README.md)\n2. [Forecast](projects/forecast/README.md)\n3. [Segmentation](projects/segments/README.md)\n4. [Contributing](CONTRIBUTING.md)\n5. [Code of Conduct](CODE_OF_CONDUCT.md)\n",
         "projects/churn/README.md": "# Churn\n", "projects/forecast/README.md": "# Forecast\n", "projects/segments/readme.md": "# Segments\n", "CONTRIBUTING.md": "# Contributing\n"}
    mk("doc-33272", sub="link", ttype="link_check", files=f, links=("README.md", ["projects/segments/README.md", "CODE_OF_CONDUCT.md"]), traps=("TR-NEARNAME",),
       must=LK, never=WEBOFF, ref_calls=5,
       turns=[T("List every link in README.md that points to a file that isn't in the repo. The server is Linux, so names are case-sensitive. Just the targets, please.", inc=["projects/segments/README.md", "CODE_OF_CONDUCT.md"], exc=["CONTRIBUTING.md", "projects/churn/README.md"])],
       gist="Case mismatch and a missing file among five links.", steps="list; read; compare.", why="")


def c73():
    f = {"帮助中心/首页.md": "# 帮助中心\n\n- [账号](账号/概述.md)\n- [支付](支付/概述.md)\n- [退款](支付/退款.md)\n- [发票](支付/发票说明.md)\n- [隐私](法律/隐私.md)\n- [条款](法律/条款.md)\n",
         "帮助中心/账号/概述.md": "# 账号\n", "帮助中心/支付/概述.md": "# 支付\n", "帮助中心/支付/退款.md": "# 退款\n", "帮助中心/支付/发票.md": "# 发票\n", "帮助中心/法律/隐私.md": "# 隐私\n"}
    mk("doc-33273", sub="link", ttype="link_check", files=f, links=("帮助中心/首页.md", ["支付/发票说明.md", "法律/条款.md"]), traps=("TR-NEARNAME",),
       must=("list_files", "read_file", "write_file"), ref_calls=5,
       turns=[T("核对 帮助中心/首页.md 的链接，把失效的写成清单放到 帮助中心/失效链接.md，每行“- 目标路径”，之后告诉我共几条。", inc=["2"]),
              T("在清单每行后面加上一句备注，对“发票说明”那条写“可能应指向 支付/发票.md”，另一条写“需要补页面”。")],
       rules={"帮助中心/失效链接.md": ["支付/发票说明.md", "法律/条款.md", "支付/发票.md", "需要补页面"]},
       gist="Write a dead-link list then annotate it.", steps="list; read; write; rewrite.", why="Two dead links.")


def c74():
    f = {"docs/home.md": "# Home\n\nNavigation: [Plans](plans.md) / [Billing](billing/overview.md) / [Support](support/contact.md) / [Status](status.md)\n",
         "docs/plans.md": "# Plans\n", "docs/billing/overview.md": "# Billing\n", "docs/support/contact.md": "# Contact\n"}
    mk("doc-33274", sub="link", ttype="link_check", files=f, links=("docs/home.md", ["status.md"]), traps=("TR-DECOY",),
       must=LK, never=WEBOFF, ref_calls=4,
       turns=[T("Is every internal link in docs/home.md pointing at an existing page? If not, which ones are dead?", inc=["status.md"], exc=["plans.md", "billing/overview.md"])],
       gist="One dead link in a one-line navigation bar.", steps="list; read; compare.", why="status.md missing.")


def c75():
    f = {"培训/课程总览.md": "# 课程总览\n\n## 基础\n- [入门](基础/入门.md)\n- [环境搭建](基础/环境搭建.md)\n- [第一个程序](基础/第一个程序.md)\n\n## 进阶\n- [并发](进阶/并发.md)\n- [性能调优](进阶/性能调优.md)\n- [安全](进阶/安全.md)\n\n## 实战\n- [项目一](实战/项目一.md)\n- [项目二](实战/项目2.md)\n- [项目三](实战/项目三.md)\n\n## 其他\n- [答疑](faq.md)\n- [评分](评分/标准.md)\n",
         "培训/基础/入门.md": "# 入门\n", "培训/基础/环境搭建.md": "# 环境\n", "培训/基础/第一个程序.md": "# 程序\n",
         "培训/进阶/并发.md": "# 并发\n", "培训/进阶/性能调优.md": "# 调优\n", "培训/进阶/安全.md": "# 安全\n",
         "培训/实战/项目一.md": "# 项目一\n", "培训/实战/项目二.md": "# 项目二\n", "培训/实战/项目三.md": "# 项目三\n", "培训/faq.md": "# FAQ\n"}
    mk("doc-33275", sub="link", ttype="link_check", files=f, links=("培训/课程总览.md", ["实战/项目2.md", "评分/标准.md"]), traps=("TR-NEARNAME",),
       must=LK, ref_calls=5,
       turns=[T("培训/课程总览.md 里有十几个链接，帮我筛出点不开的，只回答失效的链接目标。", inc=["实战/项目2.md", "评分/标准.md"], exc=["基础/入门.md", "faq.md", "进阶/并发.md"])],
       gist="Two dead links among thirteen.", steps="list; read; compare.", why="项目2 vs 项目二; 评分/标准 absent.")


BUILDERS = [c67, c68, c69, c70, c71, c72, c73, c74, c75]
