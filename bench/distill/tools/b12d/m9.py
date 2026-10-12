"""M9 (bash) half of the v1.41 b12d batch: ids 9101-9120.

M9a multi-file aggregation (6), M9c long files (4), M9d missing-command recovery (4), M9e bash offered but the
right action is one read or a reply (6). Shapes follow ../b12b/m9.py: a README pins the matching rule, a
look-alike value is the decoy, every answer is one exact scalar a single pipeline computes. The reference
solution of each bash case is replayed in the just-bash sidecar by build.py."""
import json
from random import Random

from common import lines, write_case

REFS = {}
SPEC = {}


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


def alt_section(alts):
    assert len(alts) == 5
    return "\n## Alternative phrasings\n" + "".join(f"{i}. {a}\n" for i, a in enumerate(alts, 1))


def fresh(value, *decoys):
    """The right answer must not be a substring of a wrong one, or a wrong answer would pass the substring check."""
    return all(str(value) not in str(d) for d in decoys)


# ------------------------------------------------------------------ M9a / M9c table aggregation


def agg(cid, *, seed, topic, desc, root, names, header, target, decoy, others, prompt, readme, readme_path, unit, alts,
        mode="sum", zh=True, rows=(140, 210), trunc=False, axes=("CHN", "OBS"), spec_sub="M9a"):
    """Tables `root/<name>.csv` with columns (id, status, amount). mode sum -> total of the rows whose status is
    exactly `target`; mode count -> number of such rows. trunc -> one file past the 64KB read cap."""
    for attempt in range(400):
        rng = Random(seed + attempt * 7919)
        files, ans, first, sub, everything, cut = {}, 0, 0, 0, 0, 0
        for index, name in enumerate(names):
            body = [",".join(header)]
            used = len((body[0] + "\n").encode())
            for i in range(rng.randint(*rows)):
                status = rng.choice([target, target, decoy] + others)
                cents = rng.randint(2000, 98000)
                row = f"{name[0]}{i:04d},{status},{money(cents)}"
                used += len((row + "\n").encode())
                body.append(row)
                add = cents if mode == "sum" else 1
                hit = status == target
                ans += add * hit
                first += add * hit * (index == 0)
                sub += add * (target in status)
                everything += add
                cut += add * hit * (used <= 64 * 1024)
            files[f"{root}/{name}.csv"] = lines(body)
        show = money if mode == "sum" else str
        value = show(ans)
        wrong = [show(sub), show(everything), show(cut if trunc else first)]
        if ans > 0 and fresh(value, *wrong) and (mode != "sum" or literal_free(files, value)):
            break
    else:
        raise SystemExit(cid + ": no seed")
    if trunc:
        assert len(files[f"{root}/{names[0]}.csv"].encode()) > 64 * 1024 and cut != ans
    files[readme_path] = lines(readme)
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
    if trunc:
        trap_lines = f"- TR-TRUNC: {names[0]}.csv is {len(files[f'{root}/{names[0]}.csv'].encode()) // 1024}KB, past read_file's 64KB cap and bash's 8KB output cap; the part inside the cap gives {show(cut)}."
        decoys = {"TR-TRUNC": show(cut), "TR-DECOY": show(sub)}
        traps = ["TR-TRUNC", "TR-DECOY"]
        why = "The status is an exact field value, the README pins the criterion, and one pipeline reads the whole file."
    else:
        trap_lines = f"- TR-MULTISRC: {len(names)} per-group tables; the first alone gives {show(first)}."
        decoys = {"TR-MULTISRC": show(first), "TR-DECOY": show(sub)}
        traps = ["TR-MULTISRC", "TR-DECOY"]
        why = f"The status is an exact field value, the README pins the criterion, all {len(names)} files are aggregated."
    notes = f"""## Traps
{trap_lines}
- TR-DECOY: 「{decoy}」 contains 「{target}」 as a substring; {readme_path} says the status is matched exactly, a substring match gives {show(sub)}.
- TR-DEFN: aggregating every row regardless of status gives {show(everything)}.

## Reference solution
1. bash: `{cmd}`
Final answer: {unit.format(v=value)}

## Why the answer is unique
{why}
{alt_section(alts)}"""
    REFS[cid] = (files, [cmd], has(value))
    token = not zh
    expect = {"output_contains_any": thousands(value) if mode == "sum" else [value], "output_contains_any_token": token,
              "max_output_chars": 600}
    SPEC[cid] = dict(kind="bash_aggregate", sub=spec_sub, needs=[readme_path])
    return write_case(
        cid, desc=desc, task_type=("count_events" if cid.startswith("log") else "filter_count") if mode == "count" else "aggregate",
        family="fam-%s-b12d-%s-01" % (cid.split("-")[0], topic), level="L2", ref_calls=1, traps=traps, decoys=decoys,
        axes=list(axes), files=files, verify=verify, notes=notes, turns=[{"prompt": prompt, "expect": expect}])


def tab_9101():
    return agg(
        "tab-9101", seed=9101, topic="topupok", desc="Sums credited top-ups across four regional tables where a look-alike status shares the word",
        root="充值/2026-09", names=["北区", "南区", "东区", "西区"], header=["流水", "状态", "金额"], target="到账", decoy="到账冲正",
        others=["处理中", "失败"], readme_path="充值/说明.md",
        readme=["# 充值说明", "", "每个大区一个文件，列：流水,状态,金额（元）。", "实际到账金额只算状态恰好是「到账」的流水；「到账冲正」已经被冲回，不算。"],
        prompt="九月四个大区的充值表里，状态为「到账」的金额一共多少元？口径见 充值/说明.md，给我数字就行。",
        unit="九月到账的充值金额合计 {v} 元（只算状态恰好是「到账」，冲正的不计）。",
        alts=["九月四个大区的充值，真正到账的总共多少钱？口径看 充值/说明.md。", "按 充值/说明.md 的规定，把九月四个区的到账充值金额加起来是多少元？",
              "统计一下九月全部大区状态为到账的充值总额（元），说明文件在 充值 目录。", "充值目录下四个大区的表，到账的金额合计多少元？只要结果数字。",
              "九月份各区充值表中「到账」状态的流水金额之和是多少？"])


def tab_9102():
    return agg(
        "tab-9102", seed=9102, topic="enrollpaid", desc="Counts paid enrolments across three campus tables where a look-alike status shares the prefix",
        root="报名/2026秋", names=["朝阳校区", "海淀校区", "丰台校区"], header=["学号", "状态", "学费"], target="已缴费", decoy="已缴费退课",
        others=["待缴费", "已退费"], readme_path="报名/说明.md",
        readme=["# 报名说明", "", "每个校区一个文件，列：学号,状态,学费（元）。", "统计在读人数只算状态恰好是「已缴费」的行；「已缴费退课」已经退出课程，单独统计。"],
        prompt="秋季三个校区的报名表里，状态为「已缴费」的一共有多少人？口径见 报名/说明.md，直接告诉我人数。", mode="count",
        unit="秋季三个校区状态恰好是「已缴费」的共 {v} 人（已缴费退课另算）。",
        alts=["三个校区秋季报名里，缴了费、状态是已缴费的有多少个学生？按 报名/说明.md。", "报名目录下三张校区表，已缴费的行数合计是多少？",
              "按说明文件的口径，秋季已缴费的在读人数是多少？", "数一下秋季各校区报名表里状态为已缴费的学员总数。",
              "报名/说明.md 里写了怎么算已缴费人数，三个校区加起来是几个人？"])


