"""b14 M10: get_weather done right, ids 10201-10300. Fixture clock 2026-09-16 (Wed):
今天 09-16 周三, 明天 09-17 周四, 后天 09-18 周五, 周六 09-19, 周日 09-20, 周一 09-21, 周二 09-22.

  M10a direct     10201-10218  明天/后天/weekday labels, landmark -> city; 4 two-turn (turn 2 needs days >= 5)
  M10d implicit   10219-10232  umbrella / clothes / laundry / outdoor plans, 5 with a local rule file; 2 two-turn
  M10b write      10233-10254  append to an existing file copying its format exactly, read back, no duplicates; 8 two-turn
  M10f switch     10255-10266  two turns, turn 2 asks about another city (a fresh lookup)
  M10g unknown    10267-10275  a place the fixture does not know: say so, invent nothing
  M10c composite  10276-10285  weather from get_weather plus one web fact from web search
  M10e concept    10286-10300  definition questions: zero calls; 5 two-turn (turn 2 asks a real forecast)

Non-composite positives require get_weather and forbid web_search/web_fetch. Prompts never name a tool.
Chinese temperatures are matched as substrings (a token rule rejects 「28度」, b12 lesson).
"""
import json
from random import Random

from common import NOWEB, case, lines, phrasings, verify_src, weather

BUILDERS = []
DATES = ["2026-09-%02d" % d for d in range(16, 23)]
WD_ZH = ["周三", "周四", "周五", "周六", "周日", "周一", "周二"]
WD_EN = ["Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue"]
COND_ZH = [("晴", 5), ("多云", 15), ("阴", 30), ("小雨", 60), ("阵雨", 55), ("雷阵雨", 70), ("中雨", 80), ("大雨", 90)]
COND_EN = [("Sunny", 5), ("Partly cloudy", 15), ("Overcast", 30), ("Light rain", 60), ("Showers", 55), ("Thunderstorms", 70), ("Drizzle", 50), ("Heavy rain", 90)]


def reg(fn):
    BUILDERS.append(fn)
    return fn


def make_fx(city, seed, *, en=False, base=(18, 27), aliases=(), set_days=None):
    """A 7-day fixture. set_days maps day index -> (cond, low, high, rain) overrides."""
    rng = Random(seed)
    table = COND_EN if en else COND_ZH
    days = []
    for i, d in enumerate(DATES):
        cond, rain = rng.choice(table)
        rain = max(0, min(95, rain + rng.choice([-10, -5, 0, 5, 10])))
        low = base[0] + rng.randint(-3, 3)
        high = max(low + 4, base[1] + rng.randint(-3, 3))
        if set_days and i in set_days:
            cond, low, high, rain = set_days[i]
        days.append((d, cond, "%d~%d" % (low, high), "%d%%" % rain))
    c0 = days[0]
    lo, hi = c0[2].split("~")
    now = (int(lo) + int(hi)) // 2
    current = ("%s %d°C feels %d°C humidity %d%% wind %d km/h" if en else "%s %d°C 体感 %d°C 湿度 %d%% 风速 %d km/h") % (
        c0[1], now, now + rng.randint(-1, 3), rng.randint(40, 90), rng.randint(3, 25))
    return weather(city, current, days, aliases=list(aliases))


def day(fx, i):
    d = fx["report"]["daily"][i]
    low, high = d["temp_c"].split("~")
    return {"date": d["date"], "cond": d["condition"], "low": low, "high": high, "rain": d["rain_chance"]}


FACT_SRC = '''
def fact(case, city, i, field):
    for e in case["weather_fixture"]:
        if e["location"] == city:
            d = e["report"]["daily"][i]
            assert d["date"] == "2026-09-%02d" % (16 + i), d
            low, high = d["temp_c"].split("~")
            return {"cond": d["condition"], "low": low, "high": high, "rain": d["rain_chance"]}[field]
    raise KeyError(city)
'''


def fact_verify(files, facts, extra=""):
    """verify.py printing the last turn's fact; facts: (city, day index, field)."""
    city, i, field = facts[-1]
    body = FACT_SRC + extra + "\nv = fact(case, %r, %d, %r)\n" % (city, i, field)
    if field in ("low", "high"):
        body += 'print(json.dumps({"expected_number": int(v)}))\n'
    else:
        body += 'print(json.dumps({"expected_string": v}, ensure_ascii=False))\n'
    if not files:
        body = 'import json\ncase = json.load(open("case.json"))\n' + body
        return body
    return verify_src(files, body)


def wexpect(value, field, en, *, extra=None, forbid_web=True, required=("get_weather",)):
    e = {"required_tools": list(required), "max_output_chars": 700} if required else {"max_output_chars": 700}
    if forbid_web:
        e["forbidden_tools"] = list(NOWEB)
    if en and field == "cond" and value[:1].isupper():
        value = value[1:]  # output_contains is case-sensitive; "hunderstorms" matches Thunderstorms and thunderstorms mid-sentence
    e["output_contains"] = [value]
    if field in ("low", "high") and en:
        e["output_contains_token"] = True
    if extra:
        e.update(extra)
    return e


def weather_case(cid, *, sub, fxs, turns, facts, desc, family, notes_traps, reply, alts, files=None, spec=None, traps=(), decoys=None,
                 ref_calls=None, task_type="special_tool", axes=("OBS",), extra_verify="", reuse_later_turns=False):
    """turns: prompts; facts: per-turn (city, day index, field) the answer must contain."""
    files = files or {}
    tl = []
    for k, (p, (city, i, field)) in enumerate(zip(turns, facts)):
        fx = [f for f in fxs if f["location"] == city][0]
        en = fx["location"].isascii()
        # a later turn about the same city may answer from the earlier report when it already covers the day
        required = () if reuse_later_turns and k else ("get_weather",)
        tl.append({"prompt": p, "expect": wexpect(day(fx, i)[field], field, en, required=required)})
    ref = "\n".join("%s. get_weather {\"location\": \"%s\", \"days\": %d}%s" % (
        "Turn %d:" % (k + 1) if len(turns) > 1 else "1", c, max(3, i + 1), " -> %s" % day([f for f in fxs if f["location"] == c][0], i)[fd])
        for k, (c, i, fd) in enumerate(facts))
    notes = "## Traps\n" + "".join("- %s\n" % t for t in notes_traps) + "\n## Reference solution\n" + ref + "\nFinal answer: %s\n" % reply
    notes += "\n## Why the answer is unique\nThe fixed clock (2026-09-16 Wed) maps the day words to one forecast row; the fixture holds one report per city.\n"
    notes += phrasings(*alts)
    days_needed = sorted({DATES[i] for _, i, _ in facts})
    return case(cid, sub=sub, spec=spec or {"kind": "weather", "dates": days_needed}, desc=desc, task_type=task_type, family=family,
                ref_calls=ref_calls if ref_calls is not None else len(turns), files=files, turns=tl, verify=fact_verify(files, facts, extra_verify),
                notes=notes, weather_fixture=fxs, traps=traps, decoys=decoys or {t: None for t in traps}, axes=axes)


# ------------------------------------------------------------------ M10a direct (10201-10218)

