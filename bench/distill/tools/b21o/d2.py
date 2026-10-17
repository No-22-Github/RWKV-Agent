"""datetime part 2: durations, multi-turn zones, recurring slots."""
from common import mk

B = []


def b(f):
    B.append(f)
    return f


@b
def d08():
    def compute(files, wx):
        import datetime
        a, t = datetime.date(2024, 3, 15), datetime.date(2026, 9, 16)
        m = (t.year - a.year) * 12 + t.month - a.month - (1 if t.day < a.day else 0)
        return {}, [[("any", ["%d个月" % m, "%d 个月" % m, "%d months" % m, "2年6个月", "2 年 6 个月", "两年半", "2年半", "2.5 years"])]]
    mk("hyb-33622", sub="datetime", desc="Full months of service since a join date", turns=[{"p": "我是 2024 年 3 月 15 日入职的，到今天满多少个月了？", "req": ["datetime"]}],
       compute=compute, must=["datetime"], traps=["TR-DEFN"], decoys={"TR-DEFN": "31个月"}, rc=2,
       notes="2024-03-15 -> 2026-09-16: 30 full months (day 16 >= 15).",
       alts=["入职满几个月了，2024-03-15 入职", "从 2024 年 3 月 15 日到现在多少个整月", "我工作了多少个月（2024/3/15 起）", "入职到今天一共多少个月", "How many full months since March 15, 2024?"])


@b
def d09():
    def compute(files, wx):
        import datetime
        n = (datetime.date(2026, 11, 20) - datetime.date(2026, 9, 16)).days
        return {}, [[("any", ["%d天" % n, "%d 天" % n, "%d days" % n, "%d day" % n])]]
    mk("hyb-33623", sub="datetime", desc="Days left until a visa expiry date given in the prompt", turns=[{"p": "我的签证 2026 年 11 月 20 日到期，从今天算还剩几天？", "req": ["datetime"]}],
       compute=compute, must=["datetime", "calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "66天"}, rc=2,
       notes="09-16 -> 11-20 = 65 days.",
       alts=["签证 11 月 20 日到期，还有多少天", "距离 2026-11-20 还有几天", "还剩几天签证过期（11/20）", "今天到 11 月 20 号隔多少天", "Days until my visa expires on 2026-11-20?"])


@b
def d10():
    def compute(files, wx):
        return {}, [[("any", ["11:00", "11点", "11 点", "11:00 AM", "11 AM", "11 am", "11:00 am", "上午11", "上午 11"])],
                    [("any", ["22:00", "晚上10点", "晚上 10 点", "10:00 PM", "10 PM", "10:00 pm", "10 pm", "10 p.m.", "22点", "22 点", "晚上十点", "晚上10:00", "晚上 10:00"])]]
    mk("hyb-33624", sub="datetime", desc="Multi-turn zone conversion: Tokyo (no DST) then New York (EDT, previous evening)",
       turns=[{"p": "现在东京几点？"}, {"p": "纽约呢？"}],
       compute=compute, must=["datetime"], traps=["TR-TZ"], decoys={"TR-TZ": "21:00"}, rc=2,
       notes="Shanghai 10:00 = Tokyo 11:00 (UTC+9) = New York 22:00 on 09-15 (EDT, UTC-4).",
       alts=["东京现在的时间", "此刻东京是几点钟", "东京时间多少", "告诉我东京现在几点", "What time is it in Tokyo now?"])


@b
def d11():
    def compute(files, wx):
        import datetime
        t = datetime.date(2026, 9, 30)
        zh = "一二三四五六日"[t.weekday()]
        en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][t.weekday()]
        n = (t - datetime.date(2026, 9, 16)).days
        return {}, [[("any", ["周" + zh, "星期" + zh, "礼拜" + zh, en])], [("any", ["%d天" % n, "%d 天" % n, "%d days" % n, "%d day" % n])]]
    mk("hyb-33625", sub="datetime", desc="Multi-turn: weekday of the month's last day, then days remaining",
       turns=[{"p": "这个月的最后一天是星期几？", "req": ["datetime"]}, {"p": "从今天到那天还剩几天？"}],
       compute=compute, must=["datetime", "calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "周二"}, rc=2,
       notes="September 2026 ends on 09-30, a Wednesday; 14 days after 09-16.",
       alts=["本月月底是周几", "九月最后一天星期几", "这月末是星期几", "月底那天是周几", "What weekday is the last day of this month?"])


@b
def d12():
    def compute(files, wx):
        import datetime
        n = (datetime.date(2026, 12, 25) - datetime.date(2026, 9, 16)).days
        return {}, [[("any", ["%d days" % n, "%d day" % n, "%d天" % n, "%d 天" % n])]]
    mk("hyb-33626", sub="datetime", desc="English: days until Christmas", turns=[{"p": "How many days are left until Christmas Day this year?", "req": ["datetime"]}],
       compute=compute, must=["datetime"], traps=["TR-DEFN"], decoys={"TR-DEFN": "99 days"}, rc=2,
       notes="09-16 -> 12-25 = 100 days.",
       alts=["Days until Dec 25?", "How long until Christmas, in days?", "Countdown to Christmas from today", "Christmas is how many days away", "离圣诞节还有几天"])


@b
def d13():
    def compute(files, wx):
        return {}, [[("any", ["9月16日", "9月16号", "09-16", "9/16", "2026-09-16", "Sep 16", "September 16", "今天", "today"])]]
    mk("hyb-33627", sub="datetime", desc="Weekly slot (Wednesday 15:00): today's slot is still ahead at 10:00",
       turns=[{"p": "我们的周会固定每周三下午 3 点，下一次是几月几号？", "req": ["datetime"]}],
       compute=compute, must=["datetime"], traps=["TR-DEFN"], decoys={"TR-DEFN": "9月23日"}, rc=1,
       notes="Today is Wednesday 10:00, the 15:00 slot has not passed -> 09-16 (today), not 09-23.",
       alts=["周三下午三点的例会，下一次哪天", "每周三 15:00 开会，最近一次是几号", "下次周会的日期", "周会下次是哪天（每周三下午 3 点）", "When is the next Wednesday 3 pm meeting?"])


@b
def d14():
    def compute(files, wx):
        import datetime
        n = (datetime.date(2026, 9, 16) - datetime.date(2025, 12, 31)).days
        return {}, [[("any", ["%d天" % n, "%d 天" % n, "%d days" % n, "%d day" % n])]]
    mk("hyb-33628", sub="datetime", desc="Days elapsed since last year's last day", turns=[{"p": "从去年最后一天（2025-12-31）到今天，一共过去了多少天？", "req": ["datetime"]}],
       compute=compute, must=["datetime", "calculator"], traps=["TR-DEFN"], decoys={"TR-DEFN": "258"}, rc=2,
       notes="2025-12-31 -> 2026-09-16 = 259 days.",
       alts=["2025 年 12 月 31 日到今天隔了多少天", "今年已经过了多少天（从去年底算）", "去年年底到现在多少天", "距离 2025-12-31 已经 过去几天", "Days since Dec 31, 2025?"])
