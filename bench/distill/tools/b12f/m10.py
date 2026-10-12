"""M10 (b12f): special-purpose tool first -- get_weather over web search.
Fixture clock is 2026-09-16 (Wed): 明天 = 09-17 (Thu), 后天 = 09-18 (Fri).
Lane b12f, ids 9141-9160: M10c composites (hyb-9141..9146: web fact + get_weather),
M10a landmark recovery (hyb-9147..9150), M10d local rules (hyb-9151..9154),
M10b write the forecast (hyb-9155..9157), M10e concept negatives (nt-9158..9160).

Newline policy for M10b: every prompt states the exact line format AND whether the
file ends with a newline; the expected file is compared exactly."""
import json

from common import lines, weather, write_case

REFS = {}
NOWEB = ["web_search", "web_fetch"]


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


# ------------------------------------------------------------------ M10c composites

def composite(cid, *, city, aliases, current, rows, qm, url, title, snippet, file, topic, desc, prompt, alts, reply,
              day_idx, date, cond, fact, query_hint, any_of=None, traps_note, decoy, cond_any=None):
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
- TR-MULTISRC: two sub-requests with two sources -- the forecast comes from get_weather ({traps_note}) and {query_hint} from web search; the weather part must not be searched, and once both facts are on screen the answer is written without more calls.
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
    else:
        expect["output_contains"] = [cond] + ([] if any_of else [fact])
        if any_of:
            expect["output_contains_any"] = any_of
    return write_case(
        cid, desc=desc, task_type="special_tool", family="fam-hyb-b12f-%s-01" % topic, level="L2", ref_calls=2,
        traps=["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": rows[day_idx][1], "TR-DECOY": decoy.split(":")[0]},
        axes=["CHN", "OBS"], files=files, verify=verify, notes=notes, weather_fixture=fx, web=web,
        turns=[{"prompt": prompt, "expect": expect}])


def hyb_9141():
    return composite(
        "hyb-9141", city="南京", aliases=["Nanjing"], current="多云 27°C 体感 29°C 湿度 68% 风速 11 km/h",
        rows=[("2026-09-16", "多云", "22~29", "20%"), ("2026-09-17", "小雨", "21~26", "60%"), ("2026-09-18", "阴", "21~27", "35%")],
        qm="南京", url="https://www.rail.example.cn/bj-nj", title="北京南到南京南 高铁票价参考",
        snippet="北京南—南京南 G 字头高铁二等座票价 443.5 元，最快 3 小时 29 分。",
        file=("出差/南京.md", ["# 南京出差", "", "- 周四到达"]), topic="njtrainfare",
        desc="Composite request: train fare from web search plus tomorrow's forecast from the weather tool",
        prompt="我明天坐高铁从北京去南京，北京南到南京南的二等座票价是多少？顺便看看南京明天的天气。",
        alts=["北京南到南京南二等座多少钱，再看南京明天天气", "查一下去南京的高铁二等座票价，还有南京明天会不会下雨", "南京明天天气如何？北京到南京高铁二等座要多少钱",
              "明天北京去南京的高铁票价和南京的天气", "北京南—南京南二等座票价是多少，南京明天什么天气"],
        reply="北京南到南京南二等座票价 443.5 元；南京明天（9 月 17 日）有小雨，降水概率 60%，气温 21~26°C，记得带伞。",
        day_idx=1, date="2026-09-17", cond="小雨", fact="443.5", query_hint="北京南 南京南 高铁 二等座 票价",
        traps_note="明天 is the second row", decoy="多云: today is 多云; only tomorrow (2026-09-17) is 小雨.")


def hyb_9142():
    return composite(
        "hyb-9142", city="敦煌", aliases=["Dunhuang"], current="晴 25°C 体感 24°C 湿度 18% 风速 14 km/h",
        rows=[("2026-09-16", "晴", "13~27", "0%"), ("2026-09-17", "晴", "14~28", "0%"), ("2026-09-18", "扬沙", "10~22", "5%")],
        qm="莫高窟", url="https://www.mgk.example.cn/ticket", title="莫高窟参观预约网：旺季票价说明",
        snippet="敦煌研究院官方预约渠道：莫高窟旺季（4 月 1 日—10 月 31 日）数字展示加实景洞窟套票 238 元，需提前预约。",
        file=("旅行/西北.md", ["# 西北行", "", "- 周五去莫高窟"]), topic="dunhuangticket",
        desc="Composite request: attraction ticket price from web search plus the day-after-tomorrow forecast from the weather tool",
        prompt="后天我去敦煌莫高窟，旺季套票多少钱？再看看敦煌后天的天气怎么样。",
        alts=["敦煌莫高窟旺季套票多少钱，敦煌后天天气呢", "后天去敦煌，莫高窟门票要多少，那天天气好吗", "敦煌后天的天气，还有莫高窟旺季票价",
              "查查敦煌莫高窟套票价格，顺便看敦煌后天天气", "莫高窟旺季门票多少钱？敦煌后天有风沙吗"],
        reply="莫高窟旺季数字展示加实景洞窟套票 238 元，需提前预约；敦煌后天（9 月 18 日）有扬沙，10~22°C，降水概率 5%，出行带好口罩。",
        day_idx=2, date="2026-09-18", cond="扬沙", fact="238", query_hint="敦煌 莫高窟 旺季 套票",
        traps_note="后天 is the third row", decoy="晴: today and tomorrow are 晴; only 后天 (2026-09-18) is 扬沙.")