DIRECT = [
    # cid, city, en, aliases, prompt(s), facts, decoy note, reply, alts, overrides
    ("hyb-10201", "南京", False, ["Nanjing"], ["后天南京白天最高能到几度？我周五在那边跑外勤。"], [("南京", 2, "high")],
     "today/tomorrow highs differ; 后天 is 2026-09-18 (周五)", "南京后天（9 月 18 日周五）最高 {v}°C。",
     ["南京周五最高温", "后天南京热不热", "9 月 18 日南京最高气温", "南京后天白天温度", "周五去南京，最高几度"], None),
    ("hyb-10202", "武汉", False, ["Wuhan"], ["明天武汉的天气状况是什么？晴还是下雨？"], [("武汉", 1, "cond")],
     "today's condition differs from tomorrow's", "武汉明天（9 月 17 日）{v}。", ["武汉明天天气", "明天武汉下雨吗", "武汉 9 月 17 日天气", "武汉明天晴不晴", "明天去武汉天气如何"],
     {0: ("晴", 22, 31, 5), 1: ("雷阵雨", 23, 29, 70)}),
    ("hyb-10203", "Lisbon", True, ["里斯本"], ["Friday night in Lisbon: how low will the temperature drop?"], [("Lisbon", 2, "low")],
     "tomorrow's low is a different number", "Lisbon's low on Friday 18 September is {v}°C.",
     ["Lisbon low on Friday", "How cold will Lisbon get the day after tomorrow?", "Overnight low in Lisbon on the 18th", "Lisbon minimum temperature in two days", "Friday night temperature in Lisbon"],
     {1: ("Sunny", 17, 26, 5), 2: ("Showers", 14, 21, 55)}),
    ("hyb-10204", "昆明", False, ["Kunming"], ["周六去昆明滇池边骑车，那天降水概率大概多少？"], [("昆明", 3, "rain")],
     "周六 is 2026-09-19 (day 4), beyond a 3-day lookup", "昆明周六（9 月 19 日）降水概率 {v}。",
     ["昆明周六会下雨吗", "周六昆明降水概率", "9 月 19 日昆明天气", "这周六昆明天气怎么样", "周六在昆明骑车要带雨衣吗"], {3: ("阵雨", 15, 22, 55)}),
    ("hyb-10205", "Osaka", True, ["大阪"], ["Is it going to rain in Osaka on Sunday? Give me the chance of rain."], [("Osaka", 4, "rain")],
     "Sunday is the 5th row (2026-09-20); a 3-day lookup stops at Friday", "Osaka on Sunday 20 September: {v} chance of rain.",
     ["Rain chance in Osaka this Sunday", "Will Sunday be wet in Osaka?", "Osaka weather for the 20th", "Should I expect rain in Osaka on Sunday?", "Sunday forecast for Osaka"],
     {4: ("Thunderstorms", 22, 28, 75)}),
    ("hyb-10206", "长沙", False, ["Changsha"], ["长沙今天最高多少度？"], [("长沙", 0, "high")],
     "tomorrow's high differs", "长沙今天最高 {v}°C。", ["长沙今天热吗", "今天长沙最高气温", "长沙今天白天多少度", "长沙 9 月 16 日最高温", "今天长沙会到几度"],
     {0: ("多云", 24, 33, 15), 1: ("阵雨", 23, 28, 55)}),
    ("hyb-10207", "Vancouver", True, ["温哥华"], ["How warm does it get in Vancouver tomorrow afternoon?"], [("Vancouver", 1, "high")],
     "today is warmer/cooler", "Vancouver's high tomorrow (Thu 17 Sep) is {v}°C.",
     ["Tomorrow's high in Vancouver", "Vancouver temperature tomorrow", "Max temp in Vancouver on Thursday", "How hot in Vancouver tomorrow?", "Vancouver forecast high, 17 Sep"],
     {0: ("Overcast", 12, 19, 30), 1: ("Sunny", 11, 22, 5)}),
    ("hyb-10208", "福州", False, ["Fuzhou"], ["福州后天什么天气？我要决定是不是改签。"], [("福州", 2, "cond")],
     "明天的天气不同", "福州后天（9 月 18 日）{v}。", ["福州后天下雨吗", "9 月 18 日福州天气", "后天福州天气怎么样", "福州周五天气", "后天去福州，天气如何"],
     {1: ("多云", 25, 32, 15), 2: ("大雨", 24, 28, 90)}),
    ("hyb-10209", "合肥", False, ["Hefei"], ["下周一合肥最低温多少？"], [("合肥", 5, "low")],
     "下周一 is 2026-09-21 (row 6); days must be >= 6", "合肥下周一（9 月 21 日）最低 {v}°C。",
     ["合肥周一最低气温", "9 月 21 日合肥最低温", "下周一合肥冷不冷", "合肥下周一早上多少度", "下周一合肥气温"], {5: ("阴", 14, 22, 30)}),
    ("hyb-10210", "Prague", True, ["布拉格"], ["Will it be dry in Prague on Saturday? What's the forecast condition?"], [("Prague", 3, "cond")],
     "Friday's condition differs", "Prague on Saturday 19 September: {v}.",
     ["Prague weather Saturday", "Is Saturday in Prague rainy?", "Prague forecast for the 19th", "What's Prague like this Saturday?", "Saturday conditions in Prague"],
     {2: ("Sunny", 9, 19, 5), 3: ("Drizzle", 10, 15, 50)}),
    # landmarks -> city
    ("hyb-10211", "杭州", False, ["Hangzhou"], ["明天想去西湖边走走，会下雨吗？说下降水概率。"], [("杭州", 1, "rain")],
     "西湖 is a lake in 杭州, not a city: the lookup is 杭州", "西湖在杭州，杭州明天降水概率 {v}。",
     ["西湖明天下雨吗", "明天游西湖要带伞吗", "杭州明天降水概率", "明天西湖天气", "去西湖散步，明天天气怎样"], {1: ("小雨", 19, 25, 65)}),
    ("hyb-10212", "北京", False, ["Beijing"], ["后天去故宫，那天最高气温多少？"], [("北京", 2, "high")],
     "故宫 is in 北京; look up the city", "故宫在北京，北京后天最高 {v}°C。",
     ["后天故宫热不热", "北京后天最高气温", "9 月 18 日故宫天气", "去故宫那天多少度", "后天北京天气"], {2: ("晴", 17, 28, 5)}),
    ("hyb-10213", "拉萨", False, ["Lhasa"], ["明天去布达拉宫，早上冷不冷？最低几度？"], [("拉萨", 1, "low")],
     "布达拉宫 is in 拉萨", "布达拉宫在拉萨，拉萨明天最低 {v}°C。",
     ["布达拉宫明天最低温", "拉萨明天早上多少度", "明天拉萨冷吗", "去布达拉宫要穿厚点吗", "拉萨 9 月 17 日最低气温"], {1: ("晴", 7, 21, 5)}),
    ("hyb-10214", "重庆", False, ["Chongqing"], ["晚上打算去洪崖洞拍夜景，今天那边降水概率多少？"], [("重庆", 0, "rain")],
     "洪崖洞 is in 重庆", "洪崖洞在重庆，重庆今天降水概率 {v}。",
     ["洪崖洞今天下雨吗", "重庆今天会下雨吗", "今晚去洪崖洞要带伞吗", "重庆今天降水概率", "洪崖洞夜景今天天气"], {0: ("雷阵雨", 25, 33, 70)}),
    ("hyb-10215", "San Francisco", True, ["旧金山", "SF"], ["I'm biking across the Golden Gate Bridge tomorrow. What's the forecast high?"], [("San Francisco", 1, "high")],
     "the bridge is in San Francisco", "Golden Gate Bridge is in San Francisco; tomorrow's high there is {v}°C.",
     ["Golden Gate Bridge weather tomorrow", "San Francisco high tomorrow", "How warm on the bridge tomorrow?", "Biking the Golden Gate tomorrow: temperature?", "SF forecast for Thursday"],
     {1: ("Partly cloudy", 13, 21, 15)}),
    ("hyb-10216", "武汉", False, ["Wuhan"], ["周六带爸妈去黄鹤楼，那天天气怎么样？"], [("武汉", 3, "cond")],
     "黄鹤楼 is in 武汉; 周六 is row 4", "黄鹤楼在武汉，武汉周六（9 月 19 日）{v}。",
     ["周六黄鹤楼天气", "武汉周六天气", "9 月 19 日黄鹤楼会下雨吗", "周六去黄鹤楼天气如何", "这周六武汉什么天"], {3: ("多云", 22, 30, 15)}),
]
DIRECT_2T = [
    ("hyb-10217", "大连", False, ["Dalian"], ["大连明天最高几度？", "那周日呢？我周日下午到。"], [("大连", 1, "high"), ("大连", 4, "high")],
     "turn 2: 周日 is 2026-09-20 (row 5); a 3-day lookup from turn 1 does not cover it", "大连周日（9 月 20 日）最高 {v}°C。",
     ["大连周日最高温", "周日大连多少度", "大连 9 月 20 日气温", "周日下午到大连热吗", "大连这个周日天气"], {1: ("晴", 18, 26, 5), 4: ("阴", 17, 22, 30)}),
    ("hyb-10218", "Melbourne", True, ["墨尔本"], ["Chance of rain in Melbourne tomorrow?", "And on Monday?"], [("Melbourne", 1, "rain"), ("Melbourne", 5, "rain")],
     "turn 2: Monday is 2026-09-21 (row 6); a 3-day lookup does not reach it", "Melbourne on Monday 21 September: {v} chance of rain.",
     ["Melbourne rain Monday", "Will it rain in Melbourne on the 21st?", "Monday forecast Melbourne", "Melbourne next Monday weather", "Is Monday wet in Melbourne?"],
     {1: ("Overcast", 9, 16, 35), 5: ("Showers", 8, 14, 60)}),
]


