"""33036-33046 latest_version."""
from common import *


def lv(cid, brand, pages, p1, val, p2=None, val2=None, files=None, pol=None, level="L2", why="", fetch=True, req1=None):
    web = [fx(brand, u, t, s, c, d) for (u, t, d, s, c) in pages]
    r1 = req1 if req1 is not None else (["web_fetch"] if fetch else ["web_search"])
    turns = [T(p1, req=r1, inc=[val])]
    if p2:
        turns.append(T(p2, inc=[val2] if isinstance(val2, str) else [], any=val2 if isinstance(val2, list) else []))
    mk(cid, tt="latest_version", desc="Find the current stable release among mixed pre-release/old pages (%s)" % brand, web=web, turns=turns,
       traps=["TR-WEBSTALE"], ref="搜索 -> 打开下载/发布页 -> 区分稳定版与预发布版", why=why or "Stable version is stated only on the releases page.",
       trap_notes=["结果里混有 beta/rc 与旧版本。"], policy=pol or WSF, level=level, ref_calls=4 if p2 else 3, files=files, sub="lv")


def build():
    lv("web-33036", "Tarnish Linter", [
        ("https://tarnish-lint.example/releases", "Releases - Tarnish Linter", "2026-09-12", "Tarnish Linter releases.", "# Releases\n\n- 9.0.0-rc.2 (pre-release) 2026-09-12\n- 8.14.3 (stable) 2026-08-30\n- 8.14.2 2026-08-02\n- 8.13.9 (LTS) 2026-06-11"),
        ("https://tarnish-lint.example/blog/9-roadmap", "Road to 9.0", "2026-07-01", "9.0 is in release candidate stage.", "# Road to 9.0\n\nRelease candidates are for testing only; 9.0 final is planned for November.")],
       "What's the current stable version of Tarnish Linter? Not a release candidate.", "8.14.3", p2="And which one is the LTS line?", val2="8.13.9")
    lv("web-33037", "雾凇笔记", [
        ("https://wusong-notes.example/download", "下载 - 雾凇笔记", "2026-09-17", "雾凇笔记各平台安装包。", "# 下载\n\n当前稳定版 4.7.2（2026-09-17 发布）。测试版 4.8.0-beta.1 仅限内测渠道。旧版本存档见历史页。"),
        ("https://wusong-notes.example/history", "历史版本 - 雾凇笔记", "2026-03-01", "雾凇笔记历史版本存档。", "# 历史版本\n\n4.5.0（2026-02）、4.4.3（2025-12）、4.3.1（2025-09）。")],
       "雾凇笔记现在最新的正式版是哪个版本？", "4.7.2")
    lv("web-33038", "Gantry Build", [
        ("https://gantry-build.example/downloads", "Downloads - Gantry Build", "2026-08-28", "Gantry Build downloads.", "# Downloads\n\nGantry 2.31.0 is the current release (2026-08-28). Nightly builds are published daily but unsupported.")],
       "My package.json pins gantry-build at 2.28.4. Is that the current release, and if not what is?",
       "2.31.0", files={"package.json": "{\n  \"name\": \"site\",\n  \"devDependencies\": {\n    \"gantry-build\": \"2.28.4\",\n    \"tarn\": \"1.9.0\"\n  }\n}\n"},
       pol={"must_offer": ["web_search", "web_fetch", "read_file"]}, req1=["read_file"], why="Local pin is old; current release only on the web.")
    lv("web-33039", "珊瑚输入法", [
        ("https://shanhu-ime.example/android", "安卓版 - 珊瑚输入法", "2026-09-09", "珊瑚输入法安卓版更新记录。", "# 安卓版\n\n最新版本 6.12.0（2026-09-09），修复语音输入崩溃。"),
        ("https://shanhu-ime.example/ios", "iOS 版 - 珊瑚输入法", "2026-09-01", "珊瑚输入法 iOS 版更新记录。", "# iOS 版\n\n最新版本 6.10.4（2026-09-01），等待 App Store 审核 6.11.0。")],
       "珊瑚输入法安卓版最新是多少版本？iOS 呢？", "6.12.0", p2="iOS 现在能下到的最新版是哪个？", val2="6.10.4", why="两个平台版本不同。")
    lv("web-33040", "Reedmace ORM", [
        ("https://reedmace-orm.example/changelog", "Changelog - Reedmace ORM", "2026-09-04", "Changelog for Reedmace ORM.", "# Changelog\n\n## 5.3.0 - 2026-09-04 (current)\nAdds JSON column helpers.\n## 5.2.7 - 2026-08-11\nSecurity fix for query logging.\n## 5.2.0 - 2026-06-20"),
        ("https://devforum.example/t/reedmace-5-4-plans", "Reedmace 5.4 plans (community thread)", "2026-09-15", "Community thread about 5.4.", "People are asking when 5.4 lands. A maintainer replied: nothing published yet, still on the 5.3 line.")],
       "Which Reedmace ORM version fixed the query logging security problem, and what version is current?", "5.2.7", p2="So what should I upgrade to?", val2="5.3.0")
    lv("web-33041", "松针办公", [
        ("https://songzhen-office.example/release", "版本发布 - 松针办公", "2026-09-19", "松针办公桌面版版本发布说明。", "# 版本发布\n\n桌面版 12.6（2026-09-19，正式版）。12.7 预览版需加入体验计划。")],
       "我电脑上的松针办公是 12.3，现在正式版是多少了？要不要升？", "12.6", files={"我的软件/松针办公.txt": "松针办公 桌面版 12.3\n安装日期 2026-04-02\n"},
       pol={"must_offer": ["web_search", "web_fetch", "read_file", "list_files"]}, req1=["web_fetch"], level="L2")
    lv("web-33042", "Glimmer Runtime", [
        ("https://glimmer-rt.example/install", "Install Glimmer Runtime", "2026-09-03", "Install guide.", "# Install\n\nThe installer fetches version 1.20.1 by default (current stable). Use --channel next for 1.21.0-next.4."),
        ("https://glimmer-rt.example/eol", "Support policy", "2026-05-15", "Support windows.", "# Support policy\n\nEach minor is supported for 12 months. 1.16 reaches end of life on 2026-11-01.")],
       "现在默认安装 Glimmer Runtime 会装到哪个版本？", "1.20.1", p2="When does 1.16 stop being supported?", val2=dates("2026-11-01"))
    lv("web-33043", "青鸟地图", [
        ("https://qingniao-map.example/app/changelog", "更新日志 - 青鸟地图", "2026-09-14", "青鸟地图 App 更新日志。", "# 更新日志\n\n8.3.0（2026-09-14）：新增离线导航。\n8.2.5（2026-08-22）：修复定位漂移。"),
        ("https://app-store-mirror.example/qingniao", "青鸟地图 - 应用商店镜像页", "2026-07-30", "应用商店镜像页，信息可能滞后。", "版本 8.1.9。（镜像页，更新不及时）")],
       "青鸟地图最新版本号是多少？那个应用商店镜像页好像没更新。", "8.3.0")
    lv("web-33044", "Basalt Auth", [
        ("https://basalt-auth.example/security/advisories", "Security advisories - Basalt Auth", "2026-09-10", "Advisories and fixed versions.", "# Advisories\n\nBA-2026-014 (high): fixed in 3.9.2. All versions before 3.9.2 are affected. Current stable is 3.10.0."),
        ("https://basalt-auth.example/releases", "Releases - Basalt Auth", "2026-09-18", "Basalt Auth releases.", "# Releases\n\n3.10.0 stable 2026-09-18\n3.9.2 2026-09-10\n3.9.1 2026-08-25")],
       "We run Basalt Auth 3.9.1. Is there a known security issue, which version fixes it and what is the current stable release?", "3.9.2", p2="Fine, which exact version should I go to?", val2="3.10.0", why="Fix version vs current stable are different numbers.")
    lv("web-33045", "栗子相册", [
        ("https://lizi-album.example/notes/windows", "Windows 版本说明 - 栗子相册", "2026-09-06", "栗子相册 Windows 版本说明。", "# Windows\n\n当前版本 2.19.0，要求 Windows 10 21H2 及以上。"),
        ("https://lizi-album.example/notes/mac", "macOS 版本说明 - 栗子相册", "2026-09-13", "栗子相册 macOS 版本说明。", "# macOS\n\n当前版本 2.20.1，要求 macOS 13 及以上。")],
       "我用 Mac，栗子相册最新版是多少，对系统有什么要求？", "2.20.1", why="Windows 与 macOS 版本不同。")
    lv("web-33046", "Spindle Queue", [
        ("https://spindlequeue.example/docs/versions", "Versions - Spindle Queue", "2026-08-22", "Supported versions.", "# Versions\n\nCurrent: 0.18.2. The 0.17 line receives security fixes only until 2026-12."),
        ("https://spindlequeue.example/blog/0-19", "0.19 coming soon", "2026-09-17", "Teaser for 0.19.", "0.19 enters feature freeze next week. Not yet released; do not use in production.")],
       "Spindle Queue 现在能用于生产的版本是哪个？我看到有篇文章提到 0.19。", "0.18.2", why="0.19 is unreleased.")
