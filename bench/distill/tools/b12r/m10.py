"""M10 (b12r): get_weather lane. Fixture clock 2026-09-16 (Wed): 明天 = 09-17, 后天 = 09-18.
Ids 9441-9460: M10c composites hyb-9441..9450 (web fact + get_weather in one request),
M10b weather-into-file doc-9451..9454, cfg-9455..9457, fs-9458..9460.

File policy for M10b: the prompt states the exact line format and the newline rule; the
expected file is compared exactly; read_file is the natural read-back."""
import json

from common import lines, weather, write_case

REFS = {}
NOWEB = ["web_search", "web_fetch"]


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


# ------------------------------------------------------------------ M10c composites

def composite(cid, *, city, aliases, current, rows, qm, url, title, snippet, file, topic, desc, prompt, alts, reply,
              day_idx, date, cond, fact, query_hint, any_of=None, decoy, cond_any=None):
    fx = [weather(city, current, rows, aliases=aliases)]
    web = [{"query_match": qm, "url": url, "url_match": url.split("//")[1].split("/")[0].split(".")[1],
            "title": title, "snippet": snippet, "content": "# %s\n\n%s" % (title, snippet), "published_at": "2026-08-30"}]
    files = {file[0]: lines(file[1])}
    verify = '''
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][%d]
assert day["date"] == %r and day["condition"] == %r
assert case["files"][%r].startswith(%r)
snippet = case["web_fixture"][0]["snippet"]
assert %r in snippet
print(json.dumps(%s, ensure_ascii=False))
''' % (day_idx, date, rows[day_idx][1], file[0], file[1][0], (any_of or [fact])[0],
           ({"expected_contains_any": any_of} if any_of else {"expected_string": fact}))
    notes = f"""## Traps
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather and {query_hint} from one web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
- TR-DECOY: {decoy}

## Reference solution
1. get_weather {{"location": "{city}", "days": {day_idx + 1}}}
2. web_search {query_hint}
Final answer: {reply}

## Why the answer is unique
One forecast row and one web snippet each carry the unique value ({fact}).
""" + phrasings(*alts)
    expect = {"required_tools": ["get_weather", "web_search"], "max_output_chars": 600}
    if cond_any:
        expect["output_contains_any"] = cond_any
        expect["output_contains"] = [fact]
        if any_of:
            expect.pop("output_contains")
            expect["output_contains_any"] = any_of
            expect["output_contains_any_2"] = None
            expect.pop("output_contains_any_2")
    else:
        expect["output_contains"] = [cond] + ([] if any_of else [fact])
        if any_of:
            expect["output_contains_any"] = any_of
    return write_case(
        cid, desc=desc, task_type="special_tool", family="fam-hyb-b12r-%s-01" % topic, level="L2", ref_calls=2,
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": rows[day_idx][1], "TR-DECOY": decoy.split(":")[0]},
        axes=["CHN", "OBS"], files=files, verify=verify, notes=notes, weather_fixture=fx, web=web,
        turns=[{"prompt": prompt, "expect": expect}])


COMPOSITES = {}


def comp(cid, **kw):
    def build():
        return composite(cid, **kw)
    build.__name__ = cid.replace("-", "_")
    COMPOSITES[cid] = build
    return build


b9441 = comp(
    "hyb-9441", city="成都", aliases=["Chengdu"], current="阴 24°C 体感 26°C 湿度 72% 风速 6 km/h",
    rows=[("2026-09-16", "多云", "22~28", "20%"), ("2026-09-17", "小雨", "20~25", "70%"), ("2026-09-18", "阴", "21~27", "30%")],
    qm="熊猫", url="https://www.panda.example.cn/visit", title="成都大熊猫繁育研究基地 参观须知",
    snippet="基地全年开放，入园时间 7:30 起，18:00 停止售票；熊猫上午最活跃，建议尽早入园。",
    file=("旅行/成都.md", ["# 成都行", "", "- 周四看熊猫"]), topic="pandaopen",
    desc="Composite request: panda base opening time from web search plus tomorrow's forecast from the weather tool",
    prompt="明天我想去成都看大熊猫，熊猫基地几点开始入园？顺便看看成都明天的天气。",
    alts=["成都熊猫基地几点开门，成都明天天气怎样", "明天去看熊猫，基地几点入园，会下雨吗", "成都明天的天气，还有熊猫基地的入园时间", "查一下成都大熊猫基地的入园时间，再看明天成都天气", "熊猫基地早上几点能进？成都明天要带伞吗"],
    reply="成都大熊猫基地 7:30 开始入园；成都明天（9 月 17 日）有小雨，降水概率 70%，气温 20~25°C，记得带伞。",
    day_idx=1, date="2026-09-17", cond="小雨", fact="7:30", any_of=["7:30", "7：30", "7点30", "7 点 30", "7点半", "七点半"],
    query_hint="成都 大熊猫基地 入园时间", decoy="多云: today is 多云; only tomorrow (2026-09-17) is 小雨. The page also lists 18:00 as the ticket cut-off, which is not the opening time.")

b9442 = comp(
    "hyb-9442", city="西安", aliases=["Xi'an", "Xian"], current="晴 28°C 体感 29°C 湿度 45% 风速 9 km/h",
    rows=[("2026-09-16", "晴", "20~30", "5%"), ("2026-09-17", "多云", "19~29", "10%"), ("2026-09-18", "大雨", "17~22", "85%")],
    qm="兵马俑", url="https://www.bmy.example.cn/ticket", title="秦始皇帝陵博物院 兵马俑门票说明",
    snippet="秦始皇帝陵博物院官方票务：旺季（3 月 1 日—11 月 30 日）门票 120 元，需提前实名预约。",
    file=("旅行/西安.md", ["# 西安行", "", "- 周五去兵马俑"]), topic="xianbmyticket",
    desc="Composite request: terracotta army ticket price from web search plus the day-after-tomorrow forecast from the weather tool",
    prompt="后天我去西安看兵马俑，旺季门票多少钱？再查查西安后天的天气。",
    alts=["兵马俑旺季门票多少钱，西安后天天气呢", "后天去西安，兵马俑票价是多少，那天会下雨吗", "西安后天的天气，还有兵马俑门票", "查查兵马俑旺季票价，顺便看西安后天天气", "兵马俑现在门票多少？西安后天有雨吗"],
    reply="兵马俑旺季门票 120 元，需提前实名预约；西安后天（9 月 18 日）有大雨，降水概率 85%，17~22°C，记得带雨具。",
    day_idx=2, date="2026-09-18", cond="大雨", fact="120", query_hint="秦始皇帝陵博物院 兵马俑 旺季 门票",
    decoy="晴: today is 晴; only 后天 (2026-09-18) is 大雨.")