def log_9103():
    return agg(
        "log-9103", seed=9103, topic="releaseok", desc="Counts successful releases across four per-service tables where a look-alike result shares the prefix",
        root="发布/2026-10", names=["gateway", "billing", "search", "notify"], header=["版本", "结果", "耗时秒"], target="上线成功", decoy="上线成功后回滚",
        others=["上线失败", "已取消"], readme_path="发布/说明.md",
        readme=["# 发布记录说明", "", "每个服务一个文件，列：版本,结果,耗时秒。", "成功率只算结果恰好是「上线成功」的记录；「上线成功后回滚」算作失败，不计入成功。"],
        prompt="十月 gateway、billing、search、notify 四个服务的发布记录里，结果为「上线成功」的一共有多少次？口径在 发布/说明.md。", mode="count",
        unit="十月四个服务结果恰好是「上线成功」的发布共 {v} 次（上线成功后回滚不算）。",
        alts=["十月四个服务一共成功上线了几次？按 发布/说明.md 的口径。", "发布记录目录下四个服务的表，上线成功的记录合计多少条？",
              "统计十月 gateway 等四个服务发布结果为上线成功的次数。", "按发布说明，十月全部服务的成功发布次数是多少？",
              "把四张发布表里结果是「上线成功」的行数加起来是多少？"])


def tab_9104():
    return agg(
        "tab-9104", seed=9104, topic="invoicepaid", desc="Sums paid invoices across four regional tables where a look-alike state shares the word",
        root="invoices/2026-Q3", names=["emea", "apac", "amer", "latam"], header=["invoice", "state", "amount"], target="paid", decoy="paid-late",
        others=["open", "void"], readme_path="invoices/README.md",
        readme=["# Invoice exports", "", "One file per region; columns invoice,state,amount (USD).", "Collected revenue counts rows whose state is exactly `paid`; `paid-late` invoices are in dispute and are reported separately."],
        prompt="What is the total collected revenue in USD across the four regional invoice tables for Q3? The rule is in invoices/README.md. Just give me the number.",
        unit="Q3 collected revenue: {v} USD (state exactly `paid`; `paid-late` is excluded).", zh=False, axes=("OBS", "CHN"),
        alts=["How much did we actually collect in Q3 over the four regions, per invoices/README.md?", "Add up the paid invoices of emea, apac, amer and latam for Q3 (USD).",
              "Total of all rows in state paid across the invoice exports? README has the rule.", "Per the README, what is Q3 collected revenue in dollars?",
              "Sum the amount of paid invoices in the four Q3 region files."])


def tab_9105():
    return agg(
        "tab-9105", seed=9105, topic="purchaseok", desc="Sums accepted purchase orders across four category tables where a look-alike status shares the prefix",
        root="采购/2026Q3", names=["办公", "设备", "耗材", "差旅"], header=["采购单", "状态", "金额"], target="已验收", decoy="已验收退货",
        others=["待验收", "已取消"], readme_path="采购/说明.md",
        readme=["# 采购说明", "", "每个品类一个文件，列：采购单,状态,金额（元）。", "实际支出只算状态恰好是「已验收」的单据；「已验收退货」已经退回供应商，不计支出。"],
        prompt="三季度办公、设备、耗材、差旅四个品类的采购表里，已验收的采购单金额合计多少元？口径见 采购/说明.md，报个数就行。",
        unit="三季度已验收的采购金额合计 {v} 元（只算状态恰好是「已验收」，退货的不计）。",
        alts=["三季度四个品类实际花了多少钱？只算已验收的，规则在 采购/说明.md。", "采购目录下四张表，状态为已验收的金额加总是多少元？",
              "按采购说明的口径，三季度已验收采购金额一共多少？", "把办公、设备、耗材、差旅里已验收的采购单金额加起来。",
              "三季度各品类「已验收」采购单的金额总和是多少元？"])


def tab_9106():
    return agg(
        "tab-9106", seed=9106, topic="ticketsdone", desc="Counts resolved tickets across three tier tables where a look-alike state shares the prefix",
        root="tickets/2026-10", names=["tier1", "tier2", "tier3"], header=["ticket", "state", "hours"], target="resolved", decoy="resolved-reopened",
        others=["open", "pending"], readme_path="tickets/README.md",
        readme=["# Support ticket exports", "", "One file per tier; columns ticket,state,hours.", "The resolved count includes only rows whose state is exactly `resolved`; `resolved-reopened` tickets are open again and are counted as open."],
        prompt="How many tickets are resolved across the three tier files for October? Use the rule in tickets/README.md and reply with the count.", mode="count",
        unit="October resolved tickets: {v} (state exactly `resolved`; reopened ones are not counted).", zh=False, axes=("OBS", "CHN"),
        alts=["Across tier1, tier2 and tier3, how many October tickets ended up resolved? README has the definition.", "Count the rows in state resolved over all October ticket files.",
              "Per tickets/README.md, what is the October resolved-ticket count?", "How many tickets are resolved (not reopened) in the three tier exports?",
              "Give me the number of resolved tickets for October from the tier tables."])


# ------------------------------------------------------------------ M9c long files


def tab_9109():
    return agg(
        "tab-9109", seed=9109, topic="walletrefund", desc="Sums one status over a single ledger past the 64KB read cap where a look-alike status shares the word",
        root="流水", names=["2026-Q3"], header=["流水号", "类型", "金额"], target="退款", decoy="退款撤销", others=["充值", "消费"], rows=(3300, 3500),
        readme_path="流水/说明.md",
        readme=["# 流水说明", "", "2026-Q3.csv 是三季度全部钱包流水，列：流水号,类型,金额（元）。", "退款合计只算类型恰好是「退款」的行；「退款撤销」表示退款被撤回，不计。"],
        prompt="三季度钱包流水里，类型为「退款」的金额一共多少元？口径见 流水/说明.md，给我数字就行。",
        unit="三季度退款金额合计 {v} 元（类型恰好是「退款」，退款撤销不算）。", trunc=True, spec_sub="M9c", axes=("LNG", "OBS"),
        alts=["钱包三季度流水里一共退了多少钱？只算类型是退款的，规则看 流水/说明.md。", "把 2026-Q3.csv 中类型为退款的金额全部加起来是多少元？",
              "三季度的退款总额是多少？注意说明文件里的口径。", "流水表里「退款」类型的金额合计，单位元。",
              "按流水/说明.md，统计三季度退款金额的总和。"])