def hyb_9143():
    return composite(
        "hyb-9143", city="Kyoto", aliases=["京都"], current="Cloudy 26°C feels 28°C humidity 70% wind 8 km/h",
        rows=[("2026-09-16", "Cloudy", "21~28", "30%"), ("2026-09-17", "Light rain", "20~25", "70%"), ("2026-09-18", "Cloudy", "20~27", "25%")],
        qm="kyoto", url="https://www.rail.example.jp/nozomi-fare", title="Nozomi Tokyo to Kyoto fares",
        snippet="Nozomi Tokyo–Kyoto reserved-seat fare: 14,720 yen, fastest journey 2 h 15 min.",
        file=("trip/japan.md", ["# Japan trip", "", "- Thursday: Tokyo to Kyoto"]), topic="kyotonozomi",
        desc="Composite request in English: train fare from web search plus tomorrow's forecast from the weather tool",
        prompt="I'm taking the Nozomi from Tokyo to Kyoto tomorrow. What does a reserved-seat ticket cost, and what will the weather in Kyoto be like tomorrow?",
        alts=["How much is a reserved seat on the Nozomi to Kyoto, and what's Kyoto's weather tomorrow?", "Nozomi fare Tokyo to Kyoto, plus the Kyoto forecast for tomorrow",
              "Kyoto tomorrow: weather, and what does the Nozomi ticket from Tokyo cost?", "Tell me the Nozomi reserved-seat price to Kyoto and whether it will rain in Kyoto tomorrow",
              "Before I head to Kyoto tomorrow: Nozomi reserved fare and the Kyoto forecast?"],
        reply="A reserved seat on the Nozomi from Tokyo to Kyoto is 14,720 yen. Kyoto tomorrow (2026-09-17) will see light rain, 70% chance, 20-25°C, so pack an umbrella.",
        day_idx=1, date="2026-09-17", cond="Light rain", fact="14,720", query_hint="Nozomi Tokyo Kyoto reserved seat fare",
        cond_any=["rain", "Rain"], traps_note="tomorrow is the second row",
        decoy="Cloudy: today is Cloudy; only tomorrow (2026-09-17) is Light rain.")


def hyb_9144():
    return composite(
        "hyb-9144", city="苏州", aliases=["Suzhou"], current="阴 26°C 体感 28°C 湿度 74% 风速 7 km/h",
        rows=[("2026-09-16", "阴", "23~29", "30%"), ("2026-09-17", "阵雨", "24~28", "55%"), ("2026-09-18", "多云", "23~30", "20%")],
        qm="苏州", url="https://www.szmuseum.example.cn/visit", title="苏州博物馆参观指南",
        snippet="苏州博物馆开放时间：周二至周日 9:00—17:00（16:00 停止入馆），周一闭馆；需实名预约。",
        file=("周末/苏州.md", ["# 苏州半日游", "", "- 下午去博物馆"]), topic="suzhoumuseum",
        desc="Composite request: museum admission cut-off from web search plus tomorrow's forecast from the weather tool",
        prompt="明天我想下午去苏州博物馆，几点停止入馆？顺便查下苏州明天的天气。",
        alts=["苏州博物馆下午几点停止入馆，苏州明天天气怎样", "明天去苏州博物馆，最晚几点进，苏州会下雨吗", "苏州明天的天气，还有博物馆的停止入馆时间",
              "查查苏州博物馆的开放时间，再看苏州明天天气", "苏州博物馆几点不让进了？明天苏州天气呢"],
        reply="苏州博物馆 16:00 停止入馆（17:00 闭馆，周一闭馆）；苏州明天（9 月 17 日）有阵雨，降水概率 55%，24~28°C，带把伞。",
        day_idx=1, date="2026-09-17", cond="阵雨", fact="16:00", any_of=["16:00", "16：00", "16点", "16 点", "下午4点", "下午四点", "下午 4 点"],
        query_hint="苏州博物馆 开放时间 停止入馆", traps_note="明天 is the second row",
        decoy="阴: today is 阴; only tomorrow (2026-09-17) is 阵雨. The page also lists 17:00 as the closing time, which is not the cut-off.")


def hyb_9145():
    return composite(
        "hyb-9145", city="东京", aliases=["Tokyo"], current="晴 28°C 体感 31°C 湿度 66% 风速 10 km/h",
        rows=[("2026-09-16", "晴", "24~31", "10%"), ("2026-09-17", "雷阵雨", "22~28", "65%"), ("2026-09-18", "多云", "22~29", "25%")],
        qm="日元", url="https://www.fx.example.cn/cny-jpy", title="人民币汇率中间价",
        snippet="今日人民币汇率中间价：100 日元 = 4.52 元人民币。",
        file=("出差/东京.md", ["# 东京出差", "", "- 周四到东京"]), topic="tokyofx",
        desc="Composite request: exchange rate from web search plus tomorrow's forecast from the weather tool",
        prompt="明天我去东京出差，今天按中间价 100 日元能换多少人民币？另外东京明天天气怎么样？",
        alts=["100 日元现在换多少人民币，东京明天天气如何", "查下日元兑人民币的中间价，再看东京明天的天气", "东京明天会下雨吗？100 日元折合人民币多少",
              "去东京之前想知道日元汇率，还有东京明天天气", "今天 100 日元兑人民币中间价多少，明天东京天气呢"],
        reply="今天中间价 100 日元 = 4.52 元人民币；东京明天（9 月 17 日）有雷阵雨，降水概率 65%，22~28°C，出门带伞。",
        day_idx=1, date="2026-09-17", cond="雷阵雨", fact="4.52", query_hint="日元 人民币 中间价",
        traps_note="明天 is the second row", decoy="晴: today is 晴; only tomorrow (2026-09-17) is 雷阵雨.")


