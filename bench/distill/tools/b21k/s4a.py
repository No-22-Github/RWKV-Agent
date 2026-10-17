"""link_check 33258-33266."""
from common import mk, WEBOFF
from s1a import T

LK = ("list_files", "read_file")


def c58():
    f = {"docs/index.md": "# 产品文档\n\n- [快速开始](start.md)\n- [安装](教程/安装.md)\n- [配置项](教程/配置.md)\n- [术语表](附录/术语表.md)\n- [官网](https://example.com/product)\n",
         "docs/start.md": "# 快速开始\n",
         "docs/教程/安装指南.md": "# 安装指南\n",
         "docs/教程/配置.md": "# 配置\n"}
    mk("doc-33258", sub="link", ttype="link_check", files=f, links=("docs/index.md", ["教程/安装.md", "附录/术语表.md"]), traps=("TR-NEARNAME",),
       must=LK, ref_calls=4,
       turns=[T("检查 docs/index.md 里的相对链接，哪些指向的文件在 docs 目录里找不到？外部网址不用管。把有问题的链接目标写出来。", inc=["教程/安装.md", "附录/术语表.md"])],
       gist="Two broken relative links in an index, one a near-name.", steps="list; read; compare.", why="安装.md vs 安装指南.md; 术语表 absent.")


def c59():
    f = {"README.md": "# Pixel Tool\n\n![logo](img/logo.png)\n\nSee the [usage guide](docs/usage.md) and the [changelog](CHANGELOG.md).\nScreenshot: ![shot](assets/shot.png)\nLicense: [MIT](LICENSE)\n",
         "assets/logo.png": "(binary)\n", "assets/shot.png": "(binary)\n", "docs/usage.md": "# Usage\n", "CHANGELOG.md": "# Changes\n", "LICENSE": "MIT\n"}
    mk("doc-33259", sub="link", ttype="link_check", files=f, links=("README.md", ["img/logo.png"]), traps=("TR-DECOY",),
       must=LK, never=WEBOFF, ref_calls=4,
       turns=[T("Which links or images in README.md point to a file that doesn't exist in this project? Answer with just the path(s) as written in the README.", inc=["img/logo.png"], exc=["assets/shot.png", "docs/usage.md"])],
       gist="Image link pointing to wrong directory.", steps="list; read; compare.", why="logo is under assets/.")


def c60():
    f = {"wiki/Home.md": "# 首页\n\n- [入门](Guide/Intro.md)\n- [常见问题](Guide/faq.md)\n- [联系我们](contact.md)\n- [路线图](Roadmap.md)\n",
         "wiki/Guide/intro.md": "# 入门\n", "wiki/Guide/faq.md": "# FAQ\n", "wiki/contact.md": "# 联系\n", "wiki/Roadmap.md": "# 路线\n"}
    mk("doc-33260", sub="link", ttype="link_check", files=f, links=("wiki/Home.md", ["Guide/Intro.md"]), traps=("TR-NEARNAME",),
       must=LK, ref_calls=4,
       turns=[T("这个 wiki 会部署到 Linux 服务器上，文件名区分大小写。帮我看看 wiki/Home.md 里有哪些链接在那边会打不开？只回答有问题的链接目标。", inc=["Guide/Intro.md"], exc=["contact.md", "Roadmap.md"])],
       gist="Case-sensitive file name mismatch in a wiki home.", steps="list; read; compare.", why="Intro.md vs intro.md.")


def c61():
    f = {"手册/目录.md": "# 手册目录\n\n1. [总则](总则.md)\n2. [流程](流程/审批.md)\n3. [模板](模板/申请表.md)\n4. [附则](附则.md)\n",
         "手册/总则.md": "# 总则\n", "手册/流程/审批.md": "# 审批\n", "手册/模板/说明.md": "# 模板说明\n"}
    mk("doc-33261", sub="link", ttype="link_check", files=f, links=("手册/目录.md", ["模板/申请表.md", "附则.md"]), traps=("TR-DECOY",),
       must=("list_files", "read_file", "write_file"), ref_calls=6,
       turns=[T("看看 手册/目录.md 里有哪些链接指向的页面还不存在？", inc=["模板/申请表.md", "附则.md"]),
              T("好，把“附则”这一页先建出来，文件里只写一行标题“# 附则”。别的缺页先不管。")],
       rules={"手册/附则.md": ["# 附则"]},
       gist="Find missing pages then create one stub.", steps="list; read; report; write stub.", why="Two broken then a stub for 附则.")


