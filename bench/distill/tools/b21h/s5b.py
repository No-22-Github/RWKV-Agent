"""b21h sub 5 (command unavailable or erroring) part b: 32345-32350."""
import json

from common import make, csv, rng, L, NAMES, NOCALC, filler_keys

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c45():
    r = rng(45)
    base = {14: 1789387200, 15: 1789473600, 16: 1789560000}
    days = [r.choice([14, 15, 15, 16, 16]) for _ in range(260)]
    rows = [("T%03d" % (i + 1), base[d] + r.randint(-10000, 10000), r.randint(10, 90)) for i, d in enumerate(days)]
    f = {"sales_epoch.csv": csv(["tid", "epoch", "amount"], rows)}
    n15, n16 = days.count(15), days.count(16)
    cmd = "awk -F, 'NR>1{print $2}' sales_epoch.csv | while read e; do date -d @$e +%%F; done | grep -c 2026-09-%d"
    make("tab-32345", sub="cmd", task_type="filter_count", desc="Count orders of a day from epoch timestamps after awk strftime is not implemented",
         files=f, turns=[("sales_epoch.csv 里 epoch 是时间戳。请用 awk 的 strftime 把它转成日期，然后数一下 9 月 15 日有多少单。", [str(n15)], ["无法转换", "没法转换", "不支持 strftime"]),
                         ("9 月 16 日呢？", [str(n16)], None)],
         truth="import datetime\nans = sum(1 for l in files['sales_epoch.csv'].splitlines()[1:] if datetime.datetime.fromtimestamp(int(l.split(',')[1]), datetime.timezone.utc).day == 15)",
         ref=[(cmd % 15, str(n15)), (cmd % 16, str(n16))],
         lazy=[("awk -F, 'NR>1{print strftime(\"%F\",$2)}' sales_epoch.csv", "err")],
         notes={"traps": "awk strftime is not implemented; use date -d @.", "steps": "loop date -d @epoch +%F | grep -c.", "unique": "days from the epochs."})


@reg
def c46():
    r = rng(46)
    vals = [r.randint(120, 380) for _ in range(200)]
    vals[111] = 482
    rows = [("r%02d" % (i + 1), v) for i, v in enumerate(vals)]
    f = {"scores.csv": csv(["run", "score"], rows)}
    make("tab-32346", sub="cmd", task_type="rank", desc="Max of a column after csvstat is not installed",
         files=f, turns=[("Run csvstat on scores.csv and tell me the maximum score.", ["482"], ["cannot", "can't", "unable", "not installed"])],
         truth="ans = str(max(int(l.split(',')[1]) for l in files['scores.csv'].splitlines()[1:]))",
         ref=[("awk -F, 'NR>1&&$2>m{m=$2}END{print m}' scores.csv", "482")],
         lazy=[("csvstat scores.csv", "err")],
         notes={"traps": "csvstat missing.", "steps": "awk max.", "unique": "482."})


@reg
def c47():
    r = rng(47)
    codes = [r.choice([200, 200, 200, 301, 404, 500, 502, 503]) for _ in range(300)]
    lines = [json.dumps({"ts": "2026-09-15T%02d:%02d" % (r.randint(0, 23), r.randint(0, 59)), "path": r.choice(["/a", "/b", "/c"]), "status": c}) for c in codes]
    n = sum(1 for c in codes if c >= 500)
    f = {"api.jsonl": "\n".join(lines) + "\n"}
    make("log-32347", sub="cmd", task_type="aggregate_jsonl", desc="Count 5xx responses in jsonl after python parsing is unavailable",
         files=f, turns=[("请用 python 解析 api.jsonl，统计状态码是 5xx 的请求有多少条。", [str(n)], ["无法解析", "没法解析", "无法统计"])],
         truth="import json\nans = sum(1 for l in files['api.jsonl'].splitlines() if json.loads(l)['status'] >= 500)",
         ref=[("grep -cE '\"status\": 5[0-9][0-9]' api.jsonl", str(n)), ("jq -s '[.[]|select(.status>=500)]|length' api.jsonl", str(n))],
         lazy=[("python3 -c \"import json;print(sum(json.loads(l)['status']>=500 for l in open('api.jsonl')))\"", "err")],
         notes={"traps": "python missing; jq or grep -E work.", "steps": "jq -s or grep.", "unique": "5xx count."})


