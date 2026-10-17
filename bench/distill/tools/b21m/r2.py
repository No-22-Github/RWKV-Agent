"""33428-33434: ambiguous contacts/meetings/code (nt) and ambiguous edits (hyb)."""
from p0 import clarify, reg, ED

R = ("list_files", "read_file")
WF = ("list_files", "read_file", "write_file")


@reg
def c33428():
    files = {"联系人/王磊.md": "# 王磊（市场部）\n邮箱：leiwang@mkt.corp.example\n电话：5501\n", "联系人/王雷.md": "# 王雷（财务部）\n邮箱：wanglei@fin.corp.example\n电话：5620\n"}
    clarify("nt-33428", files=files, p1="帮我查一下小王的邮箱。", p2="市场部那个。", stems=["王磊", "王雷"], must=R, ans2="leiwang@mkt.corp.example",
            excl1=["leiwang@", "wanglei@"], excl2=["wanglei@fin"],
            desc="Asks for 'Xiao Wang's email' with two similarly named contacts in different departments", ref="两位姓王的联系人，追问是哪位（部门）；答市场部后给出 leiwang@mkt.corp.example。")


@reg
def c33429():
    files = {"meetings/2026-09-09-kickoff.md": "# Kickoff 09-09\nAttendees: Ana, Bo, Chen.\nDecision: scope frozen, ticket KO-1180 opened for infra.\n",
             "meetings/2026-09-12-review.md": "# Review 09-12\nAttendees: Ana, Dmitri.\nDecision: ship behind a flag; QA ticket QA-4471 assigned to Dmitri.\n"}
    clarify("nt-33429", files=files, p1="Give me the ticket id from the meeting notes.", p2="The review one.", stems=["kickoff", "review"], must=R, ans2="QA-4471",
            excl1=["KO-1180", "QA-4471"], excl2=["KO-1180"],
            desc="Asks for the ticket id from 'the meeting notes' when two meetings exist", ref="Two meeting notes, ask which one; review gives QA-4471.")


@reg
def c33430():
    files = {"utils/text_utils.py": "def normalize(s):\n    \"\"\"去掉首尾空白并把全角字符转成半角。\"\"\"\n    return s.strip()\n",
             "utils/num_utils.py": "def normalize(s):\n    \"\"\"去掉千分位逗号后转成 float。\"\"\"\n    return float(s.replace(',', ''))\n"}
    clarify("nt-33430", files=files, p1="normalize 这个函数是干嘛的？", p2="数字那个。", stems=["text_utils", "num_utils"], must=R, ans2="千分位",
            excl1=["千分位", "全角"], excl2=["全角"],
            desc="Asks what 'normalize' does when two modules define a function of that name", ref="两个模块都有 normalize，追问指哪个；数字那个去千分位转 float。")


@reg
def c33431():
    files = {"项目/项目A.md": "# 项目A\n负责人：陈楠\n状态：进行中\n", "项目/项目B.md": "# 项目B\n负责人：陈楠\n状态：筹备\n"}
    clarify("nt-33431", files=files, p1="把负责人改成赵敏。", p2="项目B。", stems=["项目A", "项目B"], must=WF,
            rules={"项目/项目B.md": ("sub", "负责人：陈楠", "负责人：赵敏")},
            desc="Asks to change the owner to Zhao Min when two project files both list the same owner", ref="两个项目都是陈楠，追问改哪个；用户答 B 后只改 项目B.md。")


@reg
def c33432():
    files = {"slides/deck-sales.md": "# Q3 Sales Review\n- revenue up 8%\n", "slides/deck-ops.md": "# Q3 Ops Review\n- uptime 99.9%\n"}
    clarify("nt-33432", files=files, p1="Change the title to 'Spring Launch'.", p2="The ops deck.", stems=["deck-sales", "deck-ops"], must=WF,
            rules={"slides/deck-ops.md": ("sub", "# Q3 Ops Review", "# Spring Launch")},
            desc="Asks to retitle 'the deck' with a sales deck and an ops deck", ref="Two decks, ask which; then retitle only deck-ops.md.")


@reg
def c33433():
    files = {"tasks/任务-登录.md": "# 登录改造\n截止：2026-09-20\n", "tasks/任务-支付.md": "# 支付对接\n截止：2026-09-25\n"}
    clarify("nt-33433", files=files, p1="把截止日期往后推一周。", p2="支付那个。", stems=["任务-登录", "任务-支付"], must=WF,
            rules={"tasks/任务-支付.md": ("sub", "2026-09-25", "2026-10-02")},
            desc="Asks to push 'the deadline' back a week with two task files each having one", ref="两个任务都有截止日，追问哪个；支付的改为 2026-10-02。")


@reg
def c33434():
    files = {"config/app.ini": "[main]\ndebug=true\nport=8000\n", "config/worker.ini": "[main]\ndebug=true\nthreads=4\n"}
    clarify("nt-33434", files=files, p1="Turn off the debug flag.", p2="Both of them.", stems=["app.ini", "worker.ini"], must=WF,
            rules={"config/app.ini": ("sub", "debug=true", "debug=false"), "config/worker.ini": ("sub", "debug=true", "debug=false")},
            desc="Asks to turn off 'the debug flag' with two ini files that both enable it; the user then says both",
            ref="Both files set debug=true, ask which; the user answers both, so both are edited.")
