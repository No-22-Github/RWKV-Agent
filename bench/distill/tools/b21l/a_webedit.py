"""b21l sub web_edit: look a value up on the web, then edit local files (33301-33316)."""
from common import mk, page, L, WEB

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c01():
    web = [page("nimbus", "https://nimbus-cli.dev/releases", "Nimbus CLI 发布说明", "Nimbus CLI 版本发布记录与下载。",
                "# Nimbus CLI 发布说明\n\n稳定版：4.12.3（2026-09-02）\n预览版：5.0.0-rc1\n\n升级前请阅读迁移指南。\n", "2026-09-02"),
           page("nimbus", "https://old-blog.example.org/nimbus-setup", "Nimbus 安装笔记", "安装 Nimbus 4.9.0 的步骤。",
                "# Nimbus 安装笔记\n\n本文基于稳定版：4.9.0 编写。\n", "2025-11-20")]
    files = {"deploy/versions.env": L("# 部署依赖版本", "REDIS_VERSION=7.2.4", "NIMBUS_VERSION=4.9.0", "NGINX_VERSION=1.25.3"),
             "deploy/README.md": "版本号统一写在 versions.env。\n"}

    def compute(files, web):
        import re
        pg = [w for w in web if "nimbus-cli.dev" in w["url"]][0]["content"]
        v = re.search(r"稳定版：(\d+\.\d+\.\d+)", pg).group(1)
        return {"deploy/versions.env": files["deploy/versions.env"].replace("NIMBUS_VERSION=4.9.0", "NIMBUS_VERSION=" + v)}, [[v]]
    mk("hyb-33301", sub="web_edit", desc="Update a pinned Nimbus CLI version from its release page, ignoring an old blog", files=files, web=web,
       turns=[{"p": "把 deploy/versions.env 里 Nimbus 的版本号改成它现在的稳定版，其他行别动。", "req": ["web_fetch"]}], compute=compute,
       must=WEB + ["read_file", "write_file"], traps=["TR-WEBSTALE"], notes="search nimbus; fetch nimbus-cli.dev/releases; edit NIMBUS_VERSION")


@reg
def c02():
    web = [page("Harbor", "https://docs.harborpay.io/api/endpoint", "Harbor Pay API 地址", "沙箱与生产环境的 API 地址说明。",
                "Harbor Pay API\n\n生产环境基础地址：https://api.harborpay.io/v3\n沙箱基础地址：https://sandbox.harborpay.io/v3\n\n旧地址 https://gateway.harborpay.io/v2 已于 2026-06 停用。\n", "2026-07-15")]
    files = {"config/payment.yaml": L("provider: harbor", "env: production", "base_url: https://gateway.harborpay.io/v2", "timeout_ms: 8000", "retries: 3"),
             "config/payment.sandbox.yaml": L("provider: harbor", "env: sandbox", "base_url: https://sandbox.harborpay.io/v3")}

    def compute(files, web):
        import re
        pg = [w for w in web if "harborpay" in w["url"]][0]["content"]
        u = re.search(r"生产环境基础地址：(\S+)", pg).group(1)
        return {"config/payment.yaml": files["config/payment.yaml"].replace("https://gateway.harborpay.io/v2", u)}, [[u]]
    mk("hyb-33302", sub="web_edit", desc="Replace a retired API base url in the production config using the provider docs", files=files, web=web,
       turns=[{"p": "Harbor 的旧接口地址好像停用了。查一下文档里现在的生产环境地址，改到 config/payment.yaml 里。", "req": ["web_fetch"]}], compute=compute,
       must=WEB + ["read_file", "write_file"], traps=["TR-SNIPPETVAGUE"], notes="sandbox config must stay unchanged")