def _direct(entry, seed):
    cid, city, en, aliases, prompts, facts, trap, reply, alts, overrides = entry

    def build():
        fx = make_fx(city, seed, en=en, aliases=aliases, set_days=overrides, base=(14, 23) if en else (19, 28))
        landmark = cid in ("hyb-10211", "hyb-10212", "hyb-10213", "hyb-10214", "hyb-10215", "hyb-10216")
        last = facts[-1]
        v = day(fx, last[1])[last[2]]
        spec = {"kind": "weather_landmark", "city": [city] + aliases} if landmark else {"kind": "weather", "dates": sorted({DATES[i] for _, i, _ in facts})}
        if landmark:
            spec["dates"] = [DATES[last[1]]]
        traps = ["TR-NEARNAME"] if landmark else ["TR-DECOY"]
        other = day(fx, (last[1] + 1) % 7 if last[1] != 1 else 0)[last[2]]
        return weather_case(cid, sub="M10a", fxs=[fx], turns=prompts, facts=facts, desc=("Two turns: " if len(prompts) > 1 else "") +
                            ("Asks about a landmark's weather; the forecast must be looked up by its city" if landmark else "Asks a dated forecast value; the day word must map to the right row"),
                            family="fam-hyb-b14-direct-%s" % cid.split("-")[1], notes_traps=["%s: %s." % (traps[0], trap)],
                            reply=reply.format(v=v), alts=alts, spec=spec, traps=traps, decoys={traps[0]: "UNKNOWN" if landmark else other})
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(DIRECT + DIRECT_2T):
    BUILDERS.append(_direct(_e, 10201 + _i))


# ------------------------------------------------------------------ M10d implicit needs (10219-10232)

IMPLICIT = [
    # cid, city, en, prompt(s), facts, overrides, files, reply, alts, trap
    ("hyb-10219", "郑州", False, ["明天要在郑州户外办签售会，需要准备雨棚吗？"], [("郑州", 1, "rain")], {1: ("中雨", 18, 24, 80)}, None,
     "建议准备：郑州明天中雨，降水概率 {v}。", ["明天郑州户外活动要不要雨棚", "郑州明天会下雨吗", "明天郑州签售会天气", "明天郑州适合户外吗", "郑州明天降水概率"], "the question never says weather; it hinges on tomorrow's rain"),
    ("hyb-10220", "哈尔滨", False, ["后天一早飞哈尔滨，要带厚外套吗？"], [("哈尔滨", 2, "low")], {2: ("晴", 6, 17, 5)}, None,
     "要带：哈尔滨后天最低只有 {v}°C，早晚很凉。", ["后天哈尔滨冷吗", "去哈尔滨穿什么", "哈尔滨后天最低温", "后天哈尔滨要穿外套吗", "哈尔滨 9 月 18 日早上几度"], "clothing depends on 后天's low"),
    ("hyb-10221", "Dublin", True, ["I want to hang the washing outside in Dublin tomorrow. Good idea?"], [("Dublin", 1, "rain")], {1: ("Showers", 9, 15, 65)}, None,
     "Not really: Dublin has showers tomorrow with a {v} chance of rain; dry it indoors.", ["Can I dry laundry outside in Dublin tomorrow?", "Dublin rain tomorrow?", "Washing line weather Dublin", "Will tomorrow be dry in Dublin?", "Dublin forecast for laundry"], "laundry hinges on tomorrow's rain"),
    ("hyb-10222", "太原", False, ["这周六想带孩子去太原汾河公园野餐，天气行不行？"], [("太原", 3, "cond")], {3: ("晴", 12, 25, 5)}, None,
     "行：太原周六{v}，适合野餐。", ["周六太原适合野餐吗", "太原周六天气", "汾河公园周六会下雨吗", "周六带孩子出去玩，太原天气如何", "9 月 19 日太原天气"], "周六 is row 4; the answer needs that row's condition"),
    ("hyb-10223", "Toronto", True, ["Should I bring a jacket for an evening run in Toronto tonight?"], [("Toronto", 0, "low")], {0: ("Partly cloudy", 8, 18, 15)}, None,
     "Yes: Toronto drops to about {v}°C tonight, so a light jacket helps.", ["Jacket needed in Toronto tonight?", "How cold is Toronto tonight?", "Evening run weather Toronto", "Toronto low today", "Is it chilly in Toronto this evening?"], "the answer rests on today's low"),
    ("hyb-10224", "厦门", False, ["明天要坐轮渡出海拍照，天气会不会有影响？"], [("厦门", 1, "cond")], {1: ("雷阵雨", 25, 30, 75)}, {"拍摄/计划.md": ["# 拍摄计划", "", "9 月 17 日 厦门 出海拍照"]},
     "有影响：厦门明天{v}，出海拍照建议改期。", ["明天厦门出海天气", "厦门明天会有雷雨吗", "明天出海拍照合适吗", "厦门明天天气", "9 月 17 日厦门出海"], "the city is only in the plan file"),
    ("hyb-10225", "济南", False, ["周日在济南有一场马拉松，参赛的话要注意什么天气情况？"], [("济南", 4, "high")], {4: ("晴", 20, 32, 5)}, None,
     "济南周日晴，最高 {v}°C，注意防晒补水。", ["周日济南马拉松天气", "济南周日热不热", "9 月 20 日济南最高温", "周日济南跑步天气", "济南这周日天气怎样"], "周日 is row 5; heat matters for a marathon"),
    # local rule files
    ("hyb-10226", "成都", False, ["按我们的规定，明天成都的户外团建能照常办吗？"], [("成都", 1, "rain")], {1: ("阵雨", 18, 24, 55)},
     {"行政/团建规定.md": ["# 户外团建规定", "", "- 当天降水概率达到 50% 及以上，改为室内活动。", "- 最高气温超过 35°C 也改室内。"]},
     "不能照常：成都明天阵雨，降水概率 {v}，达到规定的 50%，改室内。", ["明天成都团建要改室内吗", "按规定明天成都还能户外吗", "成都明天降水概率", "团建规定和明天天气", "明天成都户外活动行不行"], "TR-RULEFILE: the threshold is in 行政/团建规定.md"),
    ("hyb-10227", "Barcelona", True, ["Going by our venue guidelines, can tomorrow's rooftop dinner in Barcelona go ahead outdoors?"], [("Barcelona", 1, "rain")], {1: ("Partly cloudy", 19, 26, 20)},
     {"events/venue-rules.md": ["# Rooftop rules", "", "- Move indoors if the day's rain chance is 40% or higher.", "- Move indoors if wind exceeds 40 km/h."]},
     "Yes: Barcelona tomorrow is partly cloudy with a {v} chance of rain, under the 40% limit.", ["Rooftop dinner Barcelona tomorrow OK?", "Barcelona rain chance tomorrow", "Check tomorrow against the venue rules", "Can we eat outside in Barcelona tomorrow?", "Venue rule check for Thursday"], "TR-RULEFILE: the threshold is in events/venue-rules.md"),
    ("hyb-10228", "南宁", False, ["后天南宁工地能不能浇筑？按施工规定判断。"], [("南宁", 2, "rain")], {2: ("小雨", 23, 29, 60)},
     {"工地/施工规定.md": ["# 浇筑条件", "", "- 当天降水概率 ≥ 50% 不得浇筑。", "- 最低气温低于 5°C 不得浇筑。"]},
     "不能：南宁后天小雨，降水概率 {v}，超过 50% 的限制。", ["后天南宁能浇混凝土吗", "按规定后天能施工吗", "南宁后天降水概率", "后天浇筑条件满足吗", "南宁 9 月 18 日能浇筑吗"], "TR-RULEFILE: the threshold is in 工地/施工规定.md"),
    ("hyb-10229", "贵阳", False, ["按学校的规定，明天贵阳的运动会还要穿长袖校服吗？"], [("贵阳", 1, "low")], {1: ("多云", 13, 22, 15)},
     {"学校/着装规定.md": ["# 运动会着装", "", "- 当天最低气温低于 15°C，穿长袖校服。", "- 否则穿短袖。"]},
     "要穿长袖：贵阳明天最低 {v}°C，低于 15°C。", ["明天贵阳运动会穿什么", "贵阳明天最低温", "按规定明天穿长袖吗", "运动会着装和明天天气", "贵阳 9 月 17 日早上冷吗"], "TR-RULEFILE: the threshold is in 学校/着装规定.md"),
    ("hyb-10230", "Auckland", True, ["Our sailing club regulations decide whether Saturday's race in Auckland runs. Does it?"], [("Auckland", 3, "cond")], {3: ("Thunderstorms", 11, 16, 75)},
     {"club/race-rules.md": ["# Race rules", "", "- Cancel if thunderstorms are forecast for race day.", "- Otherwise the race runs."]},
     "It's cancelled: Auckland's Saturday forecast is {v}, which the rules rule out.", ["Is Saturday's Auckland race on?", "Auckland weather Saturday", "Sailing rules vs Saturday forecast", "Will the race run in Auckland?", "Thunderstorms in Auckland on the 19th?"], "TR-RULEFILE: the rule is in club/race-rules.md"),
]
IMPLICIT_2T = [
    ("hyb-10231", "西宁", False, ["明天去西宁，衣服带薄的还是厚的？", "那后天去青海湖那边呢？还按西宁看。"], [("西宁", 1, "low"), ("西宁", 2, "low")], {1: ("晴", 9, 21, 5), 2: ("多云", 5, 16, 15)}, None,
     "后天更冷，西宁最低 {v}°C，要带厚外套。", ["西宁后天最低温", "后天去青海湖冷吗", "西宁 9 月 18 日早上多少度", "后天西宁要穿厚的吗", "青海湖后天穿什么"], "turn 2 is a different day; the earlier answer does not carry over"),
    ("hyb-10232", "Singapore", True, ["Do I need an umbrella in Singapore today?", "What about tomorrow?"], [("Singapore", 0, "rain"), ("Singapore", 1, "rain")], {0: ("Thunderstorms", 26, 32, 70), 1: ("Partly cloudy", 26, 33, 20)}, None,
     "Tomorrow looks drier: {v} chance of rain in Singapore.", ["Singapore rain tomorrow?", "Umbrella for Singapore tomorrow?", "Singapore forecast Thursday", "Will it pour in Singapore tomorrow?", "Singapore rain chance on the 17th"], "turn 2 is another day; reuse the report only if it covers it"),
]