def hyb_9146():
    return composite(
        "hyb-9146", city="福州", aliases=["Fuzhou"], current="阴 27°C 体感 31°C 湿度 85% 风速 12 km/h",
        rows=[("2026-09-16", "中雨", "25~28", "80%"), ("2026-09-17", "多云", "25~32", "30%"), ("2026-09-18", "晴", "26~33", "10%")],
        qm="福州", url="https://www.fzmetro.example.cn/line1", title="福州地铁 1 号线运营时间",
        snippet="福州地铁 1 号线运营时间：6:30—22:45（以首末站发车为准）。",
        file=("生活/福州.md", ["# 福州日常", "", "- 周三晚上聚餐"]), topic="fuzhoumetro",
        desc="Composite request: last metro time from web search plus today's forecast from the weather tool",
        prompt="今晚我在福州坐地铁 1 号线回家，末班车几点？再看看福州今天的天气。",
        alts=["福州地铁 1 号线末班车几点，福州今天天气怎样", "今天福州下雨吗？地铁 1 号线最晚几点", "福州今天的天气，还有地铁 1 号线运营到几点",
              "查一下福州地铁 1 号线的末班时间和福州今天的天气", "福州 1 号线晚上最后一班是几点，今天要带伞吗"],
        reply="福州地铁 1 号线末班车 22:45（首班 6:30）；福州今天有中雨，降水概率 80%，25~28°C，晚上回家带伞。",
        day_idx=0, date="2026-09-16", cond="中雨", fact="22:45", any_of=["22:45", "22：45", "22点45", "22 点 45"],
        query_hint="福州地铁 1 号线 运营时间 末班车", traps_note="今天 is the first row",
        decoy="多云: tomorrow is 多云; today (2026-09-16) is 中雨.")


# ------------------------------------------------------------------ M10a landmark recovery

