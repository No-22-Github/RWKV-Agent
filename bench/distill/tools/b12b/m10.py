"""M10 (b12b): special-purpose tool first -- get_weather over web search.
Fixture clock is 2026-09-16 (Wed): 明天 = 09-17 (Thu), 后天 = 09-18 (Fri).
Builders share the shapes of ../b12a/m10.py (direct lookup, rule file + forecast, concept negative);
ids hyb-9051..9058, nt-9059/9060."""
import json

from common import lines, weather, write_case

REFS = {}
NOWEB = ["web_search", "web_fetch"]


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


DAY = '''
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][%d]
assert day["date"] == %r
'''


def direct(cid, *, city, current, rows, aliases, file, head, idx, date, answer, answer_key, prompt, trap, decoy,
           topic, desc, reply, why, alts, level="L1", axes=("OBS",), contains=None, number=False, tok=True):
    fx = [weather(city, current, rows, aliases=aliases)]
    files = {file[0]: lines(file[1])}
    verify = DAY % (idx, date) + 'assert case["files"][%r].startswith(%r)\n' % (file[0], head)
    if number:
        verify += 'print(json.dumps({"expected_number": int(%s)}))\n' % answer
    else:
        verify += 'print(json.dumps({"expected_string": %s}))\n' % answer
    notes = f"""## Traps
- {trap}: {decoy[1]}

## Reference solution
1. get_weather {{"location": "{city}", "days": 3}}
Final answer: {reply}

## Why the answer is unique
{why}
""" + phrasings(*alts)
    expect = {"required_tools": ["get_weather"], "forbidden_tools": NOWEB,
              "output_contains": contains or [answer_key], "max_output_chars": 600}
    if number and tok:
        expect["output_contains_token"] = True
    return write_case(cid, desc=desc, task_type="special_tool", family="fam-hyb-b12b-%s-01" % topic, level=level,
                      ref_calls=1, traps=[trap], decoys={trap: decoy[0]}, axes=list(axes), files=files, verify=verify,
                      notes=notes, weather_fixture=fx, turns=[{"prompt": prompt, "expect": expect}])


def hyb_9051():
    return direct(
        "hyb-9051", city="成都", aliases=["Chengdu"], current="阴 23°C 体感 24°C 湿度 80% 风速 5 km/h",
        rows=[("2026-09-16", "阴", "20~25", "40%"), ("2026-09-17", "多云", "21~28", "25%"), ("2026-09-18", "晴", "22~31", "10%")],
        file=("出差/成都.md", ["# 成都出差", "", "- 周四上午客户拜访"]), head="# 成都出差", idx=1, date="2026-09-17",
        answer='day["temp_c"].split("~")[1]', answer_key="28", number=True, tok=False, axes=("OBS", "CHN"),
        prompt="我明天要去成都见客户，那天最高气温会到多少度？",
        trap="TR-DECOY", decoy=("25", "today's high is 25; tomorrow (2026-09-17) is 28."),
        topic="chengduhigh", desc="Asks tomorrow's high temperature of a city; get_weather answers it directly",
        reply="成都明天（9 月 17 日）多云，最高气温 28°C、最低 21°C，降水概率 25%。",
        why="The fixed clock makes 明天 = 2026-09-17, the second forecast row.",
        alts=["成都明天最高几度？", "明天成都会不会很热，最高多少", "9 月 17 日成都的最高气温", "明天去成都，最热的时候大概多少度", "What is Chengdu's high tomorrow?"])


def hyb_9052():
    return direct(
        "hyb-9052", city="青岛", aliases=["Qingdao"], current="多云 21°C 体感 20°C 湿度 72% 风速 22 km/h",
        rows=[("2026-09-16", "多云", "18~23", "15%"), ("2026-09-17", "多云", "18~24", "20%"), ("2026-09-18", "中雨", "17~21", "75%")],
        file=("周末/青岛.md", ["# 青岛周末", "", "- 周五傍晚到海边走走"]), head="# 青岛周末", idx=2, date="2026-09-18",
        answer='day["rain_chance"]', answer_key="75%", axes=("OBS", "CHN"),
        prompt="周五傍晚我想去青岛的海边散步，那天天气怎么样，会下雨吗？",
        trap="TR-DECOY", decoy=("20%", "tomorrow is 20%; Friday (2026-09-18) is 75% (中雨)."),
        topic="qingdaofri", desc="Asks the weather on Friday evening (the day after tomorrow) in a coastal city",
        reply="青岛周五（9 月 18 日）有中雨，降水概率 75%，气温 17~21°C，不太适合去海边散步。",
        why="The fixed clock makes Friday = 2026-09-18, the third forecast row.",
        alts=["青岛周五天气如何，适合去海边吗", "周五青岛下雨吗", "9 月 18 日青岛的天气", "青岛后天傍晚能散步吗，有雨吗", "Will it rain in Qingdao on Friday?"])