def c62():
    f = {"project/docs/api/overview.md": "# API overview\n\n- [Auth](auth.md)\n- [Errors](../errors.md)\n- [Rate limits](../limits/rate.md)\n- [Changelog](../../CHANGELOG.md)\n",
         "project/docs/api/auth.md": "# Auth\n", "project/docs/errors.md": "# Errors\n", "project/docs/limits.md": "# Limits\n", "project/CHANGELOG.md": "# Changes\n"}
    mk("doc-33262", sub="link", ttype="link_check", files=f, links=("project/docs/api/overview.md", ["../limits/rate.md"]), traps=("TR-NEARNAME",),
       must=LK, never=WEBOFF, ref_calls=4,
       turns=[T("In project/docs/api/overview.md, which relative links do not resolve to an existing file? Remember the paths are relative to that file's own folder. Give the link targets as written.", inc=["../limits/rate.md"], exc=["../errors.md", "auth.md"])],
       gist="Parent-relative links, one wrong.", steps="list; resolve; compare.", why="limits/rate.md doesn't exist; ../../CHANGELOG.md resolves.")


def c63():
    f = {"笔记/读书.md": "# 读书笔记\n\n读完了[《设计模式》][dp]，下一本是[《重构》][rf]，还有[《代码大全》][cc]。\n\n[dp]: 书单/设计模式.md\n[rf]: 书单/重构.md\n[cc]: 书单/代码大全第二版.md\n",
         "笔记/书单/设计模式.md": "# 设计模式\n", "笔记/书单/重构.md": "# 重构\n", "笔记/书单/代码大全.md": "# 代码大全\n"}
    mk("doc-33263", sub="link", ttype="link_check", files=f, links=("笔记/读书.md", ["书单/代码大全第二版.md"]), traps=("TR-NEARNAME",),
       must=LK, ref_calls=4,
       turns=[T("笔记/读书.md 里用的是引用式链接（文末定义的那种），帮我查一下哪个指向的文件不存在，写出文末写的路径。", inc=["书单/代码大全第二版.md"], exc=["书单/重构.md"])],
       gist="Reference-style link pointing to a renamed file.", steps="list; read; compare.", why="")


def c64():
    f = {"站点/首页.md": "# 欢迎\n\n[产品](产品/列表.md) | [价格](价格.md) | [博客](博客/最新.md) | [关于](关于.md)\n\n[在线演示](http://demo.example.org/)\n",
         "站点/产品/列表.md": "# 产品\n", "站点/价格.md": "# 价格\n", "站点/关于.md": "# 关于\n", "站点/博客/2026-09.md": "# 九月\n"}
    mk("doc-33264", sub="link", ttype="link_check", files=f, links=("站点/首页.md", ["博客/最新.md"]), traps=("TR-DECOY",),
       must=("list_files", "read_file", "write_file"), ref_calls=5,
       turns=[T("检查 站点/首页.md 的相对链接，把有问题的写进 站点/坏链报告.md，每行一条“- 链接目标”；不用写正常的。写完告诉我有几条坏链。", inc=["1"])],
       rules={"站点/坏链报告.md": ["博客/最新.md"]},
       gist="Write a bad-link report file.", steps="list; read; write report.", why="One broken link: 博客/最新.md.")


def c65():
    f = {"guide/index.md": "# Guide\n\n- [Install](install.md)\n- [Usage](usage.md)\n- [Troubleshooting](trouble-shooting.md)\n",
         "guide/install.md": "# Install\n", "guide/usage.md": "# Usage\n", "guide/troubleshooting.md": "# Troubleshooting\n"}
    fixed = "# Guide\n\n- [Install](install.md)\n- [Usage](usage.md)\n- [Troubleshooting](troubleshooting.md)\n"
    mk("doc-33265", sub="link", ttype="link_check", files=f, links=("guide/index.md", ["trouble-shooting.md"]), traps=("TR-NEARNAME",),
       must=("list_files", "read_file", "write_file"), never=WEBOFF, ref_calls=6,
       turns=[T("Check the relative links in guide/index.md and tell me which one is broken.", inc=["trouble-shooting.md"]),
              T("The page itself is fine, only the link is wrong. Fix the link in guide/index.md so it points at the real file and leave everything else as it is.")],
       rules={"guide/index.md": fixed},
       gist="Find the broken link then repair it in the index.", steps="list; read; report; rewrite.", why="Final index has troubleshooting.md.")


def c66():
    f = {"资料/索引.md": "# 资料索引\n\n- [年度总结](年度%20总结.md)\n- [会议记录](会议记录%202026.md)\n- [预算](预算表.md)\n- [联系人](联系人%20名单.md)\n",
         "资料/年度 总结.md": "# 年度总结\n", "资料/会议记录 2026.md": "# 会议\n", "资料/预算 表.md": "# 预算\n", "资料/联系人 名单.md": "# 名单\n"}
    mk("doc-33266", sub="link", ttype="link_check", files=f, links=("资料/索引.md", ["预算表.md"]), traps=("TR-NEARNAME",),
       must=LK, ref_calls=4,
       turns=[T("资料/索引.md 里有几个链接，目标文件名带空格（有的写成 %20）。请核对哪些链接对应的文件确实不存在，只回答不存在的那个目标。", inc=["预算表.md"], exc=["会议记录%202026.md"])],
       gist="Space and %20 names resolve; one name lacks the space.", steps="list; decode; compare.", why="预算表.md vs 预算 表.md.")


BUILDERS = [c58, c59, c60, c61, c62, c63, c64, c65, c66]
