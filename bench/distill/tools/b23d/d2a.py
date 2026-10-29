"""b23d D2 part a: 4-turn chains, ids 35236-35247."""
from common import mk, T, L

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c36():
    f = "config/atlas-queue.yaml"
    files = {f: L("queue: atlas", "workers: 4", "visibility_timeout_s: 30", "dead_letter_after: 5")}
    mk("hyb-35236", sub="D2", tt="undo", trap="TR-CLAIM", desc="Two edits, then revert only the first and recap with originals", files=files,
       turns=[T("What are workers and dead_letter_after in config/atlas-queue.yaml?", inc=["4", "5"]),
              T("Set workers to 8.", inc=["8"]),
              T("Now set dead_letter_after to 3.", inc=["3"]),
              T("Change of plan: put workers back to what it was, but keep the dead-letter change. Give me the final values and tell me what dead_letter_after was originally.", inc=["4", "3", "5"])],
       edits=[(f, "dead_letter_after: 5", "dead_letter_after: 3")], must=["read_file", "replace_lines", "write_file"], rc=6)


@reg
def c37():
    f = "文档/周六排班.txt"
    files = {f: L("早班：小林、阿杰", "晚班：老周、小美", "机动：陈姐")}
    mk("hyb-35237", sub="D2", tt="multi", trap="TR-CLAIM", desc="Shift swaps in several steps, then read out the schedule and the original morning pair", files=files,
       turns=[T("周六早班有谁？排班在 文档/周六排班.txt。", inc=["小林", "阿杰"]),
              T("阿杰请假，换成陈姐，机动班空出来写“待定”。", inc=["陈姐", "待定"]),
              T("晚班老周也请假，让阿杰顶上，他的假取消了。", inc=["阿杰"]),
              T("现在整个排班怎么安排的？念一遍。另外提醒我，最开始早班是哪两个人。", inc=["小林", "阿杰", "陈姐", "待定", "小美"])],
       edits=[(f, "早班：小林、阿杰", "早班：小林、陈姐"), (f, "晚班：老周、小美", "晚班：阿杰、小美"), (f, "机动：陈姐", "机动：待定")], must=["read_file", "replace_lines", "write_file"], rc=6)


@reg
def c38():
    f = "deploy/rollout-plan.md"
    files = {f: L("canary: 5%", "wave1: 25%", "wave2: 60%", "full: 100%")}
    mk("hyb-35238", sub="D2", tt="undo", trap="TR-CLAIM", desc="Staged edits rejected, then only one of them redone", files=files,
       turns=[T("What percent is wave1 in deploy/rollout-plan.md?", inc=["25"]),
              T("Make wave1 20% and wave2 50%."),
              T("I rejected that change. Do the plan values still show 25 and 60? Check the file.", inc=["25", "60"], review="reject"),
              T("Apply just the wave2 change this time (50%). Then summarize: what wave1 was at the start, what I first asked it to become, and what the file says now.", inc=["25", "20", "50"])],
       edits=[(f, "wave2: 60%", "wave2: 50%")], must=["read_file", "replace_lines", "write_file"], rc=6)


@reg
def c39():
    log, conf = "日志/推送服务.log", "配置/推送服务.conf"
    files = {log: L("10:21 ERROR 推送超时 阈值=4s", "10:25 INFO 重试成功"), conf: L("[push]", "timeout=4", "retries=2")}
    mk("hyb-35239", sub="D2", tt="comp", trap="TR-MULTISRC", desc="Read a threshold from a log, derive a config edit, adjust again, recap the history", files=files,
       turns=[T("推送服务日志里报错说的超时阈值是几秒？", inc=["4"]),
              T("把 配置/推送服务.conf 里的 timeout 调成日志里那个值的两倍，告诉我调成了多少。", inc=["8"]),
              T("调完之后又报了 8 秒才响应，所以直接改到 10 吧。", inc=["10"]),
              T("总结一下 timeout 的变化过程，从多少到多少再到多少，另外日志里最初说的阈值是几秒。", inc=["4", "8", "10"])],
       edits=[(conf, "timeout=4", "timeout=10")], vals=["8"], must=["read_file", "replace_lines", "write_file", "search_text"], rc=7)