b9443 = comp(
    "hyb-9443", city="广州", aliases=["Guangzhou"], current="雷阵雨 27°C 体感 31°C 湿度 88% 风速 13 km/h",
    rows=[("2026-09-16", "雷阵雨", "26~32", "75%"), ("2026-09-17", "多云", "26~33", "40%"), ("2026-09-18", "晴", "27~34", "15%")],
    qm="广州塔", url="https://www.cantontower.example.cn/tickets", title="广州塔 观光票价",
    snippet="广州塔官方售票：主塔观光票成人 150 元，现场与线上同价；儿童、老人另有优惠。",
    file=("生活/广州.md", ["# 广州周末", "", "- 晚上去珠江边"]), topic="cantontower",
    desc="Composite request: tower admission price from web search plus today's forecast from the weather tool",
    prompt="今晚想上广州塔，成人观光票多少钱？另外广州今天的天气怎么样？",
    alts=["广州塔成人票多少钱，广州今天天气如何", "今天去广州塔，票价多少，会下雨吗", "广州今天的天气，还有广州塔观光票价格", "查下广州塔成人票价，再看广州今天天气", "广州塔观光票要多少？今天广州有雷雨吗"],
    reply="广州塔主塔观光票成人 150 元；广州今天有雷阵雨，降水概率 75%，26~32°C，晚上出门带好伞。",
    day_idx=0, date="2026-09-16", cond="雷阵雨", fact="150", query_hint="广州塔 成人 观光票 价格",
    decoy="多云: tomorrow is 多云; today (2026-09-16) is 雷阵雨.")

b9444 = comp(
    "hyb-9444", city="厦门", aliases=["Xiamen"], current="多云 29°C 体感 33°C 湿度 76% 风速 11 km/h",
    rows=[("2026-09-16", "晴", "27~33", "10%"), ("2026-09-17", "阵雨", "26~31", "60%"), ("2026-09-18", "多云", "26~32", "25%")],
    qm="鼓浪屿", url="https://www.gly-ferry.example.cn/fare", title="厦门—鼓浪屿 轮渡票价",
    snippet="厦门至鼓浪屿轮渡（游客）往返船票 35 元，须在码头或线上实名购票；上岛景点另计。",
    file=("旅行/厦门.md", ["# 厦门行", "", "- 周四上岛"]), topic="glyferry",
    desc="Composite request: ferry fare from web search plus tomorrow's forecast from the weather tool",
    prompt="明天坐船去鼓浪屿，往返船票多少钱？再看看厦门明天的天气。",
    alts=["去鼓浪屿的轮渡往返多少钱，厦门明天天气呢", "明天上鼓浪屿，船票多少，会下雨吗", "厦门明天的天气，还有去鼓浪屿的往返船票", "查下鼓浪屿轮渡往返票价，顺便看厦门明天天气", "鼓浪屿往返船票多少钱？厦门明天有雨吗"],
    reply="厦门到鼓浪屿的游客往返船票 35 元；厦门明天（9 月 17 日）有阵雨，降水概率 60%，26~31°C，上岛带把伞。",
    day_idx=1, date="2026-09-17", cond="阵雨", fact="35", query_hint="厦门 鼓浪屿 轮渡 往返 船票",
    decoy="晴: today is 晴; only tomorrow (2026-09-17) is 阵雨.")

b9445 = comp(
    "hyb-9445", city="London", aliases=["伦敦"], current="Overcast 15°C feels 13°C humidity 80% wind 18 km/h",
    rows=[("2026-09-16", "Overcast", "12~16", "35%"), ("2026-09-17", "Light rain", "11~15", "75%"), ("2026-09-18", "Cloudy", "10~16", "30%")],
    qm="heathrow", url="https://www.heathrowexpress.example.uk/fares", title="Heathrow Express fares",
    snippet="Heathrow Express to London Paddington: adult single £25 when booked online, journey time 15 minutes.",
    file=("trip/uk.md", ["# UK trip", "", "- Thursday: land at Heathrow"]), topic="heathrowexpress",
    desc="Composite request in English: airport train fare from web search plus tomorrow's forecast from the weather tool",
    prompt="I land at Heathrow tomorrow and want to take the Heathrow Express to Paddington. How much is an adult single, and what will the weather in London be like tomorrow?",
    alts=["Heathrow Express adult single fare to Paddington, plus London's forecast for tomorrow", "How much is the Heathrow Express and will it rain in London tomorrow?", "London tomorrow: weather, and the price of the Heathrow Express to Paddington", "What does an adult single on the Heathrow Express cost, and what's tomorrow's London weather?", "Tomorrow I arrive in London: Heathrow Express fare and the forecast, please"],
    reply="An adult single on the Heathrow Express to Paddington is £25 booked online (15 minutes). London tomorrow (2026-09-17) will see light rain, 75% chance, 11-15°C, so bring an umbrella.",
    day_idx=1, date="2026-09-17", cond="Light rain", fact="£25", any_of=["£25", "25 pounds", "GBP 25", "25 GBP"], query_hint="Heathrow Express adult single fare Paddington",
    cond_any=["rain", "Rain"], decoy="Overcast: today is Overcast; only tomorrow (2026-09-17) is Light rain.")