def landmark(cid, *, landmark_name, city, aliases, current, rows, file, idx, date, prompt, alts, answer, answer_expr,
             reply, why, topic, desc, decoy, number=False):
    fx = [weather(city, current, rows, aliases=aliases)]
    files = {file[0]: lines(file[1])}
    verify = '''
import json
case = json.load(open("case.json"))
fx = case["weather_fixture"][0]
day = fx["report"]["daily"][%d]
assert day["date"] == %r
assert %r not in fx["location"] and all(%r not in a for a in fx["aliases"])
assert case["files"][%r].startswith(%r)
print(json.dumps({"expected_string": %s}, ensure_ascii=False))
''' % (idx, date, landmark_name, landmark_name, file[0], file[1][0], answer_expr)
    notes = f"""## Traps
- TR-NEARNAME: {landmark_name} is a scenic spot / district of {city}, not a city of its own; get_weather resolves cities only, so asking for {landmark_name} returns location not found and the retry is {city} (asking for {city} straight away is equally good).
- TR-DECOY: {decoy}

## Reference solution
1. get_weather {{"location": "{city}", "days": 3}} (or {landmark_name} first, then {city} after the not-found error; the same failing name is never retried)
Final answer: {reply}

## Why the answer is unique
{why}
""" + phrasings(*alts)
    expect = {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "output_contains": [answer], "max_output_chars": 600}
    return write_case(
        cid, desc=desc, task_type="special_tool", family="fam-hyb-b12f-%s-01" % topic, level="L2", ref_calls=1,
        traps=["TR-NEARNAME", "TR-DECOY"], decoys={"TR-NEARNAME": "UNKNOWN", "TR-DECOY": decoy.split(":")[0]},
        axes=["ERR", "OBS"], files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": prompt, "expect": expect}])


def hyb_9147():
    return landmark(
        "hyb-9147", landmark_name="亚龙湾", city="三亚", aliases=["Sanya"], current="晴 31°C 体感 37°C 湿度 78% 风速 15 km/h",
        rows=[("2026-09-16", "晴", "27~33", "10%"), ("2026-09-17", "雷阵雨", "26~31", "70%"), ("2026-09-18", "多云", "26~32", "30%")],
        file=("旅行/海南.md", ["# 海南行", "", "- 周四上午亚龙湾潜水"]), idx=1, date="2026-09-17",
        prompt="明天上午我去亚龙湾潜水，会下雨吗？降水概率多少？", answer="70%", answer_expr='day["rain_chance"]',
        alts=["亚龙湾明天降水概率是多少", "明天去亚龙湾潜水，下雨的可能性大吗", "9 月 17 日亚龙湾会下雨吗", "亚龙湾明天天气怎么样，会不会有雷雨", "Will it rain at Yalong Bay tomorrow (亚龙湾)?"],
        reply="亚龙湾属于三亚，三亚明天（9 月 17 日）有雷阵雨，降水概率 70%，气温 26~31°C，潜水行程建议改期或备好雨具。",
        why="亚龙湾 is a bay in 三亚; tomorrow is the second forecast row.", topic="yalongbay",
        desc="Asks tomorrow's rain chance at a beach resort bay; the forecast must be looked up by its city",
        decoy="10%: today's rain chance is 10%; tomorrow (2026-09-17) is 70%.")


def hyb_9148():
    return landmark(
        "hyb-9148", landmark_name="北戴河", city="秦皇岛", aliases=["Qinhuangdao"], current="晴 22°C 体感 22°C 湿度 55% 风速 13 km/h",
        rows=[("2026-09-16", "晴", "15~26", "0%"), ("2026-09-17", "晴", "16~27", "5%"), ("2026-09-18", "多云", "17~29", "10%")],
        file=("周末/海边.md", ["# 海边小住", "", "- 周五清晨看日出"]), idx=2, date="2026-09-18",
        prompt="后天清晨我去北戴河海边看日出，那天最低气温大概多少度？", answer="17", answer_expr='day["temp_c"].split("~")[0]',
        alts=["北戴河后天最低几度", "后天早上北戴河冷不冷，最低多少", "9 月 18 日北戴河的最低气温", "后天去北戴河看日出，要穿多少，先告诉我最低温", "What will the low be at Beidaihe (北戴河) the day after tomorrow?"],
        reply="北戴河在秦皇岛，秦皇岛后天（9 月 18 日）多云，最低气温 17°C、最高 29°C，清晨海边有点凉，带件薄外套。",
        why="北戴河 is a seaside district of 秦皇岛; the day after tomorrow is the third forecast row.", topic="beidaihesunrise",
        desc="Asks the low temperature at a seaside district the day after tomorrow; the forecast must be looked up by its city",
        decoy="16: tomorrow's low is 16; the day after tomorrow (2026-09-18) is 17.")


def hyb_9149():
    return landmark(
        "hyb-9149", landmark_name="漓江", city="桂林", aliases=["Guilin"], current="小雨 25°C 体感 28°C 湿度 90% 风速 6 km/h",
        rows=[("2026-09-16", "小雨", "22~27", "75%"), ("2026-09-17", "阴", "22~28", "40%"), ("2026-09-18", "多云", "23~30", "20%")],
        file=("旅行/广西.md", ["# 广西行", "", "- 周三上午漓江竹筏"]), idx=0, date="2026-09-16",
        prompt="今天上午我坐竹筏游漓江，今天天气怎么样？要不要带伞？", answer="小雨", answer_expr='day["condition"]',
        alts=["漓江今天天气如何", "今天去漓江漂流会下雨吗", "漓江今日天气，要带伞吗", "今天漓江竹筏能坐吗，天气怎样", "Is it raining at the Li River (漓江) today?"],
        reply="漓江在桂林，桂林今天有小雨，降水概率 75%，气温 22~27°C，竹筏游记得带伞或穿雨衣。",
        why="漓江 is a river at 桂林; today is the first forecast row.", topic="lijiangraft",
        desc="Asks today's weather on a famous river; the forecast must be looked up by its city",
        decoy="阴: tomorrow is 阴 with 40%; today (2026-09-16) is 小雨 with 75%.")


def hyb_9150():
    return landmark(
        "hyb-9150", landmark_name="外滩", city="上海", aliases=["Shanghai"], current="阴 27°C 体感 30°C 湿度 80% 风速 14 km/h",
        rows=[("2026-09-16", "阴", "23~29", "40%"), ("2026-09-17", "小雨", "22~27", "60%"), ("2026-09-18", "多云", "23~31", "20%")],
        file=("旅行/上海.md", ["# 上海行", "", "- 周五晚上外滩看夜景"]), idx=2, date="2026-09-18",
        prompt="后天晚上我去外滩看夜景，那天最高气温大概多少度？", answer="31", answer_expr='day["temp_c"].split("~")[1]',
        alts=["外滩后天最高几度", "后天去外滩，热不热，最高多少", "9 月 18 日外滩的最高气温", "后天晚上外滩看夜景，白天最高温是多少", "How warm will the Bund (外滩) get the day after tomorrow?"],
        reply="外滩在上海，上海后天（9 月 18 日）多云，最高气温 31°C、最低 23°C，降水概率 20%，晚上看夜景天气不错。",
        why="外滩 is a waterfront district of 上海; the day after tomorrow is the third forecast row.", topic="bundnight",
        desc="Asks the high temperature at a waterfront district the day after tomorrow; the forecast must be looked up by its city",
        decoy="27: tomorrow's high is 27; the day after tomorrow (2026-09-18) is 31.")


# ------------------------------------------------------------------ M10d local rules

def rule_case(cid, *, city, aliases, current, rows, rule_path, rule_lines, topic, desc, prompt, alts, rule_trap, decoy,
              expect_extra, answer_text, reply, why, check):
    fx = [weather(city, current, rows, aliases=aliases)]
    folder = rule_path.rsplit("/", 1)[0]
    note_path = folder + "/说明.md" if folder else "说明.md"
    note_lines = ["# 说明", "", "本目录存放日常规则。"] if not rule_lines[0].isascii() else ["# README", "", "This folder holds the standing rules."]
    files = {rule_path: lines(rule_lines), note_path: lines(note_lines)}
    verify = '''
import json
case = json.load(open("case.json"))
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
assert case["files"][%r].startswith(%r)
assert case["files"][%r].startswith(%r)
%s
print(json.dumps(%s, ensure_ascii=False))
''' % (rule_path, rule_lines[0], note_path, note_lines[0], check,
           ({"expected_contains_any": expect_extra["output_contains_any"]} if "output_contains_any" in expect_extra
            else {"expected_string": answer_text}))
    notes = f"""## Traps
- TR-RULEFILE: {rule_trap}
- TR-DECOY: {decoy}

## Reference solution
1. read_file {rule_path} (list_files first)
2. get_weather {{"location": "{city}", "days": 2}}
Final answer: {reply}

## Why the answer is unique
{why}
""" + phrasings(*alts)
    expect = {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}
    expect.update(expect_extra)
    return write_case(
        cid, desc=desc, task_type="special_tool", family="fam-hyb-b12f-%s-01" % topic, level="L2", ref_calls=2,
        traps=["TR-RULEFILE", "TR-DECOY"], decoys={"TR-RULEFILE": "UNKNOWN", "TR-DECOY": decoy.split(":")[0]},
        axes=["DEC", "CHN", "OBS"], files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": prompt, "expect": expect}])


def hyb_9151():
    return rule_case(
        "hyb-9151", city="承德", aliases=["Chengde"], current="晴 20°C 体感 19°C 湿度 45% 风速 9 km/h",
        rows=[("2026-09-16", "晴", "12~24", "10%"), ("2026-09-17", "阵雨", "8~19", "65%"), ("2026-09-18", "多云", "9~21", "20%")],
        rule_path="营地/收费规定.md",
        rule_lines=["# 营地收费规定", "", "- 帐篷营位基础费：80 元/顶/晚。", "- 当晚所在日最低气温低于 10°C：每顶另收取暖垫费 50 元。",
                    "- 当日降水概率 ≥ 60%：基础费减半（取暖垫费不变）。", "- 其余不额外收费。"],
        topic="chengdecamp", desc="Applies a campsite fee rule (cold surcharge and rain discount) to tomorrow's forecast to compute a total",
        prompt="我们明天晚上在承德的营地订一顶帐篷，按营地的收费规定，总共要付多少钱？",
        alts=["承德营地明天一顶帐篷多少钱，按规定算", "明晚承德营地订一顶帐篷一共多少", "按收费规定，承德营地明天帐篷总价是多少", "承德营地明天晚上一顶帐篷要付多少，算上天气加减费", "How much for one tent at the Chengde campsite tomorrow night under the fee rules?"],
        rule_trap="two clauses fire at once (low 8 < 10 adds 50; rain 65% >= 60% halves the 80 base to 40) and the discount does not touch the surcharge; total 40 + 50 = 90.",
        decoy="80: today's low is 12 and rain 10%, so no clause fires and the fee would be the plain 80; tomorrow is 90.",
        expect_extra={"output_contains": ["90"]}, answer_text="90",
        reply="一共 90 元：承德明天最低气温 8°C，低于 10°C 加收取暖垫费 50 元；降水概率 65%，达到 60%，基础费 80 元减半为 40 元；40 + 50 = 90 元。",
        why="Base 80 halved = 40, plus 50 cold surcharge = 90; no other combination gives 90.",
        check='''low, high = day["temp_c"].split("~")
assert int(low) < 10 and int(day["rain_chance"].rstrip("%")) >= 60
assert 80 // 2 + 50 == 90''')


def hyb_9152():
    return rule_case(
        "hyb-9152", city="合肥", aliases=["Hefei"], current="晴 30°C 体感 33°C 湿度 55% 风速 8 km/h",
        rows=[("2026-09-16", "多云", "24~31", "20%"), ("2026-09-17", "晴", "26~34", "5%"), ("2026-09-18", "阴", "25~30", "35%")],
        rule_path="场地/婚礼规定.md",
        rule_lines=["# 草坪婚礼场地规定", "", "- 当日降水概率 ≥ 30%：改到室内厅。", "- 当日最高气温 ≥ 33°C：改到室内厅。", "- 其余情况在草坪举行。"],
        topic="hefeiwedding", desc="Applies a venue rule with a heat trigger to tomorrow's sunny but hot forecast to decide lawn or indoor hall",
        prompt="按场地规定，合肥明天的婚礼是在草坪办还是改室内？结论请只用「改室内」或「照常」二选一，另一个词不要出现，再用一句话说明依据。",
        alts=["合肥明天草坪婚礼要不要改室内，按场地规定", "明天合肥的婚礼场地，规定怎么说", "按规定合肥明天婚礼改室内吗", "合肥草坪婚礼明天能不能照规定办", "Under the venue rules, does tomorrow's Hefei lawn wedding move indoors?"],
        rule_trap="the second clause is a heat limit (high >= 33°C); tomorrow is sunny with 5% rain, so common sense says the lawn is fine, but the high of 34°C moves it indoors.",
        decoy="照常: today's high is 31 and tomorrow looks dry; only the 34 high trips the rule.",
        expect_extra={"output_contains_any": ["改室内"], "output_excludes": ["照常"]}, answer_text="改室内",
        reply="改室内：合肥明天最高气温 34°C，达到规定的 33°C，婚礼改到室内厅；虽然天晴、降水概率只有 5%。",
        why="High 34 >= 33 triggers the indoor clause; the prompt forbids the other verdict word.",
        check='''assert int(day["temp_c"].split("~")[1]) >= 33 and int(day["rain_chance"].rstrip("%")) < 30''')


def hyb_9153():
    return rule_case(
        "hyb-9153", city="Auckland", aliases=["奥克兰"], current="Cloudy 14°C feels 11°C humidity 70% wind 24 km/h",
        rows=[("2026-09-16", "Cloudy", "12~17", "20%"), ("2026-09-17", "Cloudy", "11~13", "30%"), ("2026-09-18", "Showers", "10~15", "65%")],
        rule_path="club/race-rules.md",
        rule_lines=["# Harbour race rules", "", "- The race is cancelled if the day's chance of rain is 60% or more.",
                    "- The race is cancelled if the day's high is below 14°C.", "- Otherwise the race proceeds."],
        topic="aucklandrace", desc="Applies a sailing club's cold-day cancellation rule to tomorrow's forecast (English)",
        prompt="Per the club's race regulations, does tomorrow's harbour race in Auckland go ahead? Give the verdict as 'cancelled' or 'proceeds', use the other word nowhere, and add one sentence of reasoning.",
        alts=["Under the race regulations, is tomorrow's harbour race in Auckland cancelled?", "Will the club cancel tomorrow's Auckland harbour race?", "Check the race regulations against Auckland's forecast for tomorrow",
              "Is the Auckland harbour race on tomorrow according to the club regulations?", "按俱乐部规则，奥克兰明天的港口帆船赛取消吗？"],
        rule_trap="the rain clause (60%) does not fire; the cold clause (high < 14°C) does: tomorrow's high is 13.",
        decoy="proceeds: tomorrow is only Cloudy with 30% rain, and today's high of 17 would pass; the 13 high cancels it.",
        expect_extra={"output_contains_any": ["cancelled", "Cancelled", "CANCELLED", "canceled", "Canceled"], "output_excludes": ["proceeds", "Proceeds"]},
        answer_text="cancelled",
        reply="Cancelled: tomorrow's high in Auckland is only 13°C, below the 14°C limit in the club rules, even though the rain chance is just 30%.",
        why="High 13 < 14 triggers the cold clause; the prompt forbids the other verdict word.",
        check='''assert int(day["temp_c"].split("~")[1]) < 14 and int(day["rain_chance"].rstrip("%")) < 60''')


def hyb_9154():
    return rule_case(
        "hyb-9154", city="贵阳", aliases=["Guiyang"], current="多云 27°C 体感 29°C 湿度 72% 风速 8 km/h",
        rows=[("2026-09-16", "多云", "21~33", "20%"), ("2026-09-17", "雷阵雨", "20~31", "70%"), ("2026-09-18", "阴", "19~27", "40%")],
        rule_path="乐园/票价规定.md",
        rule_lines=["# 水上乐园票价规定", "", "- 门票基础价：100 元/人。", "- 当日降水概率 ≥ 50%：全场 5 折。",
                    "- 当日最高气温 < 25°C：水上项目关闭，仅按 3 折售票。", "- 其余按基础价。"],
        topic="guiyangwaterpark", desc="Applies a water park pricing rule (rain discount) to tomorrow's forecast to compute a group total",
        prompt="按乐园的票价规定，贵阳明天我们 3 个人去水上乐园，门票一共多少钱？",
        alts=["贵阳水上乐园明天 3 个人门票多少钱，按规定算", "明天贵阳乐园三个人的票价一共多少", "按票价规定，贵阳明天 3 人门票总价", "贵阳水上乐园明天三张票要多少钱", "How much for 3 tickets to the Guiyang water park tomorrow under the pricing rules?"],
        rule_trap="the rain clause (>= 50%) fires for tomorrow's 70%; the cold clause (high < 25°C) does not (high 31); 100 * 0.5 * 3 = 150.",
        decoy="300: today is dry (20%) and would cost the plain 3 x 100; tomorrow is 150.",
        expect_extra={"output_contains": ["150"]}, answer_text="150",
        reply="一共 150 元：贵阳明天有雷阵雨，降水概率 70%，达到 50%，全场 5 折，每人 50 元，3 人 150 元。",
        why="100 x 50% x 3 = 150; the cold clause is not triggered.",
        check='''assert int(day["rain_chance"].rstrip("%")) >= 50 and int(day["temp_c"].split("~")[1]) >= 25
assert 100 * 3 // 2 == 150''')


# ------------------------------------------------------------------ M10b write the forecast

def hyb_9155():
    fx = [weather("乌鲁木齐", "晴 22°C 体感 21°C 湿度 30% 风速 10 km/h",
                  [("2026-09-16", "晴", "11~26", "0%"), ("2026-09-17", "多云", "9~24", "5%"), ("2026-09-18", "晴", "10~25", "0%")], aliases=["Urumqi"])]
    before = '{"city":"克拉玛依","date":"2026-09-14","condition":"晴","low":12,"high":28}\n'
    after = '{"city":"乌鲁木齐","date":"2026-09-17","condition":"多云","low":9,"high":24}\n'
    verify = '''
import json
case = json.load(open("case.json"))
path = "数据/forecast.json"
before = case["files"][path]
assert before.startswith('{"city":"克拉玛依"') and before.endswith(chr(10)) and before.count(chr(10)) == 1
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
text = '{"city":"乌鲁木齐","date":"%s","condition":"%s","low":%s,"high":%s}' % (day["date"], day["condition"], low, high) + chr(10)
print(json.dumps({"files": {path: text}}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-DEFN: the old file is another city and date; the whole file is overwritten with one compact JSON line (keys in the given order, no spaces, low/high bare integers). Tomorrow is the second row, not today's.
Newline policy: exactly one line, ending with one newline; nothing else in the file.

## Reference solution
1. get_weather {"location": "乌鲁木齐", "days": 2}
2. write_file 数据/forecast.json with {"city":"乌鲁木齐","date":"2026-09-17","condition":"多云","low":9,"high":24} plus a trailing newline
3. read_file 数据/forecast.json to confirm
Final answer: 已把乌鲁木齐明天（2026-09-17）的预报（多云，9~24°C）写进 数据/forecast.json，旧内容已覆盖。

## Why the answer is unique
明天 is the second forecast row; the JSON layout is fully specified.
""" + phrasings("把乌鲁木齐明天的预报写成 JSON 放进 数据/forecast.json", "用乌鲁木齐明天预报覆盖 forecast.json，格式见上", "forecast.json 改成乌鲁木齐 9 月 17 日的预报", "乌鲁木齐明天天气写入 JSON 文件，一行就行", "Overwrite forecast.json with Urumqi's forecast for tomorrow as one JSON line.")
    return write_case(
        "hyb-9155", desc="Overwrites a one-line JSON forecast file with tomorrow's forecast in a fully specified compact layout",
        task_type="tool_then_write", family="fam-hyb-b12f-urumqijson-01", level="L1", ref_calls=3,
        traps=["TR-DEFN"], decoys={"TR-DEFN": "晴"}, axes=["OBS"],
        files={"数据/forecast.json": before}, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"数据/forecast.json": {"equals": after}}},
        turns=[{"prompt": "把乌鲁木齐明天的预报写进 数据/forecast.json，整个文件覆盖成下面这一行 JSON（键的顺序、无空格都照抄，最低、最高写成不带单位的整数）："
                          '{"city":"乌鲁木齐","date":"<日期，格式 2026-09-17>","condition":"<天气>","low":<最低>,"high":<最高>}。'
                          "这一行以换行结束，文件里不要有别的内容。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def hyb_9156():
    fx = [weather("太原", "多云 20°C 体感 19°C 湿度 50% 风速 12 km/h",
                  [("2026-09-16", "多云", "12~22", "15%"), ("2026-09-17", "阴", "13~21", "35%"), ("2026-09-18", "小雨", "12~19", "60%")], aliases=["Taiyuan"])]
    before = lines(["date,city,condition,low,high,rain_chance", "2026-09-14,大同,晴,10,22,0%", "2026-09-15,大同,多云,11,23,10%"])
    row = "2026-09-17,太原,阴,13,21,35%"
    verify = '''
import json
case = json.load(open("case.json"))
path = "记录/天气.csv"
before = case["files"][path]
assert before.startswith("date,city,condition,low,high,rain_chance") and before.endswith(chr(10))
assert before.count(chr(10)) == 3
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
low, high = day["temp_c"].split("~")
row = ",".join([day["date"], "太原", day["condition"], low, high, day["rain_chance"]])
print(json.dumps({"files": {path: before + row + chr(10)}}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-DEFN: the CSV column order is fixed by the header; existing rows (another city) must stay untouched; low/high are bare numbers, the rain chance keeps its % sign.
- TR-DECOY: today (多云 12~22 15%) is the first row; the row is for tomorrow.
Newline policy: expected = existing text (ends with one newline) + the new row + exactly one trailing newline.

## Reference solution
1. get_weather {"location": "太原", "days": 2}
2. append_file 记录/天气.csv with "2026-09-17,太原,阴,13,21,35%\\n" (or write_file with the whole text)
3. read_file 记录/天气.csv to confirm
Final answer: 已在 记录/天气.csv 末尾追加太原明天的一行（阴，13~21，降水概率 35%）。

## Why the answer is unique
明天 is the second forecast row; the column order comes from the header.
""" + phrasings("把太原明天的天气追加进天气.csv", "记录/天气.csv 末尾加一行太原 9 月 17 日的预报", "天气表补上太原明天那一行", "太原明天预报按表头格式记到 csv 里", "Append Taiyuan's forecast for tomorrow as a new row of the weather CSV.")
    return write_case(
        "hyb-9156", desc="Appends tomorrow's forecast as a CSV row following the header's column order, leaving existing rows unchanged",
        task_type="tool_then_write", family="fam-hyb-b12f-taiyuancsv-01", level="L2", ref_calls=3,
        traps=["TR-DEFN", "TR-DECOY"], decoys={"TR-DEFN": "UNKNOWN", "TR-DECOY": "多云"}, axes=["OBS"],
        files={"记录/天气.csv": before}, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"记录/天气.csv": {"equals": before + row + "\n"}}},
        turns=[{"prompt": "在 记录/天气.csv 末尾追加太原明天的预报，一行，列顺序跟表头一致（date,city,condition,low,high,rain_chance）；"
                          "日期写 2026-09-17 这种格式，最低、最高写不带单位的整数，降水概率带 % 号，不要改动已有各行。"
                          "每行都以换行结束，追加后文件必须恰好以一个换行结尾。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


def hyb_9157():
    fx = [weather("拉萨", "多云 17°C 体感 16°C 湿度 40% 风速 15 km/h",
                  [("2026-09-16", "多云", "10~20", "30%"), ("2026-09-17", "阵雨", "9~18", "55%"), ("2026-09-18", "晴", "9~21", "5%")], aliases=["Lhasa"])]
    before = "拉萨|2026-09-16|多云|10~20|30%"
    after = "拉萨|2026-09-18|晴|9~21|5%"
    verify = '''
import json
case = json.load(open("case.json"))
path = "状态/天气.txt"
before = case["files"][path]
assert before.startswith("拉萨|2026-09-16") and not before.endswith(chr(10))
day = case["weather_fixture"][0]["report"]["daily"][2]
assert day["date"] == "2026-09-18"
text = "|".join(["拉萨", day["date"], day["condition"], day["temp_c"], day["rain_chance"]])
print(json.dumps({"files": {path: text}}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-DEFN: the status file holds exactly one line and has NO trailing newline, before and after; the line is for the day after tomorrow (2026-09-18, the third row), not tomorrow's 阵雨.
Newline policy: expected file is the bare line "拉萨|2026-09-18|晴|9~21|5%" with no newline at the end.

## Reference solution
1. get_weather {"location": "拉萨", "days": 3}
2. write_file 状态/天气.txt with the single line, no trailing newline
3. read_file 状态/天气.txt to confirm
Final answer: 已把拉萨后天（2026-09-18）的预报（晴，9~21°C，降水概率 5%）写进 状态/天气.txt，文件只有这一行、没有结尾换行。

## Why the answer is unique
后天 is the third forecast row; the single-line format is spelled out and the temperature range keeps the forecast's own form.
""" + phrasings("拉萨后天的天气写进状态文件，只要一行", "状态/天气.txt 改成拉萨 9 月 18 日预报，不带结尾换行", "用拉萨后天预报覆盖天气.txt 那一行", "把拉萨后天天气按竖线格式写到状态文件", "Replace the status line with Lhasa's forecast for the day after tomorrow, no trailing newline.")
    return write_case(
        "hyb-9157", desc="Overwrites a one-line status file with the day-after-tomorrow forecast in a pipe-separated layout and no trailing newline",
        task_type="tool_then_write", family="fam-hyb-b12f-lhasastatus-01", level="L1", ref_calls=3,
        traps=["TR-DEFN"], decoys={"TR-DEFN": "阵雨"}, axes=["OBS"],
        files={"状态/天气.txt": before}, verify=verify, notes=notes, weather_fixture=fx,
        case_expect={"files": {"状态/天气.txt": {"equals": after}}},
        turns=[{"prompt": "状态/天气.txt 里只放一行，格式是「城市|日期|天气|最低~最高|降水概率」（日期写 2026-09-18 这种格式，温度保持「9~21」这种写法不加单位，降水概率带 % 号）。"
                          "请用拉萨后天的预报覆盖它。整个文件的内容就是这一行字符本身，行尾不加换行符。",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "max_output_chars": 600}}])


# ------------------------------------------------------------------ M10e concept negatives

def concept(cid, *, topic, desc, prompt, words, answer, trap_note, alts, limit=800):
    verify = '''
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
assert case["turns"][0]["expect"]["tools"] == [] and case["turns"][0]["expect"]["require_active_no_call"] is True
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % json.dumps(words, ensure_ascii=False)
    notes = f"""## Traps
- TR-NOTOOLNEED: {trap_note}

## Reference solution
No tool call. Final answer: {answer}

## Why the answer is unique
Standard meteorological explanation; no location or date is asked for.
""" + phrasings(*alts)
    return write_case(
        cid, desc=desc, task_type="concept", family="fam-nt-b12f-%s-01" % topic, level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": "查一下今天的天气"}, axes=["DEC"],
        files={}, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": words,
                                              "max_output_chars": limit}}])


def nt_9158():
    return concept(
        "nt-9158", topic="typhoonscale", desc="Weather concept question (typhoon intensity grades) with the weather tool offered; answered without a call",
        prompt="台风是按什么分级的？热带风暴、强台风、超强台风大概差在哪？",
        words=["热带风暴", "强台风", "超强台风"],
        answer="按近中心附近的最大平均风力分级：热带低压 6-7 级、热带风暴 8-9 级、强热带风暴 10-11 级、台风 12-13 级、强台风 14-15 级、超强台风 16 级及以上，级别越高风力越强、破坏越大。",
        trap_note="a classification question answerable from general knowledge; get_weather is offered but no city or date is asked for.",
        alts=["台风怎么分级", "超强台风比强台风强在哪", "热带风暴和台风差几级", "台风按风力分哪几档", "How are typhoons graded by intensity?"])


def nt_9159():
    return concept(
        "nt-9159", topic="weatherclimate", desc="English concept question (weather versus climate) with the weather tool offered; answered without a call",
        prompt="What is the difference between weather and climate? Keep it short.",
        words=["long-term", "long term", "decades", "30 years", "average"],
        answer="Weather is the state of the atmosphere at a particular place and time (hours to days), while climate is the long-term average of that weather over decades.",
        trap_note="a general-knowledge question; get_weather is offered but no location or date is asked for.",
        alts=["Weather vs climate: what's the difference?", "Explain how climate differs from weather.", "Is a cold week a change in climate or weather?", "Why do scientists say weather is not climate?", "天气和气候有什么区别？"])


def nt_9160():
    return concept(
        "nt-9160", topic="coldfront", desc="Weather concept question (cold front passage) with the weather tool offered; answered without a call",
        prompt="冷锋过境的时候，天气一般会怎么变化？",
        words=["降温", "气温下降", "降水", "大风"],
        answer="冷锋过境时冷空气推着暖空气上升，常伴随阴天、降水或雷雨和偏北大风，过后气温明显下降、气压升高，天空转晴。",
        trap_note="a general-knowledge question; get_weather is offered but no city or date is asked for.",
        alts=["冷锋过后会降温吗", "冷空气过境天气有什么变化", "冷锋来了会下雨吗", "什么是冷锋过境，天气怎么变", "What usually happens to the weather when a cold front passes?"])


BUILDERS = [hyb_9141, hyb_9142, hyb_9143, hyb_9144, hyb_9145, hyb_9146, hyb_9147, hyb_9148, hyb_9149, hyb_9150,
            hyb_9151, hyb_9152, hyb_9153, hyb_9154, hyb_9155, hyb_9156, hyb_9157, nt_9158, nt_9159, nt_9160]
SPEC = {
    "hyb-9141": dict(kind="weather", sub="M10c", dates=["2026-09-17"]),
    "hyb-9142": dict(kind="weather", sub="M10c", dates=["2026-09-18"]),
    "hyb-9143": dict(kind="weather", sub="M10c", dates=["2026-09-17"]),
    "hyb-9144": dict(kind="weather", sub="M10c", dates=["2026-09-17"]),
    "hyb-9145": dict(kind="weather", sub="M10c", dates=["2026-09-17"]),
    "hyb-9146": dict(kind="weather", sub="M10c", dates=["2026-09-16"]),
    "hyb-9147": dict(kind="weather_landmark", sub="M10a", landmark="亚龙湾", city=("三亚", "Sanya")),
    "hyb-9148": dict(kind="weather_landmark", sub="M10a", landmark="北戴河", city=("秦皇岛", "Qinhuangdao")),
    "hyb-9149": dict(kind="weather_landmark", sub="M10a", landmark="漓江", city=("桂林", "Guilin")),
    "hyb-9150": dict(kind="weather_landmark", sub="M10a", landmark="外滩", city=("上海", "Shanghai")),
    "hyb-9151": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["营地/收费规定.md"]),
    "hyb-9152": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["场地/婚礼规定.md"]),
    "hyb-9153": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["club/race-rules.md"]),
    "hyb-9154": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["乐园/票价规定.md"]),
    "hyb-9155": dict(kind="weather_write", sub="M10b"),
    "hyb-9156": dict(kind="weather_write", sub="M10b"),
    "hyb-9157": dict(kind="weather_write", sub="M10b"),
    "nt-9158": dict(kind="zero_call", sub="M10e"),
    "nt-9159": dict(kind="zero_call", sub="M10e"),
    "nt-9160": dict(kind="zero_call", sub="M10e"),
}