def long_event(cid, *, seed, topic, desc, root, logname, readme_name, event, decoy_event, others, prompt, zh, alts, unit):
    """Append-only order log past the read cap; the answer is the order id of the last exact `event` line."""
    rng = Random(seed)
    rows, last_exact, last_sub = [], None, None
    for i in range(2400):
        ts = f"2026-10-0{1 + i // 800}T{(i // 40) % 24:02d}:{(i * 7) % 60:02d}:{(i * 13) % 60:02d}"
        ev = rng.choices([event, decoy_event] + others, [3, 3] + [30] * len(others))[0]
        oid = "O" + "".join(rng.choice("0123456789") for _ in range(6))
        rows.append(f"{ts} 节点{rng.randint(1, 6)} {ev} 订单={oid} 渠道={rng.choice(['app', 'web', 'store'])}" if zh else
                    f"{ts} node{rng.randint(1, 6)} {ev} order={oid} channel={rng.choice(['app', 'web', 'store'])}")
        if ev == event:
            last_exact = oid
        if event in ev:
            last_sub = oid
    assert last_exact != last_sub, "decoy must sit after the last exact line"
    path = f"{root}/{logname}"
    text = lines(rows)
    head = text.encode()[:64 * 1024].decode(errors="ignore").splitlines()
    cut_id = [r for r in head if f" {event} " in r][-1].split("=")[1].split(" ")[0]
    assert len(text.encode()) > 64 * 1024 and cut_id != last_exact
    files = {path: text, f"{root}/{readme_name}": lines(
        [f"{logname} 按时间顺序追加，导出时共 {len(rows)} 行。", f"「{event}」是独立事件；「{decoy_event}」是补货之后的回执，不算「{event}」。"] if zh else
        [f"{logname} is append-only in time order, {len(rows)} lines at export.", f"`{event}` is its own event; `{decoy_event}` is the receipt after a restock and does not count as `{event}`."])}
    field = "订单=" if zh else "order="
    verify = '''
import json
case = json.load(open("case.json"))
rows = case["files"][%r].splitlines()
readme = case["files"][%r]
assert str(len(rows)) in readme
last = None
for row in rows:
    parts = row.split(" ")
    assert len(parts) == 5 and parts[3].startswith(%r), row
    if parts[2] == %r:
        last = parts[3][len(%r):]
assert last
print(json.dumps({"expected_string": last}))
''' % (path, f"{root}/{readme_name}", field, event, field)
    cmd = f"grep ' {event} ' {path} | tail -1"
    notes = f"""## Traps
- TR-TRUNC: {logname} is {len(text.encode()) // 1024}KB, past read_file's 64KB cap and bash's 8KB output cap; the last exact event inside the cap is {cut_id}.
- TR-DECOY: 「{decoy_event}」 lines contain 「{event}」; a plain substring grep ends on {last_sub}.

## Reference solution
1. bash: `{cmd}`
Final answer: {unit.format(v=last_exact)}

## Why the answer is unique
The log is append-only in time order (README), so the last exact-event line is the latest one; the README says the receipt event is a different event.
{alt_section(alts)}"""
    REFS[cid] = (files, [cmd], has(last_exact))
    SPEC[cid] = dict(kind="bash_aggregate", sub="M9c", needs=[f"{root}/{readme_name}"])
    return write_case(
        cid, desc=desc, task_type="locate_error", family="fam-%s-b12d-%s-01" % (cid.split("-")[0], topic), level="L2", ref_calls=1,
        traps=["TR-TRUNC", "TR-DECOY"], decoys={"TR-TRUNC": cut_id, "TR-DECOY": last_sub}, axes=["LNG", "OBS"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": {"output_contains": [last_exact], "max_output_chars": 600}}])


def log_9107():
    return long_event(
        "log-9107", seed=9107, topic="stockout", desc="Finds the order of the last out-of-stock event in a log past the read cap where a restock receipt contains the event name",
        root="订单日志", logname="order.log", readme_name="说明.md", event="库存不足", decoy_event="库存不足已补货", others=["下单成功", "支付完成", "库存预占"],
        prompt="订单日志里最后一次「库存不足」事件对应的订单号是多少？口径见 订单日志/说明.md。", zh=True,
        unit="最后一次库存不足的订单是 {v}（order.log 末尾附近那条，已补货回执不算）。",
        alts=["order.log 里最近一次库存不足发生在哪个订单上？按说明文件的口径。", "订单日志中最后一条「库存不足」事件的订单号是什么？",
              "帮我找出最后一次库存不足的订单号，已补货回执不算。", "说明.md 里讲了事件的区别，最近一次库存不足的是哪一单？",
              "订单日志按时间追加，最后一个库存不足事件属于哪个订单？"])


def log_9108():
    rng = Random(9108)
    for attempt in range(300):
        rng = Random(9108 + attempt * 7919)
        rows, exact, sub = [], 0, 0
        for i in range(3000):
            ts = f"2026-10-04T{(i // 120) % 24:02d}:{(i // 2) % 60:02d}:{(i * 17) % 60:02d}Z"
            code = rng.choices(["E4021", "E40210", "E5003", "E4090", "W1001"], [4, 4, 30, 30, 40])[0]
            rows.append(f"{ts} level={'ERROR' if code[0] == 'E' else 'WARN'} code={code} svc={rng.choice(['api', 'auth', 'sync'])} msg=handled")
            exact += code == "E4021"
            sub += code.startswith("E4021")
        value = str(exact)
        if fresh(value, sub, len(rows)) and exact != sub:
            break
    files = {"var/edge-events.log": lines(rows), "var/NOTES.txt": lines([f"edge-events.log: one line per event, {len(rows)} lines at export.", "Codes are exact: E4021 (upstream timeout) and E40210 (upstream timeout, retried) are different codes."])}
    assert len(files["var/edge-events.log"].encode()) > 64 * 1024
    verify = '''
import json
case = json.load(open("case.json"))
rows = case["files"]["var/edge-events.log"].splitlines()
assert str(len(rows)) in case["files"]["var/NOTES.txt"]
n = 0
for row in rows:
    parts = row.split(" ")
    assert len(parts) == 5 and parts[2].startswith("code="), row
    n += parts[2] == "code=E4021"
print(json.dumps({"expected_contains_any": [str(n)]}))
'''
    cmd = "grep -c 'code=E4021 ' var/edge-events.log"
    notes = f"""## Traps
- TR-TRUNC: edge-events.log is {len(files['var/edge-events.log'].encode()) // 1024}KB, past read_file's 64KB cap and bash's 8KB output cap; counting the visible part undercounts.
- TR-DECOY: code E40210 begins with E4021; a prefix grep counts {sub} instead of {exact}.

## Reference solution
1. bash: `{cmd}`
Final answer: There are {value} lines with code E4021 in var/edge-events.log (E40210 is a different code).

## Why the answer is unique
README pins that codes are exact; the grep pattern ends with a space so E40210 does not match.
{alt_section(["How many events in var/edge-events.log carry error code E4021?", "Count lines with code=E4021 in the edge events log; README explains the code format.", "edge-events.log: number of E4021 entries? Exact code only.", "Tell me how many times code E4021 shows up in var/edge-events.log.", "How often did the upstream timeout code E4021 occur in edge-events.log?"])}"""
    REFS["log-9108"] = (files, [cmd], has(value))
    SPEC["log-9108"] = dict(kind="bash_aggregate", sub="M9c", needs=["var/NOTES.txt"])
    return write_case(
        "log-9108", desc="Counts one exact error code in an application log past the read cap where a longer code shares its prefix",
        task_type="count_events", family="fam-log-b12d-errcode-01", level="L2", ref_calls=1, traps=["TR-TRUNC", "TR-DECOY"],
        decoys={"TR-TRUNC": "undercount", "TR-DECOY": str(sub)}, axes=["LNG", "OBS"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "How many lines in var/edge-events.log have error code E4021? var/NOTES.txt explains how codes are written. Reply with the count.",
                "expect": {"output_contains_any": [value], "output_contains_any_token": True, "max_output_chars": 600}}])


def log_9110():
    for attempt in range(300):
        rng = Random(9110 + attempt * 7919)
        rows, per = [], {"/v2/refund": [], "/v2/refund-status": [], "/v2/quote": [], "/v2/pay": []}
        for i in range(2300):
            route = rng.choices(list(per), [6, 6, 30, 30])[0]
            ms = rng.randint(20, 2400) if route != "/v2/refund-status" else rng.randint(20, 3900)
            ts = f"2026-10-0{1 + i // 800}T{(i // 40) % 24:02d}:{(i * 7) % 60:02d}:{(i * 13) % 60:02d}"
            rows.append(f"{ts} 路由={route} 状态={rng.choice([200, 200, 200, 502])} 耗时={ms}ms")
            per[route].append((ms, len("\n".join(rows[:i + 1]).encode())))
        text = lines(rows)
        exact = max(m for m, _ in per["/v2/refund"])
        sub = max(m for r in ("/v2/refund", "/v2/refund-status") for m, _ in per[r])
        cut = max([m for m, e in per["/v2/refund"] if e <= 64 * 1024] or [0])
        unique = sum(m == exact for m, _ in per["/v2/refund"]) == 1
        if len(text.encode()) > 64 * 1024 and unique and sub != exact and cut != exact and fresh(exact, sub, cut):
            break
    files = {"接口监控/latency.log": text, "接口监控/口径.md": lines([f"latency.log 按时间追加，导出时共 {len(rows)} 行，耗时单位毫秒。", "路由按完整路径区分：/v2/refund 与 /v2/refund-status 是两个接口，不要合并。"])}
    verify = '''
import json
case = json.load(open("case.json"))
rows = case["files"]["接口监控/latency.log"].splitlines()
assert str(len(rows)) in case["files"]["接口监控/口径.md"]
best = []
for row in rows:
    parts = row.split(" ")
    assert len(parts) == 4 and parts[1].startswith("路由=") and parts[3].startswith("耗时=") and parts[3].endswith("ms"), row
    if parts[1] == "路由=/v2/refund":
        best.append(int(parts[3][3:-2]))
assert best.count(max(best)) == 1
print(json.dumps({"expected_contains_any": [str(max(best))]}))
'''
    cmd = r"""awk '$2=="路由=/v2/refund" {split($4,a,"="); v=a[2]+0; if (v>m) m=v} END{print m}' 接口监控/latency.log"""
    notes = f"""## Traps
- TR-TRUNC: latency.log is {len(text.encode()) // 1024}KB, past read_file's 64KB cap and bash's 8KB output cap; the maximum inside the cap is {cut}.
- TR-DECOY: /v2/refund-status starts with /v2/refund; a prefix match gives {sub} ms.

## Reference solution
1. bash: `{cmd}`
Final answer: /v2/refund 最慢的一次耗时 {exact} ms（/v2/refund-status 不算）。

## Why the answer is unique
Route is matched as a whole field (说明.md); the maximum is a single line.
{alt_section(["latency.log 里 /v2/refund 这个接口最慢的一次要多久？", "接口监控日志中退款接口 /v2/refund 的最大耗时是多少毫秒？", "找出 /v2/refund 路由耗时最高的那条，耗时多少 ms？", "按说明.md 的路由口径，/v2/refund 的峰值耗时是多少？", "退款接口最慢那次请求耗时几毫秒（不含 refund-status）？"])}"""
    REFS["log-9110"] = (files, [cmd], has(str(exact)))
    SPEC["log-9110"] = dict(kind="bash_aggregate", sub="M9c", needs=["接口监控/口径.md"])
    return write_case(
        "log-9110", desc="Finds the slowest request of one route in an access log past the read cap where a longer route shares its prefix",
        task_type="locate_error", family="fam-log-b12d-slowrefund-01", level="L2", ref_calls=1, traps=["TR-TRUNC", "TR-DECOY"],
        decoys={"TR-TRUNC": str(cut), "TR-DECOY": str(sub)}, axes=["LNG", "OBS"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "接口监控目录的 latency.log 里，路由 /v2/refund 最慢的一次请求耗时多少毫秒？口径见 接口监控/口径.md，直接告诉我数字。",
                "expect": {"output_contains_any": [str(exact)], "max_output_chars": 600}}])