def hyb_9053():
    return direct(
        "hyb-9053", city="Seoul", aliases=["首尔"], current="Clear 17°C feels 15°C humidity 50% wind 12 km/h",
        rows=[("2026-09-16", "Clear", "11~21", "0%"), ("2026-09-17", "Clear", "9~20", "5%"), ("2026-09-18", "Cloudy", "10~19", "30%")],
        file=("trip/seoul.md", ["# Seoul trip", "", "- Landing Thursday early morning"]), head="# Seoul trip", idx=1, date="2026-09-17",
        answer='day["temp_c"].split("~")[0]', answer_key="9", number=True, level="L1",
        prompt="I land in Seoul early tomorrow morning. How cold will it get, i.e. what is tomorrow's low?",
        trap="TR-DECOY", decoy=("11", "today's low is 11; tomorrow (2026-09-17) is 9."),
        topic="seoullow", desc="Asks in English for tomorrow's low temperature of a city",
        reply="Seoul's low tomorrow (2026-09-17) is 9°C, with a high of 20°C and clear skies; bring a light jacket.",
        why="Tomorrow is the second forecast row.",
        alts=["What's the low in Seoul tomorrow?", "How chilly is Seoul tomorrow morning?", "Seoul minimum temperature on 2026-09-17", "Do I need a jacket in Seoul tomorrow morning? Give me the low.", "首尔明天最低气温是多少？"])


def hyb_9054():
    return direct(
        "hyb-9054", city="杭州", aliases=["Hangzhou"], current="小雨 24°C 体感 26°C 湿度 88% 风速 6 km/h",
        rows=[("2026-09-16", "小雨", "22~26", "70%"), ("2026-09-17", "阴", "22~28", "30%"), ("2026-09-18", "多云", "23~30", "15%")],
        file=("西湖/游览.md", ["# 西湖游览", "", "- 下午三点断桥"]), head="# 西湖游览", idx=0, date="2026-09-16",
        answer='day["condition"]', answer_key="小雨", axes=("OBS", "CHN"),
        prompt="我现在人在杭州，今天天气怎么样？出门要带伞吗？",
        trap="TR-DECOY", decoy=("阴", "tomorrow is 阴 with 30%; today (2026-09-16) is 小雨 with 70%."),
        topic="hangzhoutoday", desc="Asks today's weather of a city and whether to bring an umbrella",
        reply="杭州今天有小雨，降水概率 70%，气温 22~26°C，出门带伞。",
        why="Today is the first forecast row.",
        alts=["杭州今天下雨吗", "今天杭州要带伞吗", "杭州今日天气", "今天在杭州出门，雨大不大", "Is it raining in Hangzhou today?"])


def hyb_9055():
    return direct(
        "hyb-9055", city="重庆", aliases=["Chongqing"], current="晴 33°C 体感 38°C 湿度 60% 风速 4 km/h",
        rows=[("2026-09-16", "晴", "26~36", "5%"), ("2026-09-17", "雷阵雨", "25~32", "65%"), ("2026-09-18", "多云", "24~33", "20%")],
        file=("火锅/聚餐.md", ["# 重庆聚餐", "", "- 明晚七点户外露台"]), head="# 重庆聚餐", idx=1, date="2026-09-17",
        answer='day["rain_chance"]', answer_key="65%", axes=("OBS", "CHN"),
        prompt="明晚我们在重庆的露台上吃火锅，明天会下雨吗，概率多大？",
        trap="TR-DECOY", decoy=("5%", "today is 5%; tomorrow (2026-09-17) is 65% (雷阵雨)."),
        topic="chongqingrain", desc="Asks tomorrow's rain chance in a city for an outdoor dinner",
        reply="重庆明天（9 月 17 日）有雷阵雨，降水概率 65%，气温 25~32°C，露台聚餐风险较大。",
        why="Tomorrow is the second forecast row.",
        alts=["重庆明天会下雨吗", "明天重庆雨大吗，能在露台吃饭吗", "9 月 17 日重庆降水概率", "明晚重庆有雷雨吗", "Will it rain in Chongqing tomorrow?"])