@reg
def c40():
    n, out = "notes/design-review-0930.md", "notes/actions-0930.txt"
    files = {n: L("# Design review 0930", "ACTION: Ravi to benchmark cache layer by Fri", "ACTION: Mei to draft migration doc by Wed", "DECISION: use Postgres 16")}
    mk("hyb-35240", sub="D2", tt="write", trap="TR-CLAIM", desc="Extract action items into a new file, move a due date, append a follow-up, recall the decision and the old date", files=files,
       turns=[T("List the action items in notes/design-review-0930.md.", inc=["Ravi", "Mei"]),
              T("Put the action items in notes/actions-0930.txt, one per line, without the 'ACTION:' prefix."),
              T("Mei's due date moves to Thursday, so fix her line in that file."),
              T("Append Ravi's follow-up 'review results with Mei' as a new last line. Then tell me the decision recorded in the meeting notes and which day Mei's item was originally due.", inc=["Postgres 16", "Wed"])],
       adds=[(out, L("Ravi to benchmark cache layer by Fri", "Mei to draft migration doc by Thu", "review results with Mei"))], exact=[out],
       must=["read_file", "write_file", "replace_lines", "append_file"], rc=7)


@reg
def c41():
    f = "数据/会员价目.csv"
    files = {f: L("套餐,月费", "基础,29", "标准,59", "旗舰,129")}
    mk("hyb-35241", sub="D2", tt="multi", trap="TR-CLAIM", desc="Three price changes over three turns, then a recap of ups and downs with the original flagship price", files=files,
       turns=[T("旗舰套餐月费多少？表在 数据/会员价目.csv。", inc=["129"]),
              T("基础涨到 35。", inc=["35"]),
              T("标准涨到 69，旗舰降到 119。", inc=["69", "119"]),
              T("这三个套餐里几个涨价、几个降价？各变了多少？旗舰原来是多少？", inc=["129", "119"], any=["10", "6"])],
       edits=[(f, "基础,29", "基础,35"), (f, "标准,59", "标准,69"), (f, "旗舰,129", "旗舰,119")], must=["read_file", "replace_lines", "write_file"], rc=6)


@reg
def c42():
    f = "src/feature_gates.ts"
    files = {f: L("export const gates = {", "  newSearch: false,", "  legacyExport: true,", "  betaChat: false,", "};")}
    mk("hyb-35242", sub="D2", tt="undo", trap="TR-CLAIM", desc="Toggle two gates, revert only the first, list final state and everything touched", files=files,
       turns=[T("Which gates are currently off in src/feature_gates.ts?", inc=["newSearch", "betaChat"]),
              T("Enable newSearch.", inc=["newSearch"]),
              T("Disable legacyExport.", inc=["legacyExport"]),
              T("I changed my mind about the first one, so revert only newSearch. Then list the final state of all gates and everything I asked you to touch.", inc=["newSearch", "legacyExport", "betaChat"])],
       edits=[(f, "legacyExport: true", "legacyExport: false")], must=["read_file", "replace_lines", "write_file"], rc=6)


@reg
def c43():
    bank, led = "数据/收入-银行.txt", "数据/收入-账本.txt"
    files = {bank: L("10-07 3200", "10-08 4580", "10-09 1260"), led: L("10-07 3200", "10-08 4850", "10-09 1260")}
    mk("hyb-35243", sub="D2", tt="comp", trap="TR-MULTISRC", desc="Compare a bank statement with a ledger, fix the ledger to match, report the difference", files=files,
       turns=[T("银行流水里 10 月 8 日那笔金额是多少？", inc=["4580"]),
              T("账本里同一天那笔呢？", inc=["4850"]),
              T("以银行流水为准，把账本改过来。", inc=["4580"]),
              T("账本原来记错了多少？原来记的是多少？", inc=["4850"], any=["270"])],
       edits=[(led, "10-08 4850", "10-08 4580")], must=["read_file", "replace_lines", "write_file", "calculator"], rc=6)