@reg
def c03():
    web = [page("Cobalt Mail", "https://status.cobaltmail.net/maintenance", "Cobalt Mail maintenance notice", "Upcoming maintenance window announced.",
                "Cobalt Mail scheduled maintenance\n\nStart: 2026-09-27 02:00 UTC\nEnd: 2026-09-27 05:30 UTC\nImpact: SMTP relay unavailable.\n", "2026-09-14")]
    files = {"ops/calendar.md": L("# Ops calendar", "", "- 2026-09-20 rotate TLS certs", "- 2026-09-27 Cobalt Mail maintenance: TBD", "- 2026-10-04 quarterly access review"),
             "ops/oncall.md": L("# On-call", "- week 39: Priya")}

    def compute(files, web):
        pg = [w for w in web if "cobaltmail" in w["url"]][0]["content"]
        s = pg.split("Start: ")[1].split("\n")[0]
        e = pg.split("End: ")[1].split("\n")[0]
        t = files["ops/calendar.md"].replace("Cobalt Mail maintenance: TBD", "Cobalt Mail maintenance: %s to %s" % (s, e))
        return {"ops/calendar.md": t}, [[s, e]]
    mk("hyb-33303", sub="web_edit", desc="Fill a TBD calendar entry with the maintenance window published on a status page", files=files, web=web,
       turns=[{"p": "Cobalt Mail posted their maintenance window. Replace the TBD in ops/calendar.md with 'START to END' exactly as the notice writes them, and tell me the window.", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-SNIPPETVAGUE"], notes="exact string copy of both timestamps")


@reg
def c04():
    web = [page("铁塔云", "https://www.tietayun.cn/pricing", "铁塔云对象存储定价", "对象存储按量计费标准。",
                "# 对象存储定价\n\n标准存储：0.12 元/GB/月\n低频存储：0.08 元/GB/月\n归档存储：0.03 元/GB/月\n\n2026-09-01 起生效。\n", "2026-08-25")]
    files = {"budget/storage.json": '{\n  "vendor": "铁塔云",\n  "tier": "标准存储",\n  "price_per_gb_month": 0.15,\n  "currency": "CNY"\n}\n',
             "budget/notes.txt": "价格以厂商公布为准。\n"}

    def compute(files, web):
        import re
        pg = [w for w in web if "tietayun" in w["url"]][0]["content"]
        p = re.search(r"标准存储：([\d.]+)", pg).group(1)
        return {"budget/storage.json": files["budget/storage.json"].replace('"price_per_gb_month": 0.15', '"price_per_gb_month": ' + p)}, [[p]]
    mk("hyb-33304", sub="web_edit", desc="Update a storage unit price in a JSON budget from the vendor price page", files=files, web=web,
       turns=[{"p": "铁塔云调价了，把 budget/storage.json 里的单价改成他们定价页上标准存储的新价格。", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-DECOY"], notes="only the matching tier price")


@reg
def c05():
    web = [page("Rust toolchain", "https://forge-lang.dev/blog/releases", "Forge toolchain releases", "Release channels for the toolchain.",
                "# Toolchain releases\n\nStable: 1.82.0\nBeta: 1.83.0-beta.2\nNightly: 1.84.0-nightly\n\nStable ships every six weeks.\n", "2026-09-08")]
    files = {"rust-toolchain.toml": L("[toolchain]", 'channel = "1.78.0"', 'components = ["rustfmt", "clippy"]'),
             "Dockerfile": L("FROM rust:1.78.0-slim AS build", "WORKDIR /app", "COPY . .", "RUN cargo build --release")}

    def compute(files, web):
        import re
        pg = [w for w in web if "forge-lang" in w["url"]][0]["content"]
        v = re.search(r"Stable: (\d+\.\d+\.\d+)", pg).group(1)
        return {"rust-toolchain.toml": files["rust-toolchain.toml"].replace("1.78.0", v),
                "Dockerfile": files["Dockerfile"].replace("rust:1.78.0", "rust:" + v)}, [[v], [v]]
    mk("hyb-33305", sub="web_edit", desc="Bump a toolchain channel, then the Docker base image, to the stable release shown on the project blog", files=files, web=web,
       turns=[{"p": "Bump rust-toolchain.toml to the stable toolchain release listed at forge-lang.dev/blog/releases.", "req": ["web_fetch"]},
              {"p": "Good. The Dockerfile base image should use that same release too, please update it.", "req": ["read_file"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-DECOY"], rc=6, notes="beta line is a decoy")


@reg
def c06():
    web = [page("星河学院", "https://www.xinghe-edu.cn/notice/2026-enroll", "星河学院 2026 秋季招生报名通知", "报名入口与截止日期调整。",
                "# 秋季招生报名通知\n\n报名网址已更换为：https://apply.xinghe-edu.cn\n报名截止日期：2026年10月12日\n咨询电话：0571-8800 2316\n", "2026-09-10")]
    files = {"公告/报名说明.md": L("# 报名说明", "", "报名网址：https://www.xinghe-edu.cn/apply", "报名截止日期：2026年9月30日", "咨询电话：0571-8800 2316"),
             "公告/往期.md": "往期截止日期：2025年9月30日\n"}

    def compute(files, web):
        import re
        pg = [w for w in web if "xinghe-edu.cn/notice" in w["url"]][0]["content"]
        u = re.search(r"报名网址已更换为：(\S+)", pg).group(1)
        d = re.search(r"报名截止日期：(\S+)", pg).group(1)
        t = files["公告/报名说明.md"].replace("https://www.xinghe-edu.cn/apply", u).replace("2026年9月30日", d)
        return {"公告/报名说明.md": t}, [[u, d]]
    mk("hyb-33306", sub="web_edit", desc="Update both the signup url and the deadline in a local notice from the school's announcement", files=files, web=web,
       turns=[{"p": "星河学院的招生通知更新了，帮我把 公告/报名说明.md 里的报名网址和截止日期都改成他们网站上最新公布的。", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-DECOY"], notes="phone number unchanged; 往期.md unchanged")


@reg
def c07():
    web = [page("python lifecycle", "https://pylife.example.dev/status", "Python version status", "Which Python versions still get security fixes.",
                "# Python version status\n\n| Version | Status | End of life |\n|---|---|---|\n| 3.9 | end-of-life | 2025-10 |\n| 3.10 | security | 2026-10 |\n| 3.11 | bugfix | 2027-10 |\n| 3.12 | bugfix | 2028-10 |\n", "2026-09-01")]
    files = {".ci/matrix.yml": L("jobs:", "  test:", "    python-version: [3.9, 3.10, 3.11, 3.12]", "    os: [ubuntu, macos]"),
             "setup.cfg": L("[metadata]", "name = tidal-sync", "python_requires = >=3.9")}

    def compute(files, web):
        return {".ci/matrix.yml": files[".ci/matrix.yml"].replace("[3.9, 3.10, 3.11, 3.12]", "[3.10, 3.11, 3.12]")}, [["3.9"]]
    mk("hyb-33307", sub="web_edit", desc="Drop end-of-life Python versions from a CI matrix according to the lifecycle page, leaving setup.cfg alone", files=files, web=web,
       turns=[{"p": "Check pylife.example.dev/status and remove any version that has reached end-of-life from the test matrix in .ci/matrix.yml. Only the CI file, not setup.cfg.", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-DECOY"], notes="only 3.9 is EOL; 3.10 still has security status")


@reg
def c08():
    web = [page("postgres tags", "https://registry.dbhub.io/postgres/tags", "postgres supported tags", "Supported tags and Dockerfile links.",
                "Supported tags\n\n- 17.0, 17, latest\n- 16.4, 16\n- 15.8, 15\n\nThe 16 series is the one pinned by most deployments.\n", "2026-09-12")]
    files = {"docker-compose.yml": L("services:", "  db:", "    image: postgres:16.1", "    ports:", '      - "5432:5432"', "  cache:", "    image: redis:7.2")}

    def compute(files, web):
        return {"docker-compose.yml": files["docker-compose.yml"].replace("postgres:16.1", "postgres:16.4")}, [["16.4"]]
    mk("hyb-33308", sub="web_edit", desc="Move a pinned postgres tag to the newest minor of the same major series listed in the registry", files=files, web=web,
       turns=[{"p": "Our compose file pins postgres:16.1. Look up the tags on registry.dbhub.io and move it to the newest 16.x, staying on major 16.", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-DECOY"], notes="do not jump to 17.0")


@reg
def c09():
    web = [page("晴岚", "https://www.qinglan-home.com/support", "晴岚智能家居 客服中心", "客服热线与邮箱。",
                "# 客服中心\n\n服务热线（2026年9月起启用）：400-720-3358\n服务邮箱：care@qinglan-home.com\n工作时间：9:00-21:00\n", "2026-09-05")]
    files = {"docs/联系我们.md": L("# 联系我们", "", "服务热线：400-620-1180", "工作时间：9:00-21:00"),
             "docs/FAQ.md": L("# 常见问题", "", "Q: 怎么联系客服？", "A: 发邮件到 help@qinglan-home.com 或拨打热线。")}

    def compute(files, web):
        import re
        pg = [w for w in web if "qinglan-home" in w["url"]][0]["content"]
        tel = re.search(r"启用）：(\S+)", pg).group(1)
        mail = re.search(r"服务邮箱：(\S+)", pg).group(1)
        return {"docs/联系我们.md": files["docs/联系我们.md"].replace("400-620-1180", tel),
                "docs/FAQ.md": files["docs/FAQ.md"].replace("help@qinglan-home.com", mail)}, [[tel], [mail]]
    mk("hyb-33309", sub="web_edit", desc="Replace a hotline in one doc, then the support mailbox in a second doc, both from the vendor support page", files=files, web=web,
       turns=[{"p": "晴岚智能家居换了客服热线，docs/联系我们.md 里的号码帮我改成他们客服页上现在的。", "req": ["web_fetch"]},
              {"p": "FAQ 里写的客服邮箱也对一下，如果和他们页面上不一样就改过来。"}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-DECOY"], rc=6, notes="second turn re-checks the page for the mailbox")


@reg
def c10():
    web = [page("reqlite", "https://reqlite.dev/changelog/3.0", "reqlite 3.0 changelog", "Breaking changes in 3.0.",
                "# reqlite 3.0\n\nBreaking: `fetchLegacy(url)` has been removed. Use `fetchV3(url, opts)` instead; pass `{}` when you have no options.\n", "2026-08-18")]
    files = {"src/client.js": L("const { fetchLegacy } = require('reqlite');", "", "async function load(u) {", "  const r = await fetchLegacy(u);", "  return r.body;", "}", "", "module.exports = { load };"),
             "package.json": '{ "name": "dash", "dependencies": { "reqlite": "^3.0.0" } }\n'}

    def compute(files, web):
        t = files["src/client.js"].replace("const { fetchLegacy }", "const { fetchV3 }").replace("fetchLegacy(u)", "fetchV3(u, {})")
        return {"src/client.js": t}, [["fetchV3"]]
    mk("hyb-33310", sub="web_edit", desc="Migrate a removed function call in client.js using the library changelog", files=files, web=web,
       turns=[{"p": "After upgrading reqlite to 3.0 our client breaks. Find what the 3.0 changelog says about fetchLegacy and fix src/client.js accordingly.", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-SNIPPETVAGUE"], notes="import and call both change; empty opts")


@reg
def c11():
    web = [page("滨海新区 社保", "https://www.binhai-hr.gov.cn/policy/si-base-2026", "滨海新区 2026 年度社保缴费基数公告", "年度缴费基数上下限调整。",
                "# 2026 年度社保缴费基数\n\n缴费基数上限：24500 元/月\n缴费基数下限：4120 元/月\n执行时间：2026年7月1日起\n", "2026-06-20")]
    files = {"payroll/params.ini": L("[social_insurance]", "base_cap = 21800", "base_floor = 3980", "employer_rate = 0.16"),
             "payroll/history.txt": "2025: cap 21800 floor 3980\n"}

    def compute(files, web):
        import re
        pg = [w for w in web if "binhai-hr" in w["url"]][0]["content"]
        c = re.search(r"上限：(\d+)", pg).group(1)
        f = re.search(r"下限：(\d+)", pg).group(1)
        t = files["payroll/params.ini"].replace("base_cap = 21800", "base_cap = " + c).replace("base_floor = 3980", "base_floor = " + f)
        return {"payroll/params.ini": t}, [[c, f]]
    mk("hyb-33311", sub="web_edit", desc="Refresh insurance base cap and floor in a payroll ini from a district government notice", files=files, web=web,
       turns=[{"p": "滨海新区公布了新的社保缴费基数，把 payroll/params.ini 里的上限和下限都更新，费率不动。", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-SNIPPETVAGUE"], notes="history.txt is a log, keep unchanged")


@reg
def c12():
    web = [page("orbit-sync", "https://orbit-sync.io/download", "Download Orbit Sync", "Installers for every platform.",
                "# Download Orbit Sync\n\nCurrent release: 2.6.1\nBackport for the 2.5 line: 2.5.9 (security fixes only)\n", "2026-09-11"),
           page("orbit-sync", "https://orbit-sync.io/security/advisory-41", "Advisory 41", "Fixed in 2.5.9 and 2.6.1.", "Advisory 41 is fixed in 2.5.9 and 2.6.1.\n", "2026-08-30")]
    files = {"scripts/install.sh": L("#!/bin/sh", "VERSION=2.5.0", 'curl -fsSL "https://orbit-sync.io/dl/orbit-$VERSION.tgz" -o orbit.tgz', "tar xzf orbit.tgz"),
             "NOTES.txt": "install via scripts/install.sh\n"}

    def compute(files, web):
        import re
        pg = [w for w in web if w["url"].endswith("/download")][0]["content"]
        v = re.search(r"Current release: (\S+)", pg).group(1)
        return {"scripts/install.sh": files["scripts/install.sh"].replace("VERSION=2.5.0", "VERSION=" + v)}, [[v]]
    mk("hyb-33312", sub="web_edit", desc="Set the install script version to the current release from the download page; a 2.5 backport and an advisory are decoys", files=files, web=web,
       turns=[{"p": "Set VERSION in scripts/install.sh to Orbit Sync's current release (the main line, not a backport).", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-DECOY"], notes="2.6.1 not 2.5.9")


@reg
def c13():
    web = [page("鹿鸣书店", "https://www.luming-books.cn/stores/hours", "鹿鸣书店 门店信息", "营业时间与优惠。",
                "# 门店信息\n\n国庆假期（10月1日至10月7日）营业时间：10:00-20:30\n平日营业时间：9:30-21:30\n停车优惠：凭购书小票免费停车2小时\n", "2026-09-09")]
    files = {"门店/营业时间.md": L("# 鹿鸣书店 营业时间", "", "平日：9:30-21:30", "国庆假期：待定")}

    def compute(files, web):
        t = files["门店/营业时间.md"].replace("国庆假期：待定", "国庆假期：10:00-20:30")
        return {"门店/营业时间.md": t + "停车优惠：凭购书小票免费停车2小时\n"}, [["10:00-20:30"], ["免费停车2小时"]]
    mk("hyb-33313", sub="web_edit", desc="Fill the holiday hours from the store site, then append the parking perk line", files=files, web=web,
       turns=[{"p": "鹿鸣书店官网上有国庆假期的营业时间，帮我填到 门店/营业时间.md 的“待定”那里。", "req": ["web_fetch"]},
              {"p": "他们页面上还有停车优惠吧？也加到这个文件最后一行，格式：停车优惠：<原文内容>。"}],
       compute=compute, must=WEB + ["read_file", "write_file", "append_file"], traps=["TR-DECOY"], rc=6, loose=["门店/营业时间.md"], notes="append a parking line in turn 2")


@reg
def c14():
    web = [page("Lumen Cloud", "https://docs.lumencloud.dev/endpoints", "Lumen Cloud regional endpoints", "Hostnames per region.",
                "# Regional endpoints\n\n| Region | Host |\n|---|---|\n| us-east | api.use1.lumencloud.dev |\n| eu-north | api.eun2.lumencloud.dev |\n| eu-west | api.euw1.lumencloud.dev |\n| ap-south | api.aps3.lumencloud.dev |\n", "2026-08-22")]
    files = {".env.example": L("REGION=eu-north", "API_HOST=api.eun1.lumencloud.dev", "API_KEY=changeme"), "deploy.md": "uses .env.example as the template\n"}

    def compute(files, web):
        import re
        pg = [w for w in web if "lumencloud" in w["url"]][0]["content"]
        h = re.search(r"\| eu-north \| (\S+) \|", pg).group(1)
        return {".env.example": files[".env.example"].replace("api.eun1.lumencloud.dev", h)}, [[h]]
    mk("hyb-33314", sub="web_edit", desc="Correct the API host for the configured region by reading the endpoint table", files=files, web=web,
       turns=[{"p": "Our .env.example has REGION=eu-north but the API_HOST looks stale. Fix API_HOST using Lumen Cloud's endpoint docs for that region.", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-NEARNAME"], notes="eun2 vs eun1 near name; region row selection")


@reg
def c15():
    web = [page("Quill DB", "https://quilldb.org/support-policy", "Quill DB 支持策略", "各版本的支持截止日期。",
                "# 支持策略\n\nQuill DB 4.x：已于 2025-12-31 结束支持\nQuill DB 5.x：支持截止 2027-03-31\nQuill DB 6.x：支持截止 2029-03-31\n", "2026-07-01")]
    files = {"资产/软件清单.csv": L("名称,版本,负责人,支持截止", "Quill DB,5.x,罗敏,2026-12-31", "Ledger UI,8.1,陈宇,2028-06-30", "Quill DB Proxy,1.4,罗敏,2027-01-31")}

    def compute(files, web):
        t = files["资产/软件清单.csv"].replace("Quill DB,5.x,罗敏,2026-12-31", "Quill DB,5.x,罗敏,2027-03-31")
        return {"资产/软件清单.csv": t}, [["2027-03-31"]]
    mk("hyb-33315", sub="web_edit", desc="Update the support end date of one csv row from the vendor support policy page", files=files, web=web,
       turns=[{"p": "资产/软件清单.csv 里 Quill DB 5.x 的支持截止日期不准了，按厂商的支持策略页改一下，别动其他行。", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-NEARNAME"], notes="Quill DB Proxy row is a near-name decoy")


@reg
def c16():
    web = [page("Tern", "https://tern-build.dev/releases", "Tern releases", "Release history.",
                "# Tern release history\n\n- 3.4.0 (2026-09-03) current\n- 3.3.2 (2026-07-20)\n- 3.3.1 (2026-06-30)\n- 3.3.0 (2026-06-02)\n", "2026-09-03")]
    files = {"env/prod.cfg": L("tern_version = 3.2.0", "workers = 6"), "env/staging.cfg": L("tern_version = 3.2.0", "workers = 2")}

    def compute(files, web):
        import re
        vs = re.findall(r"- (\d+\.\d+\.\d+) \(", [w for w in web if "tern-build" in w["url"]][0]["content"])
        return {"env/prod.cfg": files["env/prod.cfg"].replace("3.2.0", vs[0]), "env/staging.cfg": files["env/staging.cfg"].replace("3.2.0", vs[1])}, [[vs[0]], [vs[1]]]
    mk("hyb-33316", sub="web_edit", desc="Pin prod to the current Tern release, then staging to the release before it", files=files, web=web,
       turns=[{"p": "Set tern_version in env/prod.cfg to the current Tern release (see tern-build.dev/releases).", "req": ["web_fetch"]},
              {"p": "Staging should run the release right before that one. Update env/staging.cfg."}],
       compute=compute, must=WEB + ["read_file", "write_file"], traps=["TR-SUPERSEDE"], rc=6, notes="staging = previous entry 3.3.2")
