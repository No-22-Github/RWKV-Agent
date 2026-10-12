"""M9 (bash) half of the v1.41 b12b batch: ids 9061-9070.

M9a multi-file aggregation (4), M9d missing-command recovery (3), M9e bash offered but the answer is a
reply (3). Shapes follow ../b12a/m9.py: a README pins the matching rule, a look-alike value is the decoy,
the reference solution is checked in the just-bash sidecar."""
import json
from random import Random

from common import lines, write_case

REFS = {}


def has(*needles):
    return lambda out, _root: None if all(n in out for n in needles) else "ref stdout %r lacks %s" % (out[:200], needles)


def thousands(value):
    whole, _, frac = value.partition(".")
    grouped = f"{int(whole):,}" + ("." + frac if frac else "")
    return [value] if grouped == value else [value, grouped]


def literal_free(files, value):
    return not any(str(value) in text for text in files.values())


def money(c):
    return f"{c // 100}.{c % 100:02d}"


def agg(cid, *, seed, topic, desc, root, names, header, target, decoy_status, other_statuses, prompt, readme, readme_path,
        unit, trap_multi, mode="sum", axes=("CHN", "OBS")):
    """Region tables `root/<name>.csv` with columns (id, status, amount). mode sum -> total amount of rows whose status
    is exactly `target`; mode count -> number of such rows."""
    for attempt in range(200):
        rng = Random(seed + attempt * 7919)
        files, ans, first, sub, everything = {}, 0, 0, 0, 0
        for index, name in enumerate(names):
            rows = [",".join(header)]
            for i in range(rng.randint(40, 70)):
                status = rng.choice([target, target, decoy_status] + other_statuses)
                cents = rng.randint(2000, 98000)
                rows.append(f"{name[0]}{i:03d},{status},{money(cents)}")
                hit = status == target
                add = cents if mode == "sum" else 1
                ans += add * hit
                first += add * hit * (index == 0)
                sub += add * (target in status)
                everything += add
            files[f"{root}/{name}.csv"] = lines(rows)
        value = money(ans) if mode == "sum" else str(ans)
        if literal_free(files, value) and ans > 0:
            break
    files[readme_path] = lines(readme)
    show = (lambda c: money(c)) if mode == "sum" else str
    cmd = ("cat %s/*.csv | awk -F, '$2==\"%s\" {s+=$3} END{printf \"%%.2f\\n\", s}'" % (root, target)) if mode == "sum" else \
          ("cat %s/*.csv | awk -F, '$2==\"%s\"' | wc -l" % (root, target))
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"][%r].startswith(%r)
total = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == %r, path
    for row in rows[1:]:
        ident, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == %r:
            total += (int(whole) * 100 + int(frac)) if %r == "sum" else 1