# ------------------------------------------------------------------ M9d missing command


def csv_files(rng, root, names, header, target, decoy, others, rows, value_fn):
    files = {}
    for name in names:
        body = [",".join(header)]
        for i in range(rng.randint(*rows)):
            body.append(value_fn(name, i, rng.choice([target, target, decoy] + others), rng))
        files[f"{root}/{name}.csv"] = lines(body)
    return files


def scr_9111():
    target, decoy = "已发货", "已发货退回"
    for attempt in range(300):
        rng = Random(9111 + attempt * 7919)
        files = csv_files(rng, "数据", ["华东", "华南", "华北"], ["运单", "状态", "重量kg"], target, decoy, ["待发货", "已取消"], (40, 70),
                          lambda n, i, s, r: f"{n[1]}{i:03d},{s},{money(r.randint(500, 90000))}")
        tot = sub = every = 0
        for text in files.values():
            for row in text.splitlines()[1:]:
                _, st, w = row.split(",")
                c = int(w.replace(".", ""))
                tot += c * (st == target)
                sub += c * (target in st)
                every += c
        value = money(tot)
        if literal_free(files, value) and fresh(value, money(sub), money(every)):
            break
    files["工具/tally.js"] = lines([
        "// 汇总已发货的重量（kg）", "const fs = require('fs');", "let total = 0;", "for (const f of fs.readdirSync('数据')) {", "  if (!f.endsWith('.csv')) continue;",
        "  for (const line of fs.readFileSync('数据/' + f, 'utf8').split('\\n').slice(1)) {", "    const c = line.split(',');",
        f"    if (c[1] === '{target}') total += parseFloat(c[2]);", "  }", "}", "console.log('已发货重量合计 ' + total.toFixed(2) + ' kg');"])
    cmd = f"""cat 数据/*.csv | awk -F, '$2=="{target}" {{s+=$3}} END{{printf "%.2f\\n", s}}'"""
    verify = '''
import json
case = json.load(open("case.json"))
js = case["files"]["工具/tally.js"]
assert "c[1] === '已发货'" in js and "toFixed(2)" in js
cents = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "运单,状态,重量kg", path
    for row in rows[1:]:
        ident, status, w = row.split(",")
        if status == "已发货":
            cents += int(w.replace(".", ""))
value = "%d.%02d" % (cents // 100, cents % 100)
print(json.dumps({"expected_contains_any": [value, "{:,}".format(cents // 100) + "." + "%02d" % (cents % 100)]}))
'''
    notes = f"""## Traps
- node is not installed, so `node 工具/tally.js` exits 127; the script has to be reproduced by hand.
- TR-DECOY: 「{decoy}」 contains 「{target}」; the script tests equality, a substring match gives {money(sub)}.
- TR-DEFN: summing every row gives {money(every)}.

## Reference solution
1. bash: `node 工具/tally.js` -> exit 127.
2. read_file 工具/tally.js: sums column 3 of every 数据/*.csv where column 2 is exactly 已发货.
3. bash: `{cmd}`
Final answer: 工具/tally.js 会输出「已发货重量合计 {value} kg」（node 不可用，我按脚本逻辑用 awk 复算）。

## Why the answer is unique
The script's filter, columns and format are explicit.
{alt_section(["把 工具/tally.js 跑一遍，已发货的重量合计是多少 kg？", "工具目录里的 tally.js 会打印已发货重量，结果是多少？", "执行 tally.js，报一下它输出的重量合计。", "tally.js 统计出的已发货总重量是多少公斤？", "运行统计脚本 tally.js，把已发货重量合计告诉我。"])}"""
    REFS["scr-9111"] = (files, [cmd], has(value))
    SPEC["scr-9111"] = dict(kind="cmd_missing", sub="M9d", needs=["工具/tally.js"], script="tally.js")
    return write_case(
        "scr-9111", desc="Asks for the printed total of a Node script in a sandbox without node; the exact-status filter must be reproduced",
        task_type="reproduce_output", family="fam-scr-b12d-nonodeship-01", level="L2", ref_calls=3, traps=["TR-DECOY", "TR-DEFN"],
        decoys={"TR-DECOY": money(sub), "TR-DEFN": money(every)}, axes=["OBS", "ERR"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "在项目根目录执行 node 工具/tally.js，把它打印的已发货重量合计（kg）告诉我。",
                "expect": {"output_contains_any": thousands(value), "max_output_chars": 600}}])


