"""local-file combos part 2."""
from common import mk, weather, L, rng, WEBX
from q1 import table

B = []


def b(f):
    B.append(f)
    return f


@b
def f08():
    files = {"schedule/events.md": L("# 近期安排", "", "- 项目评审：2026-10-14", "- 团建：2026-10-23", "- 季度汇报：2026-11-05")}

    def compute(files, wx):
        import datetime
        t = datetime.date(2026, 10, 14)
        zh = "一二三四五六日"[t.weekday()]
        en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][t.weekday()]
        return {}, [[("any", ["周" + zh, "星期" + zh, "礼拜" + zh, en])]]
    mk("hyb-33664", sub="files", task="local_first", desc="Weekday of an event date found in a schedule file", files=files,
       turns=[{"p": "schedule 文件夹里写的项目评审是星期几？", "req": ["read_file"]}],
       compute=compute, must=["read_file", "list_files", "datetime"], traps=["TR-DECOY"], decoys={"TR-DECOY": "周五"}, rc=2,
       notes="项目评审 2026-10-14 is a Wednesday; the decoy is the 团建 date's weekday.",
       alts=["项目评审那天是周几", "安排表里的评审日期是星期几", "评审日是礼拜几", "看一下 schedule/events.md，项目评审周几", "What weekday is the project review in schedule/events.md?"])


@b
def f09():
    files = {"家电/保修卡.md": L("# 洗衣机保修卡", "", "购买日期：2025-11-08", "整机保修：24 个月", "电机保修：10 年", "客服热线：见包装")}

    def compute(files, wx):
        import datetime
        e = datetime.date(2027, 11, 8)
        n = (e - datetime.date(2026, 9, 16)).days
        return {}, [[("any", ["2027-11-08", "2027年11月8日", "2027年11月8号", "11月8日", "11月8号", "Nov 8", "November 8"])],
                    [("any", ["%d天" % n, "%d 天" % n, "%d days" % n, "%d day" % n])]]
    mk("hyb-33665", sub="files", task="multi_turn", desc="Multi-turn: warranty end date from purchase date + months, then days left", files=files,
       turns=[{"p": "家电文件夹里洗衣机的整机保修到哪天结束？", "req": ["read_file"]},
              {"p": "从今天算，还剩多少天？"}],
       compute=compute, must=["read_file", "list_files", "datetime", "calculator"], traps=["TR-DECOY"], decoys={"TR-DECOY": "2035-11-08"}, rc=3,
       notes="Purchase 2025-11-08 + 24 months = 2027-11-08 (the 10-year motor warranty is the decoy); 418 days from 09-16.",
       alts=["洗衣机整机保修什么时候到期", "保修卡上的整机保修期截止日", "整机保修结束日期是哪天", "洗衣机保修（24 个月）到几号", "When does the washing machine's full warranty end?"])


@b
def f10():
    r = rng("f10")
    ppl = ["周杰", "吴敏", "郑凯", "冯雪", "蒋涛", "沈岚"]
    rows = [(r.choice(ppl), r.randint(120, 880)) for _ in range(160)]
    tot = {}
    for p, a in rows:
        tot[p] = tot.get(p, 0) + a
    files = {"奖金/规则.md": L("# 奖金规定", "", "季度销售额合计达到 15000 元的人可以领奖金。", "按销售记录汇总，不看单笔。"),
             "奖金/销售记录.csv": table(["rep", "amount"], rows)}
    ok = sorted(p for p, v in tot.items() if v >= 15000)
    assert 1 <= len(ok) < len(ppl) and all(abs(v - 15000) > 100 for v in tot.values()), tot

    def compute(files, wx):
        import csv
        import io
        t = {}
        for x in csv.DictReader(io.StringIO(files["奖金/销售记录.csv"])):
            t[x["rep"]] = t.get(x["rep"], 0) + int(x["amount"])
        ok = sorted(p for p, v in t.items() if v >= 15000)
        return {"奖金/名单.txt": ok}, [[("all", ok)], []]
    mk("hyb-33666", sub="files", task="tool_then_write", desc="Multi-turn: apply a threshold from a rules file to grouped sums, then save the name list", files=files,
       turns=[{"p": "按奖金文件夹里的规定，销售记录里哪些人可以领奖金？", "req": ["read_file", "data_query"]},
              {"p": "把名单写到 奖金/名单.txt，一行一个名字。"}],
       compute=compute, must=["read_file", "data_query", "bash", "write_file"], traps=["TR-RULEFILE"], decoys={"TR-RULEFILE": "all six"}, rc=4,
       notes="Rule file says the cumulative threshold 15000 per person; group the csv by rep and sum; list those at or above 15000. Totals: %s." % sorted(tot.items()),
       alts=["谁达到了奖金线", "销售记录汇总后哪些人能拿奖金", "按规定筛出奖金获得者", "奖金名单是哪几个人", "Who qualifies for the bonus per the rules file and sales records?"])


