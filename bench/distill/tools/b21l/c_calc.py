"""b21l sub calc: take rates from a web page, quantities from local files, compute (33333-33348)."""
from common import mk, page, L, rng, nv, nv2, WEB

B = []
BC = WEB + ["read_file", "calculator"]


def reg(f):
    B.append(f)
    return f


@reg
def c33():
    web = [page("欧元", "https://fx.tianhe-bank.cn/daily", "天河银行 外汇牌价", "每日外汇中间价。",
                "# 外汇中间价（2026-09-15）\n\n欧元/人民币：7.85\n美元/人民币：7.12\n日元/人民币（100日元）：4.82\n", "2026-09-15"),
           page("欧元", "https://finance-blog.example.cn/eur-2025", "欧元汇率回顾", "2025 年欧元走势。", "2025年底欧元/人民币约 7.62。\n", "2025-12-30")]
    files = {"采购/欧洲订单.csv": L("订单,供应商,金额_EUR", "P-101,Brandl GmbH,1200", "P-102,Maison Clerc,860", "P-103,Studio Voss,455")}

    def compute(files, web):
        import re
        pg = [w for w in web if "tianhe-bank" in w["url"]][0]["content"]
        rate = float(re.search(r"欧元/人民币：([\d.]+)", pg).group(1))
        tot = sum(int(l.split(",")[2]) for l in files["采购/欧洲订单.csv"].splitlines()[1:]) * rate
        tot = round(tot, 2)
        v = ["%.2f" % tot, ("%.2f" % tot).rstrip("0").rstrip("."), "{:,.2f}".format(tot), "{:,.0f}".format(tot) if tot == int(tot) else "{:,.2f}".format(tot)]
        return {}, [list(dict.fromkeys(v))]
    mk("hyb-33333", sub="calc", desc="Convert euro purchase orders to CNY at the bank's published middle rate", files=files, web=web,
       turns=[{"p": "采购/欧洲订单.csv 里的三笔订单都是欧元，按天河银行外汇牌价页上的欧元中间价，折合人民币一共多少？", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-DIRMAP", "TR-WEBSTALE"], notes="2515 * 7.85 = 19742.75")


@reg
def c34():
    web = [page("Zephyr Freight", "https://zephyrfreight.com/rates", "Zephyr Freight rate card", "Per-kilogram rates by delivery zone.",
                "# Rate card (effective 2026-09-01)\n\nZone A: $2.40 per kg\nZone B: $3.15 per kg\nZone C: $4.80 per kg\n\nMinimum charge per parcel: none.\n", "2026-09-01")]
    files = {"shipping/parcels.csv": L("parcel,weight_kg,zone", "A1,12,A", "A2,5,B", "A3,8,C", "A4,20,A", "A5,3,B", "A6,15,C", "A7,9,B")}

    def compute(files, web):
        import re
        pg = [w for w in web if "zephyrfreight" in w["url"]][0]["content"]
        rt = {z: float(p) for z, p in re.findall(r"Zone (\w): \$([\d.]+) per kg", pg)}
        t = round(sum(int(l.split(",")[1]) * rt[l.split(",")[2]] for l in files["shipping/parcels.csv"].splitlines()[1:]), 2)
        return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t)]))]
    mk("hyb-33334", sub="calc", desc="Shipping cost for a parcel list using the carrier's per-kg zone rates", files=files, web=web,
       turns=[{"p": "What will it cost to ship everything in shipping/parcels.csv at Zephyr Freight's per-kilogram rates for each parcel's zone? Give me the total in dollars.", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-SNIPPETVAGUE"], notes="sum weight*zone rate")


@reg
def c35():
    web = [page("分时电价", "https://www.northgrid.cn/tariff/commercial", "北网 工商业分时电价", "峰谷平电价标准。",
                "# 工商业分时电价（2026年9月起）\n\n峰时：1.08 元/度\n平时：0.72 元/度\n谷时：0.36 元/度\n\n峰时 8:00-11:00、18:00-22:00；谷时 23:00-次日7:00。\n", "2026-08-28")]
    files = {"车间/9月用电.csv": L("日期区间,峰时_度,平时_度,谷时_度", "1-10日,3200,5400,2100", "11-20日,3500,5900,2300", "21-30日,3100,5200,2000")}

    def compute(files, web):
        import re
        pg = [w for w in web if "northgrid" in w["url"]][0]["content"]
        p, n, g = [float(re.search(k + r"：([\d.]+) 元/度", pg).group(1)) for k in ("峰时", "平时", "谷时")]
        rows = [list(map(int, l.split(",")[1:])) for l in files["车间/9月用电.csv"].splitlines()[1:]]
        t = round(sum(a * p + b * n + c * g for a, b, c in rows), 2)
        return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t), "{:,.0f}".format(t)]))]
    mk("hyb-33335", sub="calc", desc="Monthly electricity bill from time-of-use prices on a utility page and a usage table", files=files, web=web,
       turns=[{"p": "按北网现在公布的工商业分时电价，算一下车间/9月用电.csv 这个月的电费一共多少钱。", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-DEFN"], notes="three kinds of kWh times three prices")


@reg
def c36():
    web = [page("Vortex Compute", "https://vortexcompute.io/pricing", "Vortex Compute pricing", "On-demand instance prices.",
                "# On-demand pricing (September 2026)\n\n- vx.small: $0.045 / hour\n- vx.medium: $0.092 / hour\n- vx.large: $0.188 / hour\n", "2026-09-01"),
           page("Vortex Compute", "https://hosting-compare.example.net/vortex", "Vortex review", "Vortex prices in early 2025.", "In 2025, vx.medium cost $0.12/hour.\n", "2025-02-11")]
    files = {"cloud/usage.csv": L("instance,hours", "vx.small,720", "vx.medium,1440", "vx.large,310", "vx.small,168")}

    def compute(files, web):
        import re
        pg = [w for w in web if "vortexcompute.io" in w["url"]][0]["content"]
        pr = dict(re.findall(r"- (vx\.\w+): \$([\d.]+) / hour", pg))
        t = round(sum(int(l.split(",")[1]) * float(pr[l.split(",")[0]]) for l in files["cloud/usage.csv"].splitlines()[1:]), 2)
        return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t)]))]
    mk("hyb-33336", sub="calc", desc="Cloud bill from hours per instance type and the provider's current hourly prices", files=files, web=web,
       turns=[{"p": "Using Vortex Compute's current on-demand prices, how much do the hours in cloud/usage.csv come to?", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-WEBSTALE"], notes="vx.small appears twice", )


@reg
def c37():
    web = [page("速达快递", "https://www.suda-express.cn/price", "速达快递 资费说明", "首重续重价格。",
                "# 同城快递资费\n\n首重（1公斤以内）：12 元\n续重：每增加1公斤（不足1公斤按1公斤计）3 元\n", "2026-05-18")]
    files = {"仓库/待发.txt": L("包裹A 2.4kg", "包裹B 0.8kg", "包裹C 5.0kg", "包裹D 1.2kg", "包裹E 3.7kg")}

    def compute(files, web):
        import math
        t = 0
        for l in files["仓库/待发.txt"].splitlines():
            w = float(l.split()[1][:-2])
            t += 12 + 3 * (math.ceil(w) - 1)
        return {}, [[str(t)]]
    mk("hyb-33337", sub="calc", desc="Courier fees with first-weight and rounded-up extra-weight rules from the carrier's page", files=files, web=web,
       turns=[{"p": "按速达快递官网的同城资费，仓库/待发.txt 里这五个包裹一共要付多少运费？", "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-DEFN"], notes="ceil weights: 3,1,5,2,4 -> 12*5 + 3*(2+0+4+1+3)=90")


@reg
def c38():
    web = [page("rail", "https://koyo-rail.example.jp/fares", "Kōyō Rail fares", "Fare table in yen.", "Adult one-way Tokyo-Nagano: 7,480 JPY\nChild one-way: 3,740 JPY\n", "2026-07-30"),
           page("exchange", "https://rates.tradedesk.example/usd-jpy", "USD/JPY today", "Spot rate.", "USD/JPY: 1 USD = 150 JPY (2026-09-15)\n", "2026-09-15")]
    files = {"trip/group.txt": L("adults: 4", "children: 2", "direction: round trip")}

    def compute(files, web):
        import re
        fares = [w for w in web if "koyo" in w["url"]][0]["content"]
        a = int(re.search(r"Adult one-way[^:]*: ([\d,]+) JPY", fares).group(1).replace(",", ""))
        c = int(re.search(r"Child one-way: ([\d,]+) JPY", fares).group(1).replace(",", ""))
        rate = int(re.search(r"1 USD = (\d+) JPY", [w for w in web if "tradedesk" in w["url"]][0]["content"]).group(1))
        yen = (4 * a + 2 * c) * 2
        usd = round(yen / rate, 2)
        return {}, [list(dict.fromkeys(["%.2f" % usd, ("%.2f" % usd).rstrip("0").rstrip(".")]))]
    mk("hyb-33338", sub="calc", desc="Round-trip group train fare in yen converted to dollars with a second page's exchange rate", files=files, web=web,
       turns=[{"p": "Our group is described in trip/group.txt. Work out the round-trip train cost on Kōyō Rail in US dollars, using their fare table and today's USD/JPY rate from rates.tradedesk.example.", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-DIRMAP"], rc=6, notes="(4*7480+2*3740)*2 / 150 = 498.67")


@reg
def c39():
    web = [page("青崖山", "https://www.qingya-scenic.cn/tickets", "青崖山景区 门票", "票价与团体优惠。",
                "# 门票价格\n\n成人票：80 元\n学生票：40 元\n60岁以上老人：免票\n团体优惠：同一批 10 人及以上，购票总额打 9 折。\n", "2026-08-12")]
    files = {"出游/报名.csv": L("姓名,类别", *["同学%02d,学生" % i for i in range(1, 13)], "赵老师,成人", "钱老师,成人", "孙奶奶,老人")}

    def compute(files, web):
        rows = [l.split(",")[1] for l in files["出游/报名.csv"].splitlines()[1:]]
        t = (80 * rows.count("成人") + 40 * rows.count("学生")) * 0.9 if len(rows) >= 10 else 80 * rows.count("成人") + 40 * rows.count("学生")
        t = round(t, 2)
        return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip(".")]))]
    mk("hyb-33339", sub="calc", desc="Group ticket cost with a free category and a 10 percent group discount read from the site", files=files, web=web,
       turns=[{"p": "出游/报名.csv 是这次去青崖山的名单，按景区网站上的票价和团体优惠，我们一共要付多少钱？", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-RULEFILE"], notes="(80*2+40*12)*0.9 = 576")


@reg
def c40():
    web = [page("Lattice AI", "https://lattice-ai.dev/api/pricing", "Lattice API pricing", "Token prices per million.",
                "# Lattice API pricing\n\nlattice-mini: input $0.30 / 1M tokens, output $1.20 / 1M tokens\nlattice-pro: input $2.50 / 1M tokens, output $10.00 / 1M tokens\n", "2026-08-05")]
    files = {"ml/usage.csv": L("day,model,input_tokens,output_tokens", "2026-09-01,lattice-pro,4200000,800000", "2026-09-02,lattice-mini,9000000,2500000", "2026-09-03,lattice-pro,1500000,300000")}

    def compute(files, web):
        import re
        pg = [w for w in web if "lattice-ai" in w["url"]][0]["content"]
        pr = {m: (float(a), float(b)) for m, a, b in re.findall(r"(lattice-\w+): input \$([\d.]+) / 1M tokens, output \$([\d.]+)", pg)}
        t = 0.0
        for l in files["ml/usage.csv"].splitlines()[1:]:
            d, m, i, o = l.split(",")
            t += int(i) / 1e6 * pr[m][0] + int(o) / 1e6 * pr[m][1]
        t = round(t, 2)
        return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip(".")]))]
    mk("hyb-33340", sub="calc", desc="API spend from token counts per model and the vendor's per-million prices", files=files, web=web,
       turns=[{"p": "Work out what the three days in ml/usage.csv cost, based on Lattice's API prices (input and output priced separately).", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-DIRMAP"], notes="pro: 10.5+8 ; mini 2.7+3 ; pro 3.75+3 = 30.95")


@reg
def c41():
    web = [page("驰程租车", "https://www.chicheng-rent.cn/price", "驰程租车 日租价格", "各车型日租金。",
                "# 日租价格表\n\n经济型：168 元/天\n舒适型：238 元/天\nSUV：318 元/天\n7座商务：468 元/天\n", "2026-09-02")]
    files = {"出差/行程.txt": L("车型：经济型", "用车天数：4"), "出差/备选方案.txt": L("车型：SUV", "用车天数：6")}

    def compute(files, web):
        import re
        pg = [w for w in web if "chicheng" in w["url"]][0]["content"]
        pr = dict((k, int(v)) for k, v in re.findall(r"(\S+)：(\d+) 元/天", pg))

        def tot(t):
            car = re.search(r"车型：(\S+)", t).group(1)
            return pr[car] * int(re.search(r"用车天数：(\d+)", t).group(1))
        return {}, [[str(tot(files["出差/行程.txt"]))], [str(tot(files["出差/备选方案.txt"]))]]
    mk("hyb-33341", sub="calc", desc="Rental cost for the main plan, then re-priced for the alternative plan file", files=files, web=web,
       turns=[{"p": "出差/行程.txt 里的车按驰程租车官网的日租价格，要花多少钱？", "req": ["web_fetch"]},
              {"p": "再看看 出差/备选方案.txt 那个方案，如果按它来，租车费是多少？"}],
       compute=compute, must=BC, traps=["TR-MULTISRC"], rc=6, notes="672 then 1908")


@reg
def c42():
    web = [page("Alder Suites", "https://aldersuites.example.com/rates", "Alder Suites rates", "Nightly room rates.",
                "# Nightly rates (2026)\n\nStandard room: $142\nDeluxe room: $189\nSuite: $260\n\nTaxes and fees are listed on the Taxes page.\n", "2026-08-01"),
           page("Alder Suites", "https://aldersuites.example.com/taxes", "Alder Suites taxes", "Occupancy tax and resort fee.",
                "# Taxes and fees\n\nOccupancy tax: 12% of the room charge\nResort fee: $15 per night\n", "2026-08-01")]
    files = {"travel/booking.txt": L("hotel: Alder Suites", "room: Deluxe room", "nights: 3")}

    def compute(files, web):
        import re
        r = [w for w in web if w["url"].endswith("/rates")][0]["content"]
        t = [w for w in web if w["url"].endswith("/taxes")][0]["content"]
        room = int(re.search(r"Deluxe room: \$(\d+)", r).group(1))
        n = int(re.search(r"nights: (\d+)", files["travel/booking.txt"]).group(1))
        base = room * n
        tax = int(re.search(r"Occupancy tax: (\d+)%", t).group(1))
        fee = int(re.search(r"Resort fee: \$(\d+)", t).group(1))
        x = round(base * (1 + tax / 100.0) + fee * n, 2)
        return {}, [[str(base)], list(dict.fromkeys(["%.2f" % x, ("%.2f" % x).rstrip("0").rstrip("."), "{:,.2f}".format(x)]))]
    mk("hyb-33342", sub="calc", desc="Room cost for the booked stay, then the all-in total once the tax page is read", files=files, web=web,
       turns=[{"p": "Based on travel/booking.txt, what is the room charge before taxes for the Alder Suites stay, at their listed nightly rate?", "req": ["web_fetch"]},
              {"p": "Now add what the hotel's taxes page says: occupancy tax and the resort fee. What is the all-in total?", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-MULTISRC"], rc=6, notes="567 then 567*1.12+45 = 680.04")


@reg
def c43():
    web = [page("粮油批发", "https://www.hengfeng-grain.cn/quote", "恒丰粮油 今日报价", "大米面粉批发价。",
                "# 今日批发报价（2026-09-15）\n\n东北大米：5.6 元/公斤\n面粉（特一粉）：4.2 元/公斤\n菜籽油：13.8 元/升\n", "2026-09-15")]
    files = {"食堂/大米用量.txt": L("9月大米用量：1850 公斤"), "食堂/面粉用量.txt": L("9月面粉用量：920 公斤")}

    def compute(files, web):
        import re
        pg = [w for w in web if "hengfeng" in w["url"]][0]["content"]
        rice = float(re.search(r"东北大米：([\d.]+)", pg).group(1))
        flour = float(re.search(r"特一粉）：([\d.]+)", pg).group(1))
        a = int(re.search(r"(\d+) 公斤", files["食堂/大米用量.txt"]).group(1))
        b = int(re.search(r"(\d+) 公斤", files["食堂/面粉用量.txt"]).group(1))
        x, y = round(a * rice, 2), round(b * flour, 2)
        f = lambda t: list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t), "{:,.2f}".format(t).rstrip("0").rstrip(".")]))
        return {}, [f(x), f(y)]
    mk("hyb-33343", sub="calc", desc="September rice cost, then flour cost from a different usage file, at today's wholesale quote", files=files, web=web,
       turns=[{"p": "按恒丰粮油今天的批发报价，食堂 9 月的大米用量要花多少钱？用量在 食堂/大米用量.txt。", "any": True, "req": ["web_fetch"]},
              {"p": "面粉也一样算一下，用量见 食堂/面粉用量.txt。", "any": True}],
       compute=compute, must=BC, traps=["TR-DEFN"], rc=6, notes="10360 then 3864")


@reg
def c44():
    web = [page("Pinecrest Post", "https://pinecrestpost.example.org/postage", "Pinecrest Post postage", "Domestic and international letter rates.",
                "# Letter postage\n\nDomestic letter (up to 1 oz): $0.78, each additional ounce $0.28\nInternational letter (up to 1 oz): $1.65, each additional ounce $0.55\n", "2026-07-10")]
    files = {"office/domestic.txt": L("3 oz", "1 oz", "2 oz"), "office/international.txt": L("1 oz", "4 oz")}

    def compute(files, web):
        import re
        pg = [w for w in web if "pinecrestpost" in w["url"]][0]["content"]
        d = [float(x) for x in re.search(r"Domestic letter \(up to 1 oz\): \$([\d.]+), each additional ounce \$([\d.]+)", pg).groups()]
        i = [float(x) for x in re.search(r"International letter \(up to 1 oz\): \$([\d.]+), each additional ounce \$([\d.]+)", pg).groups()]

        def cost(t, rate):
            return sum(rate[0] + rate[1] * (int(l.split()[0]) - 1) for l in t.splitlines())
        out = []
        for v in (cost(files["office/domestic.txt"], d), cost(files["office/international.txt"], i)):
            v = round(v, 2)
            out.append(list(dict.fromkeys(["%.2f" % v, ("%.2f" % v).rstrip("0").rstrip("."), "{:,.2f}".format(v)])))
        return {}, out
    mk("hyb-33344", sub="calc", desc="Postage for a list of domestic letters, then for an international list from another file", files=files, web=web,
       turns=[{"p": "Using Pinecrest Post's published letter postage, how much to mail the domestic letters listed in office/domestic.txt (each line is one letter's weight)?", "any": True, "req": ["web_fetch"]},
              {"p": "And the international ones in office/international.txt?", "any": True}],
       compute=compute, must=BC, traps=["TR-MULTISRC"], rc=6, notes="domestic 3.38 ; intl 3.30+... ")


@reg
def c45():
    web = [page("跨境小包", "https://www.fengyun-logistics.cn/volume-rule", "风云物流 计费规则", "体积重与计费重量。",
                "# 计费规则\n\n体积重（公斤）= 长×宽×高（厘米）÷ 6000\n计费重量取实重与体积重中较大者，向上取整到整公斤。\n运费：8 元/公斤\n", "2026-06-06")]
    files = {"发货/货物.csv": L("货物,实重_kg,长,宽,高", "台灯,2.0,40,30,25", "抱枕,0.9,50,50,30", "书,4.0,30,22,12")}

    def compute(files, web):
        import math
        out = []
        tot = 0
        for l in files["发货/货物.csv"].splitlines()[1:]:
            n, w, a, b, c = l.split(",")
            kg = math.ceil(max(float(w), int(a) * int(b) * int(c) / 6000.0) - 1e-9)
            out.append(kg * 8)
        return {}, [[str(out[0])], [str(sum(out))]]
    mk("hyb-33345", sub="calc", desc="Volumetric billing weight rule from a logistics page: first one item, then all three", files=files, web=web,
       turns=[{"p": "按风云物流网站上的计费规则，发货/货物.csv 里的台灯运费是多少？", "req": ["web_fetch"]},
              {"p": "那三件货全部一起寄，运费合计多少？"}],
       compute=compute, must=BC, traps=["TR-DEFN"], rc=6, notes="lamp 25000/6000=4.17 -> 5kg=40; pillow 75000/6000=12.5 -> 13kg=104; book 4 vs 2.2 -> 4kg=32; total 176")


@reg
def c46():
    web = [page("Marlin Desk", "https://marlindesk.io/pricing", "Marlin Desk pricing", "Per-seat plans.",
                "# Marlin Desk pricing\n\nBilled monthly per seat, price depends on team size:\n\n- 1-10 seats: $14 per seat\n- 11-50 seats: $11 per seat\n- 51+ seats: $9 per seat\n\nThe price band for your total seat count applies to every seat.\n", "2026-09-04")]
    files = {"it/teamA.txt": "seats: 8\n", "it/teamB.txt": "seats: 36\n", "it/teamC.txt": "seats: 64\n"}

    def compute(files, web):
        import re
        out = []
        for k in ("A", "B"):
            n = int(re.search(r"seats: (\d+)", files["it/team%s.txt" % k]).group(1))
            p = 14 if n <= 10 else (11 if n <= 50 else 9)
            out.append([str(n * p)])
        return {}, out
    mk("hyb-33346", sub="calc", desc="Monthly seat bill for team A, then team B in a different pricing band", files=files, web=web,
       turns=[{"p": "What would Marlin Desk cost per month for the team described in it/teamA.txt, going by their pricing page?", "req": ["web_fetch"]},
              {"p": "And for the team in it/teamB.txt?"}],
       compute=compute, must=BC, traps=["TR-DEFN"], rc=6, notes="8*14=112 ; 36*11=396")


@reg
def c47():
    web = [page("油价", "https://www.fuelwatch-cn.com/today", "今日成品油价格", "各省市油价。",
                "# 今日成品油价格（2026-09-16）\n\n92号汽油：7.58 元/升\n95号汽油：8.07 元/升\n0号柴油：7.31 元/升\n", "2026-09-16")]
    files = {"车队/车辆.txt": L("车牌：沪A·31K77", "油号：95号汽油", "百公里油耗：8.5 升"), "车队/本月行程.txt": L("9月1日 142 公里", "9月8日 60 公里", "9月12日 200 公里")}

    def compute(files, web):
        import re
        pg = [w for w in web if "fuelwatch" in w["url"]][0]["content"]
        price = float(re.search(r"95号汽油：([\d.]+)", pg).group(1))
        km = sum(int(x) for x in re.findall(r"(\d+) 公里", files["车队/本月行程.txt"]))
        v = round(km * 8.5 / 100 * price, 2)
        return {}, [list(dict.fromkeys(["%.2f" % v, ("%.2f" % v).rstrip("0").rstrip("."), "{:,.2f}".format(v)]))]
    mk("hyb-33347", sub="calc", desc="Fuel cost for the month's mileage from a car file and today's fuel price", files=files, web=web,
       turns=[{"p": "车队/车辆.txt 里那辆车这个月跑了 车队/本月行程.txt 里的这些路程，按今天的油价算，油费大概是多少钱？", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-DEFN"], notes="402 km * 8.5/100 * 8.07 = 275.76")


@reg
def c48():
    web = [page("overtime", "https://labor.state-xy.example.gov/overtime-rules", "Overtime pay rules", "Premium multipliers for overtime work.",
                "# Overtime pay\n\nWeekday overtime: 1.5 times the base hourly wage\nWeekend overtime: 2 times the base hourly wage\nPublic holiday overtime: 3 times the base hourly wage\n", "2026-03-01")]
    files = {"hr/ot_log.csv": L("date,kind,hours", "2026-09-02,weekday,2", "2026-09-05,weekend,6", "2026-09-09,weekday,3", "2026-09-13,weekend,4", "2026-09-14,weekday,1"), "hr/rate.txt": "base hourly wage: $20\n"}

    def compute(files, web):
        import re
        pg = [w for w in web if "labor.state" in w["url"]][0]["content"]
        m = {"weekday": float(re.search(r"Weekday overtime: ([\d.]+)", pg).group(1)), "weekend": float(re.search(r"Weekend overtime: ([\d.]+)", pg).group(1))}
        base = int(re.search(r"\$(\d+)", files["hr/rate.txt"]).group(1))
        t = sum(int(l.split(",")[2]) * base * m[l.split(",")[1]] for l in files["hr/ot_log.csv"].splitlines()[1:])
        t = round(t, 2)
        return {}, [list(dict.fromkeys(["%.2f" % t, ("%.2f" % t).rstrip("0").rstrip("."), "{:,.2f}".format(t)]))]
    mk("hyb-33348", sub="calc", desc="Overtime pay with weekday and weekend multipliers read from a government rules page", files=files, web=web,
       turns=[{"p": "Calculate this month's overtime pay from hr/ot_log.csv and the base wage in hr/rate.txt. The multipliers are on the government overtime rules page.", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BC, traps=["TR-DEFN"], notes="weekday 6h*30=180 ; weekend 10h*40=400 -> 580")
