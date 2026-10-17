"""fs largest 33701-33706, duplicates 33707-33712."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


def sized(r, spec):
    return {p: blob(r, n, tag=p.split("/")[-1][:6]) for p, n in spec.items()}


BIG = "find . -type f -printf '%s %p\\n' | sort -rn | head -3"


@reg
def l1():
    r = rng("l1")
    spec = {"assets/icons/logo.svg": 1830, "assets/icons/spinner.svg": 940, "assets/fonts/body.woff": 6420,
            "assets/fonts/mono.woff": 5870, "assets/img/hero/banner_wide.png": 9650, "assets/img/thumb_01.png": 2310,
            "assets/img/thumb_02.png": 2290, "assets/readme.txt": 410, "assets/css/site.css": 3770}
    f = sized(r, spec)
    make("fs-33701", sub="largest", task_type="largest", desc="Largest file in a nested asset tree, then the runner-up size",
         files=f, turns=[T("assets 目录里（包括所有子目录）哪个文件最大？只回答文件名。", ["banner_wide.png"], exc=["site.css", "body.woff"]),
                         T("第二大的是哪个，多少字节？", ["body.woff"], any_=[], )],
         truth="answers=[max(files, key=lambda p: len(files[p].encode())).split('/')[-1], sorted(files, key=lambda p: -len(files[p].encode()))[1].split('/')[-1]]",
         ref=[(BIG, "9650 ./assets/img/hero/banner_wide.png")], lazy=[("ls -S assets | head -1", "empty")] if False else [],
         notes={"traps": "Biggest file is three levels deep; ls on the top directory shows only css/fonts/icons/img/readme.", "steps": "find -printf sizes | sort -rn.", "unique": "banner_wide.png 9650 bytes, body.woff 6420."},
         traps=("TR-DECOY",), rc=3)


@reg
def l2():
    r = rng("l2")
    spec = {"exports/2026-q1/orders.csv": 7310, "exports/2026-q1/refunds.csv": 1480, "exports/2026-q2/orders.csv": 8895,
            "exports/2026-q2/refunds.csv": 1620, "exports/archive/orders_old.csv": 8120, "exports/archive/notes.md": 530,
            "exports/summary.json": 9340, "exports/schema.sql": 2050}
    f = sized(r, spec)
    make("fs-33702", sub="largest", task_type="largest", desc="Largest csv in exports where a json is bigger and two csv share a name",
         files=f, turns=[T("exports 里最大的 csv 文件是哪个？给出完整路径。", ["exports/2026-q2/orders.csv"], exc=["summary.json 是最大", "exports/archive/orders_old.csv 是最大"])],
         truth="answers=[max((p for p in files if p.endswith('.csv')), key=lambda p: len(files[p].encode()))]",
         ref=[("find exports -name '*.csv' -printf '%s %p\\n' | sort -rn | head -2", "8895 exports/2026-q2/orders.csv")],
         notes={"traps": "summary.json is bigger than every csv; orders.csv appears in two quarter directories so the bare name is ambiguous.", "steps": "find -name '*.csv' -printf.", "unique": "Q2 orders.csv 8895 bytes."},
         traps=("TR-DECOY", "TR-NEARNAME"), axes=("OBS", "ERR"), rc=3)


@reg
def l3():
    r = rng("l3")
    spec = {"site/index.html": 2780, "site/about.html": 1930, "site/css/main.css": 4410, "site/js/app.js": 6015,
            "site/js/vendor/chart.min.js": 9870, "site/js/vendor/dom.min.js": 3340, "site/.cache/render.tmp": 12460,
            "site/img/team.jpg": 7120}
    f = sized(r, spec)
    make("fs-33703", sub="largest", task_type="largest", desc="Largest file including a hidden cache directory",
         files=f, turns=[T("Which is the largest file under site/, hidden folders included? Give its path.", ["render.tmp"], exc=["chart.min.js is the largest", "chart.min.js is largest"]),
                         T("And the largest one that is not inside a hidden folder?", ["chart.min.js"])],
         truth="answers=[max(files, key=lambda p: len(files[p].encode())).split('/')[-1], max((p for p in files if '/.' not in p), key=lambda p: len(files[p].encode())).split('/')[-1]]",
         ref=[("find site -type f -printf '%s %p\\n' | sort -rn | head -2", "12460 site/.cache/render.tmp")],
         lazy=[("ls -S site/*/ | head -1", "err")] if False else [],
         notes={"traps": "The biggest file is in .cache, which plain ls and shell globs skip.", "steps": "find lists dotted dirs.", "unique": "render.tmp 12460; excluding hidden, chart.min.js 9870."},
         traps=("TR-DECOY",), rc=3)


@reg
def l4():
    r = rng("l4")
    spec = {"backup/db/dump_mon.sql": 5210, "backup/db/dump_tue.sql": 5390, "backup/db/dump_wed.sql": 5880, "backup/db/dump_thu.sql": 5640,
            "backup/files/photos.idx": 3120, "backup/files/docs.idx": 2070, "backup/logs/run.log": 4310, "backup/MANIFEST": 760}
    f = sized(r, spec)
    make("fs-33704", sub="largest", task_type="largest", desc="Top three files by size, ranked, with sizes",
         files=f, turns=[T("backup 里最大的三个文件是哪几个？按从大到小排，写出文件名和字节数。", ["dump_wed.sql", "dump_thu.sql", "dump_tue.sql"], exc=["dump_mon.sql 排第"]),
                         ]
         , truth="s=sorted(files,key=lambda p:-len(files[p].encode()))[:3]\nanswers=[s[0].split('/')[-1]]",
         ref=[(BIG, "5880 ./backup/db/dump_wed.sql")],
         notes={"traps": "Four near-equal dumps; order matters.", "steps": "find -printf | sort -rn | head -3.", "unique": "wed 5880, thu 5640, tue 5390."},
         traps=("TR-DECOY",), rc=3)


@reg
def l5():
    r = rng("l5")
    spec = {"src/core/engine.go": 5230, "src/core/engine_test.go": 7410, "src/core/types.go": 1260, "src/net/client.go": 4980,
            "src/net/client_test.go": 3110, "docs/design.md": 8830, "vendor/lib/big_table.go": 11250, "src/main.go": 940}
    f = sized(r, spec)
    make("fs-33705", sub="largest", task_type="largest", desc="Largest file inside src only, bigger files exist outside",
         files=f, turns=[T("只看 src 目录（含子目录），最大的文件是哪个？再告诉我它有多少字节。", ["engine_test.go"], exc=["big_table.go 是最大"]),
                         T("那 src 里最大的不含测试文件（_test.go 结尾）的是哪个？", ["engine.go"])],
         truth="s=[p for p in files if p.startswith('src/')]\nm=max(s,key=lambda p:len(files[p].encode()))\nm2=max((p for p in s if not p.endswith('_test.go')),key=lambda p:len(files[p].encode()))\nanswers=[m.split('/')[-1],m2.split('/')[-1]]",
         ref=[("find src -type f -printf '%s %p\\n' | sort -rn | head -2", "7410 src/core/engine_test.go")],
         notes={"traps": "vendor and docs hold larger files outside src; engine.go vs engine_test.go near names.", "steps": "find src -printf.", "unique": "engine_test.go 7410; then engine.go 5230."},
         traps=("TR-DECOY", "TR-NEARNAME"), axes=("OBS", "ERR"), rc=3)


@reg
def l6():
    r = rng("l6")
    spec = {"mail/inbox/a1.eml": 1530, "mail/inbox/a2.eml": 2210, "mail/inbox/a3.eml": 880, "mail/sent/b1.eml": 3340,
            "mail/sent/b2.eml": 1870, "mail/drafts/c1.eml": 2960, "mail/trash/d1.eml": 3995, "mail/trash/d2.eml": 640}
    f = sized(r, spec)
    make("fs-33706", sub="largest", task_type="largest", desc="Largest message overall vs outside the trash folder",
         files=f, turns=[T("mail 里哪封邮件占的空间最大？", ["d1.eml"]),
                         T("不算 trash 的话呢？", ["b1.eml"])],
         truth="answers=[max(files,key=lambda p:len(files[p].encode())).split('/')[-1], max((p for p in files if '/trash/' not in p),key=lambda p:len(files[p].encode())).split('/')[-1]]",
         ref=[("find mail -type f -printf '%s %p\\n' | sort -rn | head -2", "3995 mail/trash/d1.eml")],
         notes={"traps": "The biggest file is in trash; second question changes scope.", "steps": "find -printf, then filter.", "unique": "d1.eml 3995; without trash b1.eml 3340."},
         traps=("TR-DECOY",), rc=3)