def rule_case(cid, *, city, aliases, current, rows, rule_path, rule_lines, topic, desc, prompt, alts, rule_trap,
              decoy, contains, any_of, answer_idx, reply, why, ref_note):
    fx = [weather(city, current, rows, aliases=aliases)]
    head = rule_lines[0]
    files = {rule_path: lines(rule_lines), rule_path.rsplit("/", 1)[0] + "/说明.md": lines(["# 说明", "", "本目录存放日常规则。"])}
    verify = '''
import json
case = json.load(open("case.json"))
report = case["weather_fixture"][0]["report"]
day = report["daily"][%d]
assert case["files"][%r].startswith(%r)
assert %s
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (answer_idx, rule_path, head, "day[%r]" % ("temp_c" if "temp_c" in contains[1] else "rain_chance"), json.dumps(any_of, ensure_ascii=False))
    notes = f"""## Traps
- TR-RULEFILE: {rule_trap}
- TR-DECOY: {decoy[1]}

## Reference solution
1. list_files / read_file {rule_path}
2. get_weather {{"location": "{city}", "days": 3}}
Final answer: {reply}

## Why the answer is unique
{why}
""" + phrasings(*alts)
    return write_case(
        cid, desc=desc, task_type="special_tool", family="fam-hyb-b12b-%s-01" % topic, level="L2", ref_calls=2,
        traps=["TR-RULEFILE", "TR-DECOY"], decoys={"TR-RULEFILE": decoy[2], "TR-DECOY": decoy[0]}, axes=["DEC", "CHN", "OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": prompt,
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": NOWEB, "output_contains": [contains[0]],
                           "output_contains_any": any_of, "max_output_chars": 600}}])


def hyb_9056():
    return rule_case(
        "hyb-9056", city="济南", aliases=["Jinan"], current="晴 28°C 体感 30°C 湿度 45% 风速 9 km/h",
        rows=[("2026-09-16", "晴", "22~30", "5%"), ("2026-09-17", "晴", "23~31", "10%"), ("2026-09-18", "多云", "22~29", "20%")],
        rule_path="社团/晨跑规则.md",
        rule_lines=["# 晨跑社规则", "", "- 当日最高气温 ≥ 30°C：训练改到早上 6 点至 7 点进行，不得安排在下午。",
                    "- 当日降水概率 ≥ 40%：训练取消。", "- 其余情况按原计划（下午 5 点）训练。"],
        topic="jinanrun", desc="Applies a running club's heat rule to tomorrow's forecast to decide the training time",
        prompt="按社团的晨跑规则，明天济南的训练还能按原计划下午 5 点进行吗？",
        alts=["明天济南晨跑社训练时间要不要改", "按社团规则，明天下午的训练照常吗", "济南明天晨跑社怎么安排", "明天训练按规则改早上还是照旧", "Under our club rules, does tomorrow's training in Jinan stay at 5 pm?"],
        rule_trap="the 30°C heat threshold and the early-morning alternative live in 社团/晨跑规则.md; rain is only 10%, so skipping the file suggests training as planned.",
        decoy=("30", "today's high is 30 (also at the limit); tomorrow's 31 is what counts.", "10%"),
        contains=("31", 'day["temp_c"].split("~")[1]'), any_of=["早上", "早晨", "6 点", "6点"], answer_idx=1,
        reply="不能按原计划：济南明天最高气温 31°C，达到规则的 30°C 上限，训练改到早上 6 点至 7 点；降水概率 10%，不影响。",
        why="Tomorrow's high 31 triggers the heat rule; rain does not trigger.", ref_note="")


def hyb_9057():
    return rule_case(
        "hyb-9057", city="沈阳", aliases=["Shenyang"], current="多云 12°C 体感 10°C 湿度 55% 风速 15 km/h",
        rows=[("2026-09-16", "多云", "8~16", "10%"), ("2026-09-17", "晴", "3~15", "5%"), ("2026-09-18", "晴", "5~18", "5%")],
        rule_path="工地/浇筑规程.md",
        rule_lines=["# 混凝土浇筑规程", "", "- 当日最低气温 < 5°C：暂停浇筑，改期。", "- 当日降水概率 ≥ 30%：暂停浇筑，改期。",
                    "- 其余情况可以浇筑。"],
        topic="shenyangpour", desc="Applies a site's low-temperature rule to tomorrow's forecast to decide whether to pour concrete",
        prompt="按工地的浇筑规程，沈阳明天的混凝土浇筑能安排吗？",
        alts=["沈阳工地明天能浇筑吗", "明天沈阳浇筑按规程行不行", "沈阳明天要不要暂停浇筑", "明天浇混凝土，规程允许吗", "Under the site rules, can we pour concrete in Shenyang tomorrow?"],
        rule_trap="the pour threshold is the daily low (< 5°C), not rain; tomorrow is sunny with 5% rain, so common sense says go ahead.",
        decoy=("16", "today's high is 16; the rule looks at the low, and tomorrow's low is 3.", "5%"),
        contains=("3°C", 'day["temp_c"].split("~")[0]'), any_of=["暂停", "改期", "不能"], answer_idx=1,
        reply="不能安排：沈阳明天最低气温 3°C，低于规程的 5°C，暂停浇筑、改期；天晴、降水概率只有 5%，不是下雨的问题。",
        why="The low of 3°C is below 5°C; the rule is explicit.", ref_note="")


def hyb_9058():
    return rule_case(
        "hyb-9058", city="南昌", aliases=["Nanchang"], current="多云 27°C 体感 30°C 湿度 70% 风速 8 km/h",
        rows=[("2026-09-16", "多云", "24~30", "20%"), ("2026-09-17", "阵雨", "23~29", "45%"), ("2026-09-18", "多云", "24~31", "25%")],
        rule_path="园务/春秋游规定.md",
        rule_lines=["# 幼儿园春秋游规定", "", "- 出行当天降水概率 ≥ 30%：取消，改期。", "- 出行当天最高气温 ≥ 35°C：改为室内活动。",
                    "- 其余情况按计划出行。"],
        topic="nanchangtrip", desc="Applies a kindergarten outing rule to tomorrow's forecast to decide whether the trip goes ahead",
        prompt="按园里的春秋游规定，南昌明天带小朋友去公园的活动还能去吗？",
        alts=["明天南昌春游按规定能去吗", "幼儿园明天去公园，规定允许吗", "南昌明天春秋游要取消吗", "按园务规定，明天出行还是改期", "Under the kindergarten rules, is tomorrow's park trip in Nanchang still on?"],
        rule_trap="the cancel threshold is a rain chance >= 30%; the high of 29°C is fine, so 阵雨 alone does not reveal the 45% figure that decides it.",
        decoy=("20%", "today's rain chance is 20%; tomorrow's 45% crosses the 30% limit.", "29"),
        contains=("45", 'day["rain_chance"].rstrip("%")'), any_of=["取消", "改期", "不能"], answer_idx=1,
        reply="不能去：南昌明天有阵雨，降水概率 45%，达到规定的 30%，春秋游取消、改期；最高气温 29°C 不是问题。",
        why="45% >= 30% triggers the cancel rule.", ref_note="")


def concept(cid, *, topic, desc, prompt, words, answer, trap_note, alts):
    verify = '''