b9446 = comp(
    "hyb-9446", city="洛阳", aliases=["Luoyang"], current="多云 26°C 体感 27°C 湿度 55% 风速 8 km/h",
    rows=[("2026-09-16", "多云", "19~29", "10%"), ("2026-09-17", "雷阵雨", "18~26", "65%"), ("2026-09-18", "阴", "17~25", "30%")],
    qm="龙门石窟", url="https://www.longmen.example.cn/ticket", title="龙门石窟景区 门票信息",
    snippet="龙门石窟景区官方：当前旺季（3 月 1 日—11 月 30 日）成人门票 90 元，网络购票免排队。",
    file=("旅行/洛阳.md", ["# 洛阳行", "", "- 周四看石窟"]), topic="longmenticket",
    desc="Composite request: grotto ticket price from web search plus tomorrow's forecast from the weather tool",
    prompt="明天去洛阳逛龙门石窟，现在这个季节门票多少钱？洛阳明天天气怎么样？",
    alts=["龙门石窟现在门票多少，洛阳明天天气如何", "明天去龙门石窟，票价多少，会下雨吗", "洛阳明天的天气，还有龙门石窟门票", "查查龙门石窟旺季门票价格，再看洛阳明天天气", "龙门石窟成人票多少钱？洛阳明天有雷雨吗"],
    reply="龙门石窟当前旺季成人门票 90 元；洛阳明天（9 月 17 日）有雷阵雨，降水概率 65%，18~26°C，带好雨具。",
    day_idx=1, date="2026-09-17", cond="雷阵雨", fact="90", query_hint="龙门石窟 旺季 成人 门票",
    decoy="多云: today is 多云; only tomorrow (2026-09-17) is 雷阵雨.")

b9447 = comp(
    "hyb-9447", city="海口", aliases=["Haikou"], current="阵雨 29°C 体感 34°C 湿度 86% 风速 14 km/h",
    rows=[("2026-09-16", "雷阵雨", "27~32", "70%"), ("2026-09-17", "阵雨", "27~31", "60%"), ("2026-09-18", "大雨", "26~30", "85%")],
    qm="三亚", url="https://www.hainan-rail.example.cn/hk-sanya", title="海口东—三亚 环岛高铁票价",
    snippet="海南环岛高铁海口东—三亚二等座票价 79.5 元，最快 1 小时 26 分。",
    file=("旅行/海南.md", ["# 海南行", "", "- 周五去三亚"]), topic="hainanrail",
    desc="Composite request: high-speed rail fare from web search plus the day-after-tomorrow forecast from the weather tool",
    prompt="后天我坐环岛高铁从海口去三亚，二等座多少钱？海口后天天气怎样？",
    alts=["环岛高铁海口到三亚二等座多少钱，海口后天天气呢", "后天海口去三亚的高铁票价，还有海口那天的天气", "海口后天的天气，以及高铁到三亚二等座价格", "查下海口东到三亚的二等座票价，再看海口后天天气", "海口到三亚二等座要多少？后天海口下大雨吗"],
    reply="海口东到三亚环岛高铁二等座 79.5 元；海口后天（9 月 18 日）有大雨，降水概率 85%，26~30°C，出发前备好雨具。",
    day_idx=2, date="2026-09-18", cond="大雨", fact="79.5", query_hint="海口东 三亚 环岛高铁 二等座 票价",
    decoy="阵雨: tomorrow is 阵雨; only 后天 (2026-09-18) is 大雨.")

b9448 = comp(
    "hyb-9448", city="呼和浩特", aliases=["Hohhot"], current="晴 21°C 体感 20°C 湿度 35% 风速 17 km/h",
    rows=[("2026-09-16", "晴", "12~24", "0%"), ("2026-09-17", "多云", "11~23", "5%"), ("2026-09-18", "阵雨", "8~17", "55%")],
    qm="内蒙古博物院", url="https://www.nmgmuseum.example.cn/visit", title="内蒙古博物院 参观指南",
    snippet="内蒙古博物院开放时间 9:00—17:00（16:30 停止入馆），每周一闭馆，法定节假日除外。",
    file=("出差/呼和浩特.md", ["# 呼和浩特出差", "", "- 周五抽空逛博物院"]), topic="nmgmuseumclosed",
    desc="Composite request: museum weekly closing day from web search plus the day-after-tomorrow forecast from the weather tool",
    prompt="后天我想去内蒙古博物院，请问它每周哪天闭馆？再看看呼和浩特后天的天气。",
    alts=["内蒙古博物院每周几闭馆，呼和浩特后天天气呢", "后天去内蒙古博物院，哪天不开门，那天天气如何", "呼和浩特后天的天气，还有内蒙古博物院的闭馆日", "查一下内蒙古博物院哪天闭馆，再看呼和浩特后天天气", "内蒙古博物院周几休息？呼和浩特后天会下雨吗"],
    reply="内蒙古博物院每周一闭馆（开放时间 9:00—17:00）；呼和浩特后天（9 月 18 日，周五）有阵雨，降水概率 55%，8~17°C，偏凉，带伞加外套。",
    day_idx=2, date="2026-09-18", cond="阵雨", fact="周一", any_of=["周一", "星期一", "礼拜一"], query_hint="内蒙古博物院 开放时间 闭馆",
    decoy="多云: tomorrow is 多云; only 后天 (2026-09-18) is 阵雨. The page also lists opening hours, which are not the closing day.")

