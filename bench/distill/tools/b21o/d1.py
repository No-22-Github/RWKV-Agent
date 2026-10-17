"""datetime: weekdays, countdowns, time zones (fixed clock 2026-09-16 Wed 10:00 Asia/Shanghai)."""
from common import mk

B = []


def b(f):
    B.append(f)
    return f


@b
def d01():
    def compute(files, wx):
        import datetime
        t = datetime.date(2026, 9, 16) + datetime.timedelta(days=45)
        zh = "一二三四五六日"[t.weekday()]
        en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][t.weekday()]
        return {}, [[("any", ["周" + zh, "星期" + zh, "礼拜" + zh, en])]]
    mk("hyb-33615", sub="datetime", desc="Weekday of the day 45 days from the fixed today", turns=[{"p": "项目验收定在 45 天以后，那天是星期几？", "req": ["datetime"]}],
       compute=compute, must=["datetime"], traps=["TR-DEFN"], decoys={"TR-DEFN": "周三"}, rc=2,
       notes="1. datetime now -> 2026-09-16\n2. add 45 days (1080h) -> 2026-10-31, a Saturday.",
       alts=["45 天后是周几", "从今天算起 45 天是星期几", "四十五天以后星期几", "验收日（45 天后）是周几", "What weekday is 45 days from today?"])


@b
def d02():
    def compute(files, wx):
        import datetime
        n = (datetime.date(2026, 10, 1) - datetime.date(2026, 9, 16)).days
        return {}, [[("any", ["%d天" % n, "%d 天" % n, "%d days" % n, "%d day" % n])]]
    mk("hyb-33616", sub="datetime", desc="Days left until October 1st", turns=[{"p": "离十月一日还有几天？", "req": ["datetime"]}],
       compute=compute, must=["datetime", "calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "16"}, rc=2,
       notes="1. datetime now -> 2026-09-16\n2. compare/difference -> 15 days.",
       alts=["距离国庆还有多少天", "今天到 10 月 1 日隔几天", "还有几天到十月一号", "十一还有多久（按天算）", "How many days until October 1?"])


@b
def d03():
    def compute(files, wx):
        # Beijing 09:30 tomorrow = 01:30 UTC = 18:30 PDT (UTC-7) today
        return {}, [[("any", ["18:30", "6:30 PM", "6:30 pm", "6:30PM", "6:30 p.m.", "下午 6:30", "下午6:30", "下午6点30", "下午 6 点 30", "晚上 6:30", "晚上6:30", "18点30"])]]
    mk("hyb-33617", sub="datetime", desc="Time-zone conversion with daylight saving: Beijing morning to San Francisco evening",
       turns=[{"p": "我们明天北京时间上午 9:30 和旧金山的同事开会，那边是几点？"}],
       compute=compute, must=["datetime"], traps=["TR-TZ"], decoys={"TR-TZ": "17:30"}, rc=1,
       notes="Beijing UTC+8, San Francisco on 2026-09-16/17 is PDT (UTC-7): 15h behind -> 18:30 on 09-16.",
       alts=["北京明早 9:30 对应旧金山几点", "旧金山那边明天北京 9:30 是几点", "北京时间明天 9 点半，旧金山时间多少", "和旧金山开会，北京明天 9:30，那边几点", "What time is 9:30 tomorrow morning Beijing time in San Francisco?"])


@b
def d04():
    def compute(files, wx):
        return {}, [[("any", ["03:00", "3:00 AM", "3:00 am", "3 AM", "3 am", "3:00 a.m.", "3am", "3:00AM"])]]
    mk("hyb-33618", sub="datetime", desc="English: Shanghai 10:00 to London during British Summer Time",
       turns=[{"p": "It's 10:00 in Shanghai right now. What time is it in London?"}],
       compute=compute, must=["datetime"], traps=["TR-TZ"], decoys={"TR-TZ": "02:00"}, rc=1,
       notes="London is on BST (UTC+1) in September, Shanghai UTC+8: 7 hours behind -> 03:00.",
       alts=["Current London time if Shanghai is 10:00?", "Convert 10:00 Shanghai to London time", "Shanghai 10 am equals what in London?", "What's the time in London when it's 10:00 in Shanghai", "上海现在 10 点，伦敦几点"])


@b
def d05():
    def compute(files, wx):
        import datetime
        t = datetime.date(2026, 9, 16) + datetime.timedelta(days=14)
        zh = "一二三四五六日"[t.weekday()]
        en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][t.weekday()]
        return {}, [[("any", ["%d月%d日" % (t.month, t.day), "%d月%d号" % (t.month, t.day), t.isoformat(), "%02d-%02d" % (t.month, t.day), "%d/%d" % (t.month, t.day), "Sep 30", "September 30"])],
                    [("any", ["周" + zh, "星期" + zh, "礼拜" + zh, en])]]
    mk("hyb-33619", sub="datetime", desc="Multi-turn: date two weeks out, then its weekday",
       turns=[{"p": "两周以后是几月几号？", "req": ["datetime"]}, {"p": "那天是星期几？"}],
       compute=compute, must=["datetime"], traps=["TR-DEFN"], decoys={"TR-DEFN": "9月23日"}, rc=2,
       notes="Today 2026-09-16 (Wed) + 14 days = 2026-09-30, also a Wednesday.",
       alts=["十四天后是几号", "下下周的今天是几月几日", "两周后的日期", "从今天起两个星期是哪天", "What is the date two weeks from today?"])


@b
def d06():
    def compute(files, wx):
        import datetime
        d, n = datetime.date(2026, 9, 16), 0
        while n < 15:
            d += datetime.timedelta(days=1)
            if d.weekday() < 5:
                n += 1
        return {}, [[("any", ["%d月%d日" % (d.month, d.day), "%d月%d号" % (d.month, d.day), d.isoformat(), "%02d-%02d" % (d.month, d.day), "%d/%d" % (d.month, d.day), "Oct 7", "October 7"])]]
    mk("hyb-33620", sub="datetime", desc="15 working days from today, weekends skipped, holidays ignored by the user's instruction",
       turns=[{"p": "合同今天签，约定 15 个工作日内交付。周末不算，法定假日先不考虑，最晚哪天交付？", "req": ["datetime"]}],
       compute=compute, must=["datetime"], traps=["TR-DEFN"], decoys={"TR-DEFN": "10月1日"}, rc=3,
       notes="Start Wed 09-16 (not counted); 15th working day lands on Wed 2026-10-07 (calendar-days answer 10-01 is the decoy).",
       alts=["今天签约，15 个工作日后最晚几号交货", "工作日 15 天后是哪天（不算节假日）", "15 个工作日以后的日期，从今天起算", "合同 15 个工作日交付，截止日期", "15 business days from today, weekends excluded: which date?"])


@b
def d07():
    def compute(files, wx):
        return {}, [[("any", ["32小时", "32 小时", "32 hours", "32 hour", "32h", "32个小时", "32 个小时"])]]
    mk("hyb-33621", sub="datetime", desc="Hours from now until tomorrow 18:00", turns=[{"p": "距离明天下午 6 点还有多少个小时？", "req": ["datetime"]}],
       compute=compute, must=["datetime", "calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "8"}, rc=2,
       notes="Now 09-16 10:00; target 09-17 18:00 -> 32 hours.",
       alts=["到明天 18:00 还有几个小时", "现在到明天傍晚六点多少小时", "离明天 6 点下班还剩几小时", "还要多少小时到明天下午 6 点", "How many hours until 6 pm tomorrow?"])