def _implicit(entry, seed):
    cid, city, en, prompts, facts, overrides, tree, reply, alts, trap = entry

    def build():
        fx = make_fx(city, seed, en=en, set_days=overrides, base=(14, 23) if en else (19, 28))
        files = {p: lines(v) for p, v in (tree or {}).items()}
        rule = trap.startswith("TR-RULEFILE")
        last = facts[-1]
        v = day(fx, last[1])[last[2]]
        spec = {"kind": "weather", "dates": sorted({DATES[i] for _, i, _ in facts})}
        if rule:
            spec["needs"] = list(files)
        traps = ["TR-RULEFILE"] if rule else ["TR-DECOY"]
        decoy = day(fx, 0 if last[1] else 1)[last[2]]
        return weather_case(cid, sub="M10d", fxs=[fx], turns=prompts, facts=facts, files=files,
                            desc=("Two turns: " if len(prompts) > 1 else "") + ("Applies a local rule file to a forecast" if rule else "Implicit weather need: the decision rests on one forecast value"),
                            family="fam-hyb-b14-implicit-%s" % cid.split("-")[1], notes_traps=[trap], reply=reply.format(v=v), alts=alts, spec=spec,
                            traps=traps, decoys={traps[0]: decoy}, axes=("DEC", "OBS"), ref_calls=len(prompts) + (1 if rule else 0),
                            reuse_later_turns=len(prompts) > 1)
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(IMPLICIT + IMPLICIT_2T):
    BUILDERS.append(_implicit(_e, 10219 + _i))


# ------------------------------------------------------------------ M10b write into an existing file, copying its format (10233-10254)

FMT_SRC = r'''
import json

WD_ZH = ["周三", "周四", "周五", "周六", "周日", "周一", "周二"]
WD_EN = ["Wed", "Thu", "Fri", "Sat", "Sun", "Mon", "Tue"]


def row(fmt, city, d, i):
    low, high = d["temp_c"].split("~")
    date = d["date"]
    m, dd = int(date[5:7]), int(date[8:10])
    rain = d["rain_chance"]
    cond = d["condition"]
    if fmt == "list_zh":
        return "- %s（%s）%s：%s，%s~%s℃，降水 %s" % (date[5:], WD_ZH[i], city, cond, low, high, rain)
    if fmt == "table_zh":
        return "| %s | %s | %s | %s | %s | %s |" % (date, WD_ZH[i], cond, low, high, rain)
    if fmt == "csv":
        return "%s,%s,%s,%s,%s,%s" % (date, city, cond, low, high, rain.rstrip("%"))
    if fmt == "log_en":
        return "%s %d Sep | %s | %s | %s-%s°C | rain %s" % (WD_EN[i], dd, city, cond, low, high, rain)
    if fmt == "jsonl":
        return json.dumps({"date": date, "city": city, "cond": cond, "low": int(low), "high": int(high), "pop": int(rain.rstrip("%"))}, ensure_ascii=False)
    if fmt == "html":
        return "    <li>%d月%d日 %s %s %s–%s°C</li>" % (m, dd, WD_ZH[i], cond, low, high)
    if fmt == "kv":
        return "日期=%s 城市=%s 天气=%s 温度=%s/%s 降水=%s" % (date, city, cond, low, high, rain)
    if fmt == "diary":
        return "%d月%d日（%s），%s，%s，最高 %s 度。" % (m, dd, WD_ZH[i], city, cond, high)
    if fmt == "md_en":
        return "* **%s %d Sep** — %s, %s to %s °C (%s rain)" % (WD_EN[i], dd, cond, low, high, rain)
    raise ValueError(fmt)


def apply(fmt, city, text, days, add, before=None):
    new = "".join(row(fmt, city, days[i], i) + "\n" for i in add)
    if before:
        k = text.index(before)
        return text[:k] + new + text[k:]
    return text + new
'''
_fns = {}
exec(FMT_SRC, _fns)


def past_rows(fmt, city, en):
    """Two earlier days (09-14 Mon, 09-15 Tue) in the same format; values are history, not fixture."""
    cond = ["Overcast", "Sunny"] if en else ["阴", "晴"]
    fake = [{"date": "2026-09-14", "condition": cond[0], "temp_c": "17~24", "rain_chance": "30%"},
            {"date": "2026-09-15", "condition": cond[1], "temp_c": "18~27", "rain_chance": "10%"}]
    out = []
    for d, wd_zh, wd_en in zip(fake, ["周一", "周二"], ["Mon", "Tue"]):
        line = _fns["row"](fmt, city, d, 0)
        out.append(line.replace("周三", wd_zh).replace("Wed", wd_en))
    return out


SHELLS = {
    "list_zh": (lambda c: ["# %s 天气记录" % c, "", "每天一行，格式照下面的写。", ""], None),
    "table_zh": (lambda c: ["# %s 出差天气" % c, "", "| 日期 | 星期 | 天气 | 最低 | 最高 | 降水 |", "|---|---|---|---|---|---|"], None),
    "csv": (lambda c: ["date,city,cond,low,high,pop"], None),
    "log_en": (lambda c: ["# Weather log: %s" % c, ""], None),
    "jsonl": (lambda c: [], None),
    "html": (lambda c: ["<html><body>", "  <h1>%s 天气</h1>" % c, "  <ul>"], "  </ul>\n"),
    "kv": (lambda c: ["# 天气台账"], None),
    "diary": (lambda c: ["# 旅行日记 · 天气", ""], None),
    "md_en": (lambda c: ["# %s trip notes" % c, "", "## Weather"], None),
}
TAILS = {"html": ["  </ul>", "</body></html>"]}