b9449 = comp(
    "hyb-9449", city="Seattle", aliases=["西雅图"], current="Sunny 21°C feels 21°C humidity 50% wind 10 km/h",
    rows=[("2026-09-16", "Sunny", "13~23", "5%"), ("2026-09-17", "Drizzle", "12~18", "60%"), ("2026-09-18", "Cloudy", "11~19", "25%")],
    qm="space needle", url="https://www.spaceneedle.example.com/tickets", title="Space Needle tickets",
    snippet="Space Needle general admission, adult: $41, open daily; timed tickets recommended.",
    file=("trip/seattle.md", ["# Seattle trip", "", "- Thursday: Space Needle"]), topic="spaceneedle",
    desc="Composite request in English: attraction ticket price from web search plus tomorrow's forecast from the weather tool",
    prompt="I'm visiting Seattle tomorrow. How much is an adult ticket for the Space Needle, and what will the weather be like there tomorrow?",
    alts=["Space Needle adult ticket price, and Seattle's forecast for tomorrow", "How much to go up the Space Needle, and will it rain in Seattle tomorrow?", "Seattle tomorrow: the weather, and the adult Space Needle admission", "What does the Space Needle cost for an adult, and how's the Seattle weather tomorrow?", "Before I go up the Space Needle tomorrow: ticket price and Seattle forecast?"],
    reply="An adult ticket for the Space Needle is $41. Seattle tomorrow (2026-09-17) will have drizzle, 60% chance of rain, 12-18°C, so bring a light rain jacket.",
    day_idx=1, date="2026-09-17", cond="Drizzle", fact="$41", any_of=["$41", "41 dollars", "41 USD", "USD 41"], query_hint="Space Needle adult general admission price",
    cond_any=["rizzle", "rain", "Rain"], decoy="Sunny: today is Sunny; only tomorrow (2026-09-17) is Drizzle.")

b9450 = comp(
    "hyb-9450", city="黄山", aliases=["Huangshan"], current="多云 19°C 体感 18°C 湿度 70% 风速 12 km/h",
    rows=[("2026-09-16", "晴", "16~26", "5%"), ("2026-09-17", "多云", "15~24", "20%"), ("2026-09-18", "大雾", "12~19", "30%")],
    qm="云谷索道", url="https://www.hsscenic.example.cn/ropeway", title="黄山云谷索道 运营与票价",
    snippet="黄山云谷索道上行单程票价 80 元，首班 7:00，运行约 8 分钟；旺季请提前预约。",
    file=("旅行/黄山.md", ["# 黄山行", "", "- 周五上山"]), topic="yungu",
    desc="Composite request: cable-car fare from web search plus the day-after-tomorrow forecast from the weather tool",
    prompt="后天上黄山，云谷索道上行单程多少钱？黄山后天天气怎么样？",
    alts=["云谷索道上行一趟多少钱，黄山后天天气如何", "后天坐云谷索道上山，票价多少，天气怎样", "黄山后天的天气，还有云谷索道上行票价", "查下云谷索道上行单程价格，顺便看黄山后天天气", "云谷索道单程上山要多少钱？黄山后天有雾吗"],
    reply="黄山云谷索道上行单程 80 元；黄山后天（9 月 18 日）有大雾，降水概率 30%，12~19°C，山上能见度低，记得多带件外套。",
    day_idx=2, date="2026-09-18", cond="大雾", fact="80", query_hint="黄山 云谷索道 上行 单程 票价",
    decoy="多云: tomorrow is 多云; only 后天 (2026-09-18) is 大雾.")


# ------------------------------------------------------------------ M10b weather into a file

