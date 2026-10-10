"""M9a-c: bash for many-file aggregation, bulk edits and long files (b12 pilot)."""
from random import Random

from common import lines, write_case

REFS = {}  # case id -> (files, reference commands, check(stdout, root))


def has(*needles):
    return lambda out, _root: None if all(n in out for n in needles) else "ref stdout %r lacks %s" % (out[:200], needles)


def literal_free(files, value):
    """True when the answer literal appears nowhere in the fixture, so the
    sabotage test cannot hit an unrelated digit run (b10 pilot lesson)."""
    return not any(str(value) in text for text in files.values())


# ---------------------------------------------------------------- M9a aggregate


def log_9001():
    for seed in range(100):
        rng = Random(9001 + seed * 7919)
        files, total = {}, 0
        services = ["订单服务", "结算服务", "库存服务", "推送服务"]
        for day in range(1, 13):
            rows = ["时间,级别,服务,事件"]
            for i in range(rng.randint(40, 70)):
                event = rng.choice(["支付超时", "支付网关超时", "库存锁定失败", "推送成功", "订单创建", "支付成功"])
                total += event == "支付超时"
                rows.append(f"2026-09-{day:02d} {8 + i // 60:02d}:{i % 60:02d},{rng.choice(['WARN', 'ERROR', 'INFO'])},{rng.choice(services)},{event}")
            files[f"日志/2026-09/app-{day:02d}.csv"] = lines(rows)
        files["日志/说明.md"] = lines(["# 日志说明", "", "每天一个文件，逗号分隔：时间,级别,服务,事件。", "「支付网关超时」是上游网关的问题，不算我们自己的支付超时。"])
        if literal_free(files, total):
            break
    first_day = sum(r.split(",")[3] == "支付超时" for r in files["日志/2026-09/app-01.csv"].splitlines()[1:])
    substring = sum(t.count("支付超时") + t.count("支付网关超时") for p, t in files.items() if p.endswith(".csv"))
    verify = '''
import json
case = json.load(open("case.json"))
total = 0
for path, text in case["files"].items():
    if not path.endswith(".csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "时间,级别,服务,事件", path
    for row in rows[1:]:
        assert row.count(",") == 3, row
        total += row.split(",")[3] == "支付超时"
print(json.dumps({"expected_number": total}))
'''
    notes = f"""## Traps
- TR-MULTISRC: 12 daily files under 日志/2026-09/; any single file gives a plausible partial count.
- TR-DECOY: 「支付网关超时」 contains the substring 支付超时 but 日志/说明.md says it is the upstream gateway, not ours; a substring grep over-counts.

## Reference solution
1. bash: `cat 日志/2026-09/*.csv | awk -F, '$4=="支付超时"' | wc -l` (exact field match, not substring).
Final answer: 九月一共 {total} 次支付超时（按事件列精确等于「支付超时」统计，网关超时不算）。

## Why the answer is unique
The decoy is excluded by the field rule written in 日志/说明.md; counting by exact field over all 12 files gives one number.
"""
    REFS["log-9001"] = (files, ["cat 日志/2026-09/*.csv | awk -F, '$4==\"支付超时\"' | wc -l"], has(str(total)))
    return write_case(
        "log-9001", desc="Counts one exact event across twelve daily CSV logs where a longer event name contains it as a substring",
        task_type="count_events", family="fam-log-b12-paytimeout-01", level="L2", ref_calls=1,
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": str(first_day), "TR-DECOY": str(substring)}, axes=["CHN", "OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "九月份各天的日志里，我们自己的「支付超时」一共出现了多少次？",
                "expect": {"output_contains": [str(total)], "output_contains_token": True, "max_output_chars": 600}}])


