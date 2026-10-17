"""b21l sub multi: the follow-up needs fresh evidence (33365-33380)."""
from common import mk, page, L, rng, WEB

B = []
BR = WEB + ["read_file", "write_file"]


def reg(f):
    B.append(f)
    return f


@reg
def c65():
    files = {"config/dev.yaml": L("app: pulse", "db:", "  host: localhost", "  port: 5433", "cache_ttl: 60"),
             "config/prod.yaml": L("app: pulse", "db:", "  host: pg-main.internal", "  port: 6432", "cache_ttl: 600"),
             "config/staging.yaml": L("app: pulse", "db:", "  host: pg-stg.internal", "  port: 5440", "cache_ttl: 120")}

    def compute(files, web):
        import re
        g = lambda p: re.search(r"port: (\d+)", files[p]).group(1)
        return {}, [[g("config/dev.yaml")], [g("config/prod.yaml")]]
    mk("hyb-33365", sub="multi", desc="Database port in dev config, then the prod config", files=files,
       turns=[{"p": "开发环境的数据库端口是多少？看 config/dev.yaml。"}, {"p": "那生产环境的呢？"}],
       compute=compute, must=["read_file"], traps=["TR-MULTISRC"], rc=3, notes="5433 then 6432")


@reg
def c66():
    files = {"app/package.json": '{\n  "name": "tidepool",\n  "version": "2.4.1",\n  "license": "Apache-2.0"\n}\n',
             "app/package-lock.json": '{\n  "name": "tidepool",\n  "version": "2.4.0",\n  "lockfileVersion": 3\n}\n'}

    def compute(files, web):
        import json
        return {}, [[json.loads(files["app/package.json"])["version"]], [json.loads(files["app/package-lock.json"])["version"]]]
    mk("hyb-33366", sub="multi", desc="Version in package.json, then the possibly different version recorded in the lockfile", files=files,
       turns=[{"p": "What version does app/package.json declare?"}, {"p": "And what version does the lockfile in the same folder record for the project?"}],
       compute=compute, must=["read_file"], traps=["TR-NEARNAME"], rc=3, notes="2.4.1 then 2.4.0")


@reg
def c67():
    r = rng(67)
    paths = ["/pay", "/login", "/cart", "/search"]
    rows = []
    for i in range(220):
        rows.append("2026-09-15 %02d:%02d %s %s" % (r.randint(0, 23), r.randint(0, 59), r.choice(paths), r.choices(["200", "500", "404"], [6, 2, 1])[0]))
    files = {"日志/web.log": "\n".join(rows) + "\n"}

    def compute(files, web):
        ls = files["日志/web.log"].splitlines()
        f = lambda p: str(sum(1 for l in ls if l.split()[2] == p and l.split()[3] == "500"))
        return {}, [[f("/pay")], [f("/login")]]
    mk("hyb-33367", sub="multi", desc="Server-error count for one path, then for another path in the same log", files=files,
       turns=[{"p": "日志/web.log 里 /pay 这个路径返回 500 的有多少次？"}, {"p": "/login 呢？"}],
       compute=compute, must=["bash", "read_file"], traps=["TR-DECOY"], rc=4, notes="grep path and status")


@reg
def c68():
    web = [page("Sable", "https://sable-notes.com/pricing", "Sable pricing", "Monthly plans.",
                "# Sable pricing\n\nPro: $12 per month\nAnnual billing has its own page: https://sable-notes.com/pricing/annual\n", "2026-09-01"),
           page("Sable annual", "https://sable-notes.com/pricing/annual", "Sable annual pricing", "Yearly plans.",
                "# Sable annual\n\nPro (annual): $96 per year, billed once\n", "2026-09-01")]

    def compute(files, web):
        import re
        a = re.search(r"Pro: \$(\d+) per month", web[0]["content"]).group(1)
        b = re.search(r"\$(\d+) per year", web[1]["content"]).group(1)
        return {}, [[a], [b]]
    mk("hyb-33368", sub="multi", desc="Monthly price on the pricing page, then the annual price that lives on a linked page", files={"README.md": "pricing check\n"}, web=web,
       turns=[{"p": "What does Sable's Pro plan cost per month? Their pricing page is at sable-notes.com/pricing.", "req": ["web_fetch"]},
              {"p": "And if I pay annually, what is the Pro price for the year?", "req": ["web_fetch"]}],
       compute=compute, must=WEB, traps=["TR-SUPERSEDE"], rc=4, notes="12 then 96 (second page)")