def scr_9112():
    for attempt in range(300):
        rng = Random(9112 + attempt * 7919)
        files, exact, sub, every = {}, 0, 0, 0
        for d in ("05", "06", "07"):
            rows = []
            for i in range(rng.randint(260, 380)):
                level = rng.choices(["FAIL", "FAIL-RETRY", "OK", "WARN"], [4, 4, 60, 12])[0]
                mod = rng.choices(["sync", "sync-v2", "export", "import"], [10, 8, 30, 30])[0]
                rows.append(f"2026-10-{d}T{(i // 16) % 24:02d}:{(i * 7) % 60:02d}:{(i * 13) % 60:02d} {level} {mod} 原因={rng.choice(['超时', '冲突', '无', '限流'])}")
                exact += level == "FAIL" and mod == "sync"
                sub += level.startswith("FAIL") and mod.startswith("sync")
            files[f"日志/2026-10-{d}.log"] = lines(rows)
        if exact > 5 and fresh(exact, sub) and exact != sub:
            break
    files["脚本/failcount.pl"] = lines([
        "# 统计 sync 模块的失败次数", "my $n = 0;", "for my $f (glob('日志/*.log')) {", "  open(my $h, '<', $f) or die \"$f: $!\";", "  while (my $line = <$h>) {",
        "    my @c = split / /, $line;", "    $n++ if $c[1] eq 'FAIL' && $c[2] eq 'sync';", "  }", "}", "print \"sync 失败次数: $n\\n\";"])
    cmd = """cat 日志/*.log | awk '$2=="FAIL" && $3=="sync"' | wc -l"""
    verify = '''
import json
case = json.load(open("case.json"))
pl = case["files"]["脚本/failcount.pl"]
assert "$c[1] eq 'FAIL' && $c[2] eq 'sync'" in pl
n = 0
for path, text in case["files"].items():
    if not path.endswith(".log"):
        continue
    assert len(text.splitlines()) == LINES[path], path
    for row in text.splitlines():
        parts = row.split(" ")
        assert len(parts) == 4, row
        n += parts[1] == "FAIL" and parts[2] == "sync"
print(json.dumps({"expected_contains_any": [str(n)]}))
'''
    value = str(exact)
    verify = "LINES = %r\n" % {p: len(t.splitlines()) for p, t in files.items() if p.endswith(".log")} + verify
    notes = f"""## Traps
- perl is not installed, so `perl 脚本/failcount.pl` exits 127; the script has to be reproduced by hand.
- TR-DECOY: FAIL-RETRY and sync-v2 look like FAIL and sync; the script compares fields exactly, a prefix match gives {sub}.

## Reference solution
1. bash: `perl 脚本/failcount.pl` -> exit 127.
2. read_file 脚本/failcount.pl: counts lines of 日志/*.log whose 2nd field is FAIL and 3rd field is sync.
3. bash: `{cmd}`
Final answer: failcount.pl 会输出「sync 失败次数: {value}」（perl 不可用，我按脚本逻辑用 awk 复算）。

## Why the answer is unique
Fields are space separated and compared exactly in the script.
{alt_section(["跑一下 脚本/failcount.pl，sync 模块失败了多少次？", "failcount.pl 打印的 sync 失败次数是几？", "执行脚本目录里的 failcount.pl，把它输出的次数告诉我。", "帮我运行 failcount.pl，得到的 sync 失败次数是多少？", "用 failcount.pl 统计一下 sync 失败总数。"])}"""
    REFS["scr-9112"] = (files, [cmd], has(value))
    SPEC["scr-9112"] = dict(kind="cmd_missing", sub="M9d", needs=["脚本/failcount.pl"], script="failcount.pl")
    return write_case(
        "scr-9112", desc="Asks for the printed count of a Perl script in a sandbox without perl; exact field comparison must be reproduced",
        task_type="reproduce_output", family="fam-scr-b12d-noperlfail-01", level="L2", ref_calls=3, traps=["TR-DECOY"],
        decoys={"TR-DECOY": str(sub)}, axes=["OBS", "ERR"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "在项目根目录执行 perl 脚本/failcount.pl，它会打印 sync 模块的失败次数，把这个次数报给我。",
                "expect": {"output_contains_any": [value], "max_output_chars": 600}}])


