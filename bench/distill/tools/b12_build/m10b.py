"""M10: special-purpose tool first (b12 pilot, part 2): composite and implicit
weather requests, plus a weather concept question that needs no tool."""
from common import lines, weather, write_case
from m10 import phrasings

REFS = {}


def hyb_9017():
    fx = [weather("成都", "阴 24°C 体感 25°C 湿度 82% 风速 6 km/h",
                  [("2026-09-16", "阴", "20~26", "30%"), ("2026-09-17", "小雨", "19~24", "60%"),
                   ("2026-09-18", "多云", "19~26", "20%"), ("2026-09-19", "晴", "18~28", "5%"),
                   ("2026-09-20", "阵雨", "19~25", "55%")], aliases=["Chengdu"])]
    web = [{"query_match": "展览", "url": "https://www.cdmuseum.cn/exhibitions/2026-autumn",
            "url_match": "cdmuseum.cn/exhibitions", "title": "成都博物馆 2026 秋季特展",
            "snippet": "「锦官城外——蜀锦千年」特展 9 月 12 日至 11 月 30 日在成都博物馆三楼开放。",
            "content": "# 2026 秋季特展\n\n「锦官城外——蜀锦千年」特展，9 月 12 日至 11 月 30 日，成都博物馆三楼临展厅，周一闭馆。",
            "published_at": "2026-09-05"}]
    files = {"周末/想法.md": lines(["# 周末想法", "", "- 看展？", "- 天气好就去青城山"])}
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["周末/想法.md"].startswith("# 周末想法")
sat = case["weather_fixture"][0]["report"]["daily"][3]
title = case["web_fixture"][0]["snippet"].split("「")[1].split("」")[0]
assert sat["date"] == "2026-09-19"
print(json.dumps({"expected_string": sat["condition"] + " " + title}, ensure_ascii=False))
'''
    notes = """## Traps
- TR-MULTISRC: two sub-requests with two different sources -- the forecast from get_weather (周六 2026-09-19 is the 4th row, so days must be >= 5) and the exhibition from web search.

## Reference solution
1. get_weather {"location": "成都", "days": 5}
2. web_search 成都 展览 九月
Final answer: 周六晴、18~28°C，周日有阵雨（降水概率 55%）；成都博物馆正在办「锦官城外——蜀锦千年」特展（到 11 月 30 日，周一闭馆），周日下雨正好看展、周六适合去青城山。

## Why the answer is unique
Weekend dates follow the fixed clock; one exhibition is listed.
""" + phrasings("成都周末天气怎么样？顺便看看有什么展", "这周末成都会下雨吗，有没有好看的展览", "周末在成都，天气和展览信息帮我查一下", "成都这周六周日天气，加上最近的展览", "Chengdu this weekend: weather and any exhibitions?")
    return write_case(
        "hyb-9017", desc="Composite request: weekend forecast from the weather tool plus an exhibition from web search",
        task_type="special_tool", family="fam-hyb-b12-weekendcombo-01", level="L1", ref_calls=2,
        traps=["TR-MULTISRC"], decoys={"TR-MULTISRC": "阵雨"}, axes=["CHN"],
        files=files, verify=verify, notes=notes, weather_fixture=fx, web=web,
        turns=[{"prompt": "帮我看下成都这个周末的天气，再搜搜成都最近有什么展览。",
                "expect": {"required_tools": ["get_weather", "web_search"], "output_contains": ["晴", "蜀锦"],
                           "max_output_chars": 600}}])


def hyb_9018():
    fx = [weather("苏州", "多云 23°C 体感 24°C 湿度 80% 风速 8 km/h",
                  [("2026-09-16", "多云", "21~27", "25%"), ("2026-09-17", "中雨", "20~24", "80%"),
                   ("2026-09-18", "阴", "20~26", "35%")], aliases=["Suzhou"])]
    files = {"拍摄/通告.md": lines(["# 外景通告", "", "日期：9 月 17 日（周四）", "地点：苏州 平江路", "时长：全天外景"])}
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["拍摄/通告.md"].startswith("# 外景通告")
assert "9 月 17 日" in case["files"]["拍摄/通告.md"]
day = case["weather_fixture"][0]["report"]["daily"][1]
assert day["date"] == "2026-09-17"
print(json.dumps({"expected_string": day["rain_chance"]}))
'''
    notes = """## Traps
- TR-DECOY: today is 25%; the shoot is tomorrow (80%, 中雨).

## Reference solution
1. get_weather {"location": "苏州", "days": 3}
Final answer: 需要。苏州明天中雨、降水概率 80%，全天外景建议带雨具和设备防雨罩，最好准备室内备选机位。

## Why the answer is unique
The question is implicitly about tomorrow's rain in 苏州; only the forecast settles it.
""" + phrasings("明天苏州拍外景，要准备防雨吗？", "苏州明天下雨吗，我们全天外拍", "明天平江路外景会不会被雨影响？", "苏州明天天气适合外拍吗？", "Do we need rain gear for tomorrow's shoot in Suzhou?")
    return write_case(
        "hyb-9018", desc="Implicit weather need: whether to bring rain gear for an outdoor shoot tomorrow",
        task_type="special_tool", family="fam-hyb-b12-raingear-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": "25%"}, axes=["DEC", "OBS"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": "明天要在苏州户外拍一整天，需要准备雨具吗？",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": ["web_search", "web_fetch"],
                           "output_contains": ["80%"], "max_output_chars": 600}}])


