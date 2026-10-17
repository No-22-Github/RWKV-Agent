"""33057-33066 deprecation."""
from common import *


def dp(cid, brand, pages, p1, inc1, p2=None, inc2=None, any1=None, files=None, pol=None, why="", req1=None):
    web = [fx(brand, u, t, s, c, d) for (u, t, d, s, c) in pages]
    turns = [T(p1, req=req1 if req1 is not None else ["web_fetch"], inc=inc1, any=any1 or [])]
    if p2:
        turns.append(T(p2, inc=inc2))
    mk(cid, tt="deprecation", desc="Find the deprecation/removal timeline and replacement for a fictional product (%s)" % brand, web=web,
       turns=turns, traps=["TR-WEBSTALE"], ref="搜索 -> 打开弃用公告 -> 说明时间线与替代方案", why=why or "Timeline and replacement only in the notice page.",
       trap_notes=["旧文档仍在宣传已弃用的接口；弃用 vs 移除是两个日期。"], policy=pol or WSF, level="L2" if p2 else "L1",
       ref_calls=4 if p2 else 3, files=files, sub="dp")


def build():
    dp("web-33057", "Wickerbill Auth", [
        ("https://wickerbill.example/blog/deprecating-basic-auth", "Deprecating Basic auth", "2026-08-25", "Basic auth is being phased out.", "# Deprecating Basic auth\n\nBasic authentication is deprecated as of 2026-08-25 and will be removed on 2027-03-01. Use API tokens (Authorization: Bearer) instead. Existing integrations keep working until the removal date."),
        ("https://wickerbill.example/docs/quickstart", "Quickstart", "2025-01-10", "Getting started.", "# Quickstart\n\nAuthenticate with Basic auth: curl -u user:pass ...")],
       "Is Basic auth still OK to use with Wickerbill Auth? Our scripts use it.", [], any1=dates("2027-03-01"), p2="What should we move to?", inc2=["Bearer"], why="Quickstart still shows the old method.")
    dp("web-33058", "烟火通知", [
        ("https://yanhuo-notify.example/notice/sms-v1-sunset", "短信接口 v1 下线公告 - 烟火通知", "2026-09-05", "短信接口 v1 下线时间。", "# 短信接口 v1 下线公告\n\nv1 接口自 2026-09-05 起标记为弃用，将于 2026-12-31 停止服务；请迁移到 v2（/api/v2/sms/send），v2 支持模板变量和回执查询。"),
        ("https://yanhuo-notify.example/dev/sms-v1", "短信接口 v1 文档", "2024-03-15", "v1 接口文档。", "# 短信接口 v1\n\nPOST /api/v1/sms 发送短信。")],
       "烟火通知的短信 v1 接口是不是要下线了？什么时候，换成什么？", [], any1=dates("2026-12-31"))
    dp("web-33059", "Ferrule Test", [
        ("https://ferrule-test.example/docs/migrating-to-8", "Migrating to 8", "2026-06-18", "Changes in Ferrule 8.", "# Migrating to Ferrule 8\n\n`expectAsync` is deprecated in 8.0 and removed in 9.0. Replace with `await expect(...).resolves`. `--legacy-runner` is removed in 8.0 already.")],
       "In Ferrule Test, is `expectAsync` deprecated or already removed?", ["9.0"], p2="And --legacy-runner?", inc2=["8.0"], why="expectAsync deprecated (removal 9.0); legacy runner already removed.")
    dp("web-33060", "荷塘小程序", [
        ("https://hetang-mp.example/dev/notice/getuserinfo", "getUserInfo 能力调整 - 荷塘小程序", "2026-07-29", "getUserInfo 接口调整。", "# getUserInfo 能力调整\n\n自 2026-10-01 起，getUserInfo 将不再返回昵称和头像，统一返回“荷塘用户”。如需头像昵称，请使用头像昵称填写组件 chooseProfile。该调整对已上线小程序同样生效。")],
       "荷塘小程序的 getUserInfo 是不是要改了？我们线上版本会受影响吗？", ["chooseProfile"])
    dp("web-33061", "Lathe CI", [
        ("https://lathe-ci.example/changelog/2026-09", "September 2026 changelog", "2026-09-12", "Changelog.", "# September 2026\n\nThe `ubuntu-20` runner image is retired on 2026-10-15. Jobs that still target it will fail with 'image not found'. Move to `ubuntu-24` (recommended) or `ubuntu-22`."),
        ("https://lathe-ci.example/docs/runners", "Runner images", "2026-02-01", "Available runner images.", "# Runner images\n\nubuntu-20, ubuntu-22, ubuntu-24.")],
       "Our Lathe CI jobs use the ubuntu-20 image. Is that going away?", [], any1=dates("2026-10-15"), p2="Which image do they recommend instead?", inc2=["ubuntu-24"])
    dp("web-33062", "星河乐谱", [
        ("https://xinghe-score.example/news/legacy-format", "旧版乐谱格式停止支持 - 星河乐谱", "2026-08-08", "旧版 .xhs 格式停止支持。", "# 旧版格式停止支持\n\n.xhs 文件自 3.0 版起仅支持只读打开，将在 4.0 版彻底移除读取能力。请使用「文件 > 转换为 .xhscore」批量转换。")],
       "星河乐谱的 .xhs 文件以后还能打开吗？我有很多老谱子。", ["xhscore"], p2="转换是在哪个菜单里？", inc2=["转换为"], files={"备忘.txt": "老谱子都在 D 盘\n"}, pol={"must_offer": ["web_search", "web_fetch"]})
    dp("web-33063", "Brackwater Maps API", [
        ("https://brackwater.example/dev/legacy-geocode", "Legacy geocoder shutdown", "2026-09-08", "Shutdown notice.", "# Legacy geocoder shutdown\n\nThe v1 geocoder (/geo/v1) stops answering on 2026-11-30. Requests after that date return HTTP 410. The v2 geocoder is a drop-in replacement for forward lookups, but reverse lookups moved to /geo/v2/reverse.")],
       "Brackwater's legacy geocoder: when does it stop working and what status code will we see afterwards?", ["410"], p2="Where do reverse lookups go?", inc2=["/geo/v2/reverse"])
    dp("web-33064", "漠河云服务", [
        ("https://mohe-cloud.example/notice/classic-network", "经典网络退役通知 - 漠河云服务", "2026-09-01", "经典网络退役。", "# 经典网络退役通知\n\n经典网络将于 2027-06-30 退役，届时实例将断网。2026-12-31 起停止新建经典网络实例。请迁移到专有网络 VPC，控制台提供一键迁移工具。")],
       "漠河云服务的经典网络要退役了吗？我现在还能新建吗？", [], any1=dates("2027-06-30"), why="停止新建与彻底退役是两个日期。")
    dp("web-33065", "Silverling Chat SDK", [
        ("https://silverling.example/docs/v4-deprecations", "v4 deprecations", "2026-09-02", "Deprecated APIs in v4.", "# v4 deprecations\n\n`client.sendLegacy()` is deprecated since 4.6 and will be removed in 5.0 (no date set yet). Use `client.send()`. There are no plans to remove `client.on('message')`.")],
       "I use client.sendLegacy() in Silverling Chat SDK. Is it going away, and when exactly?", ["5.0"], p2="So what do I call instead?", inc2=["client.send()"], why="No removal date is published; the answer must not invent one.")
    dp("web-33066", "琥珀词典", [
        ("https://hupo-dict.example/blog/plugin-api-v1", "插件 API v1 退场计划 - 琥珀词典", "2026-08-30", "插件 API v1 退场。", "# 插件 API v1 退场计划\n\n阶段一（2026-09-01）：新插件不再能用 v1 上架；阶段二（2027-01-15）：v1 插件在 5.0 中不再加载。v2 API 文档见开发者中心。")],
       "琥珀词典的插件 API v1 什么时候不能用了？我要提前告诉用户。", [], any1=dates("2027-01-15"), p2="那现在还能上架 v1 的新插件吗？", inc2=["不再"])