def tab_9002():
    for seed in range(100):
        rng = Random(9002 + seed * 7919)
        files, total = {}, 0
        for month in range(3, 9):
            rows = ["order_id,sku,status,amount_usd"]
            for i in range(rng.randint(25, 45)):
                sku = rng.choice(["KX-200", "KX-310", "KXL-12", "MB-450", "PT-77"])
                status = rng.choice(["shipped", "shipped", "refunded", "cancelled"])
                cents = rng.randint(1500, 48000)
                if status == "refunded" and sku.startswith("KX-"):
                    total += cents
                rows.append(f"Q{month}{i:03d},{sku},{status},{cents // 100}.{cents % 100:02d}")
            files[f"exports/2026-{month:02d}/orders.csv"] = lines(rows)
        files["exports/README.md"] = lines(["Monthly order exports.", "KX- is the Kestrel line; KXL- is the unrelated Kestrel Lite accessory line."])
        value = f"{total // 100}.{total % 100:02d}"
        if literal_free(files, value):
            break

    def refund_cents(texts, prefix):
        cents = 0
        for text in texts:
            for row in text.splitlines()[1:]:
                _, sku, status, amount = row.split(",")
                if status == "refunded" and sku.startswith(prefix):
                    whole, frac = amount.split(".")
                    cents += int(whole) * 100 + int(frac)
        return f"{cents // 100}.{cents % 100:02d}"
    march_only = refund_cents([files["exports/2026-03/orders.csv"]], "KX-")
    with_lite = refund_cents([t for p, t in files.items() if p.endswith(".csv")], "KX")
    verify = '''
import json
case = json.load(open("case.json"))
cents = 0
for path, text in case["files"].items():
    if not path.endswith("orders.csv"):
        continue
    rows = text.splitlines()
    assert rows[0] == "order_id,sku,status,amount_usd", path
    for row in rows[1:]:
        oid, sku, status, amount = row.split(",")
        whole, frac = amount.split(".")
        if status == "refunded" and sku.startswith("KX-"):
            cents += int(whole) * 100 + int(frac)
print(json.dumps({"expected_number": cents / 100}))
'''
    notes = f"""## Traps
- TR-MULTISRC: six monthly exports; one month alone is a plausible wrong total.
- TR-DECOY: KXL- SKUs share the KX prefix but exports/README.md says they are a different line; `grep KX` over-counts.

## Reference solution
1. bash: `cat exports/*/orders.csv | awk -F, '$3=="refunded" && $2 ~ /^KX-/ {{s+=$4}} END{{printf "%.2f\\n", s}}'`
Final answer: refunds on the Kestrel (KX-) line from March to August total ${value}; KXL- accessories are excluded per exports/README.md.

## Why the answer is unique
Status and SKU are exact fields; the README pins KX- versus KXL-.
"""
    REFS["tab-9002"] = (files, ["cat exports/*/orders.csv | awk -F, '$3==\"refunded\" && $2 ~ /^KX-/ {s+=$4} END{printf \"%.2f\\n\", s}'"], has(value))
    return write_case(
        "tab-9002", desc="Sums refunded amounts for one SKU family across six monthly exports with a look-alike prefix",
        task_type="aggregate", family="fam-tab-b12-refundsum-01", level="L2", ref_calls=1,
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": march_only, "TR-DECOY": with_lite}, axes=["CHN", "OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "How much did we refund on the Kestrel line across the March to August order exports?",
                "expect": {"output_contains": [value], "output_contains_token": True, "max_output_chars": 600}}])


# ---------------------------------------------------------------- M9b bulk edit