WRITES = [
    # cid, fmt, city, en, path, add per turn, prompts, today_present
    ("hyb-10233", "list_zh", "杭州", False, "笔记/杭州天气.md", [[1]], ["把杭州明天的天气照 笔记/杭州天气.md 里现有的格式加一行，写完核对一遍。"], False),
    ("hyb-10234", "table_zh", "南京", False, "出差/南京.md", [[1, 2]], ["查一下南京明后两天的天气，按 出差/南京.md 表格的列和写法各加一行，加完检查表格。"], False),
    ("hyb-10235", "csv", "苏州", False, "数据/天气.csv", [[1]], ["把苏州明天的预报追加到 数据/天气.csv，跟已有行一个格式，写完核对。"], False),
    ("hyb-10236", "log_en", "Lisbon", True, "trip/weather.log", [[1]], ["Add tomorrow's Lisbon forecast to trip/weather.log, matching the existing lines exactly. Check the file afterwards."], False),
    ("hyb-10237", "jsonl", "深圳", False, "看板/weather.jsonl", [[1, 2]], ["看板/weather.jsonl 是深圳的天气记录，把今天起三天的预报补进去，已经有的别重复写，格式和现有行完全一致。写完看一下文件。"], True),
    ("hyb-10238", "html", "上海", False, "站点/天气.html", [[1]], ["站点/天气.html 的列表里加上上海明天的天气，写法跟现有的 li 一样，放在列表最后。改完检查一下页面文件。"], False),
    ("hyb-10239", "kv", "重庆", False, "台账/重庆.txt", [[3, 4]], ["把重庆这个周末两天的天气按 台账/重庆.txt 的格式各记一行，写完核对一下。"], False),
    ("hyb-10240", "diary", "武汉", False, "日记/天气.md", [[1]], ["按 日记/天气.md 里的句式，把武汉明天的天气写进去，写完读一遍确认。"], False),
    ("hyb-10241", "md_en", "Edinburgh", True, "notes/edinburgh.md", [[1, 2]], ["Put the next two days of Edinburgh weather under the Weather heading in notes/edinburgh.md, same style as the lines already there. Re-read it when done."], False),
    ("hyb-10242", "list_zh", "广州", False, "笔记/广州天气.md", [[2]], ["笔记/广州天气.md 只差后天那一天了，帮我照格式补上，写完核对。"], False),
    ("hyb-10243", "table_zh", "天津", False, "出差/天津.md", [[1]], ["出差/天津.md 表里今天已经填了，帮我加上明天那行，格式照抄，加完检查。"], True),
    ("hyb-10244", "csv", "Berlin", True, "data/berlin.csv", [[1, 2]], ["Append the Berlin forecast for tomorrow and the day after to data/berlin.csv in the same column format. Verify the file afterwards."], False),
    ("hyb-10245", "log_en", "Seoul", True, "trip/seoul.log", [[3]], ["Log Saturday's Seoul forecast in trip/seoul.log the same way as the earlier lines, then check it."], False),
    ("hyb-10246", "kv", "宁波", False, "台账/宁波.txt", [[1]], ["宁波明天的天气按 台账/宁波.txt 的格式记一行，记完核对。"], False),
    # two turns: turn 2 adds the next day without duplicating turn 1
    ("hyb-10247", "list_zh", "烟台", False, "笔记/烟台天气.md", [[1], [2]], ["把烟台明天的天气照 笔记/烟台天气.md 的格式加一行，写完核对。", "后天的也补上，前面写过的别重复。"], False),
    ("hyb-10248", "table_zh", "无锡", False, "出差/无锡.md", [[1], [2]], ["无锡明天的天气按 出差/无锡.md 表格加一行，加完检查。", "再把后天加上，检查一下表里没有重复的行。"], False),
    ("hyb-10249", "csv", "珠海", False, "数据/珠海.csv", [[1], [2]], ["珠海明天的预报追加到 数据/珠海.csv，格式跟已有行一致，写完核对。", "后天的也追加一行，别把明天的再写一遍。"], False),
    ("hyb-10250", "jsonl", "Munich", True, "dash/munich.jsonl", [[1], [2]], ["Append tomorrow's Munich forecast to dash/munich.jsonl, same keys and layout as the existing lines. Check it after.", "Now the day after tomorrow too. Don't repeat tomorrow's line."], False),
    ("hyb-10251", "html", "桂林", False, "站点/桂林.html", [[1], [2]], ["站点/桂林.html 列表里加上桂林明天的天气，写法照现有的 li。改完检查。", "后天的也加进列表末尾，加完再看一下页面文件，别重复。"], False),
    ("hyb-10252", "kv", "三亚", False, "台账/三亚.txt", [[1], [2]], ["三亚明天的天气按 台账/三亚.txt 的格式记一行，记完核对。", "后天的也记上，只加后天那一行。"], False),
    ("hyb-10253", "diary", "扬州", False, "日记/扬州.md", [[1], [2]], ["按 日记/扬州.md 的句式写上扬州明天的天气，写完读一遍。", "后天的也照样写一句。"], False),
    ("hyb-10254", "md_en", "Montreal", True, "notes/montreal.md", [[1], [2]], ["Add tomorrow's Montreal weather under the Weather heading in notes/montreal.md, same style as the existing entries. Re-read it after.", "Add the day after tomorrow as well, without repeating tomorrow."], False),
]


def _write(entry, seed):
    cid, fmt, city, en, path, adds, prompts, today = entry

    def build():
        fx = make_fx(city, seed, en=en, base=(12, 21) if en else (19, 28), aliases=[])
        days = fx["report"]["daily"]
        shell, _ = SHELLS[fmt]
        body = shell(city) + past_rows(fmt, city, en)
        if today:
            body.append(_fns["row"](fmt, city, days[0], 0))
        before = None
        if fmt in TAILS:
            body += TAILS[fmt]
            before = TAILS[fmt][0] + "\n"
        original = lines(body)
        flat = [i for turn in adds for i in turn]
        final = _fns["apply"](fmt, city, original, days, flat, before)
        files = {path: original}
        vbody = FMT_SRC + '''
fx = case["weather_fixture"][0]
assert fx["location"] == %r
days = fx["report"]["daily"]
assert [d["date"] for d in days][:5] == ["2026-09-16", "2026-09-17", "2026-09-18", "2026-09-19", "2026-09-20"]
text = case["files"][%r]
print(json.dumps({"files": {%r: apply(%r, %r, text, days, %r, %r)}}, ensure_ascii=False))
''' % (city, path, path, fmt, city, flat, before)
        tl = []
        for k, (p, add) in enumerate(zip(prompts, adds)):
            e = {"forbidden_tools": list(NOWEB), "max_output_chars": 700}
            if k == 0:
                e["required_tools"] = ["get_weather"]
            tl.append({"prompt": p, "expect": e})
        need = max(flat) + 1
        added = "".join(_fns["row"](fmt, city, days[i], i) + "\n" for i in flat)
        notes = """## Traps
- TR-DEFN: the line format (separators, units, weekday, date style, city spelling) comes only from the existing lines of %s; the tool's labels are not that format.%s%s
- The file ends with a newline; new lines go %s, one per day, each ending in a newline.

## Reference solution
1. read_file %s (format)
2. get_weather {"location": "%s", "days": %d}
3. write: %s
4. read_file %s once to confirm
Final answer: added the %s line(s) to %s in the existing format.

## Why the answer is unique
The format is copied from the file and the values from the fixture (clock 2026-09-16 Wed); expect.files pins the whole file.
""" % (path, "\n- Today's row is already in the file; writing it again is a duplicate." if today else "",
       "\n- Turn 2 adds only the next day; turn 1's line must not appear twice." if len(adds) > 1 else "",
       "before `%s`" % before.strip() if before else "at the end", path, city, max(3, need), " / ".join(repr(l) for l in added.splitlines()), path,
       ", ".join(DATES[i] for i in flat), path)
        notes += phrasings(*(["把%s天气按文件格式记下来" % city, "%s 的预报补到记录文件里" % city, "照着已有行的格式写%s的天气" % city,
                              "%s天气记录更新一下" % city, "Add %s weather to the log in its format" % city] if not en else
                             ["Log %s's forecast in the file's format" % city, "Update the %s weather file" % city, "Append %s weather like the other lines" % city,
                              "Add the forecast lines for %s" % city, "把 %s 的天气按格式写进文件" % city]))
        traps = ["TR-DEFN"] + (["TR-DUPROW"] if today or len(adds) > 1 else [])
        decoys = {"TR-DEFN": None}
        if "TR-DUPROW" in traps:
            decoys["TR-DUPROW"] = None
        return case(cid, sub="M10b", spec={"kind": "weather_write"}, desc=("Two turns: " if len(adds) > 1 else "") +
                    "Looks up the forecast and adds it to an existing file, copying the file's own line format exactly", task_type="tool_then_write",
                    family="fam-hyb-b14-write-%s" % cid.split("-")[1], ref_calls=3 + (len(adds) - 1), files=files, turns=tl,
                    verify=verify_src(files, vbody), notes=notes, weather_fixture=[fx], traps=traps, decoys=decoys, axes=("CON", "VER"),
                    case_expect={"files": {path: {"equals": final}}})
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(WRITES):
    BUILDERS.append(_write(_e, 10233 + _i))


# ------------------------------------------------------------------ M10f city switch across turns (10255-10266)

SWITCH = [
    # cid, (city1, en1, al1), (city2, en2, al2), prompts, facts
    ("hyb-10255", ("石家庄", False, ["Shijiazhuang"]), ("保定", False, ["Baoding"]), ["石家庄明天会下雨吗？说下降水概率。", "那保定呢？"], [("石家庄", 1, "rain"), ("保定", 1, "rain")]),
    ("hyb-10256", ("兰州", False, ["Lanzhou"]), ("银川", False, ["Yinchuan"]), ["兰州后天最高多少度？", "银川后天呢？"], [("兰州", 2, "high"), ("银川", 2, "high")]),
    ("hyb-10257", ("沈阳", False, ["Shenyang"]), ("长春", False, ["Changchun"]), ["沈阳今天早晚冷不冷？最低几度？", "我晚上到长春，长春今天最低多少？"], [("沈阳", 0, "low"), ("长春", 0, "low")]),
    ("hyb-10258", ("泉州", False, ["Quanzhou"]), ("汕头", False, ["Shantou"]), ["泉州周六什么天气？", "汕头周六呢？两个地方我都要去。"], [("泉州", 3, "cond"), ("汕头", 3, "cond")]),
    ("hyb-10259", ("Bangkok", True, ["曼谷"]), ("Chiang Mai", True, ["清迈"]), ["What's the chance of rain in Bangkok tomorrow?", "And in Chiang Mai?"], [("Bangkok", 1, "rain"), ("Chiang Mai", 1, "rain")]),
    ("hyb-10260", ("绍兴", False, ["Shaoxing"]), ("嘉兴", False, ["Jiaxing"]), ["绍兴明天天气怎么样？", "换成嘉兴看看，明天呢？"], [("绍兴", 1, "cond"), ("嘉兴", 1, "cond")]),
    ("hyb-10261", ("威海", False, ["Weihai"]), ("杭州", False, ["Hangzhou"]), ["威海后天降水概率多少？", "那后天去西湖那边呢？"], [("威海", 2, "rain"), ("杭州", 2, "rain")]),
    ("hyb-10262", ("Toronto", True, ["多伦多"]), ("Ottawa", True, ["渥太华"]), ["How cold does Toronto get tomorrow night?", "Ottawa?"], [("Toronto", 1, "low"), ("Ottawa", 1, "low")]),
    ("hyb-10263", ("开封", False, ["Kaifeng"]), ("洛阳", False, ["Luoyang"]), ["开封周日最高多少度？", "洛阳周日呢？"], [("开封", 4, "high"), ("洛阳", 4, "high")]),
    ("hyb-10264", ("张家界", False, ["Zhangjiajie"]), ("凤凰", False, ["Fenghuang"]), ["张家界明天适合爬山吗？什么天气？", "第二站去凤凰，凤凰明天天气呢？"], [("张家界", 1, "cond"), ("凤凰", 1, "cond")]),
    ("hyb-10265", ("Seoul", True, ["首尔"]), ("Busan", True, ["釜山"]), ["Seoul high on Saturday?", "What about Busan on Saturday?"], [("Seoul", 3, "high"), ("Busan", 3, "high")]),
    ("hyb-10266", ("丽江", False, ["Lijiang"]), ("大理", False, ["Dali"]), ["丽江后天要带伞吗？降水概率多少？", "我后天其实在大理，大理呢？"], [("丽江", 2, "rain"), ("大理", 2, "rain")]),
]