def wfile(cid, *, topic, desc, task_type, city, aliases, current, rows, idx, files, expected, calc, prompt, alts, reply,
          decoy, plan, trap_text, level="L1"):
    fx = [weather(city, current, rows, aliases=aliases)]
    date = rows[idx][0]
    verify = ('import json\ncase = json.load(open("case.json"))\nfiles = case["files"]\n'
              'day = case["weather_fixture"][0]["report"]["daily"][%d]\nassert day["date"] == %r\n'
              'low, high = day["temp_c"].split("~")\ncond = day["condition"]\nrain = day["rain_chance"]\n' % (idx, date)
              + calc.strip("\n") + '\nassert exp == %r\nprint(json.dumps({"files": exp}, ensure_ascii=False))\n' % expected)
    notes = f"""## Traps
- TR-DEFN: {trap_text}
- TR-DECOY: {decoy}

## Reference solution
1. get_weather {{"location": "{city}", "days": {idx + 1}}}
{plan}
Final answer: {reply}

## Why the answer is unique
The forecast row for {date} is fixed and the line format and newline rule are spelled out in the prompt.
""" + phrasings(*alts)
    return write_case(
        cid, desc=desc, task_type=task_type, family="fam-%s-b12r-%s-01" % (cid.split("-")[0], topic), level=level,
        ref_calls=3, traps=["TR-DEFN"], decoys={"TR-DEFN": rows[0][1] if idx else "UNKNOWN"}, axes=["OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx, case_expect={"files": {p: {"equals": t} for p, t in expected.items()}},
        turns=[{"prompt": prompt, "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def doc_9451():
    before = lines(["# 出行日志", "", "- 09-14 北京 晴 14~26°C", "- 09-15 北京 多云 15~25°C"])
    after = before + "- 09-17 上海 小雨 18~24°C\n"
    return wfile(
        "doc-9451", topic="logappend", task_type="write_structured",
        desc="Appends one log line with tomorrow's forecast to a markdown trip log in an exact format",
        city="上海", aliases=["Shanghai"], current="阴 25°C 体感 27°C 湿度 75% 风速 10 km/h",
        rows=[("2026-09-16", "阴", "21~27", "30%"), ("2026-09-17", "小雨", "18~24", "65%"), ("2026-09-18", "多云", "19~26", "25%")],
        idx=1, files={"日志/出行日志.md": before}, expected={"日志/出行日志.md": after},
        calc='''path = "日志/出行日志.md"
assert files[path].startswith("# 出行日志") and files[path].endswith(chr(10)) and files[path].count(chr(10)) == 4
exp = {path: files[path] + "- %s 上海 %s %s°C" % (day["date"][5:], cond, day["temp_c"]) + chr(10)}''',
        prompt="在 日志/出行日志.md 末尾追加一行上海明天的天气，格式是「- 月-日 城市 天气 最低~最高°C」，比如已有的「- 09-15 北京 多云 15~25°C」。"
               "已有各行不要动，新加的这一行以换行结束，文件末尾只有这一个换行。",
        alts=["给出行日志加一条上海明天的天气", "日志/出行日志.md 最后补一行上海 9 月 17 日的预报，格式跟前面一样", "把上海明天的天气记到出行日志末尾", "出行日志续一行：上海明天天气，照已有行的写法", "Append Shanghai's forecast for tomorrow as a new line at the end of the trip log."],
        reply="已在 日志/出行日志.md 末尾追加「- 09-17 上海 小雨 18~24°C」，原有内容没动。",
        decoy="阴: today's row is 阴; the line is for tomorrow (2026-09-17, 小雨).",
        plan='2. append_file 日志/出行日志.md with "- 09-17 上海 小雨 18~24°C\\n"\n3. read_file 日志/出行日志.md to confirm',
        trap_text="the new line goes after the existing four lines and must end with exactly one newline; tomorrow is the second forecast row.")


def doc_9452():
    before = lines(["# 苏州出差简报", "", "- 出发：周四早班高铁", "- 住宿：观前街酒店", "- 明天天气：【待填】", "- 联系人：李敏"])
    after = before.replace("【待填】", "阵雨 24~28°C")
    return wfile(
        "doc-9452", topic="briefplaceholder", task_type="write_structured",
        desc="Replaces one placeholder line in a markdown brief with tomorrow's forecast, leaving the other lines untouched",
        city="苏州", aliases=["Suzhou"], current="阴 26°C 体感 28°C 湿度 74% 风速 7 km/h",
        rows=[("2026-09-16", "阴", "23~29", "30%"), ("2026-09-17", "阵雨", "24~28", "55%"), ("2026-09-18", "多云", "23~30", "20%")],
        idx=1, files={"简报/出差简报.md": before}, expected={"简报/出差简报.md": after},
        calc='''path = "简报/出差简报.md"
assert files[path].count("【待填】") == 1 and files[path].endswith(chr(10))
exp = {path: files[path].replace("【待填】", "%s %s°C" % (cond, day["temp_c"]))}''',
        prompt="简报/出差简报.md 里有一行「- 明天天气：【待填】」，把【待填】三个字连同括号换成苏州明天的天气，写成「天气 最低~最高°C」（比如「晴 16~24°C」）。其他各行原样保留，文件仍以一个换行结尾。",
        alts=["出差简报里的待填换成苏州明天的天气", "简报/出差简报.md 的明天天气那行填上苏州 9 月 17 日预报", "把简报中的【待填】改成苏州明天的天气和温度", "出差简报补全：明天天气一栏写苏州明天的预报", "Fill the placeholder on the tomorrow-weather line of the brief with Suzhou's forecast."],
        reply="已把简报里的「【待填】」换成「阵雨 24~28°C」，其他行没动。",
        decoy="阴: today's row is 阴; the placeholder is for tomorrow (阵雨).",
        plan='2. replace_lines (or write_file) on 简报/出差简报.md: the line becomes "- 明天天气：阵雨 24~28°C"\n3. read_file 简报/出差简报.md to confirm',
        trap_text="only the placeholder (with its brackets) is replaced, the rest of the line and file stay byte-identical.")


def doc_9453():
    before = "出门带伞\n"
    after = "武汉今天：多云\n气温 21~30°C，降水概率 20%\n"
    return wfile(
        "doc-9453", topic="notereplace", task_type="write_structured",
        desc="Overwrites a one-line reminder note with a two-line forecast note in an exact layout",
        city="武汉", aliases=["Wuhan"], current="多云 28°C 体感 31°C 湿度 66% 风速 9 km/h",
        rows=[("2026-09-16", "多云", "21~30", "20%"), ("2026-09-17", "雷阵雨", "22~29", "70%"), ("2026-09-18", "阴", "21~28", "35%")],
        idx=0, files={"提醒/今日提醒.txt": before}, expected={"提醒/今日提醒.txt": after},
        calc='''path = "提醒/今日提醒.txt"
assert files[path] == "出门带伞" + chr(10)
exp = {path: "武汉今天：%s" % cond + chr(10) + "气温 %s°C，降水概率 %s" % (day["temp_c"], rain) + chr(10)}''',
        prompt="把 提醒/今日提醒.txt 整个覆盖成两行：第一行「武汉今天：<天气>」，第二行「气温 <最低~最高>°C，降水概率 <百分比>」。"
               "两行都以换行结束，除这两行外文件里不要有别的内容。数据用武汉今天的预报。",
        alts=["用武汉今天的天气覆盖今日提醒.txt，两行", "今日提醒改成武汉今天的天气和气温、降水概率", "提醒文件重写：第一行武汉今天天气，第二行气温和降水概率", "把今日提醒的内容换成武汉今天的预报，格式见上", "Overwrite the reminder note with Wuhan's forecast for today in two lines."],
        reply="已把 提醒/今日提醒.txt 覆盖成武汉今天的两行预报：多云，21~30°C，降水概率 20%。",
        decoy="雷阵雨: tomorrow is 雷阵雨; today (2026-09-16) is 多云.",
        plan='2. write_file 提醒/今日提醒.txt with "武汉今天：多云\\n气温 21~30°C，降水概率 20%\\n"\n3. read_file 提醒/今日提醒.txt to confirm',
        trap_text="the whole file is overwritten (the old 出门带伞 line disappears); today is the first forecast row; the rain chance keeps its % sign.")


def doc_9454():
    before = lines(["| 日期 | 城市 | 天气 | 气温 |", "| --- | --- | --- | --- |", "| 09-16 | 长沙→成都 | 阴 | 22~28°C |",
                    "| 09-17 | 成都 | 待填 | 待填 |", "| 09-18 | 成都→重庆 | 待填 | 待填 |"])
    after = before.replace("| 09-17 | 成都 | 待填 | 待填 |", "| 09-17 | 成都 | 小雨 | 20~25°C |")
    return wfile(
        "doc-9454", topic="tablerow", task_type="write_structured",
        desc="Fills one row of a markdown itinerary table with tomorrow's forecast and leaves the other pending row alone",
        city="成都", aliases=["Chengdu"], current="阴 24°C 体感 26°C 湿度 72% 风速 6 km/h",
        rows=[("2026-09-16", "多云", "22~28", "20%"), ("2026-09-17", "小雨", "20~25", "70%"), ("2026-09-18", "阴", "21~27", "30%")],
        idx=1, files={"行程/行程表.md": before}, expected={"行程/行程表.md": after},
        calc='''path = "行程/行程表.md"
assert files[path].count("| 待填 | 待填 |") == 2 and files[path].endswith(chr(10))
exp = {path: files[path].replace("| 09-17 | 成都 | 待填 | 待填 |", "| 09-17 | 成都 | %s | %s°C |" % (cond, day["temp_c"]))}''',
        prompt="行程/行程表.md 是个 markdown 表格。把 09-17 那一行的两个「待填」换成成都明天的天气和气温，天气写汉字描述，气温写成「最低~最高°C」。"
               "其他行（包括 09-18 那行的待填）都不要动，保持表格竖线和空格的写法，文件仍以一个换行结尾。",
        alts=["行程表 09-17 那行填成都明天的天气和气温", "把行程/行程表.md 里 9 月 17 日的待填换成成都明天预报", "表格里 09-17 一行补上成都明天的天气，09-18 别动", "行程表的明天那行：天气和气温按成都预报填", "Fill the 09-17 row of the itinerary table with Chengdu's forecast for tomorrow."],
        reply="已把 09-17 那行填成「小雨 / 20~25°C」，09-18 那行仍是待填。",
        decoy="多云: today's row is 多云; the row to fill is 09-17 (小雨).",
        plan='2. replace_lines (or write_file) on 行程/行程表.md: the 09-17 row becomes "| 09-17 | 成都 | 小雨 | 20~25°C |"\n3. read_file 行程/行程表.md to confirm',
        trap_text="two rows contain 待填; only the 09-17 row is filled and the table pipes and spacing stay the same.")


def cfg_9455():
    before = lines(["TRIP_CITY=杭州", "TRIP_DATE=2026-09-17", "TRIP_WEATHER=", "TRIP_LOW=", "TRIP_HIGH=", "TRIP_OWNER=ops"])
    after = lines(["TRIP_CITY=杭州", "TRIP_DATE=2026-09-17", "TRIP_WEATHER=多云", "TRIP_LOW=20", "TRIP_HIGH=27", "TRIP_OWNER=ops"])
    return wfile(
        "cfg-9455", topic="envfill", task_type="edit_value",
        desc="Fills three empty KEY= values in an env file from tomorrow's forecast, keeping bare unquoted values",
        city="杭州", aliases=["Hangzhou"], current="阴 25°C 体感 27°C 湿度 73% 风速 8 km/h",
        rows=[("2026-09-16", "阴", "21~26", "40%"), ("2026-09-17", "多云", "20~27", "20%"), ("2026-09-18", "小雨", "20~25", "60%")],
        idx=1, files={"配置/trip.env": before}, expected={"配置/trip.env": after},
        calc='''path = "配置/trip.env"
assert "TRIP_DATE=2026-09-17" in files[path] and files[path].count("=" + chr(10)) == 3
exp = {path: files[path].replace("TRIP_WEATHER=" + chr(10), "TRIP_WEATHER=" + cond + chr(10)).replace("TRIP_LOW=" + chr(10), "TRIP_LOW=" + low + chr(10)).replace("TRIP_HIGH=" + chr(10), "TRIP_HIGH=" + high + chr(10))}''',
        prompt="配置/trip.env 里 TRIP_DATE 是 2026-09-17。把 TRIP_WEATHER、TRIP_LOW、TRIP_HIGH 三项的空值填成杭州那天的预报：天气写汉字描述，最低、最高写不带单位的整数，值不加引号。"
               "其他行不动，文件仍以一个换行结尾。",
        alts=["trip.env 里三个空值按杭州明天的预报填上", "配置/trip.env 的天气和最低最高温补上杭州 9 月 17 日数据", "给 trip.env 填杭州明天的天气、最低温、最高温", "trip.env 里 TRIP_DATE 那天的杭州预报填进去，不加引号", "Fill the empty weather, low and high entries in trip.env with Hangzhou's forecast for TRIP_DATE."],
        reply="已把 trip.env 填好：TRIP_WEATHER=多云，TRIP_LOW=20，TRIP_HIGH=27，其他行没动。",
        decoy="阴: today's row is 阴; TRIP_DATE points at 2026-09-17 (多云).",
        plan='2. replace_lines (or write_file) on 配置/trip.env: TRIP_WEATHER=多云, TRIP_LOW=20, TRIP_HIGH=27\n3. read_file 配置/trip.env to confirm',
        trap_text="the date to use is the one stored in TRIP_DATE (tomorrow), values are bare, and the TRIP_OWNER line stays.")


def cfg_9456():
    before = lines(["site: 青岛海滩", "forecast:", "  date: 2026-09-18", "  condition: unknown", "  low: 0", "  high: 0", "  rain_chance: 0", "owner: ops"])
    after = lines(["site: 青岛海滩", "forecast:", "  date: 2026-09-18", "  condition: 多云", "  low: 18", "  high: 24", "  rain_chance: 40", "owner: ops"])
    return wfile(
        "cfg-9456", topic="yamlforecast", task_type="edit_value",
        desc="Fills the four fields of a YAML forecast block from the day-after-tomorrow forecast, rain chance without percent sign",
        city="青岛", aliases=["Qingdao"], current="晴 23°C 体感 23°C 湿度 68% 风速 19 km/h",
        rows=[("2026-09-16", "晴", "19~25", "5%"), ("2026-09-17", "阴", "18~23", "25%"), ("2026-09-18", "多云", "18~24", "40%")],
        idx=2, files={"站点/status.yaml": before}, expected={"站点/status.yaml": after},
        calc='''path = "站点/status.yaml"
assert "  date: 2026-09-18" in files[path] and "  condition: unknown" in files[path]
exp = {path: files[path].replace("condition: unknown", "condition: " + cond).replace("low: 0", "low: " + low).replace("high: 0", "high: " + high).replace("rain_chance: 0", "rain_chance: " + rain.rstrip("%"))}''',
        prompt="站点/status.yaml 的 forecast 块里 date 是 2026-09-18。把 condition、low、high、rain_chance 四项改成青岛那天的预报："
               "condition 写汉字天气描述，low、high 写不带单位的整数，rain_chance 写不带 % 号的整数，值都不加引号。缩进和其他行保持原样，文件仍以一个换行结尾。",
        alts=["status.yaml 的 forecast 四项按青岛后天预报填", "站点/status.yaml 里 date 那天的青岛天气写进去", "给 status.yaml 的预报块填青岛 9 月 18 日数据", "yaml 里天气、最低、最高、降水概率四项改成青岛后天的值", "Update the forecast block of status.yaml with Qingdao's forecast for the listed date."],
        reply="已把 status.yaml 的 forecast 块改成：多云，最低 18，最高 24，降水概率 40，其他行没动。",
        decoy="晴: today's row is 晴; the date in the file is 2026-09-18, the third row (多云).",
        plan='2. replace_lines (or write_file) on 站点/status.yaml for the four fields\n3. read_file 站点/status.yaml to confirm',
        trap_text="the block date (09-18) selects the third row, rain_chance loses its % sign, indentation is kept.")


def cfg_9457():
    before = lines(["[app]", "name = \"gateway\"", "port = 8080", "", "[forecast]", "city = \"大连\"", "condition = \"\"", "range = \"\"", "", "[log]", "level = \"info\""])
    after = before.replace("condition = \"\"", "condition = \"晴\"").replace("range = \"\"", "range = \"17~23\"")
    return wfile(
        "cfg-9457", topic="tomlforecast", task_type="edit_value",
        desc="Fills two empty quoted TOML values in a [forecast] table from tomorrow's forecast, leaving other tables untouched",
        city="大连", aliases=["Dalian"], current="多云 22°C 体感 22°C 湿度 62% 风速 20 km/h",
        rows=[("2026-09-16", "多云", "16~22", "15%"), ("2026-09-17", "晴", "17~23", "5%"), ("2026-09-18", "晴", "16~24", "5%")],
        idx=1, files={"配置/app.toml": before}, expected={"配置/app.toml": after},
        calc='''path = "配置/app.toml"
assert files[path].count('= ""') == 2 and files[path].endswith(chr(10))
exp = {path: files[path].replace('condition = ""', 'condition = "' + cond + '"').replace('range = ""', 'range = "' + day["temp_c"] + '"')}''',
        prompt="配置/app.toml 的 [forecast] 表里 city 是大连，condition 和 range 还是空字符串。把它们填成大连明天的预报："
               "condition 写汉字天气描述，range 写「最低~最高」（不带单位），两个值都放在双引号里，等号两边的空格保持原样。其他行不动，文件仍以一个换行结尾。",
        alts=["app.toml 里 forecast 表的天气和温度范围按大连明天填上", "配置/app.toml 的空 condition、range 填大连明天预报", "给 toml 里 [forecast] 补上大连明天的天气和范围", "大连明天的天气写进 app.toml 的 forecast 表，值加双引号", "Fill the empty condition and range in the [forecast] table of app.toml with Dalian's forecast for tomorrow."],
        reply="已把 app.toml 的 [forecast] 填成 condition = \"晴\"、range = \"17~23\"，其他行没动。",
        decoy="多云: today's row is 多云; the values are for tomorrow (晴).",
        plan='2. replace_lines (or write_file) on 配置/app.toml: condition = "晴" and range = "17~23"\n3. read_file 配置/app.toml to confirm',
        trap_text="only the two empty values change, quotes and the spaces around = stay, and the [app]/[log] tables are untouched.")


def fs_9458():
    f = {"日报/2026-09-16.txt": "天气：多云 23~29°C\n", "日报/2026-09-17.txt": "天气：待填\n", "日报/2026-09-18.txt": "天气：待填\n"}
    exp = dict(f)
    exp["日报/2026-09-17.txt"] = "天气：雷阵雨 26~32°C\n"
    return wfile(
        "fs-9458", topic="dailyfile", task_type="bulk_edit",
        desc="Picks tomorrow's file by its date name in a daily-report directory and writes the forecast line into it",
        city="深圳", aliases=["Shenzhen"], current="多云 29°C 体感 34°C 湿度 80% 风速 12 km/h",
        rows=[("2026-09-16", "多云", "23~29", "30%"), ("2026-09-17", "雷阵雨", "26~32", "70%"), ("2026-09-18", "阵雨", "25~31", "55%")],
        idx=1, files=f, expected=exp,
        calc='''assert files["日报/2026-09-17.txt"] == "天气：待填" + chr(10) and files["日报/2026-09-18.txt"] == "天气：待填" + chr(10)
exp = dict(files)
exp["日报/2026-09-17.txt"] = "天气：%s %s°C" % (cond, day["temp_c"]) + chr(10)''',
        prompt="日报目录里每天一个文件，文件名就是日期。明天那个文件里只有「天气：待填」一行，把它改成深圳明天的天气，写成「天气：<天气> <最低~最高>°C」，以换行结束。别的日期的文件不要动。",
        alts=["日报里明天的文件填上深圳明天的天气", "把 2026-09-17 那天的日报天气一行改成深圳预报", "日报目录中明天那份，天气一栏按深圳明天预报写", "深圳明天的天气写进明天日期的日报文件", "Write Shenzhen's forecast for tomorrow into tomorrow's file in the daily-report folder."],
        reply="已把 日报/2026-09-17.txt 改成「天气：雷阵雨 26~32°C」，其他日期的文件没动。",
        decoy="多云: today's row is 多云; the right file is 2026-09-17.txt (雷阵雨), and 2026-09-18.txt also says 待填 but must stay.",
        plan='2. write_file 日报/2026-09-17.txt with "天气：雷阵雨 26~32°C\\n"\n3. read_file 日报/2026-09-17.txt to confirm',
        trap_text="two files say 待填; tomorrow's file is selected by its date name, the day-after-tomorrow file stays.")


def fs_9459():
    f = {"天气/海口.txt": "雷阵雨\n27~32°C\n"}
    exp = {"天气/海口.txt": f["天气/海口.txt"], "天气/南宁.txt": "晴\n25~34°C\n"}
    return wfile(
        "fs-9459", topic="newcityfile", task_type="bulk_edit",
        desc="Creates a new two-line city weather file next to an existing example, with the day-after-tomorrow forecast",
        city="南宁", aliases=["Nanning"], current="多云 30°C 体感 35°C 湿度 70% 风速 8 km/h",
        rows=[("2026-09-16", "多云", "25~33", "20%"), ("2026-09-17", "阵雨", "25~32", "50%"), ("2026-09-18", "晴", "25~34", "10%")],
        idx=2, files=f, expected=exp,
        calc='''assert files["天气/海口.txt"] == "雷阵雨" + chr(10) + "27~32°C" + chr(10)
exp = dict(files)
exp["天气/南宁.txt"] = cond + chr(10) + day["temp_c"] + "°C" + chr(10)''',
        prompt="照 天气/海口.txt 的格式，给南宁后天的天气新建 天气/南宁.txt：第一行只写天气，第二行写「最低~最高°C」，两行都以换行结束，不要有别的内容。海口那个文件不要改。",
        alts=["仿照海口.txt 为南宁后天天气建一个南宁.txt", "天气目录里新增南宁.txt，内容是南宁后天预报，格式同海口", "南宁后天的天气按海口.txt 的写法存成新文件", "建 天气/南宁.txt，两行：天气和温度范围，数据取南宁后天", "Create 天气/南宁.txt in the same two-line format as 海口.txt using Nanning's forecast for the day after tomorrow."],
        reply="已新建 天气/南宁.txt：第一行「晴」，第二行「25~34°C」，海口.txt 没动。",
        decoy="多云: today's row is 多云; the file is for the day after tomorrow (晴).",
        plan='2. read_file 天气/海口.txt (optional, format example)\n3. write_file 天气/南宁.txt with "晴\\n25~34°C\\n"\n4. read_file 天气/南宁.txt to confirm',
        trap_text="the new file is created (not existing yet) with the example file's two-line layout; 后天 is the third row.")


def fs_9460():
    before = "1. 带身份证\n2. 带充电宝\n预报：待更新"
    after = "1. 带身份证\n2. 带充电宝\n预报：小雨 11~17°C"
    return wfile(
        "fs-9460", topic="lastlinenonl", task_type="bulk_edit",
        desc="Replaces the final newline-less line of a short packing note with tomorrow's forecast, keeping the no-trailing-newline form",
        city="西宁", aliases=["Xining"], current="多云 15°C 体感 14°C 湿度 55% 风速 13 km/h",
        rows=[("2026-09-16", "多云", "9~19", "20%"), ("2026-09-17", "小雨", "11~17", "60%"), ("2026-09-18", "阴", "10~18", "35%")],
        idx=1, files={"笔记/出行提示.txt": before}, expected={"笔记/出行提示.txt": after},
        calc='''path = "笔记/出行提示.txt"
assert files[path].endswith("预报：待更新") and files[path].count(chr(10)) == 2
exp = {path: files[path].replace("待更新", "%s %s°C" % (cond, day["temp_c"]))}''',
        prompt="笔记/出行提示.txt 最后一行是「预报：待更新」，把「待更新」换成西宁明天的天气，写成「<天气> <最低~最高>°C」。前两行不动，这个文件原来行尾没有换行符，改完也不要加。",
        alts=["出行提示最后一行的待更新换成西宁明天预报", "笔记/出行提示.txt 末行填西宁明天的天气和温度", "把出行提示里的预报行改成西宁明天的天气，不加结尾换行", "西宁明天的天气写进出行提示最后一行", "Replace 待更新 at the end of the packing note with Xining's forecast for tomorrow, keeping no trailing newline."],
        reply="已把 笔记/出行提示.txt 最后一行改成「预报：小雨 11~17°C」，前两行没动，行尾仍没有换行。",
        decoy="多云: today's row is 多云; the line is for tomorrow (小雨).",
        plan='2. replace_lines (or write_file) on 笔记/出行提示.txt: last line becomes "预报：小雨 11~17°C", no trailing newline\n3. read_file 笔记/出行提示.txt to confirm',
        trap_text="the file has no trailing newline before and after; only the 待更新 text changes.")


BUILDERS = [COMPOSITES[k] for k in sorted(COMPOSITES)] + [doc_9451, doc_9452, doc_9453, doc_9454, cfg_9455, cfg_9456, cfg_9457,
                                                         fs_9458, fs_9459, fs_9460]
SPEC = {k: dict(kind="weather", sub="M10c", dates=[]) for k in COMPOSITES}
_DATES = {"hyb-9441": "2026-09-17", "hyb-9442": "2026-09-18", "hyb-9443": "2026-09-16", "hyb-9444": "2026-09-17", "hyb-9445": "2026-09-17",
          "hyb-9446": "2026-09-17", "hyb-9447": "2026-09-18", "hyb-9448": "2026-09-18", "hyb-9449": "2026-09-17", "hyb-9450": "2026-09-18"}
for _k, _d in _DATES.items():
    SPEC[_k]["dates"] = [_d]
for _k in ("doc-9451", "doc-9452", "doc-9453", "doc-9454", "cfg-9455", "cfg-9456", "cfg-9457", "fs-9458", "fs-9459", "fs-9460"):
    SPEC[_k] = dict(kind="weather_write", sub="M10b")
