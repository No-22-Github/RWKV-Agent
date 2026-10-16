"""b21h sub 2 (column / separator traps) part b: 32318-32322."""
from common import make, csv, rng, L, NAMES, NOCALC, filler_keys, people, WORDS

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c18():
    r = rng(18)
    def sec(name, n, extra=()):
        return ["%s:" % name] + ["  %s: %d" % (k, r.randint(1, 500)) for k in filler_keys(r, n, avoid=("max_conn",))] + list(extra)
    rows = sec("limits", 20) + ["server:", "  host: 10.2.0.7", "  max_conn: 800", "  idle_timeout: 45"] + sec("tracing", 22) + ["storage:", "  data_dir: /srv/data", "  max_conn: 120"] + sec("alerts", 20) + sec("jobs", 16)
    f = {"app.yaml": L(*rows)}
    make("cfg-32318", sub="col", task_type="read_effective", desc="Read a yaml-style value with an equals-based lookup that finds nothing",
         files=f, turns=[("app.yaml 里 server 下面的 max_conn 是多少？", ["800"], None),
                         ("storage 下面那个呢？", ["120"], None)],
         truth="ans = '800'",
         ref=[("grep -n max_conn app.yaml", "800"), ("grep -n max_conn app.yaml", "120")],
         lazy=[("awk -F= '/max_conn/{print $2}' app.yaml | tr -d '\\n'", "empty"), ("grep -c 'max_conn=' app.yaml", "zero")],
         notes={"traps": "yaml uses colon, and the key occurs twice under different sections.", "steps": "grep -n max_conn, then read context.", "unique": "server 800, storage 120."}, policy=NOCALC)


@reg
def c19():
    r = rng(19)
    items = ["%s %s" % (a, b) for a in ["Copper", "Oak", "Linen", "Glass", "Brass", "Wool", "Tin", "Clay", "Birch", "Slate", "Cotton", "Maple"] for b in ["kettle", "shelf", "throw", "carafe", "hook", "rug", "lantern", "planter", "tray", "basket", "clock", "vase", "stool"]]
    rows = [("P%03d" % (i + 11), it, 100 + r.randint(5, 95)) for i, it in enumerate(items)]
    f = {"catalog.tsv": csv(["code", "title", "price"], rows, sep="\t")}
    code, title, price = rows[97]
    make("tab-32319", sub="col", task_type="filter_count", desc="Look up a price by code in a tsv catalog",
         files=f, turns=[("What is the price of %s in catalog.tsv?" % code, [str(price)], ["not found", "no such", "does not exist", "doesn't exist"])],
         truth="ans = [l.split('\\t')[2] for l in files['catalog.tsv'].splitlines()[1:] if l.split('\\t')[0] == '%s'][0]" % code,
         ref=[("awk -F'\\t' '$1==\"%s\"{print $3}' catalog.tsv" % code, str(price))],
         lazy=[("awk -F, '$1==\"%s\"{print $3}' catalog.tsv" % code, "empty")],
         notes={"traps": "Tab separated.", "steps": "head; awk -F'\\t'.", "unique": "One row."})


@reg
def c20():
    r = rng(20)
    shells = ["/bin/bash", "/bin/zsh", "/usr/sbin/nologin"]
    users = ["svc%02d" % i for i in range(60)] + ["deploy", "backup", "monitor", "builder", "reports", "etl", "mailer"] + ["job%02d" % i for i in range(40)]
    rows = ["%s:x:%d:%d:%s:/home/%s:%s" % (u, 1100 + i, 1100 + i, u.title(), u, shells[i % 3]) for i, u in enumerate(users)]
    sh = {u: shells[i % 3] for i, u in enumerate(users)}
    f = {"users.conf": "\n".join(rows) + "\n"}
    make("cfg-32320", sub="col", task_type="read_effective", desc="Read a field from a colon separated account file",
         files=f, turns=[("users.conf 里 builder 这个账号的 uid 是多少？", [str(1100 + users.index("builder"))], ["没有 builder", "找不到", "不存在"])],
         truth="ans = [l.split(':')[2] for l in files['users.conf'].splitlines() if l.split(':')[0] == 'builder'][0]",
         ref=[("awk -F: '$1==\"builder\"{print $3}' users.conf", str(1100 + users.index("builder")))],
         lazy=[("awk -F, '$1==\"builder\"{print $3}' users.conf", "empty")],
         notes={"traps": "Colon separated, no header.", "steps": "head; awk -F:.", "unique": "uid 1103."}, policy=NOCALC)


@reg
def c21():
    r = rng(21)
    regs = ["north", "south", "east", "west", "coast", "inland", "delta", "ridge", "plains", "harbor", "valley", "isles", "uplands", "marsh"]
    used = regs[:11]
    rows = [("R%03d" % (i + 1), used[i % 11] if i < 40 else r.choice(used), r.randint(20, 90)) for i in range(300)]
    text = L("# export 2026-09-14 by finance-bot", "# do not edit by hand", "# columns follow") + csv(["rid", "region", "score"], rows)
    f = {"regional_scores.csv": text}
    make("tab-32321", sub="col", task_type="aggregate", desc="Count distinct values of a column when the real header is on line 4",
         files=f, turns=[("How many different regions appear in regional_scores.csv?", ["11"], ["is 0", "no region", "not found", "no column"])],
         truth="ans = len(set(l.split(',')[1] for l in files['regional_scores.csv'].splitlines()[4:]))",
         ref=[("grep -v '^#' regional_scores.csv | awk -F, 'NR>1{print $2}' | sort -u | wc -l", "11")],
         lazy=[("head -1 regional_scores.csv | tr ',' '\\n' | grep -n region", "empty")],
         notes={"traps": "Comment lines precede the header.", "steps": "head -5; skip comment lines; distinct count.", "unique": "11 distinct."})


@reg
def c22():
    r = rng(22)
    us = ["admin"] * 136 + ["guest"] * 88 + ["ops"] * 64
    r.shuffle(us)
    lines = ["2026-09-1%d 1%d:%02d login ok user:%s ip=10.0.%d.%d" % (r.randint(0, 5), r.randint(0, 9), r.randint(0, 59), u, r.randint(0, 3), r.randint(2, 200)) for u in us]
    f = {"auth.log": "\n".join(lines) + "\n"}
    n = us.count("admin")
    make("log-32322", sub="col", task_type="count_events", desc="Count logins of a user whose field is written user:name instead of user=name",
         files=f, turns=[("auth.log 里 admin 登录了多少次？", [str(n)], ["共 0", "为 0", "有 0 次", "没有登录", "没有 admin"]),
                         ("guest 呢？", [str(us.count("guest"))], None)],
         truth="ans = sum(1 for l in files['auth.log'].splitlines() if 'user:admin ' in l)",
         ref=[("grep -c 'user:admin ' auth.log", str(n)), ("grep -c 'user:guest ' auth.log", str(us.count("guest")))],
         lazy=[("grep -c 'user=admin' auth.log", "zero")],
         notes={"traps": "Field is user:admin.", "steps": "head -2; grep.", "unique": "17 admin."})