def _switch(entry, seed):
    cid, c1, c2, prompts, facts = entry

    def build():
        fx1 = make_fx(c1[0], seed, en=c1[1], aliases=c1[2], base=(14, 23) if c1[1] else (19, 28))
        fx2 = make_fx(c2[0], seed + 500, en=c2[1], aliases=c2[2], base=(14, 23) if c2[1] else (19, 28))
        for k in range(50):
            if day(fx1, facts[0][1])[facts[0][2]] != day(fx2, facts[1][1])[facts[1][2]]:
                break
            fx2 = make_fx(c2[0], seed + 500 + k + 1, en=c2[1], aliases=c2[2], base=(14, 23) if c2[1] else (19, 28))
        v2 = day(fx2, facts[1][1])[facts[1][2]]
        v1 = day(fx1, facts[0][1])[facts[0][2]]
        alts = ["%s和%s两地天气" % (c1[0], c2[0]), "先查%s再查%s" % (c1[0], c2[0]), "%s天气怎样，再看%s" % (c1[0], c2[0]),
                "%s 的天气呢" % c2[0], "Compare %s and %s weather" % (c1[0], c2[0])]
        landmark = "西湖" in prompts[1]
        return weather_case(cid, sub="M10f", fxs=[fx1, fx2], turns=prompts, facts=facts,
                            desc="Two turns: a forecast question about one city, then the same question about another city (a fresh lookup)",
                            family="fam-hyb-b14-switch-%s" % cid.split("-")[1],
                            notes_traps=["TR-DECOY: turn 1's value (%s) is for %s; turn 2 needs %s's own report." % (v1, c1[0], c2[0])] +
                            (["西湖 is in 杭州; the lookup is 杭州."] if landmark else []),
                            reply="%s：%s。" % (c2[0], v2), alts=alts,
                            spec={"kind": "weather_switch", "cities": [[c1[0]] + c1[2], [c2[0]] + c2[2]], "dates": [DATES[facts[1][1]]]},
                            traps=["TR-DECOY"], decoys={"TR-DECOY": v1})
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(SWITCH):
    BUILDERS.append(_switch(_e, 10255 + _i))


# ------------------------------------------------------------------ M10g place the fixture does not know (10267-10275)

NOTFOUND = ["查不到", "没有查到", "未查到", "没查到", "没能查到", "未能查到", "查询不到", "找不到", "没找到", "未找到", "无法获取", "获取不到", "无法查询",
            "没有这个地方", "没有收录", "无法识别", "不识别",
            "not found", "couldn't find", "could not find", "can't find", "cannot find", "unable to find", "no forecast", "not available", "isn't available",
            "couldn't get", "could not get", "couldn't retrieve", "could not retrieve", "could not be resolved", "no match"]

UNKNOWN = [
    # cid, missing, known (city, en, aliases) or None, prompts, known fact or None, en
    ("hyb-10267", "婺源", ("南昌", False, ["Nanchang"]), ["明天想去婺源看晒秋，那边天气怎么样？"], None, False),
    ("hyb-10268", "阿尔山", ("呼伦贝尔", False, ["Hulunbuir"]), ["阿尔山后天冷不冷？要穿羽绒服吗？"], None, False),
    ("hyb-10269", "Hallstatt", ("Vienna", True, ["维也纳"]), ["What's the weather in Hallstatt tomorrow?"], None, True),
    ("hyb-10270", "霞浦", ("福州", False, ["Fuzhou"]), ["周六去霞浦拍滩涂，那天下雨吗？"], None, False),
    ("hyb-10271", "稻城亚丁", ("成都", False, ["Chengdu"]), ["稻城亚丁和成都明天哪边天气好一点？"], ("成都", 1, "cond"), False),
    ("hyb-10272", "Tórshavn", ("Copenhagen", True, ["哥本哈根"]), ["I'm choosing between Tórshavn and Copenhagen for tomorrow. What's the weather in each?"], ("Copenhagen", 1, "cond"), True),
    ("hyb-10273", "元阳", ("昆明", False, ["Kunming"]), ["元阳梯田和昆明，后天分别什么天气？"], ("昆明", 2, "cond"), False),
    ("hyb-10274", "喀纳斯", ("乌鲁木齐", False, ["Urumqi"]), ["乌鲁木齐明天最低几度？", "那喀纳斯呢？"], ("乌鲁木齐", 1, "low"), False),
    ("hyb-10275", "涠洲岛", ("北海", False, ["Beihai"]), ["北海明天天气怎么样？", "涠洲岛那边呢？"], ("北海", 1, "cond"), False),
]


