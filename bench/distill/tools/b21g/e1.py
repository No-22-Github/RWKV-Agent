"""b21g sub E: compute, then write a result file, 32243-32250."""
import json
from random import Random

from common import L, emit, jl, reg


@reg
def e1(i):
    rng = Random(3224300 + i * 7919)
    rows = [{"order": "O%05d" % (n * 3 + rng.randint(0, 2)), "status": rng.choices(["paid", "refunded", "pending", "cancelled"], [8, 2, 3, 2])[0],
             "amount": rng.randint(10, 990) if rng.random() < 0.92 else None} for n in range(rng.randint(420, 560))]
    files = {"orders/day.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(l) for l in files["orders/day.jsonl"].splitlines()]
        t = {}
        for r in rows:
            if r["amount"] is not None:
                t[r["status"]] = t.get(r["status"], 0) + r["amount"]
        out = "status,total\n" + "".join("%s,%d\n" % (k, t[k]) for k in sorted(t))
        return {"turns": [{"number": len(t), "items": []}], "files": {"orders/summary.csv": out}, "decoys": {}}
    emit("tab-32243", sub="writeout", task_type="write_summary", desc="Sums amounts per status from a JSONL with null amounts and writes a sorted two-column csv",
         files=files, solve=solve, traps=["TR-MISSING"],
         turns=[{"prompt": "orders/day.jsonl 是今天的订单。按 status 把 amount 加起来（没有金额的订单不算），写到 orders/summary.csv：第一行是表头 status,total，之后每个状态一行，格式 状态,合计，按状态名字母顺序排列。写完告诉我一共有几种状态。"}],
         ref=(["jq -rs 'map(select(.amount!=null))|group_by(.status)|map(\"\\(.[0].status),\\(map(.amount)|add)\")|.[]' orders/day.jsonl | sort | sed '1i status,total' > orders/summary.csv; wc -l < orders/summary.csv; cat orders/summary.csv"], 0),
         notes_traps=["TR-MISSING: some amounts are null."], notes_ref=["jq group_by status and sum, sort, prepend header, write file; report the count of statuses."],
         unique="Exact file content is determined by the stated format.")


@reg
def e2(i):
    rng = Random(3224400 + i * 7919)
    prods = ["Alder", "Birch", "Cedar", "Dogwood", "Elm", "Fir", "Ginkgo", "Hazel", "Ironwood"]
    rows = ["product,units,price"]
    for n in range(rng.randint(450, 600)):
        rows.append("%s,%d,%d" % (rng.choice(prods), rng.randint(1, 9), rng.randint(5, 80)))
    files = {"sales/week.csv": L(*rows), "report/.keep": "\n"}

    def solve(files):
        t = {}
        for l in files["sales/week.csv"].splitlines()[1:]:
            p, u, pr = l.split(",")
            t[p] = t.get(p, 0) + int(u) * int(pr)
        r = sorted(t.items(), key=lambda kv: -kv[1])[:3]
        assert r[2][1] > sorted(t.values())[-4]
        out = "".join("%d. %s: %d\n" % (k + 1, p, v) for k, (p, v) in enumerate(r))
        return {"turns": [{"number": r[0][1], "items": [r[0][0]]}, {"number": 3, "items": []}], "files": {"report/top3.txt": out}, "decoys": {}}
    emit("tab-32244", sub="writeout", task_type="write_summary", desc="Ranks products by units times price then writes the top three to a text file in a second turn",
         files=files, solve=solve, traps=["TR-DEFN"],
         turns=[{"prompt": "sales/week.csv has one sale per row (units sold at price each). Which product earned the most this week, and how much? Revenue is units times price, summed per product."},
                {"prompt": "Good. Write the top 3 products by revenue to report/top3.txt, one per line in the form `1. Name: revenue`, best first."}],
         ref=(["tail -n +2 sales/week.csv | awk -F, '{r[$1]+=$2*$3} END{for(p in r) print r[p], p}' | sort -rn | head -3 | awk '{printf \"%d. %s: %d\\n\", NR, $2, $1}' > report/top3.txt; cat report/top3.txt; echo 3"], 0),
         notes_traps=["TR-DEFN: revenue is units*price, not a plain row count or price sum."], notes_ref=["awk accumulate units*price per product, sort -rn, head -3, format into the file."], unique="Distinct top three revenues.")


@reg
def e3(i):
    rng = Random(3224500 + i * 7919)
    rows = [{"user": "u%03d" % rng.choices(range(1, 90), [rng.randint(1, 6) for _ in range(89)])[0], "event": rng.choices(["view", "purchase"], [5, 2])[0]} for _ in range(rng.randint(500, 700))]
    files = {"埋点/log.jsonl": jl(rows), "埋点/README.txt": "每行一个事件。\n"}

    def solve(files):
        c = {}
        for l in files["埋点/log.jsonl"].splitlines():
            r = json.loads(l)
            if r["event"] == "purchase":
                c[r["user"]] = c.get(r["user"], 0) + 1
        u = sorted(k for k, v in c.items() if v >= 4)
        assert len(u) >= 4
        return {"turns": [{"number": len(u), "items": []}], "files": {"埋点/heavy_users.txt": "".join(x + "\n" for x in u)}, "decoys": {}}
    emit("tab-32245", sub="writeout", task_type="write_summary", desc="Lists users with at least four purchases from a JSONL and writes their ids sorted into a text file",
         files=files, solve=solve, traps=["TR-DUPROW"],
         turns=[{"prompt": "埋点/log.jsonl 里 event 为 purchase 的是下单事件。把下单次数不少于 4 次的用户 id 写到 埋点/heavy_users.txt，一行一个，按 id 排序。写完告诉我一共有几个用户。"}],
         ref=(["jq -r 'select(.event==\"purchase\")|.user' 埋点/log.jsonl | sort | uniq -c | awk '$1>=4{print $2}' | sort > 埋点/heavy_users.txt; wc -l < 埋点/heavy_users.txt; cat 埋点/heavy_users.txt"], 0),
         notes_traps=["TR-DUPROW: one row per event, so users repeat."], notes_ref=["jq -r users of purchases | sort | uniq -c | awk filter >=4, write."], unique="Threshold inclusive, ids sorted.")


@reg
def e4(i):
    rng = Random(3224600 + i * 7919)
    files = {}
    for k in range(rng.randint(70, 100)):
        files["logs/%s/%s-%03d.%s" % (rng.choice(["api", "web", "job"]), rng.choice(["svc", "req", "err"]), k, rng.choice(["log", "log", "gz", "txt"]))] = "x" * rng.randint(10, 3000) + "\n"
    files["logs/index.csv"] = "path,bytes\n"

    def solve(files):
        rows = sorted((p, len(v.encode())) for p, v in files.items() if p.endswith(".log"))
        out = "path,bytes\n" + "".join("%s,%d\n" % r for r in rows)
        return {"turns": [{"number": len(rows), "items": []}], "files": {"logs/index.csv": out}, "decoys": {}}
    emit("fs-32246", sub="writeout", task_type="bulk_edit", desc="Builds a path,bytes index of every .log file in a 90-file tree into an existing index csv",
         files=files, solve=solve, traps=["TR-TRUNC"],
         turns=[{"prompt": "logs/index.csv currently only has a header line (path,bytes). Fill it in: one row per .log file anywhere under logs/ (not .gz or .txt), as path,bytes where path starts with logs/ and bytes is the file size, sorted by path. Keep the header. Then tell me how many rows you added."}],
         ref=(["find logs -type f -name '*.log' -exec wc -c {} + | grep -v ' total$' | awk '{print $2\",\"$1}' | sort > /tmp/rows.txt; (echo path,bytes; cat /tmp/rows.txt) > logs/index.csv; wc -l < /tmp/rows.txt; cat logs/index.csv"], 0),
         notes_traps=["TR-TRUNC: ~90 files so a listing is cut at 50."], notes_ref=["find -name '*.log' -exec wc -c; awk to path,bytes; sort; prepend header."], unique="Byte sizes and sorted paths are determined.")


@reg
def e5(i):
    rng = Random(3224700 + i * 7919)
    files = {}
    dirs = ["图片", "文档", "音频", "视频", "压缩包", "其它"]
    w = rng.sample(range(5, 60), len(dirs))
    for d, n in zip(dirs, w):
        for k in range(n):
            files["资料/%s/f%03d.dat" % (d, k)] = "d\n"
    files["资料/counts.txt"] = ""

    def solve(files):
        c = {}
        for p in files:
            if p.endswith(".dat"):
                d = p.split("/")[1]
                c[d] = c.get(d, 0) + 1
        top = max(c.items(), key=lambda kv: kv[1])
        out = "".join("%s %d\n" % (d, c[d]) for d in sorted(c))
        return {"turns": [{"number": top[1], "items": [top[0]]}, {"number": len(c), "items": []}], "files": {"资料/counts.txt": out}, "decoys": {"TR-TRUNC": 50}}
    emit("fs-32247", sub="writeout", task_type="count_by_type", desc="Finds the folder with most files, then writes per-folder counts into an existing empty text file",
         files=files, solve=solve, traps=["TR-TRUNC"],
         turns=[{"prompt": "资料 目录下有 6 个子目录，文件很多。哪个子目录里的文件最多？有多少个？"},
                {"prompt": "好，把每个子目录的文件数写进 资料/counts.txt，一行一个，格式“目录名 数量”（中间一个空格），按目录名排序。写完告诉我一共写了几行。"}],
         ref=(["find 资料 -type f -name '*.dat' | cut -d/ -f2 | sort | uniq -c | awk '{print $2\" \"$1}' | sort > 资料/counts.txt; wc -l < 资料/counts.txt; cat 资料/counts.txt"], 0),
         notes_traps=["TR-TRUNC: 150+ files."], notes_ref=["find | cut -d/ -f2 | sort | uniq -c, reformat, write."], unique="Counts are exact; file lines sorted by name (byte order).")


@reg
def e6(i):
    rng = Random(3224800 + i * 7919)
    files = {}
    for k in range(rng.randint(90, 130)):
        files["svc/%s/s%03d.yaml" % (rng.choice(["a", "b", "c"]), k)] = L("name: s%03d" % k, "enabled: %s" % rng.choice(["true", "false", "true"]), "port: %d" % rng.randint(2000, 9000))
    files["svc/disabled.txt"] = ""

    def solve(files):
        d = sorted(t.splitlines()[0].split(": ")[1] for p, t in files.items() if p.endswith(".yaml") and "enabled: false" in t.splitlines())
        return {"turns": [{"number": len(d), "items": []}], "files": {"svc/disabled.txt": "".join(x + "\n" for x in d)}, "decoys": {}}
    emit("cfg-32248", sub="writeout", task_type="read_effective", desc="Collects names of services with enabled false from 110 yaml files into an existing text file",
         files=files, solve=solve, traps=["TR-TRUNC"],
         turns=[{"prompt": "Under svc/ there are lots of yaml files, each with a name and an enabled flag. Put the names of the services where enabled is false into svc/disabled.txt, one name per line, sorted alphabetically. Then tell me how many there are."}],
         ref=(["grep -rl '^enabled: false' svc | xargs grep -h '^name:' | sed 's/name: //' | sort > svc/disabled.txt; wc -l < svc/disabled.txt; cat svc/disabled.txt"], 0),
         notes_traps=["TR-TRUNC: >100 files."], notes_ref=["grep -rl enabled: false | xargs grep -h name: | sed | sort > file."], unique="Names sorted bytewise.")


@reg
def e7(i):
    rng = Random(3224900 + i * 7919)
    files = {}
    for k in range(rng.randint(80, 110)):
        files["配置/w%03d.json" % k] = json.dumps({"name": "w%03d" % k, "timeout_ms": rng.choice([500, 800, 1000, 1500, 3000])}, indent=2) + "\n"
    files["配置/slow.txt"] = ""

    def solve(files):
        s = sorted(json.loads(t)["name"] for p, t in files.items() if p.endswith(".json") and json.loads(t)["timeout_ms"] > 1000)
        return {"turns": [{"number": len(s), "items": []}, {"number": len(s), "items": []}], "files": {"配置/slow.txt": "".join(x + "\n" for x in s)}, "decoys": {"TR-LONG": 50}}
    emit("cfg-32249", sub="writeout", task_type="read_effective", desc="Counts workers with timeout above 1000 ms in 100 json configs and then writes their names to a file",
         files=files, solve=solve, traps=["TR-TRUNC"],
         turns=[{"prompt": "配置 目录里每个 worker 一个 json。timeout_ms 大于 1000 的有多少个？"},
                {"prompt": "把这些 worker 的 name 写进 配置/slow.txt，一行一个，按名字排序。写完告诉我文件里有几行。"}],
         ref=(["jq -rs 'map(select(.timeout_ms>1000)|.name)|sort|.[]' 配置/w*.json > 配置/slow.txt; wc -l < 配置/slow.txt; cat 配置/slow.txt"], 0),
         notes_traps=["TR-TRUNC: ~100 files."], notes_ref=["jq -rs select timeout_ms>1000, names sorted, write; wc -l."], unique="Strict greater than 1000.")


@reg
def e8(i):
    rng = Random(3225000 + i * 7919)
    files = {}
    for k in range(rng.randint(100, 140)):
        files["owners/%s.cfg" % ("n%03d" % k)] = L("node=n%03d" % k, "team=%s" % rng.choice(["alpha", "beta", "gamma"]), "tier=%d" % rng.randint(1, 3))
    files["owners/summary.json"] = "{}\n"

    def solve(files):
        c = {}
        for p, t in files.items():
            if p.endswith(".cfg"):
                tm = [l.split("=")[1] for l in t.splitlines() if l.startswith("team=")][0]
                c[tm] = c.get(tm, 0) + 1
        out = "{" + ",".join('"%s":%d' % (k, c[k]) for k in sorted(c)) + "}\n"
        return {"turns": [{"number": len(c), "items": []}], "files": {"owners/summary.json": out}, "decoys": {}}
    emit("cfg-32250", sub="writeout", task_type="read_effective", desc="Counts node configs per team and writes a compact sorted JSON object into an existing file",
         files=files, solve=solve, traps=["TR-TRUNC"],
         turns=[{"prompt": "owners/ has one .cfg per node, each with a team= line. Count the nodes per team and replace owners/summary.json with a single-line JSON object mapping team to count, keys in alphabetical order, no spaces (for example {\"x\":1,\"y\":2}). Tell me how many teams there are."}],
         ref=(["grep -rh '^team=' owners | sed 's/team=//' | sort | uniq -c | awk 'BEGIN{printf \"{\"} {printf \"%s\\\"%s\\\":%d\", (NR>1?\",\":\"\"), $2, $1} END{print \"}\"}' > owners/summary.json; cat owners/summary.json; grep -c team owners/summary.json; echo 3"], 0),
         notes_traps=["TR-TRUNC: ~120 files."], notes_ref=["grep team lines | sort | uniq -c | awk to JSON object."], unique="Counts per team are exact; compact JSON with trailing newline.")