@reg
def c48():
    r = rng(48)
    extra = []
    for k in range(16):
        extra += ["", "[svc%02d]" % k, "host = svc%02d.internal" % k, "pool = %d" % r.randint(1, 900)] + ["%s = %d" % (a, r.randint(1, 900)) for a in filler_keys(r, 3, avoid=("pool",))]
    f = {"app.ini": L("[db]", "host = pg-3.internal", "pool = 250", "", "[cache]", "host = redis-2.internal", "pool = 64", "", "[web]", "pool = 32", *extra)}
    make("cfg-32348", sub="cmd", task_type="read_effective", desc="Read a section value after python configparser is unavailable",
         files=f, turns=[("用 python 的 configparser 读一下 app.ini，[db] 段的 pool 是多少？", ["250"], ["无法读取", "没法读取", "读取失败"]),
                         ("[cache] 段的呢？", ["64"], None)],
         truth="ans = '250'",
         ref=[("awk '/^\\[/{s=$0} s==\"[db]\" && /^pool/' app.ini", "250"), ("awk '/^\\[/{s=$0} s==\"[cache]\" && /^pool/' app.ini", "64")],
         lazy=[("python3 -c \"import configparser as c;p=c.ConfigParser();p.read('app.ini');print(p['db']['pool'])\"", "err")],
         notes={"traps": "pool appears in three sections; python missing.", "steps": "awk with section tracking or sed range.", "unique": "db 250, cache 64."}, policy=NOCALC)


@reg
def c49():
    r = rng(49)
    regs = [r.choice(["华南", "华东", "华北"]) for _ in range(200)]
    rows = [("K%03d" % (i + 1), g, r.randint(1, 9)) for i, g in enumerate(regs)]
    f = {"revenue.csv": csv(["kid", "region", "revenue"], rows)}
    t = sum(x[2] for x in rows if x[1] == "华南")
    make("tab-32349", sub="cmd", task_type="aggregate", desc="Group sum after miller is not installed",
         files=f, turns=[("用 mlr 按 region 汇总 revenue.csv 的 revenue，我要知道华南的总收入。", [str(t)], ["无法汇总", "没法汇总", "无法统计"])],
         truth="ans = sum(int(l.split(',')[2]) for l in files['revenue.csv'].splitlines()[1:] if l.split(',')[1] == '华南')",
         ref=[("awk -F, '$2==\"华南\"{s+=$3}END{print s}' revenue.csv", str(t))],
         lazy=[("mlr --icsv --opprint stats1 -a sum -f revenue -g region revenue.csv", "err")],
         notes={"traps": "mlr missing.", "steps": "awk group sum.", "unique": "sum of 华南."})


@reg
def c50():
    r = rng(50)
    vals = r.sample(range(100, 1000), 301)
    rows = [("q%02d" % (i + 1), v) for i, v in enumerate(vals)]
    f = {"latency.csv": csv(["probe", "ms"], rows)}
    med = sorted(vals)[150]
    make("tab-32350", sub="cmd", task_type="rank", desc="Median where awk asort silently yields nothing",
         files=f, turns=[("What is the median of the ms column in latency.csv? Sort it with awk's asort if you like.", [str(med)], ["no median", "cannot", "can't", "unable"])],
         truth="ans = str(sorted(int(l.split(',')[1]) for l in files['latency.csv'].splitlines()[1:])[150])",
         ref=[("awk -F, 'NR>1{print $2}' latency.csv | sort -n | sed -n '151p'", str(med))],
         lazy=[("awk -F, 'NR>1{a[NR]=$2}END{n=asort(a);print a[int((n+1)/2)]}' latency.csv", "empty")],
         notes={"traps": "asort prints nothing in this awk.", "steps": "sort -n | sed -n 21p.", "unique": "301 distinct values, median is the 151st."}, policy=NOCALC)