def hyb_9019():
    fx = [weather("Hangzhou", "Overcast 21°C feels 21°C humidity 85% wind 10 km/h",
                  [("2026-09-16", "Overcast", "19~24", "35%"), ("2026-09-17", "Light rain", "18~23", "60%"),
                   ("2026-09-18", "Cloudy", "18~25", "25%")], aliases=["杭州"])]
    files = {"site/rules.md": lines(["# Pour rules", "", "- No concrete pours when the forecast rain chance for the day is 40% or more.",
                                     "- Minimum air temperature 5°C."])}
    verify = '''
import json
case = json.load(open("case.json"))
rules = case["files"]["site/rules.md"]
assert rules.startswith("# Pour rules") and "40% or more" in rules
day = case["weather_fixture"][0]["report"]["daily"][1]
assert int(day["rain_chance"].rstrip("%")) >= 40
print(json.dumps({"expected_string": day["rain_chance"]}))
'''
    notes = """## Traps
- TR-RULEFILE: the go/no-go threshold is in site/rules.md (40%); tomorrow's 60% crosses it while today's 35% would not.

## Reference solution
1. read_file site/rules.md
2. get_weather {"location": "Hangzhou", "days": 3}
Final answer: Hold the pour: tomorrow's Hangzhou forecast is light rain with a 60% chance, above the 40% limit in site/rules.md; Friday (25%) looks workable.

## Why the answer is unique
The rule and the forecast together decide; temperature is not limiting.
""" + phrasings("Can we pour in Hangzhou tomorrow under our site rules?", "Is tomorrow OK for the concrete pour?", "Check tomorrow's weather against the pour rules.", "Should the crew pour tomorrow?", "杭州明天能浇混凝土吗？按我们的规定")
    return write_case(
        "hyb-9019", desc="Applies a local rain-chance rule to tomorrow's forecast to decide on a concrete pour",
        task_type="special_tool", family="fam-hyb-b12-pourrule-01", level="L1", ref_calls=2,
        traps=["TR-RULEFILE"], decoys={"TR-RULEFILE": "35%"}, axes=["CHN"],
        files=files, verify=verify, notes=notes, weather_fixture=fx,
        turns=[{"prompt": "Should the Hangzhou crew pour concrete tomorrow?",
                "expect": {"required_tools": ["get_weather"], "forbidden_tools": ["web_search", "web_fetch"],
                           "output_contains": ["60%"], "max_output_chars": 600}}])


def nt_9020():
    words = ["70%", "百分之七十", "七成"]
    verify = '''
import json
case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "降水概率 70%%" in prompt
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % json_list(words)
    notes = """## Traps
- TR-NOTOOLNEED: a definition question; get_weather is offered but no forecast is asked for.

## Reference solution
No tool call. Final answer: 降水概率 70% 指在预报的时段和区域里，出现可测量降水（一般≥0.1 毫米）的可能性是七成，不是 70% 的地方会下雨，也不代表下 70% 的时间；数字越高越该带伞。

## Why the answer is unique
Standard meteorological definition; no city or date is named.
"""
    return write_case(
        "nt-9020", desc="Weather concept question with the weather tool offered; answered without any call",
        task_type="concept", family="fam-nt-b12-popdefinition-01", level="L1", ref_calls=0,
        traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": "70% 的地区会下雨"}, axes=["DEC"],
        files={}, verify=verify, notes=notes,
        turns=[{"prompt": "天气预报里说的「降水概率 70%」到底是什么意思？",
                "expect": {"tools": [], "output_contains_any": words, "max_output_chars": 600}}])


def json_list(items):
    import json
    return json.dumps(items, ensure_ascii=False)


BUILDERS = [hyb_9017, hyb_9018, hyb_9019, nt_9020]
