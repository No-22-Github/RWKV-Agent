"""weather: comparisons, landmarks, thresholds, multi-turn, unknown place."""
from common import mk, weather, WEBX

B = []


def b(f):
    B.append(f)
    return f


@b
def w06():
    wx = [weather("苏州", "多云 25°C", [("2026-09-16", "多云", "22~28", "20%"), ("2026-09-17", "阴", "21~27", "30%"), ("2026-09-18", "小雨", "20~24", "60%")]),
          weather("无锡", "阴 24°C", [("2026-09-16", "阴", "21~27", "25%"), ("2026-09-17", "多云", "20~31", "10%"), ("2026-09-18", "多云", "20~26", "20%")])]

    def compute(files, wx):
        hi = {w["location"]: int(w["report"]["daily"][1]["temp_c"].split("~")[1]) for w in wx}
        d = hi["无锡"] - hi["苏州"]
        return {}, [[("any", ["%d度" % d, "%d 度" % d, "%d°C" % d, "%d℃" % d, "%d°" % d, "%d ℃" % d, "%d °C" % d])]]
    mk("hyb-33606", sub="weather", desc="Two-city comparison: tomorrow's high temperature difference", wx=wx,
       turns=[{"p": "明天苏州和无锡哪个更热？最高气温差几度？", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather"], traps=["TR-MULTISRC"], decoys={"TR-MULTISRC": "1"}, rc=2,
       notes="1. get_weather 苏州\n2. get_weather 无锡\nTomorrow highs: 苏州 27, 无锡 31 -> 无锡 hotter by 4 degrees.",
       alts=["苏州无锡明天最高温差多少", "对比一下苏州和无锡明天的气温", "明天无锡比苏州高几度", "两个城市苏州、无锡明天哪边热", "Which is hotter tomorrow, Suzhou or Wuxi, and by how many degrees?"])


@b
def w07():
    wx = [weather("北京", "晴 22°C 体感 22°C 湿度 40% 风速 10 km/h", [("2026-09-16", "晴", "15~25", "0%"), ("2026-09-17", "多云", "14~23", "10%"), ("2026-09-18", "小雨", "13~19", "55%")])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"][2]
        return {}, [[("all", [d["rain_chance"]])]]
    mk("hyb-33607", sub="weather", desc="A landmark must be mapped to its city; day after tomorrow", wx=wx,
       turns=[{"p": "后天带爸妈逛故宫，天气行不行？", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather"], traps=["TR-NEARNAME"], decoys={"TR-NEARNAME": "0%"}, rc=2,
       notes="1. get_weather 故宫 -> location not found\n2. get_weather 北京 days>=3\nAnswer: 09-18 小雨, 55% rain chance.",
       alts=["故宫后天会下雨吗", "后天去故宫天气如何", "北京故宫后天的天气预报", "后天故宫游玩要带伞吗", "Weather at the Forbidden City the day after tomorrow?"])


@b
def w08():
    wx = [weather("上海", "阴 26°C", [("2026-09-16", "阴", "24~29", "40%"), ("2026-09-17", "雷阵雨", "24~28", "85%"), ("2026-09-18", "阴", "23~28", "30%")], aliases=["Shanghai"])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"][1]
        return {}, [[("all", [d["rain_chance"]])]]
    mk("hyb-33608", sub="weather", desc="District name must be mapped to its city", wx=wx,
       turns=[{"p": "明天浦东新区的外场活动会被雨影响吗？", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather", "web_fetch"], traps=["TR-NEARNAME"], decoys={"TR-NEARNAME": "40%"}, rc=2,
       notes="1. get_weather 浦东新区 -> not found (or retry)\n2. get_weather 上海\nAnswer: tomorrow 雷阵雨 85%.",
       alts=["浦东明天下雨吗", "明天浦东新区户外活动天气", "上海浦东明天降水概率", "浦东明天的天气适合办外场吗", "Rain in Pudong tomorrow?"])


@b
def w09():
    wx = [weather("西安", "晴 28°C", [("2026-09-16", "晴", "20~31", "0%"), ("2026-09-17", "多云", "19~29", "10%"), ("2026-09-18", "晴", "19~30", "5%")])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"][1]
        return {}, [[("any", ["不用", "不需要", "不必", "无需", "不会下雨", "不太可能下雨", "降水概率较低", "10%", "no need", "not needed", "don't need"])]]
    mk("hyb-33609", sub="weather", desc="Low rain chance tomorrow: a clear no to the umbrella question", wx=wx,
       turns=[{"p": "我明早在西安跑步，会下雨吗？要穿雨衣吗", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather"], traps=["TR-DECOY"], decoys={"TR-DECOY": "晴"}, rc=1,
       notes="1. get_weather 西安\nAnswer: tomorrow 多云 10% rain chance -> no raincoat.",
       alts=["西安明早跑步需要雨衣吗", "明天西安会下雨吗", "西安明天降水概率", "明早西安适合户外跑步吗", "Will it rain in Xi'an tomorrow morning?"])


@b
def w10():
    wx = [weather("厦门", "多云 29°C", [("2026-09-16", "多云", "26~32", "30%"), ("2026-09-17", "多云", "26~33", "25%"), ("2026-09-18", "晴", "26~34", "10%"),
                                       ("2026-09-19", "雷阵雨", "25~31", "70%"), ("2026-09-20", "晴", "25~33", "15%")])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"]
        sat = d[3]
        assert sat["date"] == "2026-09-19"
        return {}, [[("all", [sat["rain_chance"]])], [("any", ["周日", "星期日", "星期天", "周天", "Sunday"])]]
    mk("hyb-33610", sub="weather", desc="Multi-turn: Saturday's rain chance, then the user asks which weekend day is better", wx=wx,
       turns=[{"p": "厦门周六天气怎么样？", "req": ["get_weather"], "forb": WEBX},
              {"p": "那周六和周日哪天更适合出海？"}],
       compute=compute, must=["get_weather"], traps=["TR-DECOY"], decoys={"TR-DECOY": "25%"}, rc=2,
       notes="1. get_weather 厦门 days>=5\nTurn1: Sat 70% thunderstorm. Turn2: Sunday 晴 15% is better; the user asks again so fetch again if unsure.",
       alts=["厦门这周六的天气", "周六厦门会下雨吗", "厦门周六预报", "查下周六的厦门天气", "Xiamen weather on Saturday?"])


@b
def w11():
    wx = [weather("长沙", "晴 30°C", [("2026-09-16", "晴", "24~33", "5%"), ("2026-09-17", "多云", "24~32", "20%"), ("2026-09-18", "阵雨", "23~29", "65%")]),
          weather("武汉", "晴 31°C", [("2026-09-16", "晴", "25~34", "0%"), ("2026-09-17", "晴", "25~35", "5%"), ("2026-09-18", "多云", "24~33", "20%")]),
          weather("南昌", "多云 29°C", [("2026-09-16", "多云", "24~31", "20%"), ("2026-09-17", "小雨", "23~28", "55%"), ("2026-09-18", "小雨", "22~27", "60%")])]

    def compute(files, wx):
        r = {w["location"]: int(w["report"]["daily"][1]["rain_chance"].rstrip("%")) for w in wx}
        dry = min(r, key=r.get)
        return {}, [[("all", [dry])]]
    mk("hyb-33611", sub="weather", desc="Three cities: which has the lowest rain chance tomorrow", wx=wx,
       turns=[{"p": "团建在长沙、武汉、南昌里选一个，明天哪个城市最不容易下雨？", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather"], traps=["TR-MULTISRC"], decoys={"TR-MULTISRC": "长沙"}, rc=3,
       notes="1-3. get_weather for each city\nTomorrow rain chance: 长沙 20%, 武汉 5%, 南昌 55% -> 武汉.",
       alts=["长沙武汉南昌明天谁降雨最少", "三个城市里明天哪个最干燥", "明天去哪个城市团建不会下雨：长沙、武汉、南昌", "比较三城明天降水概率", "Which of Changsha, Wuhan, Nanchang is driest tomorrow?"])


@b
def w12():
    wx = [weather("兰州", "晴 21°C", [("2026-09-16", "晴", "12~24", "0%"), ("2026-09-17", "多云", "11~22", "10%"), ("2026-09-18", "晴", "11~25", "0%"),
                                      ("2026-09-19", "晴", "12~27", "5%"), ("2026-09-20", "多云", "13~26", "15%"), ("2026-09-21", "小雨", "12~20", "50%"), ("2026-09-22", "阴", "11~19", "30%")])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"]
        m = max(d, key=lambda x: int(x["temp_c"].split("~")[1]))
        return {}, [[("all", [m["temp_c"].split("~")[1]])]]
    mk("hyb-33612", sub="weather", desc="Seven-day forecast: the hottest day's high", wx=wx,
       turns=[{"p": "兰州未来一周最高气温是多少度？出现在哪天？", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather"], traps=["TR-DECOY"], decoys={"TR-DECOY": "24"}, rc=1,
       notes="1. get_weather 兰州 days 7\nHighest high is 27 on 09-19 (周六).",
       alts=["兰州这周最热是几度", "未来七天兰州最高温", "兰州下周前最高气温多少", "兰州一周预报里最热的一天", "Hottest day in Lanzhou over the next week?"])


@b
def w13():
    wx = [weather("昆明", "多云 22°C", [("2026-09-16", "多云", "15~24", "30%"), ("2026-09-17", "小雨", "15~21", "60%"), ("2026-09-18", "多云", "14~23", "25%")])]

    def compute(files, wx):
        return {}, [[("any", ["查不到", "找不到", "没有找到", "未找到", "无法查询", "无法获取", "没有查到", "没查到", "不支持", "not found", "couldn't find", "could not find", "unable", "no data"])]]
    mk("hyb-33613", sub="weather", desc="A place the weather source does not know: say so instead of inventing a forecast", wx=wx,
       turns=[{"p": "帮我查下洱海边的双廊古镇明天的天气。", "req": ["get_weather"], "forb": WEBX}],
       compute=compute, must=["get_weather", "web_search"], traps=["TR-ABSENT"], decoys={"TR-ABSENT": "小雨"}, rc=2,
       notes="1. get_weather 双廊古镇 -> not found; retry with 大理 / 洱海 -> not found (fixture only holds 昆明).\nFinal answer must say the forecast cannot be found, not invent one.",
       alts=["双廊古镇明天天气", "洱海双廊明天会下雨吗", "查一下双廊的天气预报", "大理双廊古镇明天天气如何", "Weather at Shuanglang town tomorrow?"])


@b
def w14():
    wx = [weather("重庆", "阴 27°C", [("2026-09-16", "阴", "24~30", "45%"), ("2026-09-17", "中雨", "22~26", "75%"), ("2026-09-18", "多云", "22~28", "30%"), ("2026-09-19", "晴", "23~31", "10%")], aliases=["Chongqing"])]

    def compute(files, wx):
        d = wx[0]["report"]["daily"]
        return {}, [[("all", [d[1]["rain_chance"]])], [("all", [d[3]["rain_chance"], d[3]["condition"]])]]
    mk("hyb-33614", sub="weather", desc="Multi-turn: tomorrow first, then Saturday which needs a deeper forecast", wx=wx,
       turns=[{"p": "重庆明天天气怎么样？", "req": ["get_weather"], "forb": WEBX},
              {"p": "周六呢？我想改到周六去洪崖洞。"}],
       compute=compute, must=["get_weather"], traps=["TR-DECOY"], decoys={"TR-DECOY": "30%"}, rc=2,
       notes="Turn1: tomorrow 中雨 75%. Turn2: Saturday 09-19 晴 10% (4th row, days>=4).",
       alts=["重庆明天的天气", "明天重庆下雨吗", "重庆明天预报", "查查重庆明天的天气", "Chongqing weather tomorrow?"])