def cfg_9003():
    rng = Random(9003)
    files, expect_files = {}, {}
    for svc in ["网关", "账单", "搜索", "推荐", "通知"]:
        body = lines([f"服务名={svc}", f"端口={rng.randint(7000, 9800)}", "日志级别=debug   # 上线前改回 info",
                      f"并发={rng.choice([8, 16, 32])}"])
        path = f"部署/{svc}/服务.env"
        files[path] = body
        expect_files[path] = {"equals": body.replace("日志级别=debug", "日志级别=info")}
    files["部署/归档/2025-旧网关/服务.env"] = lines(["服务名=旧网关", "日志级别=debug"])
    files["部署/说明.md"] = lines(["# 部署", "", "每个服务一个目录；归档/ 下是下线服务的留档，审计要求原样保留。"])
    expect_files["部署/归档/2025-旧网关/服务.env"] = {"unchanged": True}
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["部署/说明.md"].startswith("# 部署" + chr(10)), "说明.md header"
assert "归档/ 下是下线服务的留档" in case["files"]["部署/说明.md"]
out = {}
for path, text in case["files"].items():
    if path.endswith("服务.env") and "/归档/" not in path:
        assert "日志级别=debug   # 上线前改回 info" in text, path
        out[path] = text.replace("日志级别=debug", "日志级别=info")