@b
def f11():
    wx = [weather("南京", "多云 26°C 体感 27°C 湿度 66% 风速 7 km/h",
                  [("2026-09-16", "多云", "22~29", "15%"), ("2026-09-17", "多云", "22~28", "20%"), ("2026-09-18", "雷阵雨", "21~26", "70%")], aliases=["Nanjing"])]
    files = {"活动/户外安排.md": L("# 户外拓展", "", "城市：南京", "日期：后天", "原则：当天降水概率达到 50% 就改到室内。")}

    def compute(files, wx):
        d = wx[0]["report"]["daily"][2]
        assert d["date"] == "2026-09-18" and int(d["rain_chance"].rstrip("%")) >= 50
        return {}, [[("any", ["室内", "改到室内", "indoors", "indoor", "改期", "取消户外"])], [("all", [wx[0]["report"]["daily"][1]["rain_chance"]])]]
    mk("hyb-33667", sub="files", task="local_first", desc="Multi-turn: a rain-chance cut-off in a file decides moving indoors; then tomorrow's chance", files=files, wx=wx,
       turns=[{"p": "活动文件夹里的户外拓展，按安排里的原则，需要改到室内吗？", "req": ["read_file", "get_weather"], "forb": WEBX},
              {"p": "那明天的降水概率是多少？"}],
       compute=compute, must=["read_file", "list_files", "get_weather"], traps=["TR-RULEFILE"], decoys={"TR-RULEFILE": "15%"}, rc=3,
       notes="File: city 南京, date 后天 (09-18), cut-off 50%. 09-18 thunderstorm 70% -> indoors. Turn2: tomorrow 20%.",
       alts=["后天的户外拓展要不要挪到室内", "按安排文件里的降水门槛，拓展能在户外吗", "拓展活动改室内吗（看活动文件夹）", "户外安排：后天南京的天气达标了吗", "Should the outdoor event move indoors per the file in 活动?"])


@b
def f12():
    files = {"notes/flight.txt": L("Flight MU-7211", "Depart: 2026-09-24 07:45 Shanghai time", "Arrive: Berlin", "Seat: 23C")}

    def compute(files, wx):
        import datetime
        n = (datetime.date(2026, 9, 24) - datetime.date(2026, 9, 16)).days
        return {}, [[("any", ["01:45", "1:45 AM", "1:45 am", "1:45 a.m.", "1:45AM", "1:45 a.m"])],
                    [("any", ["%d days" % n, "%d day" % n, "%d天" % n, "%d 天" % n])]]
    mk("hyb-33668", sub="files", task="multi_turn", desc="English multi-turn: departure time converted to Berlin time (CEST), then days until the flight", files=files,
       turns=[{"p": "Read notes/flight.txt. What is the departure time in Berlin local time?", "req": ["read_file"]},
              {"p": "And how many days from today until that flight?"}],
       compute=compute, must=["read_file", "datetime"], traps=["TR-TZ"], decoys={"TR-TZ": "00:45"}, rc=3,
       notes="Shanghai UTC+8, Berlin CEST UTC+2 on 2026-09-24 -> 6 hours behind: 01:45. Days: 8.",
       alts=["What time does the flight leave in Berlin time?", "Convert the departure in notes/flight.txt to Berlin time", "Berlin local time at departure?", "Departure time Berlin per flight.txt", "航班起飞时间换算成柏林当地时间是几点"])


