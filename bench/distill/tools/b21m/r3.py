"""33435-33440: more ambiguous edits (hyb) and read-only sums/counts/dates (hyb)."""
from p0 import clarify, reg

R = ("list_files", "read_file")
WF = ("list_files", "read_file", "write_file")
RB = ("list_files", "read_file", "bash")


@reg
def c33435():
    files = {"价目/标准版.csv": "item,price\n基础套餐,59\n加购包,15\n", "价目/专业版.csv": "item,price\n基础套餐,129\n加购包,25\n"}
    clarify("nt-33435", files=files, p1="把基础套餐的价格改成 99。", p2="专业版。", stems=["标准版", "专业版"], must=WF,
            rules={"价目/专业版.csv": ("sub", "基础套餐,129", "基础套餐,99")},
            desc="Asks to set the basic plan price to 99 when standard and pro price lists both have that item", ref="两份价目表都有基础套餐，追问哪份；专业版改成 99。")


@reg
def c33436():
    files = {"tools/cli/README.md": "# cli\nAuthor: Wu Qiang\n", "tools/server/README.md": "# server\nAuthor: Wu Qiang\n"}
    clarify("nt-33436", files=files, p1="把 README 里的作者名更新为林夏。", p2="两个都改。", stems=["cli", "server"], must=WF,
            rules={"tools/cli/README.md": ("sub", "Wu Qiang", "林夏"), "tools/server/README.md": ("sub", "Wu Qiang", "林夏")},
            desc="Asks to update the author in 'the README' when cli and server each have one; the user then says both",
            ref="两个 README，追问哪个；用户答两个都改，两个都改。")


@reg
def c33437():
    files = {"docs/intro-en.md": "# Intro\nYou will recieve a welcome email.\n", "docs/intro-draft.md": "# Intro (draft)\nSet up teh workspace first.\n"}
    clarify("nt-33437", files=files, p1="Fix the typo in the intro.", p2="The draft.", stems=["intro-en", "intro-draft"], must=WF,
            rules={"docs/intro-draft.md": ("sub", "teh workspace", "the workspace")},
            desc="Asks to fix 'the typo in the intro' when two intro files each carry a different typo", ref="Two intros each with a typo, ask which; fix only the draft's 'teh'.")


@reg
def c33438():
    t = [("机票", 1850), ("酒店", 1320), ("打车", 240), ("餐饮", 860)]
    o = [("打印", 135), ("咖啡机", 1280), ("文具", 96)]
    files = {"expenses/expenses-travel.csv": "item,amount\n" + "".join("%s,%d\n" % x for x in t),
             "expenses/expenses-office.csv": "item,amount\n" + "".join("%s,%d\n" % x for x in o)}
    clarify("nt-33438", files=files, p1="帮我算一下总额。", p2="办公的那份。", stems=["expenses-travel", "expenses-office"], must=RB, ans2=str(sum(a for _, a in o)),
            excl1=[str(sum(a for _, a in t)), str(sum(a for _, a in o))], excl2=[str(sum(a for _, a in t))],
            desc="Asks for 'the total' with travel and office expense sheets", ref="两份费用表，追问哪份；办公合计 1511。")


@reg
def c33439():
    be = "# Backend issues\n" + "".join("- [ ] issue %d\n" % i for i in range(1, 8)) + "- [x] done a\n- [x] done b\n"
    fe = "# Frontend issues\n" + "".join("- [ ] issue %d\n" % i for i in range(1, 14)) + "- [x] done a\n"
    files = {"issues/backend.md": be, "issues/frontend.md": fe}
    clarify("nt-33439", files=files, p1="How many open issues are there?", p2="Frontend.", stems=["backend", "frontend"], must=RB, ans2="13",
            desc="Asks how many issues are open without saying backend or frontend (7 vs 13 unchecked boxes)", ref="Two issue lists, ask which; frontend has 13 unchecked.")


@reg
def c33440():
    files = {"backup/backup-db.log": "2026-09-13 02:00 start\n2026-09-14 02:00 done size=3.1G\n", "backup/backup-files.log": "2026-09-08 03:30 start\n2026-09-09 03:41 done size=812M\n"}
    clarify("nt-33440", files=files, p1="帮我看看上次备份是哪天做的。", p2="文件备份。", stems=["backup-db", "backup-files"], must=R, ans2="2026-09-09",
            excl1=["2026-09-14", "2026-09-09"], excl2=["2026-09-14"],
            desc="Asks when 'the last backup' was done while db and files backups have separate logs", ref="两份备份日志，追问数据库还是文件；文件备份最后一次 2026-09-09。")
