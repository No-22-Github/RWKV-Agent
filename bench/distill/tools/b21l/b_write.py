"""b21l sub write: read data, compute, write a report file (33317-33332)."""
from common import mk, L, rng, nv

B = []
BW = ["bash", "read_file", "write_file"]


def reg(f):
    B.append(f)
    return f


@reg
def c17():
    r = rng(17)
    cities = ["杭州", "苏州", "宁波", "无锡"]
    w = [5, 4, 3, 2]
    rows = ["订单号,城市,金额"]
    for i in range(210):
        rows.append("D%04d,%s,%d" % (6100 + i, r.choices(cities, w)[0], r.randint(20, 400)))
    files = {"订单/q3.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        from collections import Counter
        c = Counter(l.split(",")[1] for l in files["订单/q3.csv"].splitlines()[1:])
        order = sorted(c, key=lambda k: -c[k])
        return {"订单/城市订单.txt": "".join("%s=%d\n" % (k, c[k]) for k in order)}, [[order[0]]]
    mk("hyb-33317", sub="write", desc="Count orders per city from a csv and write city=count lines, name the top city", files=files,
       turns=[{"p": "订单/q3.csv 里每个城市各有多少笔订单？按订单数从多到少写到 订单/城市订单.txt，每行“城市=数量”，然后告诉我哪个城市最多。"}],
       compute=compute, must=BW, traps=["TR-HEADER"], loose=["订单/城市订单.txt"], notes="awk -F, count by $2 skipping line 1")


@reg
def c18():
    r = rng(18)
    rows = []
    for i in range(230):
        st = r.choices([200, 200, 200, 301, 404, 500, 502, 503], k=1)[0]
        rows.append("10.0.%d.%d - [15/Sep/2026:%02d:%02d:00] \"GET /p/%d\" %d %d" % (r.randint(0, 9), r.randint(1, 99), r.randint(0, 23), r.randint(0, 59), r.randint(1, 40), st, r.randint(200, 9000)))
    files = {"logs/access.log": "\n".join(rows) + "\n"}

    def compute(files, web):
        import re
        n = {"500": 0, "502": 0, "503": 0}
        for l in files["logs/access.log"].splitlines():
            m = re.search(r'" (\d{3}) \d+$', l)
            if m and m.group(1) in n:
                n[m.group(1)] += 1
        return {"logs/errors.txt": "".join("%s=%d\n" % (k, n[k]) for k in ("500", "502", "503"))}, [[str(n["500"])]]
    mk("hyb-33318", sub="write", desc="Count 500, 502 and 503 responses in an access log and write them to a report", files=files,
       turns=[{"p": "Count how many requests in logs/access.log ended with status 500, 502 and 503 and write logs/errors.txt with three lines like 500=<count>. Also tell me the 500 count."}],
       compute=compute, must=BW, traps=["TR-DECOY"], loose=["logs/errors.txt"], notes="status is the field before the byte size; sizes can equal 500 etc")


@reg
def c19():
    r = rng(19)
    rows = ["sku,名称,库存,安全库存"]
    for i in range(170):
        s = r.randint(5, 80)
        rows.append("K%03d,物料%d,%d,%d" % (i + 1, i + 1, r.randint(0, 120), s))
    files = {"仓库/库存.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        out = []
        for l in files["仓库/库存.csv"].splitlines()[1:]:
            a = l.split(",")
            if int(a[2]) < int(a[3]):
                out.append(a[0])
        return {"仓库/补货清单.txt": "".join(s + "\n" for s in out)}, [[str(len(out))]]
    mk("hyb-33319", sub="write", desc="List skus whose stock is below the safety stock into a restock file", files=files,
       turns=[{"p": "仓库/库存.csv 里库存低于安全库存的 sku 有哪些？每行一个编号写进 仓库/补货清单.txt（等于安全库存的不算），再告诉我一共几个。"}],
       compute=compute, must=BW, traps=["TR-HEADER"], loose=["仓库/补货清单.txt"], notes="awk $3<$4 on comma split")


@reg
def c20():
    r = rng(20)
    people = ["Mara", "Ilya", "Chen", "Dora", "Femi", "Gus"]
    rows = ["date,person,hours"]
    for i in range(190):
        rows.append("2026-09-%02d,%s,%s" % (r.randint(1, 15), r.choice(people), r.choice(["2", "3", "4", "6", "8"])))
    files = {"time/sheet.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        t = {}
        for l in files["time/sheet.csv"].splitlines()[1:]:
            d, p, h = l.split(",")
            t[p] = t.get(p, 0) + int(h)
        top = max(t, key=lambda k: t[k])
        return {"time/top.txt": "%s,%d\n" % (top, t[top])}, [[top]]
    mk("hyb-33320", sub="write", desc="Total hours per person from a timesheet and record the top person", files=files,
       turns=[{"p": "Who logged the most hours in time/sheet.csv? Write 'name,total' on one line to time/top.txt and tell me the name."}],
       compute=compute, must=BW, traps=["TR-HEADER"], notes="sum by person")


@reg
def c21():
    r = rng(21)
    apis = ["/api/user", "/api/order", "/api/cart", "/api/search", "/api/pay"]
    rows = []
    for i in range(200):
        rows.append("2026-09-14 %02d:%02d:%02d %s %dms" % (r.randint(0, 23), r.randint(0, 59), r.randint(0, 59), r.choice(apis), r.randint(40, 1400)))
    files = {"监控/latency.log": "\n".join(rows) + "\n"}

    def compute(files, web):
        slow = []
        for l in files["监控/latency.log"].splitlines():
            p = l.split()
            ms = int(p[3][:-2])
            slow.append((ms, p[2]))
        n = sum(1 for m, _ in slow if m > 800)
        worst = max(slow)[1]
        return {"监控/慢请求.txt": "数量=%d\n最慢接口=%s\n" % (n, worst)}, [[str(n), worst]]
    mk("hyb-33321", sub="write", desc="Count requests slower than 800 ms and find the slowest endpoint, write both to a file", files=files,
       turns=[{"p": "监控/latency.log 里耗时超过 800ms 的请求有多少个？最慢的那一次是哪个接口？写到 监控/慢请求.txt，两行：“数量=…”和“最慢接口=…”，也在这里告诉我。"}],
       compute=compute, must=BW, traps=["TR-DECOY"], loose=["监控/慢请求.txt"], notes="exactly 800 not slow")


@reg
def c22():
    r = rng(22)
    cats = ["Travel", "Meals", "Software", "Office"]
    rows = ["id,category,amount_usd"]
    for i in range(175):
        rows.append("E%03d,%s,%d" % (i + 1, r.choice(cats), r.randint(5, 90)))
    files = {"finance/expenses.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        t = {}
        for l in files["finance/expenses.csv"].splitlines()[1:]:
            a = l.split(",")
            t[a[1]] = t.get(a[1], 0) + int(a[2])
        big = max(t, key=lambda k: t[k])
        return {"finance/by_category.txt": "".join("%s: %d\n" % (k, t[k]) for k in ("Travel", "Meals", "Software", "Office"))}, [[big]]
    mk("hyb-33322", sub="write", desc="Sum expenses per category into a report and name the biggest category", files=files,
       turns=[{"p": "Total finance/expenses.csv by category and write finance/by_category.txt with lines like 'Travel: 123' for Travel, Meals, Software and Office (in that order). Which category cost the most?"}],
       compute=compute, must=BW, traps=["TR-HEADER"], loose=["finance/by_category.txt"], notes="sum column 3 grouped by column 2")


@reg
def c23():
    r = rng(23)
    cls = ["一班", "二班", "三班"]
    rows = ["姓名,班级,分数"]
    for i in range(165):
        rows.append("学生%03d,%s,%d" % (i + 1, r.choice(cls), r.randint(40, 100)))
    files = {"教务/期中.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        d = {}
        for l in files["教务/期中.csv"].splitlines()[1:]:
            n, c, s = l.split(",")
            d.setdefault(c, []).append(int(s))
        return {"教务/班级统计.txt": "".join("%s,%d,%d\n" % (c, len(d[c]), max(d[c])) for c in ("一班", "二班", "三班"))}, [["%s,%d,%d" % ("一班", len(d["一班"]), max(d["一班"]))]]
    mk("hyb-33323", sub="write", desc="Per-class head count and top score written as csv lines", files=files,
       turns=[{"p": "教务/期中.csv 里每个班有多少人、最高分是多少？写到 教务/班级统计.txt，每行“班级,人数,最高分”，按一班二班三班的顺序，并把一班那行念给我。"}],
       compute=compute, must=BW, traps=["TR-HEADER"], loose=["教务/班级统计.txt"], notes="group by column 2")


@reg
def c24():
    r = rng(24)
    rows = ["sensor,ts,temp_c"]
    for i in range(205):
        s = "S%02d" % r.randint(1, 14)
        rows.append("%s,%02d:%02d,%d" % (s, r.randint(0, 23), r.randint(0, 59), r.randint(55, 88)))
    files = {"iot/readings.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        hot = sorted({l.split(",")[0] for l in files["iot/readings.csv"].splitlines()[1:] if int(l.split(",")[2]) > 80})
        return {"iot/alerts.txt": "".join(s + "\n" for s in hot)}, [[str(len(hot))]]
    mk("hyb-33324", sub="write", desc="Collect sensors that ever read above 80 C into an alerts file sorted by name", files=files,
       turns=[{"p": "Which sensors in iot/readings.csv ever reported a temperature above 80? Put each sensor id once, sorted, one per line in iot/alerts.txt, and say how many there are."}],
       compute=compute, must=BW, traps=["TR-HEADER"], loose=["iot/alerts.txt"], notes="distinct sensors with temp>80")


@reg
def c25():
    r = rng(25)
    rows = ["用户,套餐,到期日"]
    for i in range(180):
        rows.append("u%03d,%s,2026-%02d-%02d" % (i + 1, r.choice(["基础", "专业", "团队"]), r.randint(7, 11), r.randint(1, 28)))
    files = {"会员/订阅.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        ex = [l.split(",")[0] for l in files["会员/订阅.csv"].splitlines()[1:] if l.split(",")[2] < "2026-09-16"]
        return {"会员/已到期.txt": "".join(u + "\n" for u in ex)}, [[str(len(ex))]]
    mk("hyb-33325", sub="write", desc="List subscribers whose end date is before 2026-09-16 into a file", files=files,
       turns=[{"p": "今天是 2026 年 9 月 16 日。会员/订阅.csv 里到期日早于今天的用户有多少个？把他们的用户名一行一个写到 会员/已到期.txt，并告诉我个数。"}],
       compute=compute, must=BW, traps=["TR-DATEFMT"], loose=["会员/已到期.txt"], notes="string compare on ISO dates; today itself is not expired")


@reg
def c26():
    r = rng(26)
    oses = ["ubuntu-22.04", "ubuntu-24.04", "debian-12", "rhel-9"]
    rows = ["host\tos\trole"]
    for i in range(160):
        rows.append("node%03d\t%s\t%s" % (i + 1, r.choices(oses, [4, 3, 2, 1])[0], r.choice(["web", "db", "batch"])))
    files = {"inventory/hosts.tsv": "\n".join(rows) + "\n"}

    def compute(files, web):
        c = {}
        for l in files["inventory/hosts.tsv"].splitlines()[1:]:
            o = l.split("\t")[1]
            c[o] = c.get(o, 0) + 1
        order = sorted(c, key=lambda k: (-c[k], k))
        return {"inventory/os_count.csv": "os,count\n" + "".join("%s,%d\n" % (k, c[k]) for k in order)}, [["%s,%d" % (order[0], c[order[0]])]]
    mk("hyb-33326", sub="write", desc="Count hosts per operating system from a tsv and write a csv, quote the biggest row", files=files,
       turns=[{"p": "Count the hosts per OS in inventory/hosts.tsv and save inventory/os_count.csv with the columns os,count (most common first). Paste me the first data row."}],
       compute=compute, must=BW, traps=["TR-DELIM"], loose=["inventory/os_count.csv"], notes="tab separated input")


@reg
def c27():
    r = rng(27)
    names = ["周岚", "吴凯", "郑宁", "孙悦", "冯琪", "韩立", "沈洁"]
    rows = ["日期,姓名,上班打卡"]
    for i in range(200):
        rows.append("2026-09-%02d,%s,%02d:%02d" % (r.randint(1, 15), r.choice(names), r.choice([8, 8, 8, 9, 9]), r.randint(0, 59)))
    files = {"考勤/打卡.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        c = {}
        for l in files["考勤/打卡.csv"].splitlines()[1:]:
            d, n, t = l.split(",")
            if t > "09:10":
                c[n] = c.get(n, 0) + 1
        late = sorted((k for k in c if c[k] >= 3), key=lambda k: (-c[k], k))
        return {"考勤/迟到.txt": "".join("%s=%d\n" % (k, c[k]) for k in late)}, [[late[0]]]
    mk("hyb-33327", sub="write", desc="Count late punches (after 09:10) per person and list those with three or more", files=files,
       turns=[{"p": "考勤/打卡.csv 里上班打卡晚于 9:10 算迟到。统计每个人迟到几次，只把迟到 3 次及以上的人写进 考勤/迟到.txt，格式“姓名=次数”，次数多的在前。迟到最多的是谁？"}],
       compute=compute, must=BW, traps=["TR-DEFN"], loose=["考勤/迟到.txt"], notes="09:10 exactly is on time")


@reg
def c28():
    r = rng(28)
    jobs = ["backup", "rotate", "reindex", "digest", "purge", "sync"]
    rows = []
    for i in range(240):
        rows.append("2026-09-%02d %s %s" % (r.randint(1, 15), r.choice(jobs), r.choices(["ok", "FAILED"], [3, 1])[0]))
    files = {"cron/history.log": "\n".join(rows) + "\n"}

    def compute(files, web):
        c = {}
        for l in files["cron/history.log"].splitlines():
            d, j, s = l.split()
            if s == "FAILED":
                c[j] = c.get(j, 0) + 1
        top = sorted(c, key=lambda k: (-c[k], k))[:3]
        return {"cron/worst.txt": "".join("%s %d\n" % (k, c[k]) for k in top)}, [[top[0]]]
    mk("hyb-33328", sub="write", desc="Rank cron jobs by FAILED runs and write the top three", files=files,
       turns=[{"p": "Which three jobs in cron/history.log failed most often? Write cron/worst.txt as 'job count' lines, worst first, and name the worst job."}],
       compute=compute, must=BW, traps=["TR-DECOY"], loose=["cron/worst.txt"], notes="count lines ending FAILED")


@reg
def c29():
    r = rng(29)
    rows = ["商品,单价,数量"]
    for i in range(185):
        rows.append("品%03d,%d,%d" % (i + 1, r.randint(3, 59), r.randint(1, 9)))
    files = {"销售/明细.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        t = 0
        for l in files["销售/明细.csv"].splitlines()[1:]:
            a = l.split(",")
            t += int(a[1]) * int(a[2])
        s = ["{:,}".format(t), str(t)]
        return {"销售/合计.txt": "合计=%d\n" % t}, [s]
    mk("hyb-33329", sub="write", desc="Total sales as the sum of price times quantity over all rows, saved as 合计=N", files=files,
       turns=[{"p": "销售/明细.csv 每行是单价和数量，帮我算出总销售额（单价×数量，全部加起来），写到 销售/合计.txt，格式“合计=数字”，数字不要加逗号，回复里也说一下。", "any": True}],
       compute=compute, must=BW + ["calculator"], traps=["TR-NUMFMT"], loose=["销售/合计.txt"], notes="awk sum $2*$3")


@reg
def c30():
    r = rng(30)
    rows = ["path,size_kb"]
    for i in range(195):
        ext = r.choice(["png", "jpg", "pdf", "mp4", "txt"])
        rows.append("assets/f%03d.%s,%d" % (i, ext, r.randint(4, 300)))
    files = {"audit/files.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        c = {}
        for l in files["audit/files.csv"].splitlines()[1:]:
            p, s = l.split(",")
            e = p.rsplit(".", 1)[1]
            c[e] = c.get(e, 0) + int(s)
        t = sorted(c, key=lambda k: (-c[k], k))
        return {"audit/by_ext.txt": "".join(".%s=%d\n" % (k, c[k]) for k in t)}, [[".%s=%d" % (t[0], c[t[0]])]]
    mk("hyb-33330", sub="write", desc="Total size per file extension from a listing and write them largest first", files=files,
       turns=[{"p": "From audit/files.csv, add up size_kb per file extension and write audit/by_ext.txt with lines like '.png=1234', largest total first. Tell me which extension takes the most space, in the same '.ext=total' form.", "any": True}],
       compute=compute, must=BW, traps=["TR-HEADER"], loose=["audit/by_ext.txt"], notes="split path at last dot")


@reg
def c31():
    r = rng(31)
    owners = ["罗敏", "高远", "唐薇", "袁朗"]
    rows = ["工单,负责人,状态"]
    for i in range(200):
        rows.append("T%04d,%s,%s" % (3000 + i, r.choices(owners, [4, 3, 2, 2])[0], r.choice(["已关闭", "处理中", "待分配", "已关闭"])))
    files = {"工单/本月.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        c = {}
        for l in files["工单/本月.csv"].splitlines()[1:]:
            t, o, s = l.split(",")
            if s != "已关闭":
                c[o] = c.get(o, 0) + 1
        t = sorted(c, key=lambda k: (-c[k], k))
        return {"工单/未关闭.txt": "".join("%s=%d\n" % (k, c[k]) for k in t)}, [[t[0]]]
    mk("hyb-33331", sub="write", desc="Open tickets per owner (anything not closed) written most-loaded first", files=files,
       turns=[{"p": "工单/本月.csv 里每个人手上还没关闭的工单各有多少（处理中和待分配都算）？按多到少写到 工单/未关闭.txt，“姓名=数量”，最后告诉我谁最多。"}],
       compute=compute, must=BW, traps=["TR-DEFN"], loose=["工单/未关闭.txt"], notes="exclude 已关闭")


@reg
def c32():
    r = rng(32)
    rows = ["insp_id,line,result"]
    for i in range(150):
        rows.append("I%04d,L%d,%s" % (i, r.randint(1, 4), r.choices(["pass", "defect"], [3, 1])[0]))
    for k in (7, 31, 90, 122):          # a few records were logged twice
        rows.append(rows[1 + k])
    r.shuffle(rows[1:]) if False else None
    files = {"qa/inspections.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        seen, c = set(), {}
        for l in files["qa/inspections.csv"].splitlines()[1:]:
            i, ln, res = l.split(",")
            if i in seen:
                continue
            seen.add(i)
            if res == "defect":
                c[ln] = c.get(ln, 0) + 1
        return {"qa/defects.txt": "".join("%s=%d\n" % (k, c.get(k, 0)) for k in ("L1", "L2", "L3", "L4")) + "total=%d\n" % sum(c.values())}, [[str(sum(c.values()))]]
    mk("hyb-33332", sub="write", desc="Defect counts per production line where repeated inspection ids count once", files=files,
       turns=[{"p": "Count the defect results per line (L1 to L4) in qa/inspections.csv. Some inspection ids got logged twice by mistake; count each id once. Write qa/defects.txt as L1=n .. L4=n and a final total=n line, and tell me the total."}],
       compute=compute, must=BW, traps=["TR-DUPROW"], loose=["qa/defects.txt"], notes="dedupe by insp_id")