@b
def f13():
    wx = [weather("Osaka", "Sunny 28°C feels 30°C humidity 62% wind 9 km/h",
                  [("2026-09-16", "Sunny", "24~31", "5%"), ("2026-09-17", "Cloudy", "24~30", "20%"), ("2026-09-18", "Heavy rain", "22~27", "85%")], aliases=["大阪"]),
          weather("Kyoto", "Cloudy 26°C",
                  [("2026-09-16", "Cloudy", "22~29", "10%"), ("2026-09-17", "Light rain", "21~26", "45%"), ("2026-09-18", "Rain", "20~24", "60%")], aliases=["京都"])]
    files = {"trip/itinerary.txt": L("Day 1 (Sep 17): Kyoto - temples", "Day 2 (Sep 18): Osaka - castle and food", "Day 3 (Sep 19): fly home")}

    def compute(files, wx):
        return {}, [[("all", ["85%"])], [("all", ["45%"])]]
    mk("hyb-33669", sub="files", task="multi_turn", desc="English multi-turn: map itinerary days to cities and dates, then look up each city's rain chance", files=files, wx=wx,
       turns=[{"p": "Per trip/itinerary.txt, what is the chance of rain in the city I visit on Day 2?", "req": ["read_file", "get_weather"], "forb": WEBX},
              {"p": "And on Day 1?"}],
       compute=compute, must=["read_file", "get_weather"], traps=["TR-MULTISRC"], decoys={"TR-MULTISRC": "20%"}, rc=3,
       notes="Day 2 = Sep 18 in Osaka: 85%. Day 1 = Sep 17 in Kyoto: 45%.",
       alts=["Rain chance on Day 2 of my itinerary?", "How likely is rain where I am on the second day?", "Second day's city: probability of rain", "Weather risk for Day 2 in trip/itinerary.txt", "行程第二天所在城市的降水概率是多少"])


@b
def f14():
    files = {"todo/待办.md": L("# 待办", "", "- 提交预算表，截止 2026-10-09", "- 更新门禁名单，截止 2026-10-19"), "todo/提醒.md": L("# 提醒", "")}

    def compute(files, wx):
        import datetime
        out = []
        for d in (datetime.date(2026, 10, 9), datetime.date(2026, 10, 19)):
            out.append("%s 周%s" % (d.isoformat(), "一二三四五六日"[d.weekday()]))
        return {"todo/提醒.md": out}, [[("any", ["2026-10-09", "10月9日", "10月9号", "10-09", "10/9"])], []]
    mk("hyb-33670", sub="files", task="tool_then_write", desc="Multi-turn: read two deadlines from a todo file and record dates with weekdays in the reminder file", files=files,
       turns=[{"p": "todo/待办.md 里的第一项事情截止日是哪天？", "req": ["read_file"]},
              {"p": "把两项待办的截止日期都写进 todo/提醒.md，每项一行，格式是“2026-10-09 周五”这样的：日期加空格加周几。"}],
       compute=compute, must=["read_file", "append_file", "write_file", "datetime"], traps=["TR-DATEFMT"], decoys={"TR-DATEFMT": "10月9日"}, rc=4,
       notes="Deadlines 2026-10-09 and 2026-10-19; the file must contain each line with the right weekday (computed from the dates).",
       alts=["待办里第一项什么时候截止", "预算表截止日期", "第一件待办的截止日是几号", "todo 文件里第一项的 deadline", "When is the first todo in todo/待办.md due?"])