print(json.dumps({"files": out}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-READONLY: 部署/归档/ also has 日志级别=debug; 部署/说明.md says archives stay byte-identical.

## Reference solution
1. bash: `find 部署 -name 服务.env | grep -v /归档/ | xargs sed -i 's/日志级别=debug/日志级别=info/'`
2. bash: `grep -rn 日志级别 部署` to confirm five services changed and the archive did not.
Final answer: 五个服务的 服务.env 都改成了 日志级别=info，行尾注释保留；归档目录没动。

## Why the answer is unique
Only the value changes; the trailing comment and the archive must stay as they are.
"""
    def check(_out, root):
        import os
        for path, rule in expect_files.items():
            text = open(os.path.join(root, path), encoding="utf-8").read()
            want = rule.get("equals", files[path])
            if text != want:
                return "%s = %r" % (path, text)
        return None
    REFS["cfg-9003"] = (files, ["find 部署 -name 服务.env | grep -v /归档/ | xargs sed -i 's/日志级别=debug/日志级别=info/'",
                                "grep -rn 日志级别 部署"], check)
    return write_case(
        "cfg-9003", desc="Flips one value in five service env files while an archived copy must stay untouched",
        task_type="edit_value", family="fam-cfg-b12-loglevel-01", level="L1", ref_calls=2,
        traps=["TR-READONLY"], decoys={"TR-READONLY": None}, axes=["CON"],
        files=files, verify=verify, notes=notes, case_expect={"files": expect_files},
        turns=[{"prompt": "要上线了，把 部署 下各个服务的日志级别从 debug 改回 info，注释别动。改完回复 DONE。",
                "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


def fs_9004():
    rng = Random(9004)
    files, expect_files, moved = {}, {}, 0
    for i in range(16):
        month = rng.randint(1, 9)
        day = rng.randint(1, 28)
        name = f"inv-2026-{month:02d}-{day:02d}-{rng.randint(100, 999)}.pdf"
        body = f"%PDF-invoice {name} total {rng.randint(100, 9000)}\n"
        files[f"inbox/{name}"] = body
        if month <= 6:
            moved += 1
            expect_files[f"inbox/{name}"] = {"absent": True}
            expect_files[f"archive/2026H1/{name}"] = {"equals": body}
        else:
            expect_files[f"inbox/{name}"] = {"unchanged": True}
    files["inbox/notes.txt"] = "Invoices are named inv-YYYY-MM-DD-<seq>.pdf by issue date.\n"
    files["archive/2026H1/.keep"] = ""
    verify = '''
import json, re
case = json.load(open("case.json"))
assert case["files"]["inbox/notes.txt"].startswith("Invoices are named inv-YYYY-MM-DD-<seq>.pdf by issue date.")
out = {}
for path, text in case["files"].items():
    m = re.fullmatch(r"inbox/(inv-2026-(\\d\\d)-\\d\\d-\\d{3}\\.pdf)", path)
    if m and int(m.group(2)) <= 6:
        assert text.startswith("%PDF-invoice " + m.group(1)), path
        out["archive/2026H1/" + m.group(1)] = text
print(json.dumps({"files": out}))
'''
    notes = f"""## Traps
None beyond the date rule: the issue month is in the file name ({moved} invoices fall in January-June).

## Reference solution
1. bash: `for f in inbox/inv-2026-0[1-6]-*.pdf; do mv "$f" archive/2026H1/; done`
2. bash: `ls inbox archive/2026H1` to confirm.
Final answer: moved the {moved} invoices dated January to June 2026 into archive/2026H1/; the later ones and notes.txt stay in inbox/.

## Why the answer is unique
The month field of each name decides membership; nothing else moves.
"""
    def check(_out, root):
        import os
        for path, rule in expect_files.items():
            exists = os.path.exists(os.path.join(root, path))
            if rule.get("absent") == exists:
                return "%s presence wrong" % path
        return None
    REFS["fs-9004"] = (files, ['for f in inbox/inv-2026-0[1-6]-*.pdf; do mv "$f" archive/2026H1/; done', "ls inbox archive/2026H1"], check)
    return write_case(
        "fs-9004", desc="Moves first-half-year invoices into an archive folder by the date encoded in each file name",
        task_type="bulk_edit", family="fam-fs-b12-invoicearchive-01", level="L0", ref_calls=2,
        files=files, verify=verify, notes=notes, case_expect={"files": expect_files},
        turns=[{"prompt": "Move every invoice in inbox issued in the first half of 2026 into archive/2026H1, and leave the rest where they are. Reply DONE when finished.",
                "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


# ---------------------------------------------------------------- M9c long files


def log_9005():
    rng = Random(9005)
    rows, last = [], None
    for i in range(2600):
        ts = f"2026-09-1{4 + i // 1000} {(i // 60) % 24:02d}:{i % 60:02d}:{rng.randint(10, 59)}"
        event = rng.choices(["请求转发", "熔断打开", "熔断关闭", "健康检查通过", "熔断半开"], [80, 2, 2, 14, 2])[0]
        if event == "熔断打开":
            last = ts
        rows.append(f"[{ts}] 网关 节点{rng.randint(1, 6)} {event} 上游=库存服务 耗时={rng.randint(3, 900)}ms")
    files = {"网关日志/gateway.log": lines(rows), "网关日志/README.md": f"按时间顺序追加写入，导出时共 {len(rows)} 行。\n"}
    head = files["网关日志/gateway.log"].encode()[:64 * 1024].decode(errors="ignore")
    trunc_last = [r for r in head.splitlines() if "熔断打开" in r][-1][1:20]
    any_last = [r for r in rows if "熔断" in r][-1][1:20]
    assert len(files["网关日志/gateway.log"].encode()) > 64 * 1024
    verify = '''
import json, re
case = json.load(open("case.json"))
rows = case["files"]["网关日志/gateway.log"].splitlines()
declared = int(case["files"]["网关日志/README.md"].split("共 ")[1].split(" 行")[0])
assert len(rows) == declared, (len(rows), declared)
last = None
prev = ""
for row in rows:
    m = re.fullmatch(r"\\[(2026-09-\\d\\d \\d\\d:\\d\\d:\\d\\d)\\] 网关 节点\\d (\\S+) 上游=库存服务 耗时=\\d+ms", row)
    assert m, row
    if m.group(2) == "熔断打开":
        last = m.group(1)
print(json.dumps({"expected_string": last}))
'''
    notes = f"""## Traps
- TR-TRUNC: gateway.log is ~{len(files['网关日志/gateway.log'].encode()) // 1024}KB, past read_file's 64KB cap and bash's 8KB output cap; the last event sits near the end.
- TR-DECOY: 熔断半开 / 熔断关闭 lines are not the open event.

## Reference solution
1. bash: `grep 熔断打开 网关日志/gateway.log | tail -1`
Final answer: 最后一次熔断打开是 {last}（网关日志/gateway.log 末尾那条），之后没有再打开。

## Why the answer is unique
The log is append-only in time order (README), so the last matching line is the latest event.
"""
    REFS["log-9005"] = (files, ["grep 熔断打开 网关日志/gateway.log | tail -1"], has(last))
    return write_case(
        "log-9005", desc="Finds the last circuit-open event in a gateway log larger than the read cap",
        task_type="locate_error", family="fam-log-b12-breaker-01", level="L2", ref_calls=1,
        traps=["TR-TRUNC", "TR-DECOY"], decoys={"TR-TRUNC": trunc_last, "TR-DECOY": any_last}, axes=["LNG", "OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "网关最近一次熔断打开是什么时候？",
                "expect": {"output_contains": [last], "max_output_chars": 600}}])


def log_9006():
    for seed in range(100):
        rng = Random(9006 + seed * 7919)
        rows, ids = [], set()
        for i in range(2400):
            rid = "req-" + "".join(rng.choice("bcdfghjkmnpqrstvwxz") for _ in range(3))
            status = rng.choices([200, 429, 503, 201], [80, 9, 4, 7])[0]
            if status == 429:
                ids.add(rid)
            rows.append(f"ts=2026-09-15T{(i // 60) % 24:02d}:{i % 60:02d}:00Z request_id={rid} route=/v2/quote status={status} retry={rng.choice(['none', 'short', 'long'])}")
        files = {"traces/edge.log": lines(rows), "traces/NOTES.txt": f"edge.log: one line per attempt, {len(rows)} lines at export.\n"}
        count = len(ids)
        if literal_free(files, count) and len(files["traces/edge.log"].encode()) > 64 * 1024:
            break
    head = files["traces/edge.log"].encode()[:64 * 1024].decode(errors="ignore").splitlines()
    trunc_count = len({r.split()[1] for r in head if "status=429" in r and len(r.split()) == 5})
    line_count = sum("status=429" in r for r in rows)
    verify = '''
import json, re
case = json.load(open("case.json"))
ids = set()
rows = case["files"]["traces/edge.log"].splitlines()
declared = int(case["files"]["traces/NOTES.txt"].split(", ")[1].split(" lines")[0])
assert len(rows) == declared, (len(rows), declared)
for row in rows:
    m = re.fullmatch(r"ts=\\S+ request_id=(req-[a-z]{3}) route=/v2/quote status=(\\d+) retry=(none|short|long)", row)
    assert m, row
    if m.group(2) == "429":
        ids.add(m.group(1))
print(json.dumps({"expected_number": len(ids)}))
'''
    notes = f"""## Traps
- TR-TRUNC: edge.log is past every read cap.
- TR-DUPROW-like: the same request_id is throttled more than once; counting lines over-counts. Answer counts distinct request IDs.

## Reference solution
1. bash: `grep 'status=429' traces/edge.log | sed 's/.*request_id=\\([^ ]*\\).*/\\1/' | sort -u | wc -l`
Final answer: {count} distinct requests were throttled with 429 (unique request_id values in traces/edge.log; repeats of the same request are counted once).

## Why the answer is unique
The prompt asks for requests, not log lines.
"""
    REFS["log-9006"] = (files, ["grep 'status=429' traces/edge.log | sed 's/.*request_id=\\([^ ]*\\).*/\\1/' | sort -u | wc -l"], has(str(count)))
    return write_case(
        "log-9006", desc="Counts distinct throttled request IDs in an edge trace larger than the read cap",
        task_type="count_events", family="fam-log-b12-throttle-01", level="L2", ref_calls=1,
        traps=["TR-TRUNC", "TR-DUPROW"], decoys={"TR-TRUNC": str(trunc_count), "TR-DUPROW": str(line_count)}, axes=["LNG", "OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "How many different requests got throttled with a 429 in traces/edge.log?",
                "expect": {"output_contains": [str(count)], "output_contains_token": True, "max_output_chars": 600}}])


BUILDERS = [log_9001, tab_9002, cfg_9003, fs_9004, log_9005, log_9006]