@reg
def c69():
    web = [page("Moss", "https://moss-cms.org/", "Moss CMS", "A small content management system.",
                "# Moss CMS\n\n当前版本：8.2.0\n系统要求见 https://moss-cms.org/requirements\n", "2026-09-07"),
           page("Moss", "https://moss-cms.org/requirements", "Moss CMS 系统要求", "运行环境要求。",
                "# 系统要求\n\nPHP 最低版本：8.1\n数据库：MySQL 8.0 或 PostgreSQL 14\n", "2026-09-07")]

    def compute(files, web):
        return {}, [["8.2.0"], ["8.1"]]
    mk("hyb-33369", sub="multi", desc="Current version from a CMS homepage, then the PHP requirement from its linked requirements page", files={"notes.txt": "cms upgrade planning\n"}, web=web,
       turns=[{"p": "Moss CMS 现在的版本号是多少？官网是 moss-cms.org。", "req": ["web_fetch"]},
              {"p": "它要求的 PHP 最低版本是多少？"}],
       compute=compute, must=WEB, traps=["TR-SNIPPETVAGUE"], rc=4, notes="8.2.0 then 8.1 from /requirements")


@reg
def c70():
    r = rng(70)
    sales = ["日期,金额"] + ["2026-09-%02d,%d" % (r.randint(1, 15), r.randint(10, 90)) for _ in range(170)]
    refunds = ["日期,金额"] + ["2026-09-%02d,%d" % (r.randint(1, 15), r.randint(5, 40)) for _ in range(60)]
    files = {"财务/sales.csv": "\n".join(sales) + "\n", "财务/refunds.csv": "\n".join(refunds) + "\n"}

    def compute(files, web):
        f = lambda p: sum(int(l.split(",")[1]) for l in files[p].splitlines()[1:])
        a, b = f("财务/sales.csv"), f("财务/refunds.csv")
        return {}, [list(dict.fromkeys([str(a), "{:,}".format(a)])), list(dict.fromkeys([str(b), "{:,}".format(b)])), list(dict.fromkeys([str(a - b), "{:,}".format(a - b)]))]
    mk("hyb-33370", sub="multi", desc="Total sales, then total refunds from a second file, then the net", files=files,
       turns=[{"p": "财务/sales.csv 的金额一共多少？", "any": True}, {"p": "财务/refunds.csv 里的退款总额呢？", "any": True}, {"p": "那这两个相减，净销售额是多少？", "any": True}],
       compute=compute, must=["bash", "read_file", "calculator"], traps=["TR-MULTISRC"], rc=6, notes="sum two columns, subtract")


@reg
def c71():
    files = {"设置/settings.json": '{\n  "theme": "light",\n  "language": "zh-CN",\n  "autosave": true\n}\n'}

    def compute(files, web):
        import json
        d = json.loads(files["设置/settings.json"])
        return {}, [[], [d["theme"], d["language"]]]
    mk("hyb-33371", sub="multi", desc="A staged edit is rejected by the user; the follow-up must read the file again instead of assuming the edit landed", files=files,
       turns=[{"p": "把 设置/settings.json 里的 theme 改成 dark。"},
              {"p": "我把你刚才的修改拒绝了，没有保存。现在这个文件里 theme 是什么？language 又是什么？", "review": "reject"}],
       compute=compute, must=["read_file", "write_file"], traps=["TR-CLAIM"], rc=4, notes="after reject the file is unchanged: light, zh-CN")


@reg
def c72():
    files = {"pkg/package.json": '{\n  "name": "kelpie",\n  "version": "1.9.3",\n  "license": "MIT",\n  "private": true\n}\n'}

    def compute(files, web):
        return {"pkg/package.json": files["pkg/package.json"].replace('"version": "1.9.3"', '"version": "2.0.0"')}, [[], ["2.0.0", "MIT"]]
    mk("hyb-33372", sub="multi", desc="Version bump accepted by the user; the follow-up asks for fields read back from the file on disk", files=files,
       turns=[{"p": "Bump the version in pkg/package.json to 2.0.0."},
              {"p": "I accepted the change. Now open the file again and tell me the version and the license field exactly as they appear.", "review": "accept"}],
       compute=compute, must=["read_file", "write_file"], traps=["TR-CLAIM"], rc=4, notes="2.0.0 and MIT")