def scr_9113():
    for attempt in range(300):
        rng = Random(9113 + attempt * 7919)
        pool = [f"C{n:04d}" for n in rng.sample(range(1000, 9999), 90)]
        files, buyers, sub_buyers, rows_paid = {}, set(), set(), 0
        for region in ("north", "south", "west"):
            body = ["order,customer,state"]
            for i in range(rng.randint(90, 130)):
                state = rng.choices(["paid", "paid-pending", "refunded", "new"], [10, 4, 3, 5])[0]
                cust = rng.choice(pool)
                body.append(f"{region[0]}{i:04d},{cust},{state}")
                if state == "paid":
                    buyers.add(cust)
                    rows_paid += 1
                if state.startswith("paid"):
                    sub_buyers.add(cust)
            files[f"data/{region}.csv"] = lines(body)
        value = str(len(buyers))
        if fresh(value, len(sub_buyers), rows_paid) and len(buyers) != len(sub_buyers):
            break
    files["tools/buyers.rb"] = lines([
        "# count distinct customers with a paid order", "seen = {}", "Dir.glob('data/*.csv').each do |f|", "  File.readlines(f).drop(1).each do |line|",
        "    order, customer, state = line.chomp.split(',')", "    seen[customer] = true if state == 'paid'", "  end", "end", "puts \"distinct paying customers: #{seen.size}\""])
    cmd = """cat data/*.csv | awk -F, '$3=="paid" {print $2}' | sort -u | wc -l"""
    verify = '''
import json
case = json.load(open("case.json"))
rb = case["files"]["tools/buyers.rb"]
assert "state == 'paid'" in rb and "seen.size" in rb
buyers = set()
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "order,customer,state", path
    for row in rows[1:]:
        order, customer, state = row.split(",")
        if state == "paid":
            buyers.add(customer)
print(json.dumps({"expected_contains_any": [str(len(buyers))]}))
'''
    notes = f"""## Traps
- ruby is not installed, so `ruby tools/buyers.rb` exits 127; the script has to be reproduced by hand.
- TR-DEFN: counting paid rows gives {rows_paid}; the script counts distinct customers.
- TR-DECOY: state paid-pending is not paid; a prefix match gives {len(sub_buyers)} customers.

## Reference solution
1. bash: `ruby tools/buyers.rb` -> exit 127.
2. read_file tools/buyers.rb: distinct customers over rows whose state is exactly paid.
3. bash: `{cmd}`
Final answer: buyers.rb prints "distinct paying customers: {value}" (ruby is not available; recomputed with awk and sort -u).

## Why the answer is unique
The script's key is the customer id and its filter is the exact state paid.
{alt_section(["Run tools/buyers.rb and tell me how many distinct paying customers it reports.", "What number does tools/buyers.rb print for distinct paying customers?", "Execute the buyers script and give me the customer count it outputs.", "tools/buyers.rb counts unique customers with a paid order: what is the result?", "Please run buyers.rb and report its distinct paying customer figure."])}"""
    REFS["scr-9113"] = (files, [cmd], has(value))
    SPEC["scr-9113"] = dict(kind="cmd_missing", sub="M9d", needs=["tools/buyers.rb"], script="buyers.rb")
    return write_case(
        "scr-9113", desc="Asks for the printed distinct-customer count of a Ruby script in a sandbox without ruby; the exact state filter and distinct key must be reproduced",
        task_type="reproduce_output", family="fam-scr-b12d-norubybuyers-01", level="L2", ref_calls=3, traps=["TR-DEFN", "TR-DECOY"],
        decoys={"TR-DEFN": str(rows_paid), "TR-DECOY": str(len(sub_buyers))}, axes=["OBS", "ERR"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "Run ruby tools/buyers.rb from the project root and tell me how many distinct paying customers it reports.",
                "expect": {"output_contains_any": [value], "output_contains_any_token": True, "max_output_chars": 600}}])


def scr_9114():
    target, decoy = "已入库", "已入库作废"
    for attempt in range(300):
        rng = Random(9114 + attempt * 7919)
        files = csv_files(rng, "数据", ["一号仓", "二号仓", "三号仓", "四号仓"], ["批次", "状态", "数量"], target, decoy, ["待入库", "已退回"], (40, 70),
                          lambda n, i, s, r: f"{n[0]}{i:03d},{s},{r.randint(5, 900)}")
        tot = sub = every = 0
        for text in files.values():
            for row in text.splitlines()[1:]:
                _, st, q = row.split(",")
                tot += int(q) * (st == target)
                sub += int(q) * (target in st)
                every += int(q)
        if fresh(tot, sub, every):
            break
    value = str(tot)
    files["justfile"] = lines([
        "# 项目任务", "", "stock:", "\t@cat 数据/*.csv | awk -F, '$2==\"%s\" {s+=$3} END{printf \"已入库数量合计 %%d 件\\n\", s}'" % target])
    cmd = """cat 数据/*.csv | awk -F, '$2=="已入库" {s+=$3} END{printf "%d\\n", s}'"""
    verify = '''
import json
case = json.load(open("case.json"))
jf = case["files"]["justfile"]
assert "stock:" in jf and "$2==\\"已入库\\"" in jf
n = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "批次,状态,数量", path
    for row in rows[1:]:
        ident, status, qty = row.split(",")
        if status == "已入库":
            n += int(qty)
print(json.dumps({"expected_contains_any": [str(n), "{:,}".format(n)]}))
'''
    notes = f"""## Traps
- just is not installed, so `just stock` exits 127; the recipe in the justfile has to be reproduced by hand.
- TR-DECOY: 「{decoy}」 contains 「{target}」; the recipe tests equality, a substring match gives {sub}.
- TR-DEFN: summing every row gives {every}.

## Reference solution
1. bash: `just stock` -> exit 127.
2. read_file justfile: the recipe is `cat 数据/*.csv | awk -F, '$2=="已入库" ...'`.
3. bash: `{cmd}`
Final answer: just stock 会输出「已入库数量合计 {value} 件」（just 不可用，我按 justfile 里的配方用 awk 复算）。

## Why the answer is unique
The recipe's filter and format are explicit.
{alt_section(["用 just 跑一下 stock 任务，已入库的数量合计是多少件？", "项目的 justfile 里有个 stock 任务，执行后打印的数量告诉我。", "执行 just stock，把输出的入库数量合计报给我。", "帮我跑 justfile 的 stock，得到的已入库件数是多少？", "just stock 会打印已入库总数，是多少？"])}"""
    REFS["scr-9114"] = (files, [cmd], has(value))
    SPEC["scr-9114"] = dict(kind="cmd_missing", sub="M9d", needs=["justfile"], script="just")
    return write_case(
        "scr-9114", desc="Asks for the printed total of a just recipe in a sandbox without just; the recipe's exact-status filter must be reproduced",
        task_type="reproduce_output", family="fam-scr-b12d-nojuststock-01", level="L2", ref_calls=3, traps=["TR-DECOY", "TR-DEFN"],
        decoys={"TR-DECOY": str(sub), "TR-DEFN": str(every)}, axes=["OBS", "ERR"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": "在项目根目录执行 just stock，把它打印的已入库数量合计（件）告诉我。",
                "expect": {"output_contains_any": [value] + (["{:,}".format(tot)] if tot >= 1000 else []), "max_output_chars": 600}}])


