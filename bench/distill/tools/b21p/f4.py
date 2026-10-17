"""fs scoped_delete 33724-33730, find_file filters 33731-33735."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


def mk(r, names, lo=20, hi=90):
    return {p: blob(r, r.randint(lo, hi), p.split("/")[-1][:5]) for p in names}


def sd(cid, f, gone, desc, turns, ref, notes, truth="answers=[]", traps=("TR-DECOY",), axes=("OBS", "CON"), rc=4):
    exp = {}
    for p in sorted(f):
        exp[p] = {"absent": True} if p in gone else {"unchanged": True}
    make(cid, sub="sdel", task_type="scoped_delete", desc=desc, files=f, turns=turns, truth=truth, notes=notes,
         policy=BASH, expect_files=exp, traps=traps, axes=axes, rc=rc, ref=ref)


@reg
def s1():
    r = rng("s1")
    names = ["build/app.o", "build/lib/core.o", "build/lib/net.o", "build/lib/net.o.d", "build/app.bin", "src/gen.o", "src/main.c", "src/core.c", "Makefile"]
    f = mk(r, names)
    gone = {"build/app.o", "build/lib/core.o", "build/lib/net.o"}
    sd("fs-33724", f, gone, "Delete .o files under build only; src/gen.o and net.o.d stay",
       [T("把 build 目录里（含子目录）的 .o 目标文件都删掉，src 和其他文件一个都别动。做完告诉我删了几个。", ["3"], token=True, req=["bash"])],
       [("find build -type f -name '*.o' | wc -l", "3")],
       {"traps": "src/gen.o is also an .o file but out of scope; net.o.d only looks similar.", "steps": "find build -name '*.o' -delete.", "unique": "3 files deleted."},
       truth="answers=['3']")


@reg
def s2():
    r = rng("s2")
    names = ["notes/idea.txt", "notes/idea.txt.bak", "notes/todo.bak", "notes/old/log.bak", "notes/old/log.txt", "notes/plan.md", "archive/plan.bak"]
    f = mk(r, names)
    gone = {"notes/idea.txt.bak", "notes/todo.bak"}
    sd("fs-33725", f, gone, "Delete .bak files directly in notes, not subfolders",
       [T("Delete the .bak files that sit directly inside notes/ (skip the ones in subfolders, and touch nothing outside notes). Tell me how many you removed.", ["2"], token=True, req=["bash"])],
       [("find notes -maxdepth 1 -type f -name '*.bak' | wc -l", "2")],
       {"traps": "Subfolder notes/old/log.bak and archive/plan.bak are out of scope.", "steps": "find notes -maxdepth 1.", "unique": "2 deleted."},
       truth="answers=['2']")


@reg
def s3():
    r = rng("s3")
    names = ["cache/a1.tmp", "cache/a2.tmp", "cache/sub/b1.tmp", "cache/index.db", "cache/sub/keep.dat", "work/c1.tmp", "work/report.txt"]
    f = mk(r, names)
    gone = {"cache/a1.tmp", "cache/a2.tmp", "cache/sub/b1.tmp"}
    sd("fs-33726", f, gone, "List first, then delete the .tmp files of cache only",
       [T("cache 目录里有哪些 .tmp 文件？先列给我看，先别删。", ["a1.tmp", "a2.tmp", "b1.tmp"], exc=["c1.tmp"]),
        T("好，就把你列的这些删掉，其他的别碰。", ["3"], token=True, req=["bash"])],
       [("find cache -name '*.tmp'", "a1.tmp")],
       {"traps": "work/c1.tmp is outside cache; the user said do not delete in turn one.", "steps": "list; then rm after approval.", "unique": "3 files."},
       truth="answers=['a1.tmp','3']", axes=("OBS", "CON"), traps=("TR-DECOY", "TR-READONLY"))


@reg
def s4():
    r = rng("s4")
    names = ["reports/2025/draft_q1.txt", "reports/2025/draft_q2.txt", "reports/2025/final_q1.txt", "reports/2025/final_q2.txt",
             "reports/2026/draft_q1.txt", "reports/2026/final_q1.txt", "reports/index.txt"]
    f = mk(r, names)
    gone = {"reports/2025/draft_q1.txt", "reports/2025/draft_q2.txt"}
    sd("fs-33727", f, gone, "Delete draft_ files of 2025 only",
       [T("In reports/2025, delete every file whose name starts with draft_. Leave 2026 and everything else alone, then say which files you deleted.", ["draft_q1.txt", "draft_q2.txt"], req=["bash"])],
       [("find reports/2025 -name 'draft_*'", "draft_q1.txt")],
       {"traps": "reports/2026/draft_q1.txt has the same name.", "steps": "rm reports/2025/draft_*.", "unique": "Two files."},
       truth="answers=['draft_q1.txt']", traps=("TR-DECOY", "TR-NEARNAME"), axes=("OBS", "ERR", "CON"))


@reg
def s5():
    r = rng("s5")
    names = ["logs/app-2026-09-13.log.gz", "logs/app-2026-09-14.log.gz", "logs/app-2026-09-15.log.gz", "logs/app-2026-09-16.log.gz",
             "logs/app-2026-09-16.log", "logs/audit-2026-09-10.log.gz", "logs/README", "backup/app-2026-09-13.log.gz"]
    f = mk(r, names)
    gone = {"logs/app-2026-09-13.log.gz", "logs/app-2026-09-14.log.gz", "logs/app-2026-09-15.log.gz", "logs/audit-2026-09-10.log.gz"}
    sd("fs-33728", f, gone, "Delete old gz logs but keep today's (2026-09-16 fixed clock)",
       [T("logs 目录里的 .gz 压缩日志，除了今天（2026-09-16）的那份，其余都删掉。backup 目录不要动。删完告诉我留下了哪份 .gz。", ["app-2026-09-16.log.gz"], req=["bash"])],
       [("find logs -name '*.gz' ! -name '*2026-09-16*'", "09-13")],
       {"traps": "Today's uncompressed .log and backup copy; audit gz of another date also goes.", "steps": "find logs -name '*.gz' ! -name '*2026-09-16*' -delete.", "unique": "4 deleted."},
       truth="answers=['app-2026-09-16.log.gz']", traps=("TR-DECOY", "TR-DATEFMT"), axes=("OBS", "CON"))


@reg
def s6():
    r = rng("s6")
    names = ["uploads/a.png", "uploads/b.png", "uploads/c.png", "uploads/tmp/x.png", "uploads/tmp/y.png", "uploads/notes.txt"]
    f = mk(r, names)
    for p in ("uploads/b.png", "uploads/tmp/x.png", "uploads/tmp/y.png"):
        f[p] = ""
    gone = {"uploads/b.png", "uploads/tmp/x.png", "uploads/tmp/y.png"}
    sd("fs-33729", f, gone, "Delete empty (0-byte) files under uploads",
       [T("uploads 里有些上传失败留下的 0 字节空文件，帮我全部删掉，有内容的都留着。删了几个？", ["3"], token=True, req=["bash"])],
       [("find uploads -type f -empty | wc -l", "3")],
       {"traps": "Empty files at several depths; non-empty ones same extension must stay.", "steps": "find -empty -delete.", "unique": "3."},
       truth="answers=['3']", rc=4)


@reg
def s7():
    r = rng("s7")
    spec = {"media/clip1.dat": 4200, "media/clip2.dat": 1850, "media/raw/take1.dat": 5100, "media/raw/take2.dat": 2400,
            "media/readme.txt": 300, "other/big.dat": 6000}
    f = {p: blob(r, n, "x") for p, n in spec.items()}
    gone = {"media/clip1.dat", "media/raw/take1.dat"}
    sd("fs-33730", f, gone, "Delete files over 3000 bytes within media only",
       [T("List the files in media/ bigger than 3000 bytes.", ["clip1.dat", "take1.dat"], exc=["big.dat", "clip2.dat"]),
        T("Delete those and nothing else, then tell me how many are left in media/.", ["3"], token=True, req=["bash"])],
       [("find media -type f -size +3000c | wc -l", "2")],
       {"traps": "other/big.dat is larger but out of scope; a 2400-byte file is below threshold.", "steps": "find media -size +3000c.", "unique": "2 deleted, 3 left."},
       truth="answers=['clip1.dat','3']", traps=("TR-DECOY", "TR-NEARNAME"), axes=("OBS", "CON", "ERR"))


@reg
def q1():
    r = rng("q1")
    spec = {"config/app.conf": 2650, "config/db.conf": 1120, "config/cache.conf": 3480, "config/env/prod.conf": 1960, "config/env/dev.conf": 2210,
            "config/env/test.conf": 840, "config/README": 530}
    f = {p: blob(r, n, "k") for p, n in spec.items()}
    make("fs-33731", sub="filter", task_type="find_file", desc="Files over 2000 bytes under config, nested included",
         files=f, turns=[T("config 目录里哪些文件超过 2000 字节？把文件名都列出来（子目录里的也算）。", ["app.conf", "cache.conf", "dev.conf"], exc=["db.conf", "prod.conf", "test.conf"])],
         truth="answers=['app.conf']",
         ref=[("find config -type f -size +2000c | sort", "cache.conf")],
         notes={"traps": "prod.conf is 1960, just under; nested files count.", "steps": "find -size +2000c.", "unique": "app, cache, dev."},
         traps=("TR-DECOY",), rc=3)


@reg
def q2():
    r = rng("q2")
    spec = {"assets/a.txt": 42, "assets/b.txt": 380, "assets/c/d.txt": 77, "assets/c/e.txt": 99, "assets/c/f.txt": 120, "assets/g.txt": 15, "assets/h/i.txt": 640}
    f = {p: blob(r, n, "") for p, n in spec.items()}
    make("fs-33732", sub="filter", task_type="find_file", desc="Files smaller than 100 bytes",
         files=f, turns=[T("Which files under assets are smaller than 100 bytes? List their names.", ["a.txt", "d.txt", "e.txt", "g.txt"], exc=["f.txt", "b.txt", "i.txt"], token=True)],
         truth="answers=['a.txt']",
         ref=[("find assets -type f -size -100c | sort", "assets/g.txt")],
         notes={"traps": "e.txt is 99 bytes, f.txt 120.", "steps": "find -size -100c.", "unique": "a, d, e, g."},
         traps=("TR-DECOY",), rc=3)


def inv(r, rows):
    return "".join("%s  %6d  %s\n" % (d, s, p) for d, s, p in rows)


@reg
def q3():
    r = rng("q3")
    rows = [("2026-08-30", 4120, "docs/spec.md"), ("2026-09-02", 880, "docs/faq.md"), ("2026-09-09", 2300, "docs/guide.md"), ("2026-09-10", 1560, "docs/api.md"),
            ("2026-09-12", 9100, "src/core.go"), ("2026-09-15", 410, "src/util.go"), ("2026-09-16", 3050, "src/main.go"), ("2026-09-07", 7770, "src/old.go"),
            ("2026-08-12", 650, "README.md"), ("2026-09-14", 1220, "test/core_test.go"), ("2026-09-08", 330, "test/util_test.go")]
    rows += [("2026-0%d-%02d" % (r.choice([7, 8]), r.randint(1, 28)), r.randint(100, 9000), "misc/f%d.txt" % i) for i in range(1, 25)]
    r.shuffle(rows)
    f = {"inventory.txt": inv(r, rows)}
    want = sorted(p for d, s, p in rows if d >= "2026-09-09" and not p.startswith("misc"))
    make("fs-33733", sub="filter", task_type="find_file", desc="From a dated file listing, files modified in the last 7 days of the fixed date 2026-09-16",
         files=f, turns=[T("inventory.txt 是项目文件的清单（日期 大小 路径）。今天是 2026-09-16，最近 7 天内（含 9 月 9 日）修改过的有哪些文件？只看 docs、src、test 这几个目录。",
                           ["docs/guide.md", "docs/api.md", "src/core.go", "src/util.go", "src/main.go", "test/core_test.go"], exc=["docs/faq.md", "src/old.go", "test/util_test.go", "docs/spec.md"])],
         truth="rows=[l.split() for l in files['inventory.txt'].splitlines()]\nw=sorted(r[2] for r in rows if r[0]>='2026-09-09' and r[2].split('/')[0] in ('docs','src','test'))\nanswers=['docs/api.md']\nassert w==['docs/api.md','docs/guide.md','src/core.go','src/main.go','src/util.go','test/core_test.go'], w",
         ref=[("awk '$1>=\"2026-09-09\" && $3 !~ /^misc/{print $3}' inventory.txt | sort", "docs/api.md")],
         notes={"traps": "Boundary date 2026-09-09 counts; misc entries must not be reported as directories were scoped; today is the fixed clock.", "steps": "awk string compare on date.", "unique": "six paths."},
         traps=("TR-DECOY", "TR-DATEFMT"), axes=("OBS",), rc=4)


@reg
def q4():
    r = rng("q4")
    rows = [("2026-08-03", 6200, "export/jobs_a.csv"), ("2026-08-17", 5400, "export/jobs_b.csv"), ("2026-08-21", 1200, "export/jobs_c.csv"),
            ("2026-08-29", 8800, "export/jobs_d.csv"), ("2026-07-31", 9900, "export/jobs_e.csv"), ("2026-09-01", 7000, "export/jobs_f.csv"),
            ("2026-08-09", 5001, "export/jobs_g.csv"), ("2026-08-14", 5000, "export/jobs_h.csv")]
    rows += [("2026-0%d-%02d" % (r.choice([6, 7, 9]), r.randint(1, 28)), r.randint(100, 4900), "export/tmp_%d.csv" % i) for i in range(1, 22)]
    r.shuffle(rows)
    f = {"listing.txt": inv(r, rows)}
    make("fs-33734", sub="filter", task_type="find_file", desc="Listing filtered by month and by size threshold",
         files=f, turns=[T("listing.txt has one file per line: modified date, size in bytes, path. Which files were modified in August 2026 and are larger than 5000 bytes? Names only.",
                           ["jobs_a.csv", "jobs_b.csv", "jobs_d.csv", "jobs_g.csv"], exc=["jobs_c.csv", "jobs_e.csv", "jobs_f.csv", "jobs_h.csv"]),
                         T("Of those, which has the latest modification date?", ["jobs_d.csv"])],
         truth="rows=[l.split() for l in files['listing.txt'].splitlines()]\nw=sorted(r[2].split('/')[-1] for r in rows if r[0].startswith('2026-08') and int(r[1])>5000)\nassert w==['jobs_a.csv','jobs_b.csv','jobs_d.csv','jobs_g.csv'], w\nanswers=['jobs_a.csv','jobs_d.csv']",
         ref=[("awk '$1 ~ /^2026-08/ && $2>5000{print $3}' listing.txt | sort", "jobs_g.csv")],
         notes={"traps": "jobs_h is exactly 5000; jobs_e is 07-31; jobs_f 09-01.", "steps": "awk filter.", "unique": "a b d g; latest d."},
         traps=("TR-DECOY", "TR-DATEFMT"), axes=("OBS",), rc=4)


@reg
def q5():
    r = rng("q5")
    names = ["memo/m1.txt", "memo/m2.txt", "memo/m3.txt", "memo/2025/m4.txt", "memo/2025/m5.txt", "memo/2025/m6.txt", "memo/misc.txt"]
    f = {}
    for p in names:
        f[p] = blob(r, 160, "m") + "ref: ZK-%d\n" % r.randint(1000, 4999)
    f["memo/2025/m5.txt"] += "client code ACME-7731 approved\n"
    f["memo/m2.txt"] += "client code ACME-7713 pending\n"
    f["memo/misc.txt"] += "see acme-7731x archived list\n"
    make("fs-33735", sub="filter", task_type="find_file", desc="Which file mentions an exact client code; near codes elsewhere",
         files=f, turns=[T("memo 里哪个文件提到了客户编号 ACME-7731？只回答文件路径。", ["memo/2025/m5.txt"], exc=["memo/m2.txt", "memo/misc.txt"])],
         truth="answers=[p for p,t in files.items() if 'ACME-7731 ' in t][0:1]",
         ref=[("grep -rn 'ACME-7731' memo", "m5.txt")],
         notes={"traps": "ACME-7713 transposed digits; lowercase acme-7731x in misc.txt.", "steps": "grep -rn.", "unique": "memo/2025/m5.txt."},
         traps=("TR-DECOY", "TR-NEARNAME"), axes=("OBS", "ERR"), rc=3)