import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"]
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
        cid, desc=desc, task_type="concept", family="fam-nt-b12b-%s-01" % topic, level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": "查一下今天的天气"}, axes=["DEC"],
        files={}, verify=verify, notes=notes,
        turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": words,
                                              "max_output_chars": 600}}])


def nt_9059():
    return concept(
        "nt-9059", topic="rainchance", desc="Weather concept question (what a rain probability means) with the weather tool offered; answered without a call",
        prompt="天气预报里说「降水概率 30%」，到底是什么意思？是会下 30% 的时间吗？",
        words=["概率", "可能性"], answer="降水概率是预报区域内某一时段出现降水的可能性，30% 表示这类天气形势下约有三成的可能出现降水，不是下雨时间占 30%，也不是雨量。",
        trap_note="a definition question; get_weather is offered but no city or date is asked for.",
        alts=["降水概率 30% 是下雨的时间占比吗", "预报说降水概率三成，什么意思", "降水概率和雨量有关系吗", "30% 的降水概率要带伞吗，这数字怎么理解", "What does a 30% chance of rain mean?"])


def nt_9060():
    return concept(
        "nt-9060", topic="seabreeze", desc="Weather concept question (why coastal cities have small day-night swings) with the weather tool offered; answered without a call",
        prompt="为什么沿海城市的昼夜温差通常比内陆小？",
        words=["比热", "海水", "水的"], answer="海水比热容大，吸热和放热都慢，白天升温慢、夜里降温也慢，所以沿海昼夜温差小；内陆地表比热小，温度起落更大。",
        trap_note="a general-knowledge question; get_weather is offered but no location or date is asked for.",
        alts=["沿海为什么昼夜温差小", "海边城市早晚温差为什么没那么大", "内陆昼夜温差大是什么原因", "为什么靠海的地方冷热变化慢", "Why do coastal cities have smaller day-night temperature swings?"])


BUILDERS = [hyb_9051, hyb_9052, hyb_9053, hyb_9054, hyb_9055, hyb_9056, hyb_9057, hyb_9058, nt_9059, nt_9060]
SPEC = {
    "hyb-9051": dict(kind="weather", sub="M10a", dates=["2026-09-17"]),
    "hyb-9052": dict(kind="weather", sub="M10a", dates=["2026-09-18"]),
    "hyb-9053": dict(kind="weather", sub="M10a", dates=["2026-09-17"]),
    "hyb-9054": dict(kind="weather", sub="M10a", dates=["2026-09-16"]),
    "hyb-9055": dict(kind="weather", sub="M10a", dates=["2026-09-17"]),
    "hyb-9056": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["社团/晨跑规则.md"]),
    "hyb-9057": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["工地/浇筑规程.md"]),
    "hyb-9058": dict(kind="weather", sub="M10d", dates=["2026-09-17"], needs=["园务/春秋游规定.md"]),
    "nt-9059": dict(kind="zero_call", sub="M10e"),
    "nt-9060": dict(kind="zero_call", sub="M10e"),
}
