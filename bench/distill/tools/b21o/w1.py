"""weather: single city, tomorrow / day after tomorrow / weekend."""
from common import mk, weather, WEBX

B = []


def b(f):
    B.append(f)
    return f


@b
def w01():
    wx = [weather("杭州", "多云 27°C 体感 29°C 湿度 71% 风速 9 km/h",
                  [("2026-09-16", "多云", "24~30", "20%"), ("2026-09-17", "中雨", "21~25", "80%"),
                   ("2026-09-18", "阴", "22~27", "40%")], aliases=["Hangzhou"])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"][1]
        assert d["date"] == "2026-09-17"
        return {}, [[("all", [d["rain_chance"]])]]
    mk("hyb-33601", sub="weather", desc="Tomorrow's rain chance in one city decides whether to carry an umbrella", wx=wx,
       turns=[{"p": "明天要去杭州见客户，需要带伞吗？", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather", "web_search"], traps=["TR-DECOY"], decoys={"TR-DECOY": "20%"},
       notes="1. get_weather {location: 杭州, days: 2 or more}\nAnswer: tomorrow (09-17) 中雨, 80% rain chance, take an umbrella; today's 20% is the decoy.",
       alts=["杭州明天会下雨吗？", "明天杭州出差要不要带雨具？", "帮我看下杭州明天的天气，需不需要伞", "杭州明天降水概率多少？", "Will I need an umbrella in Hangzhou tomorrow?"])


@b
def w02():
    wx = [weather("成都", "阴 23°C 体感 24°C 湿度 80% 风速 5 km/h",
                  [("2026-09-16", "阴", "20~25", "35%"), ("2026-09-17", "小雨", "19~24", "60%"),
                   ("2026-09-18", "多云", "20~27", "25%"), ("2026-09-19", "晴", "21~30", "5%")], aliases=["Chengdu"])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"][2]
        assert d["date"] == "2026-09-18"
        return {}, [[("all", [d["condition"], d["rain_chance"]])]]
    mk("hyb-33602", sub="weather", desc="Day-after-tomorrow forecast needs the third row of the forecast", wx=wx,
       turns=[{"p": "后天我想在成都逛街，天气怎么样？", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather"], traps=["TR-DECOY"], decoys={"TR-DECOY": "60%"}, rc=1,
       notes="1. get_weather {location: 成都, days: 3 or more}\nAnswer: 09-18 多云, rain chance 25%.",
       alts=["成都后天天气如何？", "后天去成都逛街会下雨吗", "查一下成都后天的预报", "成都大后天前一天的天气（即后天）怎么样", "What is Chengdu's weather the day after tomorrow?"])


@b
def w03():
    wx = [weather("青岛", "晴 26°C 体感 27°C 湿度 60% 风速 18 km/h",
                  [("2026-09-16", "晴", "22~28", "5%"), ("2026-09-17", "晴", "22~29", "5%"),
                   ("2026-09-18", "多云", "21~27", "15%"), ("2026-09-19", "雷阵雨", "20~25", "75%"),
                   ("2026-09-20", "阴", "19~24", "40%")], aliases=["Qingdao"])]

    def compute(files, wx):
        sat, sun = wx[0]["report"]["daily"][3], wx[0]["report"]["daily"][4]
        assert sat["date"] == "2026-09-19" and sun["date"] == "2026-09-20"
        return {}, [[("all", [sat["rain_chance"], sun["rain_chance"]])]]
    mk("hyb-33603", sub="weather", desc="Weekend forecast: Saturday and Sunday are the 4th and 5th rows", wx=wx,
       turns=[{"p": "这周末想在青岛海边烧烤，周六周日天气分别怎么样？哪天更合适？", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather"], traps=["TR-DECOY"], decoys={"TR-DECOY": "5%"}, rc=1,
       notes="1. get_weather {location: 青岛, days: 5 or more}\nAnswer: Sat 雷阵雨 75%, Sun 阴 40%; Sunday is better.",
       alts=["青岛周六周日的天气预报", "周末青岛会下雨吗，哪天适合海边烧烤", "帮我查青岛这个周末的天气", "青岛周六周日降水概率各是多少", "Saturday and Sunday weather in Qingdao?"])


@b
def w04():
    wx = [weather("Lisbon", "Sunny 25°C feels 26°C humidity 55% wind 14 km/h",
                  [("2026-09-16", "Sunny", "19~26", "0%"), ("2026-09-17", "Partly cloudy", "18~24", "10%"),
                   ("2026-09-18", "Showers", "17~21", "70%")], aliases=["里斯本"])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"][1]
        assert d["date"] == "2026-09-17"
        return {}, [[("any", ["Partly cloudy", "partly cloudy", "Partly Cloudy", "partly sunny"])]]
    mk("hyb-33604", sub="weather", desc="English request for tomorrow's conditions in Lisbon", wx=wx,
       turns=[{"p": "I land in Lisbon tomorrow morning. What will the sky look like?", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather"], traps=["TR-DECOY"], decoys={"TR-DECOY": "Sunny"}, rc=1,
       notes="1. get_weather {location: Lisbon, days: 2+}\nAnswer: tomorrow is Partly cloudy (today Sunny is the decoy).",
       alts=["What's the weather in Lisbon tomorrow?", "Lisbon forecast for tomorrow please", "Will it be cloudy in Lisbon tomorrow?", "Tomorrow in Lisbon: sun or clouds?", "里斯本明天天气怎样"])


@b
def w05():
    wx = [weather("Denver", "Clear 18°C feels 17°C humidity 30% wind 12 km/h",
                  [("2026-09-16", "Clear", "9~22", "0%"), ("2026-09-17", "Cloudy", "8~19", "20%"),
                   ("2026-09-18", "Snow showers", "-1~7", "65%")], aliases=["丹佛"])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"][2]
        assert d["date"] == "2026-09-18"
        return {}, [[("any", ["Snow", "snow"])]]
    mk("hyb-33605", sub="weather", desc="English request for the day after tomorrow in Denver", wx=wx,
       turns=[{"p": "We're hiking near Denver the day after tomorrow. Anything I should pack for the weather?", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather", "web_search"], traps=["TR-DECOY"], decoys={"TR-DECOY": "Clear"}, rc=1,
       notes="1. get_weather {location: Denver, days: 3}\nAnswer: 09-18 snow showers, -1~7, pack warm layers.",
       alts=["What will the weather be like in Denver in two days?", "Pack list for Denver hike, day after tomorrow", "Denver forecast two days from now", "Is it going to snow near Denver on the 18th?", "丹佛后天天气如何"])
