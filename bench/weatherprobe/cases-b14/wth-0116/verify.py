# WEATHERPROBE-CANARY-3b9e51a2 : weatherprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f624040e5cbb0b95118ccdc1763101d45288ce3a2bfa2274038de25d0b614947', "fixture changed"
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

fx = case["weather_fixture"][0]
assert fx["location"] == '桂林'
days = fx["report"]["daily"]
assert [d["date"] for d in days][:5] == ["2026-09-16", "2026-09-17", "2026-09-18", "2026-09-19", "2026-09-20"]
text = case["files"]['站点/桂林.html']
print(json.dumps({"files": {'站点/桂林.html': apply('html', '桂林', text, days, [1, 2], '  </ul>\n')}}, ensure_ascii=False))