value = ("%%d.%%02d" %% (total // 100, total %% 100)) if %r == "sum" else str(total)
print(json.dumps({"expected_contains_any": [value, "{:,}".format(total // 100) + "." + "%%02d" %% (total %% 100)] if %r == "sum" else [value]}))
''' % (readme_path, readme[0], ",".join(header), target, mode, mode, mode)
    notes = f"""## Traps
- TR-MULTISRC: {len(names)} per-region tables; the first alone gives {show(first)}.
- TR-DECOY: 「{decoy_status}」 contains 「{target}」 as a substring; {readme_path} says the status is matched exactly, a substring match gives {show(sub)}.
- {trap_multi}

## Reference solution
1. bash: `{cmd}`
Final answer: {unit.format(v=value)}

## Why the answer is unique
The status is an exact field value, the README pins the criterion, all {len(names)} files are summed.
"""
    REFS[cid] = (files, [cmd], has(value))
    expect = {"output_contains_any": thousands(value) if mode == "sum" else [value], "output_contains_any_token": True,
              "max_output_chars": 600}
    return write_case(
        cid, desc=desc, task_type="count_events" if mode == "count" else "aggregate", family="fam-%s-b12b-%s-01" % (cid.split("-")[0], topic),
        level="L2", ref_calls=1, traps=["TR-MULTISRC", "TR-DECOY"],
        decoys={"TR-MULTISRC": show(first), "TR-DECOY": show(sub)}, axes=list(axes), files=files, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": expect}])


def tab_9061():
    return agg(
        "tab-9061", seed=9061, topic="freightsigned", desc="Sums freight of signed shipments across three regional tables where a look-alike status shares the word",
        root="运单/2026-09", names=["华东", "华南", "华北"], header=["运单", "状态", "运费"], target="已签收", decoy_status="部分已签收",
        other_statuses=["在途", "退回"], readme_path="运单/说明.md",
        readme=["# 运单说明", "", "每个大区一个文件，列：运单,状态,运费（元）。", "统计签收运费时，状态必须恰好是「已签收」；「部分已签收」尚未结算，不计入。"],
        prompt="九月三个大区的运单表里，已签收的运费一共多少元？口径见 运单/说明.md。", unit="九月已签收的运费合计 {v} 元（状态恰好是「已签收」，部分已签收不算）。",
        trap_multi="TR-DEFN: summing every row regardless of status is far higher.")


def tab_9062():
    return agg(
        "tab-9062", seed=9062, topic="expenseok", desc="Sums approved expense amounts across department tables where a look-alike status shares the prefix",
        root="报销/2026Q3", names=["研发部", "市场部", "运营部", "财务部"], header=["单号", "状态", "金额"], target="已通过", decoy_status="已通过待复核",
        other_statuses=["已驳回", "审批中"], readme_path="报销/说明.md",
        readme=["# 报销说明", "", "每个部门一个文件，列：单号,状态,金额（元）。", "已入账金额只算状态恰好是「已通过」的单据；「已通过待复核」还没有入账。"],
        prompt="三季度各部门的报销表里，已通过的单据金额合计是多少元？按 报销/说明.md 的口径。", unit="三季度已通过的报销金额合计 {v} 元（只算状态恰好是「已通过」的单据，待复核的不计）。",
        trap_multi="TR-DEFN: summing every row regardless of status is far higher.")


def log_9063():
    return agg(
        "log-9063", seed=9063, topic="jobsok", desc="Counts successful job runs across per-queue tables where a look-alike status shares the word",
        root="任务记录/2026-10", names=["batch", "stream", "report"], header=["任务", "状态", "耗时秒"], target="success", decoy_status="success-retry",
        other_statuses=["failed", "timeout"], readme_path="任务记录/说明.md",
        readme=["# 任务记录说明", "", "每个队列一个文件，列：任务,状态,耗时秒。", "统计成功次数时，状态必须恰好是 success；success-retry 表示重试后才成功，单独统计，不算在内。"],
        prompt="十月 batch、stream、report 三个队列的记录里，状态为 success 的任务一共有多少个？口径见 任务记录/说明.md。", unit="十月三个队列状态恰好是 success 的任务共 {v} 个（success-retry 另算）。",
        trap_multi="TR-DEFN: counting every row gives the total number of runs.", mode="count")


def tab_9064():
    return agg(
        "tab-9064", seed=9064, topic="stockin", desc="Sums stock received across warehouse tables where a look-alike movement type shares the prefix",
        root="库存/2026-09", names=["north", "south", "east", "harbor"], header=["item", "type", "qty"], target="in", decoy_status="in-void",
        other_statuses=["out", "adjust"], readme_path="库存/README.md",
        readme=["# Inventory ledgers", "", "One file per warehouse; columns item,type,qty (decimal units).", "Received stock counts rows whose type is exactly `in`; `in-void` rows reverse a receipt and are tracked separately."],
        prompt="Across the four warehouse ledgers for September, how many units were received in total? Use the criterion in 库存/README.md.",
        unit="Total received in September: {v} units (type exactly `in`; `in-void` reversals are not counted).",
        trap_multi="TR-DEFN: summing every row regardless of type is far higher.", axes=("OBS", "CHN"))


def make_case(cid, *, seed, topic, desc, names, unit_word, cols, target, decoy_status, other, report_label, prompt, fam_word):
    for attempt in range(100):
        rng = Random(seed + attempt * 7919)
        files, total, everything, substring = {}, 0, 0, 0
        for name in names:
            rows = [",".join(cols)]
            for i in range(rng.randint(35, 55)):
                status = rng.choice([target, target, decoy_status] + other)
                cents = rng.randint(2000, 98000)
                rows.append(f"{name[0]}{i:03d},{status},{money(cents)}")
                total += cents * (status == target)
                substring += cents * (target in status)
                everything += cents
            files[f"数据/{name}.csv"] = lines(rows)
        value = money(total)
        if literal_free(files, value):
            break
    files["Makefile"] = lines([
        "DATA := 数据", "", ".PHONY: report", "report:",
        "\t@cat $(DATA)/*.csv | awk -F, '$$2==\"%s\" {s+=$$3} END{printf \"%s %%.2f %s\\n\", s}'" % (target, report_label, unit_word)])
    cmd = r'''cat 数据/*.csv | awk -F, '$2=="%s" {s+=$3} END{printf "%%.2f\n", s}' ''' % target
    cmd = cmd.strip()
    verify = '''
import json
case = json.load(open("case.json"))
make = case["files"]["Makefile"]
assert make.startswith("DATA := 数据")
assert "$$2==\\"%s\\"" in make
cents = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == %r, path
    for row in rows[1:]:
        ident, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == %r:
            cents += int(whole) * 100 + int(frac)
value = f"{cents // 100}.{cents %% 100:02d}"
print(json.dumps({"expected_contains_any": [value, f"{cents // 100:,}.{cents %% 100:02d}"]}))
''' % (target, ",".join(cols), target)
    notes = f"""## Traps
- make is not installed, so `make report` exits 127; the recipe in the Makefile has to be reproduced by hand.
- TR-DECOY: 「{decoy_status}」 contains 「{target}」 as a substring; the recipe tests equality, a substring match gives {money(substring)}.
- TR-DEFN: summing every row gives {money(everything)}.

## Reference solution
1. bash: `make report` -> exit 127.
2. read_file Makefile: the recipe is `cat 数据/*.csv | awk -F, '$2=="{target}" {{...}}'` ($$ is make's escape for $).
3. bash: `{cmd}`
Final answer: make report 会输出「{report_label} {value} {unit_word}」（make 不可用，我按 Makefile 里的配方用 awk 复算：状态恰好是「{target}」的行）。

## Why the answer is unique
The recipe's filter and format are explicit in the Makefile.
"""
    REFS[cid] = (files, [cmd], has(value))
    return write_case(
        cid, desc=desc, task_type="reproduce_output", family=f"fam-scr-b12b-{topic}-01", level="L2", ref_calls=2,
        traps=["TR-DECOY", "TR-DEFN"], decoys={"TR-DECOY": money(substring), "TR-DEFN": money(everything)}, axes=["OBS", "ERR"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": {"output_contains_any": thousands(value), "output_contains_any_token": True, "max_output_chars": 600}}])


def scr_9065():
    return make_case(
        "scr-9065", seed=9065, topic="nomakepaid", desc="Asks for a make target's printed total in a sandbox without make; the recipe's exact-status filter must be reproduced",
        names=["线上", "门店", "批发"], unit_word="元", cols=["订单", "状态", "金额"], target="已支付", decoy_status="已支付待核销", other=["已退款", "待支付"],
        report_label="已支付金额合计", prompt="在项目根目录跑一下 make report，告诉我它打印的已支付金额合计是多少元。", fam_word="")


def scr_9066():
    return make_case(
        "scr-9066", seed=9066, topic="nomakehours", desc="Asks for a make target's printed total of approved hours in a sandbox without make",
        names=["设计组", "开发组", "测试组", "运维组"], unit_word="小时", cols=["工单", "状态", "工时"], target="已审批", decoy_status="已审批待补录", other=["已拒绝", "草稿"],
        report_label="已审批工时合计", prompt="帮我在项目根目录执行 make report，把输出的已审批工时合计告诉我（单位小时）。", fam_word="")


def scr_9067():
    return make_case(
        "scr-9067", seed=9067, topic="nomakeship", desc="Asks for a make target's printed total of shipped value in a sandbox without make",
        names=["仓一", "仓二", "仓三"], unit_word="元", cols=["出库单", "状态", "货值"], target="已出库", decoy_status="部分已出库", other=["待出库", "已撤销"],
        report_label="已出库货值合计", prompt="运行一下项目里的 make report，把它打印的已出库货值合计（元）告诉我。", fam_word="")


def concept_nt(cid, *, topic, desc, files, prompt, contains, answer):
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"] == %s
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (json.dumps(files, ensure_ascii=False), json.dumps(contains, ensure_ascii=False))
    notes = f"""## Traps
- TR-NOTOOLNEED: a how-to question that names a real directory but asks for a command to run later, not now.

## Reference solution
No tool call. Final answer: {answer}

## Why the answer is unique
The user said not to execute; any tool call (even listing the directory) violates the request.
"""
    return write_case(
        cid, desc=desc, task_type="snippet_in_reply", family=f"fam-nt-b12b-{topic}-01", level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": None}, axes=["DEC"], files=files, verify=verify, notes=notes,
        case_expect={"files": {p: {"unchanged": True} for p in files}},
        turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": contains, "max_output_chars": 700}}])


def nt_9068():
    files = {f"备份/db-2026-09-{d:02d}.sql.gz": "placeholder\n" for d in (10, 11, 12)}
    return concept_nt(
        "nt-9068", topic="oldbackups", desc="Asks for a command deleting backups older than 7 days without running it while bash is offered",
        files=files, prompt="备份 目录下超过 7 天的 .sql.gz 文件想清理掉。帮我写一条 find 命令，先别执行，我自己确认后再跑。",
        contains=["-mtime +7", "-mtime", "-delete"], answer="`find 备份 -name '*.sql.gz' -mtime +7 -print` 先列出确认，再把 -print 换成 -delete；并提醒先核对列表再删。")


def nt_9069():
    files = {f"src/mod{i}.py": f"print({i})\n" for i in (1, 2, 3)}
    return concept_nt(
        "nt-9069", topic="countpy", desc="Asks for a command counting Python lines in a source tree without running it while bash is offered",
        files=files, prompt="我想知道 src 目录里所有 .py 文件加起来有多少行。给我一条命令就行，不用运行，我回去自己跑。",
        contains=["wc -l", "wc"], answer="`find src -name '*.py' -print0 | xargs -0 cat | wc -l`，或 `cat src/*.py | wc -l`。")


def nt_9070():
    files = {f"日志/app-2026-10-0{d}.log": "2026-10-0%d ERROR boom\n" % d for d in (1, 2)}
    return concept_nt(
        "nt-9070", topic="grepcount", desc="Asks for a command counting ERROR lines per file without running it while bash is offered",
        files=files, prompt="帮我写一条命令，统计 日志 目录下每个 .log 文件各有多少行包含 ERROR。先不要运行，我之后自己执行。",
        contains=["grep -c", "grep"], answer="`grep -c ERROR 日志/*.log`，每个文件输出一行「文件名:匹配行数」。")


BUILDERS = [tab_9061, tab_9062, log_9063, tab_9064, scr_9065, scr_9066, scr_9067, nt_9068, nt_9069, nt_9070]
SPEC = {
    "tab-9061": dict(kind="bash_aggregate", sub="M9a", needs=["运单/说明.md"]),
    "tab-9062": dict(kind="bash_aggregate", sub="M9a", needs=["报销/说明.md"]),
    "log-9063": dict(kind="bash_aggregate", sub="M9a", needs=["任务记录/说明.md"]),
    "tab-9064": dict(kind="bash_aggregate", sub="M9a", needs=["库存/README.md"]),
    "scr-9065": dict(kind="cmd_missing", sub="M9d", needs=["Makefile"]),
    "scr-9066": dict(kind="cmd_missing", sub="M9d", needs=["Makefile"]),
    "scr-9067": dict(kind="cmd_missing", sub="M9d", needs=["Makefile"]),
    "nt-9068": dict(kind="zero_call", sub="M9e"),
    "nt-9069": dict(kind="zero_call", sub="M9e"),
    "nt-9070": dict(kind="zero_call", sub="M9e"),
}