# ------------------------------------------------------------------ M9e bash offered, direct read or reply


def read_case(cid, *, topic, desc, task_type, files, verify, answer, decoy, prompt, contains, notes_trap, why, token, alts):
    notes = f"""## Traps
- TR-DECOY: {notes_trap}

## Reference solution
1. read_file {answer[0]}
Final answer: {answer[1]}

## Why the answer is unique
{why}
Why bash is not the tool here: one named file and one fact, so read_file is the direct read. The turn forbids bash so the rows teach that bash being offered does not make it the default.
{alt_section(alts)}"""
    SPEC[cid] = dict(kind="bash_avoided", sub="M9e")
    expect = {"output_contains_any": contains, "forbidden_tools": ["bash"], "max_output_chars": 600}
    if token:
        expect["output_contains_any_token"] = True
    return write_case(
        cid, desc=desc, task_type=task_type, family="fam-%s-b12d-%s-01" % (cid.split("-")[0], topic), level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": decoy}, axes=["OBS"], files=files, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": expect}])


def doc_9115():
    files = {
        "docs/RELEASE.md": lines(["# 发布状态", "", "当前稳定版：3.1.2（2026-09-30 发布）", "下一个预览版：3.2.0-beta1，只给内部测试，不对外。", "上一个稳定版：3.0.4，已停止维护。"]),
        "docs/INSTALL.md": lines(["# 安装", "", "示例命令里的版本号 3.0.4 是旧文档遗留，以 RELEASE.md 为准。"]),
    }
    verify = '''
import json
case = json.load(open("case.json"))
text = case["files"]["docs/RELEASE.md"]
assert text.startswith("# 发布状态") and "当前稳定版：3.1.2" in text
assert case["files"]["docs/INSTALL.md"].startswith("# 安装") and "3.0.4" in case["files"]["docs/INSTALL.md"]
print(json.dumps({"expected_contains_any": ["3.1.2"]}))
'''
    return read_case(
        "doc-9115", topic="stableversion", desc="Single-file release note lookup of the stable version while bash is offered; the read tool is the right call",
        task_type="policy_lookup", files=files, verify=verify, answer=("docs/RELEASE.md", "当前稳定版是 3.1.2（RELEASE.md；3.2.0-beta1 是内部预览，3.0.4 已停止维护）。"), decoy="3.2.0-beta1",
        prompt="docs/RELEASE.md 里写的当前稳定版是哪个版本号？", contains=["3.1.2"], token=False,
        notes_trap="the same file also lists a preview 3.2.0-beta1 and the old 3.0.4; INSTALL.md still shows 3.0.4.", why="The user names RELEASE.md and its line 当前稳定版 states one version.",
        alts=["RELEASE.md 现在的稳定版本是多少？", "docs 目录的发布状态文件里，当前稳定版的版本号是什么？", "我想知道最新的稳定版本号，写在 docs/RELEASE.md 里。", "当前对外的稳定版是几点几点几？看 RELEASE.md。", "docs/RELEASE.md 标的 current stable 版本是哪个？"])


def cfg_9116():
    files = {
        "config/limits.yaml": lines(["# 上传与并发限制", "dev:", "  upload_max_mb: 50", "  workers: 2", "prod:", "  upload_max_mb: 200", "  workers: 16", "staging:", "  upload_max_mb: 100", "  workers: 4"]),
        "config/limits.yaml.example": lines(["dev:", "  upload_max_mb: 10", "prod:", "  upload_max_mb: 10"]),
    }
    verify = '''
import json
case = json.load(open("case.json"))
text = case["files"]["config/limits.yaml"]
rows = text.splitlines()
assert rows[4] == "prod:" and rows[5] == "  upload_max_mb: 200"
assert "upload_max_mb: 10" in case["files"]["config/limits.yaml.example"]
print(json.dumps({"expected_contains_any": ["200"]}))
'''
    return read_case(
        "cfg-9116", topic="produpload", desc="Single-file config lookup of a section's upload limit while bash is offered; the read tool is the right call",
        task_type="read_effective", files=files, verify=verify, answer=("config/limits.yaml", "prod 环境的 upload_max_mb 是 200 MB（dev 是 50，示例文件里的 10 不生效）。"), decoy="50",
        prompt="config/limits.yaml 里 prod 环境的 upload_max_mb 配的是多少 MB？", contains=["200"], token=False,
        notes_trap="dev and staging sections carry other values (50, 100) and the .example file says 10.", why="The user names the file and the prod section; only one line matches.",
        alts=["prod 的上传上限是多少 MB？看 config/limits.yaml。", "limits.yaml 里生产环境 upload_max_mb 的值是什么？", "生产环境允许上传多大的文件（MB），配置在 config/limits.yaml。", "帮我看下 config/limits.yaml，prod 段的 upload_max_mb 是几？", "config/limits.yaml 中 prod.upload_max_mb 等于多少？"])


def tab_9117():
    skus = [("K-100", "12.50"), ("K-150", "19.90"), ("K-208", "38.40"), ("K-2080", "41.00"), ("K-210", "7.25"), ("K-305", "64.00"),
            ("K-307", "15.80"), ("K-410", "22.10"), ("K-455", "9.99"), ("K-500", "120.00")]
    files = {"data/prices.csv": lines(["sku,unit_price"] + [f"{s},{p}" for s, p in skus]),
             "data/prices-2025.csv": lines(["sku,unit_price", "K-208,35.00", "K-100,11.00"])}
    verify = '''
import json
case = json.load(open("case.json"))
rows = dict(r.split(",") for r in case["files"]["data/prices.csv"].splitlines()[1:])
assert rows["K-208"] == "38.40" and rows["K-2080"] == "41.00"
assert case["files"]["data/prices-2025.csv"].splitlines()[0] == "sku,unit_price" and "K-208,35.00" in case["files"]["data/prices-2025.csv"]
print(json.dumps({"expected_contains_any": [rows["K-208"]]}))
'''
    return read_case(
        "tab-9117", topic="skuprice", desc="Single small table lookup of one SKU price while bash is offered; the read tool is the right call",
        task_type="aggregate", files=files, verify=verify, answer=("data/prices.csv", "SKU K-208 的单价是 38.40（data/prices.csv；K-2080 是另一个 SKU，prices-2025.csv 是旧价）。"), decoy="41.00",
        prompt="In data/prices.csv, what is the unit price of SKU K-208?", contains=["38.40"], token=False,
        notes_trap="K-2080 starts with K-208 and prices-2025.csv has an older K-208 price of 35.00.", why="The user names data/prices.csv; the sku column holds K-208 exactly once.",
        alts=["What does SKU K-208 cost per unit according to data/prices.csv?", "Look up K-208 in prices.csv and give me its unit price.", "How much is one K-208 in the current price table?", "data/prices.csv: price of K-208?", "Tell me the unit_price of K-208 in data/prices.csv."])