@reg
def c44():
    f = "finance/q4-budget.md"
    files = {f: L("Engineering: 52000", "Marketing: 18000", "Travel: 7500", "Tools: 4200")}
    mk("hyb-35244", sub="D2", tt="comp", trap="TR-CLAIM", desc="Budget total, a percentage raise, a cut, then net change versus the original", files=files,
       turns=[T("What's the total budget in finance/q4-budget.md?", any=["81700", "81,700"]),
              T("Raise Marketing by 15% and tell me the new Marketing figure.", any=["20700", "20,700"]),
              T("Cut Travel by 400 and tell me the new total.", any=["84000", "84,000"]),
              T("What is the net change versus the original total, and what was the original total?", any=["2300", "2,300", "81700", "81,700"])],
       edits=[(f, "Marketing: 18000", "Marketing: 20700"), (f, "Travel: 7500", "Travel: 7100")], vals=["20700"], must=["read_file", "replace_lines", "write_file", "calculator"], rc=6, dep="original total 81700 from turn 1")


@reg
def c45():
    f = "清单/读书会书单.txt"
    files = {f: L("《活着》", "《百年孤独》", "《三体》")}
    mk("hyb-35245", sub="D2", tt="multi", trap="TR-CLAIM", desc="Append two books over two turns, remove one, report final list and the initial count", files=files,
       turns=[T("书单里现在有几本？文件是 清单/读书会书单.txt。", inc=["3"]),
              T("追加《平凡的世界》。"),
              T("再追加《围城》，然后告诉我现在一共几本。", inc=["5"]),
              T("《百年孤独》大家都读过了，从书单划掉。告诉我最后书单里是哪几本，以及最开始是几本。", inc=["活着", "三体", "平凡的世界", "围城", "3"])],
       edits=[(f, "《百年孤独》\n", "")], adds=[(f, L("《平凡的世界》", "《围城》"))], must=["read_file", "append_file", "replace_lines", "write_file"], rc=6)


@reg
def c46():
    f = "scripts/nightly.cron"
    files = {f: L("0 2 * * * backup.sh", "30 3 * * * rotate-logs.sh", "0 4 * * 0 vacuum-db.sh")}
    mk("hyb-35246", sub="D2", tt="multi", trap="TR-CLAIM", desc="Reschedule jobs across turns with an accept in the middle; recall the original backup hour", files=files,
       turns=[T("What time does the backup run in scripts/nightly.cron?", any=["2:00", "02:00", "0 2", "2 AM", "2am", "2 a.m."]),
              T("Move the backup to 01:00."),
              T("I accepted that. Now move log rotation to 02:30 and tell me which job runs first each night.", inc=["backup"], review="accept"),
              T("Give me the nightly schedule as a short list, and remind me what time the backup used to run.", any=["2:00", "02:00", "0 2", "2 AM", "2am", "2 a.m."], inc=["rotate-logs", "vacuum-db"])],
       edits=[(f, "0 2 * * * backup.sh", "0 1 * * * backup.sh"), (f, "30 3 * * * rotate-logs.sh", "30 2 * * * rotate-logs.sh")], must=["read_file", "replace_lines", "write_file"], rc=6,
       dep="original backup time 02:00")


@reg
def c47():
    f = "配置/告警阈值.ini"
    files = {f: L("[alert]", "cpu = 80", "mem = 75", "disk = 90")}
    mk("hyb-35247", sub="D2", tt="undo", trap="TR-CLAIM", desc="Two staged edits rejected together, then only the second redone", files=files,
       turns=[T("把 配置/告警阈值.ini 里的 cpu 阈值调到 70。"),
              T("mem 阈值调到 65，然后告诉我这两项现在各是多少。", inc=["70", "65"]),
              T("这两个改动我都拒绝了，没保存。现在 cpu 和 mem 阈值是多少？", inc=["80", "75"], review="reject"),
              T("只把 mem 改成 65，cpu 保持不动。然后告诉我 cpu 最初是多少、我最先想把它改成多少。", inc=["80", "70"])],
       edits=[(f, "mem = 75", "mem = 65")], must=["read_file", "replace_lines", "write_file"], rc=7)