def _unknown(entry, seed):
    cid, missing, known, prompts, kfact, en = entry

    def build():
        fx = make_fx(known[0], seed, en=known[1], aliases=known[2], base=(14, 23) if known[1] else (17, 26))
        two_turn = len(prompts) > 1
        tl = []
        if two_turn:
            v = day(fx, kfact[1])[kfact[2]]
            tl.append({"prompt": prompts[0], "expect": wexpect(v, kfact[2], en)})
            tl.append({"prompt": prompts[1], "expect": {"forbidden_tools": list(NOWEB), "output_contains_any": NOTFOUND, "max_output_chars": 700}})
        elif kfact:
            v = day(fx, kfact[1])[kfact[2]]
            tl.append({"prompt": prompts[0], "expect": wexpect(v, kfact[2], en, extra={"output_contains_any": NOTFOUND})})
        else:
            tl.append({"prompt": prompts[0], "expect": {"required_tools": ["get_weather"], "forbidden_tools": list(NOWEB), "output_contains_any": NOTFOUND,
                                                        "output_excludes": ["°C", "℃", "°F"], "max_output_chars": 700}})
        body = '''
import json
case = json.load(open("case.json"))
names = [e["location"].lower() for e in case["weather_fixture"]] + [a.lower() for e in case["weather_fixture"] for a in e["aliases"]]
assert not any(n in %r.lower() for n in names), "the missing place must not resolve"
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (missing, json.dumps(NOTFOUND, ensure_ascii=False))
        extract = "This path keeps an unrecovered `location not found`; `corpus paths` drops such paths today (see b14-authoring.md)." if not (kfact and not two_turn) else \
            "Asking for %s first and %s second gives miss-then-success, which `corpus paths` keeps; the other order is dropped." % (missing, known[0])
        notes = """## Traps
- TR-ABSENT: the fixture has no report for %s (only %s); get_weather answers `location not found`. The answer says so plainly and invents no numbers; it does not substitute a nearby city as if it were %s.
- %s

## Reference solution
1. get_weather {"location": "%s", "days": 3} -> location not found%s
Final answer: %s

## Why the answer is unique
The fixture fixes which names resolve; %s is not one of them.
""" % (missing, known[0], missing, extract, missing,
       ("\n2. get_weather {\"location\": \"%s\", \"days\": 3}" % known[0]) if kfact else "",
       ("查不到%s的天气预报（天气服务里没有这个地点）；%s的情况见上。" % (missing, known[0])) if not en else ("I couldn't find a forecast for %s (the weather service doesn't know that place)." % missing),
       missing)
        notes += phrasings(*(["%s天气" % missing, "%s明天会下雨吗" % missing, "去%s要带什么衣服" % missing, "%s最近天气怎么样" % missing, "Weather in %s?" % missing]))
        return case(cid, sub="M10g", spec={"kind": "weather_unknown", "missing": missing, "known": [known[0]] + known[2] if kfact else []},
                    desc=("Two turns: " if two_turn else "") + "Asks the forecast for a place the weather service does not know; the answer must say it was not found",
                    task_type="special_tool", family="fam-hyb-b14-unknown-%s" % cid.split("-")[1], ref_calls=1 + bool(kfact), files={}, turns=tl,
                    verify=body, notes=notes, weather_fixture=[fx], traps=["TR-ABSENT"], decoys={"TR-ABSENT": "UNKNOWN"}, axes=("ERR", "OBS"))
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(UNKNOWN):
    BUILDERS.append(_unknown(_e, 10267 + _i))


# ------------------------------------------------------------------ M10c composite: weather + one web fact (10276-10285)

COMPOSITE = [
    # cid, city, en, aliases, day, field, web(query_match, url, title, snippet), fact strings any-of, prompts, reply, alts
    ("hyb-10276", "南京", False, ["Nanjing"], 1, "cond", ("中山陵", "https://www.zsl-scenic.example.cn/notice", "中山陵景区 开放公告",
     "中山陵陵寝每周一闭馆维护，其余时间 8:30—17:00 开放，需提前一天实名预约。"), ["周一"],
     ["明天去南京中山陵，它每周哪天闭馆？顺便看下南京明天天气。"], "中山陵每周一闭馆；南京明天{v}。",
     ["中山陵哪天闭馆，南京明天天气", "明天去中山陵开不开门，天气如何", "南京明天天气和中山陵开放时间", "查中山陵闭馆日，再看南京明天天气", "中山陵周几不开？南京明天下雨吗"]),
    ("hyb-10277", "武汉", False, ["Wuhan"], 2, "rain", ("黄鹤楼", "https://www.hhl-tickets.example.cn/price", "黄鹤楼 门票价格",
     "黄鹤楼公园成人票 70 元，学生半价，夜游场次另售。"), ["70"],
     ["后天带同学去黄鹤楼，成人票多少钱？武汉后天会下雨吗？"], "黄鹤楼成人票 70 元；武汉后天降水概率 {v}。",
     ["黄鹤楼门票多少钱，武汉后天天气", "后天去黄鹤楼，票价和天气", "武汉后天下雨吗，黄鹤楼成人票价", "查黄鹤楼票价，再看武汉后天降水", "黄鹤楼要多少钱？后天武汉天气"]),
    ("hyb-10278", "长沙", False, ["Changsha"], 3, "cond", ("橘子洲", "https://www.jzz-fireworks.example.cn/2026", "橘子洲焰火 2026 下半年安排",
     "2026 年 9 月至 10 月，橘子洲焰火在每周六 20:30 燃放，时长约 15 分钟。"), ["20:30", "20点30", "晚上八点半", "八点半"],
     ["这周六想去橘子洲看焰火，几点放？长沙周六天气怎么样？"], "橘子洲焰火周六 20:30 燃放；长沙周六{v}。",
     ["橘子洲焰火几点开始，长沙周六天气", "周六看焰火，时间和天气", "长沙周六会下雨吗，焰火几点", "查橘子洲焰火时间，再看长沙周六天气", "橘子洲周六焰火几点？那天天气呢"]),
    ("hyb-10279", "Osaka", True, ["大阪"], 1, "cond", ("kaiyukan", "https://www.kaiyukan.example.jp/en/hours", "Osaka Aquarium Kaiyukan hours",
     "Kaiyukan is open daily 10:00-20:00; last entry one hour before closing."), ["20:00", "8 pm", "8pm", "8:00 pm"],
     ["I'm in Osaka tomorrow. What time does Kaiyukan aquarium close, and what's the weather going to be?"], "Kaiyukan closes at 20:00 (last entry 19:00); Osaka tomorrow: {v}.",
     ["Kaiyukan closing time and Osaka weather tomorrow", "When does the Osaka aquarium close? Will it rain tomorrow?", "Osaka tomorrow: aquarium hours and forecast", "Kaiyukan hours plus tomorrow's weather", "What time does Kaiyukan shut, and tomorrow's Osaka forecast?"]),
    ("hyb-10280", "青岛", False, ["Qingdao"], 2, "high", ("啤酒节", "https://www.qd-beerfest.example.cn/2026", "2026 青岛国际啤酒节",
     "2026 青岛国际啤酒节金沙滩主会场 8 月 15 日开幕，9 月 20 日闭幕。"), ["9 月 20 日", "9月20日", "20 日", "20日"],
     ["青岛啤酒节今年哪天闭幕？我后天过去，青岛后天最高几度？"], "啤酒节 9 月 20 日闭幕；青岛后天最高 {v}°C。",
     ["青岛啤酒节闭幕时间，后天青岛气温", "后天去青岛，啤酒节还开吗，天气如何", "青岛啤酒节什么时候结束，后天多少度", "查啤酒节闭幕日，再看青岛后天天气", "啤酒节哪天结束？青岛后天热吗"]),
    ("hyb-10281", "大连", False, ["Dalian"], 1, "rain", ("圣亚", "https://www.sy-ocean.example.cn/ticket", "圣亚海洋世界 票价",
     "圣亚海洋世界成人通票 230 元，1.2 米以下儿童免票。"), ["230"],
     ["明天带孩子去大连圣亚，成人通票多少钱？大连明天降水概率多少？"], "圣亚成人通票 230 元；大连明天降水概率 {v}。",
     ["圣亚海洋世界门票，大连明天会下雨吗", "明天去圣亚，票价和天气", "大连明天天气和圣亚票价", "查圣亚成人票，再看大连明天降水", "圣亚多少钱？大连明天下雨吗"]),
    ("hyb-10282", "Vancouver", True, ["温哥华"], 3, "rain", ("capilano", "https://www.capilano.example.ca/admission", "Capilano Suspension Bridge Park admission",
     "Capilano Suspension Bridge Park general admission, adult: CA$72.95."), ["72.95"],
     ["We're doing the Capilano Suspension Bridge on Saturday. How much is adult admission, and what's the chance of rain in Vancouver that day?"], "Adult admission is CA$72.95; Vancouver on Saturday has a {v} chance of rain.",
     ["Capilano adult ticket price and Saturday rain chance", "How much is Capilano, and will it rain Saturday?", "Vancouver Saturday forecast plus Capilano admission", "Capilano bridge price; Vancouver weather on the 19th", "Saturday at Capilano: cost and rain?"]),
    ("hyb-10283", "杭州", False, ["Hangzhou"], 1, "cond", ("游船", "https://www.westlake-boat.example.cn/price", "西湖游船 价格",
     "西湖手划船每船每小时 150 元，限乘 4 人；电瓶游船成人 55 元。"), ["150"],
     ["明天在西湖坐手划船，一小时多少钱？杭州明天天气怎么样？"], "西湖手划船每船每小时 150 元；杭州明天{v}。",
     ["西湖手划船多少钱，杭州明天天气", "明天去西湖划船，价格和天气", "杭州明天天气，西湖手划船收费", "查西湖手划船价格，再看杭州明天天气", "西湖划船一小时多少钱？明天下雨吗"]),
]
COMPOSITE_2T = [
    ("hyb-10284", "苏州", False, ["Suzhou"], 1, "cond", ("拙政园", "https://www.zzy-garden.example.cn/visit", "拙政园 参观须知",
     "拙政园旺季（4 月 16 日—10 月 30 日）门票 90 元，7:30 开园。"), ["90"],
     ["苏州明天天气怎么样？", "那拙政园现在门票多少钱？"], "拙政园旺季门票 90 元。",
     ["拙政园门票多少", "拙政园旺季票价", "苏州拙政园现在多少钱", "拙政园成人票价格", "去拙政园要买多少钱的票"]),
    ("hyb-10285", "Lisbon", True, ["里斯本"], 2, "rain", ("tram 28", "https://www.carris.example.pt/en/fares", "Carris tram fares",
     "A single tram ticket bought on board costs €3.10; the 24-hour pass is €6.80."), ["3.10", "3.1"],
     ["Will it rain in Lisbon the day after tomorrow?", "How much is a single ticket on tram 28 if I buy it on board?"], "A single tram ticket bought on board is €3.10.",
     ["Tram 28 single fare on board", "How much is a Lisbon tram ticket?", "Carris tram ticket price", "Cost of riding tram 28 once", "On-board tram fare in Lisbon"]),
]


def _composite(entry, seed, two_turn=False):
    cid, city, en, aliases, di, field, web, fact_any, prompts, reply, alts = entry

    def build():
        fx = make_fx(city, seed, en=en, aliases=aliases, base=(14, 23) if en else (19, 28))
        qm, url, title, snippet = web
        fixture = [{"query_match": qm, "url": url, "url_match": url.split("//")[1].split("/")[0], "title": title, "snippet": snippet,
                    "content": "# %s\n\n%s" % (title, snippet), "published_at": "2026-09-01"}]
        v = day(fx, di)[field]
        if two_turn:
            tl = [{"prompt": prompts[0], "expect": wexpect(v, field, en)},
                  {"prompt": prompts[1], "expect": {"required_tools": ["web_search"], "forbidden_tools": ["get_weather"], "output_contains_any": fact_any, "max_output_chars": 700}}]
        else:
            e = wexpect(v, field, en, forbid_web=False, required=("get_weather", "web_search"))
            e["output_contains_any"] = fact_any
            tl = [{"prompt": prompts[0], "expect": e}]
        body = FACT_SRC + '''