@reg
def c73():
    files = {"清单/采购.txt": L("打印纸", "墨盒", "订书钉", "便签")}

    def compute(files, web):
        return {}, [[], ["4"]]
    mk("hyb-33373", sub="multi", desc="Append an item, the user rejects it, then ask how many lines the file has now", files=files,
       turns=[{"p": "在 清单/采购.txt 最后加一行“笔记本”。"},
              {"p": "我没有接受这次改动，已经撤掉了。现在 清单/采购.txt 里一共几行？", "review": "reject"}],
       compute=compute, must=["read_file", "write_file", "append_file"], traps=["TR-CLAIM"], rc=4, notes="4 lines, not 5")


@reg
def c74():
    files = {"conf/runtime.ini": L("[runtime]", "mode = fast", "retries = 3", "log = info")}

    def compute(files, web):
        return {"conf/runtime.ini": files["conf/runtime.ini"].replace("mode = fast", "mode = safe")}, [[], ["safe"]]
    mk("hyb-33374", sub="multi", desc="First change is rejected and replaced by a different change; final file must carry only the second", files=files,
       turns=[{"p": "Change retries to 10 in conf/runtime.ini."},
              {"p": "I rejected that edit, so the file is back to what it was. Instead, set mode to safe and leave everything else alone. Tell me the mode line afterwards.", "review": "reject"}],
       compute=compute, must=["read_file", "write_file"], traps=["TR-CLAIM"], rc=5, notes="only mode changes")