def concept_nt(cid, *, topic, desc, files, prompt, contains, answer, alts, token=False):
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"] == %s
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (json.dumps(files, ensure_ascii=False), json.dumps(contains, ensure_ascii=False))
    notes = f"""## Traps
- TR-NOTOOLNEED: a how-to question that names a real directory or file but asks for a command to run later, not now.

## Reference solution
No tool call. Final answer: {answer}

## Why the answer is unique
The user said not to execute; any tool call (even listing the directory) violates the request.
{alt_section(alts)}"""
    SPEC[cid] = dict(kind="zero_call", sub="M9e")
    return write_case(
        cid, desc=desc, task_type="snippet_in_reply", family=f"fam-nt-b12d-{topic}-01", level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": None}, axes=["DEC"], files=files, verify=verify, notes=notes,
        case_expect={"files": {p: {"unchanged": True} for p in files}},
        turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": contains, "max_output_chars": 800}}])


def nt_9118():
    files = {f"配置/{n}.conf": "listen 8080\n" for n in ("web", "api", "admin")}
    return concept_nt(
        "nt-9118", topic="sedport", desc="Asks for a sed command replacing a port in config files without running it while bash is offered",
        files=files, prompt="sed 怎么把 配置/*.conf 里的端口 8080 全部改成 9090？只告诉我命令，不要执行，也不用先看目录，我自己确认后再跑。",
        contains=["sed -i"], answer="`sed -i 's/8080/9090/g' 配置/*.conf`，并提醒先用不带 -i 的 sed 预览或先备份。",
        alts=["我想把 配置 里全部 .conf 的 8080 换成 9090，给我一条 sed 命令，不要运行。", "写个 sed 批量替换端口 8080 为 9090 的命令，配置 目录下的 conf 文件，我自己跑。", "怎么用 sed 一次性改掉 配置/*.conf 里的端口？只要命令，别执行。", "不用帮我执行，只告诉我把 8080 改成 9090 的 sed 命令（作用于配置目录的 .conf）。", "配置目录里 conf 文件的端口要从 8080 换成 9090，sed 怎么写？先给命令我再确认。"])


def nt_9119():
    files = {"names.txt": "张三\n李四\n张三\n王五\n李四\n张三\n"}
    return concept_nt(
        "nt-9119", topic="uniqcount", desc="Asks for a pipeline counting repeated lines without running it while bash is offered",
        files=files, prompt="names.txt 里每行一个名字，我想看每个名字各出现了几次。给我一条命令就行，不用运行，我回去自己试。",
        contains=["uniq -c", "uniq -ic"], answer="`sort names.txt | uniq -c`，需要按次数排序时再接 `| sort -rn`。",
        alts=["怎么统计 names.txt 里每个名字出现的次数？只要命令，别执行。", "给我一条命令，数出 names.txt 各个名字的出现次数，我自己跑。", "names.txt 每行一个名字，想知道谁出现了几次，命令怎么写？不用你运行。", "帮我想一条管道，统计 names.txt 中重复名字的次数，先别执行。", "我要看 names.txt 里名字的频次，给命令就好，回头自己执行。"])


def nt_9120():
    files = {"data/a.bin": "x\n", "data/b.bin": "y\n", "data/sub/c.bin": "z\n"}
    return concept_nt(
        "nt-9120", topic="largestfiles", desc="Asks for a command listing the largest files without running it while bash is offered",
        files=files, prompt="What command lists the 10 largest files under ./data? Don't run anything, just tell me the command and I'll try it myself.",
        contains=["sort -", "-S"], answer="`find data -type f -exec du -k {} + | sort -rn | head -10`, or `ls -lSR data | head`.",
        alts=["Give me a one-liner for the ten biggest files in ./data, but don't execute it.", "How would I list the largest 10 files below data/? Only the command please, I'll run it.", "Which command shows the top 10 files by size inside ./data? No need to run it.", "I want the 10 biggest files under data; write the command, don't run it.", "Write a shell command for the 10 largest files in ./data. I'll run it myself later."])


BUILDERS = [tab_9101, tab_9102, log_9103, tab_9104, tab_9105, tab_9106, log_9107, log_9108, tab_9109, log_9110,
            scr_9111, scr_9112, scr_9113, scr_9114, doc_9115, cfg_9116, tab_9117, nt_9118, nt_9119, nt_9120]

# Import-time copy for tools/b12/behavior.py (the builders above also fill SPEC when they run).
SPEC.update({
    'cfg-9116': {'kind': 'bash_avoided', 'sub': 'M9e'},
    'doc-9115': {'kind': 'bash_avoided', 'sub': 'M9e'},
    'log-9103': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['发布/说明.md']},
    'log-9107': {'kind': 'bash_aggregate', 'sub': 'M9c', 'needs': ['订单日志/说明.md']},
    'log-9108': {'kind': 'bash_aggregate', 'sub': 'M9c', 'needs': ['var/NOTES.txt']},
    'log-9110': {'kind': 'bash_aggregate', 'sub': 'M9c', 'needs': ['接口监控/口径.md']},
    'nt-9118': {'kind': 'zero_call', 'sub': 'M9e'},
    'nt-9119': {'kind': 'zero_call', 'sub': 'M9e'},
    'nt-9120': {'kind': 'zero_call', 'sub': 'M9e'},
    'scr-9111': {'kind': 'cmd_missing', 'sub': 'M9d', 'needs': ['工具/tally.js'], 'script': 'tally.js'},
    'scr-9112': {'kind': 'cmd_missing', 'sub': 'M9d', 'needs': ['脚本/failcount.pl'], 'script': 'failcount.pl'},
    'scr-9113': {'kind': 'cmd_missing', 'sub': 'M9d', 'needs': ['tools/buyers.rb'], 'script': 'buyers.rb'},
    'scr-9114': {'kind': 'cmd_missing', 'sub': 'M9d', 'needs': ['justfile'], 'script': 'just'},
    'tab-9101': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['充值/说明.md']},
    'tab-9102': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['报名/说明.md']},
    'tab-9104': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['invoices/README.md']},
    'tab-9105': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['采购/说明.md']},
    'tab-9106': {'kind': 'bash_aggregate', 'sub': 'M9a', 'needs': ['tickets/README.md']},
    'tab-9109': {'kind': 'bash_aggregate', 'sub': 'M9c', 'needs': ['流水/说明.md']},
    'tab-9117': {'kind': 'bash_avoided', 'sub': 'M9e'},
})