import json
case = json.load(open("case.json"))
v = fact(case, %r, %d, %r)
snippet = case["web_fixture"][0]["snippet"]
want = %s
assert any(w in snippet for w in want)
print(json.dumps({"expected_contains_any": want}, ensure_ascii=False))
''' % (city, di, field, json.dumps(fact_any, ensure_ascii=False))
        notes = """## Traps
- TR-MULTISRC: two sub-requests, two sources: the forecast from get_weather (%s, row %d) and the fact from one web search; the weather part is not searched, and once both are on screen the answer is written.

## Reference solution
1. get_weather {"location": "%s", "days": %d} -> %s
2. web_search %s
Final answer: %s

## Why the answer is unique
One forecast row and one snippet carry the values.
""" % (DATES[di], di + 1, city, max(3, di + 1), v, qm, reply.format(v=v)) + phrasings(*alts)
        return case(cid, sub="M10c", spec={"kind": "weather", "dates": [DATES[di]]}, desc=("Two turns: forecast first, then a web fact" if two_turn else
                    "Composite request: a forecast from the weather tool plus one fact from web search"), task_type="special_tool",
                    family="fam-hyb-b14-combo-%s" % cid.split("-")[1], ref_calls=2, files={}, turns=tl, verify=body, notes=notes,
                    weather_fixture=[fx], web=fixture, traps=["TR-MULTISRC"], decoys={"TR-MULTISRC": day(fx, 0 if di else 1)[field]}, axes=("CHN", "OBS"))
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(COMPOSITE):
    BUILDERS.append(_composite(_e, 10276 + _i))
for _i, _e in enumerate(COMPOSITE_2T):
    BUILDERS.append(_composite(_e, 10284 + _i, two_turn=True))


# ------------------------------------------------------------------ M10e weather concepts: no call (10286-10300)

CONCEPT = [
    ("nt-10286", "手机天气里写着「体感 31℃」，可气温才 28℃，这个体感数是按什么算出来的？", ["湿度", "风"], "体感温度综合了气温、湿度和风速：潮湿闷热时比气温高，风大时比气温低。"),
    ("nt-10287", "紫外线指数 8 算高吗？出门要注意什么？", ["防晒", "很强", "较强", "高"], "8 属于很强（8–10），需要防晒霜、遮阳帽，避开中午时段。"),
    ("nt-10288", "露点是什么意思？露点高了人会有什么感觉？", ["闷", "潮"], "露点是空气冷却到饱和的温度；露点越高越闷热潮湿。"),
    ("nt-10289", "「阵雨」和「雷阵雨」有什么区别？", ["雷", "闪电"], "阵雨是来得快去得快的降雨；雷阵雨同时伴有雷电，对流更强。"),
    ("nt-10290", "南方说的「回南天」是怎么形成的？", ["暖湿", "冷", "凝结"], "冬春之交暖湿气流回流，遇到被冷空气冻凉的墙面地面凝结成水，屋里返潮。"),
    ("nt-10291", "台风预警的蓝黄橙红四个颜色分别代表什么程度？", ["红色", "蓝色"], "蓝色最轻、红色最严重，依次表示 24 小时内可能受影响的风力等级递增。"),
    ("nt-10292", "What does \"feels like\" temperature mean on a weather app?", ["humidity", "wind"], "It folds humidity and wind into the air temperature: humid heat feels hotter, wind makes cold feel colder."),
    ("nt-10293", "My app says \"scattered showers\" for this afternoon. Does that mean it will rain the whole time everywhere around me?", ["some", "parts", "patchy", "not everywhere", "on and off", "not all"], "No: scattered showers are brief, patchy bursts that hit some places and not others; dry spells in between are normal."),
    ("nt-10294", "Why is it usually colder on a clear night than a cloudy one?", ["radiat", "heat"], "Clouds trap outgoing heat; clear skies let the ground radiate it away, so temperatures drop further."),
    ("nt-10295", "「能见度 500 米」对开车有什么影响？", ["雾灯", "减速", "车距"], "能见度 500 米属于大雾，应开雾灯、减速并拉大车距，高速可能限行。"),
]
CONCEPT_2T = [
    ("nt-10296", "「最低气温 12℃」一般指一天里什么时候的温度？", ["清晨", "日出", "凌晨", "早上"], ("西安", False, ["Xi'an"]), "那西安明天最低多少度？", (1, "low")),
    ("nt-10297", "空气湿度 90% 是不是就一定会下雨？", ["不一定", "不等于"], ("广州", False, ["Guangzhou"]), "那广州明天下雨的可能性有多大？", (1, "rain")),
    ("nt-10298", "What does a 30% chance of rain actually mean?", ["30", "chance"], ("Dublin", True, ["都柏林"]), "OK, so what's the chance of rain in Dublin tomorrow?", (1, "rain")),
    ("nt-10299", "秋老虎是什么意思？", ["立秋", "高温", "炎热"], ("南昌", False, ["Nanchang"]), "南昌后天最高多少度，还算秋老虎吗？", (2, "high")),
    ("nt-10300", "天气预报说「多云转晴」是什么意思？", ["先", "转"], ("合肥", False, ["Hefei"]), "那合肥周六什么天气？", (3, "cond")),
]


def _concept(entry):
    cid, prompt, any_of, reply = entry

    def build():
        body = '''import json
case = json.load(open("case.json"))
assert case["turns"][0]["prompt"].strip()
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % json.dumps(any_of, ensure_ascii=False)
        notes = """## Traps
- TR-NOTOOLNEED: a definition question; get_weather and web search are offered but no place or date is asked about.

## Reference solution
No tool call. Final answer: %s

## Why the answer is unique
Standard meteorological explanation; no forecast is involved.
""" % reply
        return case(cid, sub="M10e", spec={"kind": "zero_call"}, desc="Weather concept question with the weather tool offered; answered without any call", task_type="concept",
                    family="fam-nt-b14-concept-%s" % cid.split("-")[1], ref_calls=0, files={},
                    turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": any_of, "max_output_chars": 900}}],
                    verify=body, notes=notes, traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": "a forecast lookup"}, axes=("DEC",))
    build.__name__ = cid.replace("-", "_")
    return build


def _concept2(entry, seed):
    cid, prompt, any_of, (city, en, aliases), p2, (di, field) = entry

    def build():
        fx = make_fx(city, seed, en=en, aliases=aliases, base=(14, 23) if en else (19, 28))
        v = day(fx, di)[field]
        body = '''import json
case = json.load(open("case.json"))
assert case["weather_fixture"][0]["location"] == %r
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (city, json.dumps(any_of, ensure_ascii=False))
        notes = """## Traps
- TR-NOTOOLNEED: turn 1 is a concept question (no call). Turn 2 asks a real forecast for %s, so get_weather is now required (row %d, %s).

## Reference solution
Turn 1: no tool call.
Turn 2: get_weather {"location": "%s", "days": %d} -> %s
Final answer turn 2: %s %s: %s.

## Why the answer is unique
Turn 1 is a definition; turn 2's value is one forecast row.
""" % (city, di + 1, DATES[di], city, max(3, di + 1), v, city, DATES[di], v)
        return case(cid, sub="M10e", spec={"kind": "concept_then_weather", "dates": [DATES[di]]},
                    desc="Two turns: a weather concept question answered without a call, then a real forecast question that needs the weather tool",
                    task_type="concept", family="fam-nt-b14-concept-%s" % cid.split("-")[1], ref_calls=1, files={},
                    turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": any_of, "max_output_chars": 900}},
                           {"prompt": p2, "expect": wexpect(v, field, en)}],
                    verify=body, notes=notes, weather_fixture=[fx], traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": "a forecast lookup in turn 1"}, axes=("DEC", "OBS"))
    build.__name__ = cid.replace("-", "_")
    return build


for _e in CONCEPT:
    BUILDERS.append(_concept(_e))
for _i, _e in enumerate(CONCEPT_2T):
    BUILDERS.append(_concept2(_e, 10296 + _i))