@reg
def c75():
    web = [page("Tideline", "https://tideline-edu.com/pricing", "Tideline pricing", "Plans for teams.",
                "# Tideline pricing\n\nPro: 120 yuan per seat per year\nEducation customers: see https://tideline-edu.com/education\n", "2026-09-03"),
           page("Tideline", "https://tideline-edu.com/education", "Tideline education offer", "Discounts for schools.",
                "# Education offer\n\nSchools and universities get 30% off list price.\n", "2026-09-03")]

    def compute(files, web):
        return {}, [["120"], ["1680"] and [x for x in ["1680", "1,680"]]]
    mk("hyb-33375", sub="multi", desc="List price per seat, then the discount from a linked education page applied to a 20-seat order", files={"readme.txt": "tideline eval\n"}, web=web,
       turns=[{"p": "Tideline 的 Pro 版每个席位一年多少钱？价格页在 tideline-edu.com/pricing。", "req": ["web_fetch"]},
              {"p": "我们是学校，要买 20 个席位。看看他们对教育机构有没有优惠，按优惠价算一年总共多少？", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["calculator"], traps=["TR-MULTISRC"], rc=5, notes="120*20*0.7 = 1680")


@reg
def c76():
    web = [page("Aspen", "https://aspen-runtime.dev/downloads", "Aspen downloads", "Get Aspen.",
                "# Downloads\n\nCurrent release: 5.2.0\nLong-term support builds are listed at https://aspen-runtime.dev/lts\n", "2026-09-10"),
           page("Aspen", "https://aspen-runtime.dev/lts", "Aspen LTS", "Long-term support.",
                "# LTS releases\n\nActive LTS: 4.8.6 (supported until 2028-04)\nMaintenance LTS: 3.12.9\n", "2026-09-10")]

    def compute(files, web):
        return {}, [["5.2.0"], ["4.8.6"]]
    mk("hyb-33376", sub="multi", desc="Current release, then the active LTS build after the user says they follow the support channel", files={"deploy.txt": "runtime: aspen\n"}, web=web,
       turns=[{"p": "What's the current Aspen release? Downloads page is aspen-runtime.dev/downloads.", "req": ["web_fetch"]},
              {"p": "Sorry, I should have said we only run long-term support builds. Which build is the active LTS then?", "req": ["web_fetch"]}],
       compute=compute, must=WEB, traps=["TR-SUPERSEDE"], rc=4, notes="5.2.0 then 4.8.6 from /lts")


@reg
def c77():
    files = {"机房/hosts.txt": L("web-03 10.20.3.13 22", "web-04 10.20.3.14 22", "db-01 10.20.8.21 5432", "db-02 10.20.8.22 5433", "cache-01 10.20.9.5 6379")}

    def compute(files, web):
        rows = {l.split()[0]: l.split() for l in files["机房/hosts.txt"].splitlines()}
        return {}, [[rows["web-03"][1]], [rows["db-02"][1], rows["db-02"][2]]]
    mk("hyb-33377", sub="multi", desc="IP of one named host, then the user corrects the host name and also wants its port", files=files,
       turns=[{"p": "机房/hosts.txt 里 web-03 的 IP 是多少？"}, {"p": "不对，我记错了，我要查的是 db-02。它的 IP 和端口分别是什么？"}],
       compute=compute, must=["read_file", "search_text"], traps=["TR-NEARNAME"], rc=3, notes="web-03 10.20.3.13 ; db-02 10.20.8.22 5433")


@reg
def c78():
    web = [page("Lumen Cloud", "https://docs.lumencloud.dev/regions", "Lumen Cloud regions", "Region codes and data residency.",
                "# Regions\n\n| Region | City | Data residency |\n|---|---|---|\n| eu-north | Stockholm | EU |\n| ap-south | Mumbai | India |\n| us-east | Virginia | US |\n", "2026-08-12")]

    def compute(files, web):
        return {}, [["Stockholm"], ["Mumbai", "India"]]
    mk("hyb-33378", sub="multi", desc="City and residency of one region on a docs table, then the user switches to another region", files={"plan.md": "# plan\n"}, web=web,
       turns=[{"p": "Where is the eu-north region of Lumen Cloud located? Docs are at docs.lumencloud.dev/regions.", "req": ["web_fetch"]},
              {"p": "Actually our deployment is in ap-south. Which city is that, and what is its data residency?"}],
       compute=compute, must=WEB, traps=["TR-DECOY"], rc=4, notes="Stockholm ; Mumbai/India")


@reg
def c79():
    web = [page("征集", "https://www.huatu-gallery.cn/call/2026", "华图美术馆 2026 作品征集", "征集通知与截止日期。",
                "# 2026 作品征集\n\n投稿截止：2026年10月20日 24:00\n", "2026-08-30"),
           page("征集", "https://huatu-gallery.cn/call-mirror", "华图美术馆 征集（备用页）", "备用镜像页。",
                "# 作品征集（备用页）\n\n投稿截止：2026年10月25日 24:00（此页已过期，以主站为准）\n", "2026-06-02")]

    def compute(files, web):
        return {}, [["10月20日"], ["10月20日"]]
    mk("hyb-33379", sub="multi", desc="Deadline from the main call page, then the user supplies a backup page url that disagrees and is marked outdated", files={"日程.txt": "投稿准备\n"}, web=web,
       turns=[{"p": "华图美术馆 2026 年作品征集的投稿截止日期是哪天？", "req": ["web_fetch"]},
              {"p": "我同事发来一个备用页 huatu-gallery.cn/call-mirror，你也看一下，上面写的截止日期和主站一致吗？以哪个为准？", "req": ["web_fetch"]}],
       compute=compute, must=WEB, traps=["TR-WEBSTALE"], rc=5, notes="main 10/20; mirror 10/25 marked expired")


@reg
def c80():
    r = rng(80)
    a = ["日期,支出"] + ["2026-08-%02d,%d" % (r.randint(1, 28), r.randint(8, 70)) for _ in range(120)]
    b = ["日期,支出"] + ["2026-08-%02d,%d" % (r.randint(1, 28), r.randint(8, 70)) for _ in range(45)]
    files = {"账本/餐饮.csv": "\n".join(a) + "\n", "账本/交通.csv": "\n".join(b) + "\n"}

    def compute(files, web):
        f = lambda p: sum(int(l.split(",")[1]) for l in files[p].splitlines()[1:])
        x, y = f("账本/餐饮.csv"), f("账本/交通.csv")
        return {}, [list(dict.fromkeys([str(x), "{:,}".format(x)])), list(dict.fromkeys([str(x + y), "{:,}".format(x + y)]))]
    mk("hyb-33380", sub="multi", desc="Food spending total, then the user remembers a second ledger file and wants the combined total", files=files,
       turns=[{"p": "账本/餐饮.csv 里 8 月餐饮支出一共多少？", "any": True},
              {"p": "我想起来还有个 账本/交通.csv 也是 8 月的，两个加在一起一共多少？", "any": True}],
       compute=compute, must=["bash", "read_file", "calculator"], traps=["TR-MULTISRC"], rc=5, notes="sum1 then sum1+sum2")
