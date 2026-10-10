"""b10e M5 script-fix cases scr-8001..8030: a small Python script with one clear bug; the model must repair it.

Judged by expect.run (the scorer runs the script on the final workspace plus hidden files and compares stdout).
Each case carries the buggy script, a minimal textual fix, data files and an independent oracle that is
checked here against the fixed script (and must differ from the buggy script's output).
"""
import os
import subprocess
import tempfile
from common import write_case

ENV = {"PATH": "/usr/bin:/bin:/usr/local/bin", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}


def run_script(script_name, script, data, hidden):
    with tempfile.TemporaryDirectory() as d:
        allf = dict(data)
        allf.update(hidden)
        allf[script_name] = script
        for p, c in allf.items():
            t = os.path.join(d, p)
            os.makedirs(os.path.dirname(t), exist_ok=True)
            with open(t, "w", encoding="utf-8", newline="") as f:
                f.write(c)
        r = subprocess.run(["python3", "-I", "-S", os.path.join(d, script_name)], cwd=d, env=dict(ENV, HOME=d),
                           capture_output=True, text=True, encoding="utf-8", timeout=10)
        return r.returncode, r.stdout.rstrip("\n"), r.stderr


VERIFY = '''
import json
import os
import subprocess
import tempfile

case = json.load(open("case.json"))
run = case["expect"]["run"]
FIXED = %r
files = dict(case["files"])
files.update(run.get("hidden_files", {}))
files[run["path"]] = FIXED
with tempfile.TemporaryDirectory() as d:
    for p, c in files.items():
        t = os.path.join(d, p)
        os.makedirs(os.path.dirname(t), exist_ok=True)
        with open(t, "w", encoding="utf-8", newline="") as f:
            f.write(c)
    r = subprocess.run(["python3", "-I", "-S", os.path.join(d, run["path"])], cwd=d, capture_output=True,
                       text=True, encoding="utf-8", timeout=10)
    if r.returncode != 0:
        raise SystemExit(r.stderr)
print(json.dumps({"expected_stdout": r.stdout.rstrip("\\n")}, ensure_ascii=False))
'''


def mk(n, slug, desc, prompt, name, buggy, fixes, data, oracle, bug, trap, ref, why, hidden=None, level="L0", calls=3):
    cid = "scr-%d" % (8000 + n)
    hidden = hidden or {}
    fixed = buggy
    for old, new in fixes:
        assert fixed.count(old) == 1, (cid, old)
        fixed = fixed.replace(old, new)
    allf = dict(data)
    allf.update(hidden)
    want = oracle(allf)
    rc, out, err = run_script(name, fixed, data, hidden)
    assert rc == 0 and out == want, (cid, "fixed", rc, out, want, err)
    rc, out, err = run_script(name, buggy, data, hidden)
    assert out != want, (cid, "buggy already correct")
    files = dict(data)
    files[name] = buggy
    exp_files = {p: {"unchanged": True} for p in data}
    run = {"path": name, "expected_stdout": want}
    if hidden:
        run["hidden_files"] = hidden
    notes = ("## Traps\n- %s\n\n## Reference solution\n%s\n\n## Why the answer is unique\n%s\n" % (trap, ref, why + "\nThe fixed script prints:\n" + want))
    write_case(
        cid, desc=desc, task_type="fix_output", family="fam-scr-b10e-%s-01" % slug, level="L0", ref_calls=calls,
        traps=[], axes=[], files=files,
        case_expect={"files": exp_files, "run": run},
        turns=[{"prompt": prompt, "expect": {"max_output_chars": 600}}],
        verify=VERIFY % fixed, notes=notes)


def csvt(rows):
    return "".join(",".join(r) + "\n" for r in rows)


def rows_of(text):
    return [l.split(",") for l in text.splitlines()[1:] if l]


# ------------------------------------------------------------ 1 subdir: canteen sales (zh)
def _o1(f):
    t = {}
    for p, c in f.items():
        if p.startswith("sales/") and p.endswith(".csv"):
            for d, q in rows_of(c):
                t[d] = t.get(d, 0) + int(q)
    return "\n".join("%s %d" % (k, t[k]) for k in sorted(t))


mk(1, "canteensales", "Fix a canteen sales tally that ignores month subfolders", 
   "食堂的 dish_tally.py 汇总出来的份数明显偏少，我怀疑是 sales 里分月存的那些文件没算进去。帮我修好，运行 python3 dish_tally.py 要把所有销售记录都统计上。",
   "dish_tally.py",
   '''import glob

totals = {}
for path in glob.glob("sales/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            dish, qty = line.strip().split(",")
            totals[dish] = totals.get(dish, 0) + int(qty)
for dish in sorted(totals):
    print(dish, totals[dish])
''',
   [('glob.glob("sales/*.csv")', 'glob.glob("sales/**/*.csv", recursive=True)')],
   {"sales/2026-09.csv": "dish,qty\n红烧肉,41\n麻婆豆腐,28\n红烧肉,19\n",
    "sales/2026-08/week4.csv": "dish,qty\n麻婆豆腐,35\n清蒸鱼,12\n",
    "sales/2026-08/week3.csv": "dish,qty\n红烧肉,22\n清蒸鱼,9\n",
    "README.md": "# 食堂销量\n\nsales/ 下每月一个文件，8 月以前的按周存在月份子文件夹里。\n"},
   _o1, "subdir", "glob only matches the top level of sales/, so the two August weekly files are skipped.",
   "1. Read dish_tally.py. 2. List sales/ (subfolder 2026-08). 3. replace_lines the glob line with a recursive glob. 4. Read back. Final: one sentence.",
   "Recursive glob picks up every csv under sales/ including nested month folders.",
   hidden={"sales/2026-07/week2.csv": "dish,qty\n清蒸鱼,6\n红烧肉,5\n"})

# ------------------------------------------------------------ 2 subdir: server logs error count (en)
def _o2(f):
    n = {}
    for p, c in f.items():
        if p.startswith("logs/") and p.endswith(".log"):
            for l in c.splitlines():
                if " ERROR " in l:
                    svc = l.split()[2]
                    n[svc] = n.get(svc, 0) + 1
    return "\n".join("%s: %d" % (k, n[k]) for k in sorted(n))


mk(2, "errcount", "Fix an error counter that does not descend into rotated log folders",
   "errcount.py reports far fewer ERROR lines than I see when grepping. I think it skips the rotated logs under logs/. Can you fix it so python3 errcount.py counts every .log file?",
   "errcount.py",
   '''import os
from collections import Counter

counts = Counter()
for name in os.listdir("logs"):
    path = os.path.join("logs", name)
    if not name.endswith(".log"):
        continue
    for line in open(path, encoding="utf-8"):
        parts = line.split()
        if len(parts) > 3 and parts[3] == "ERROR":
            counts[parts[2]] += 1
for svc in sorted(counts):
    print(f"{svc}: {counts[svc]}")
''',
   [('''for name in os.listdir("logs"):
    path = os.path.join("logs", name)
    if not name.endswith(".log"):
        continue
    for line in open(path, encoding="utf-8"):
        parts = line.split()
        if len(parts) > 3 and parts[3] == "ERROR":
            counts[parts[2]] += 1''',
     '''for root, _dirs, names in os.walk("logs"):
    for name in names:
        if not name.endswith(".log"):
            continue
        for line in open(os.path.join(root, name), encoding="utf-8"):
            parts = line.split()
            if len(parts) > 3 and parts[3] == "ERROR":
                counts[parts[2]] += 1''')],
   {"logs/app.log": "2026-09-30 10:01:02 api ERROR timeout\n2026-09-30 10:01:05 api INFO ok\n2026-09-30 10:02:00 billing ERROR card\n",
    "logs/rotated/app.1.log": "2026-09-29 23:50:00 api ERROR reset\n2026-09-29 23:51:00 api ERROR reset\n2026-09-29 23:55:00 worker ERROR oom\n",
    "logs/rotated/old/app.2.log": "2026-09-28 01:00:00 billing ERROR card\n",
    "README.md": "Service logs live in logs/; rotated files are moved into logs/rotated/.\n"},
   _o2, "subdir", "os.listdir is flat; rotated logs are in subfolders.",
   "Read errcount.py, list logs/, replace the loop with os.walk, read back.",
   "os.walk visits rotated/ and rotated/old/ as well as the top level.",
   hidden={"logs/rotated/app.0.log": "2026-09-29 12:00:00 worker ERROR oom\n"})

# ------------------------------------------------------------ 3 subdir: clinic visits per doctor (en)
def _o3(f):
    t = {}
    for p, c in f.items():
        if p.endswith(".txt") and p.startswith("visits/"):
            for l in c.splitlines():
                if l.strip():
                    d = l.split("|")[1].strip()
                    t[d] = t.get(d, 0) + 1
    return "\n".join("%s=%d" % (k, t[k]) for k in sorted(t))


mk(3, "clinicvisits", "Fix a clinic visit counter that misses per-clinic subfolders",
   "Our clinic_visits.py only counts the visit files sitting directly in visits/, but each satellite clinic has its own subfolder. Please fix it so python3 clinic_visits.py counts them all.",
   "clinic_visits.py",
   '''from pathlib import Path

counts = {}
for path in Path("visits").glob("*.txt"):
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        doctor = line.split("|")[1].strip()
        counts[doctor] = counts.get(doctor, 0) + 1
for doctor in sorted(counts):
    print(f"{doctor}={counts[doctor]}")
''',
   [('.glob("*.txt")', '.rglob("*.txt")')],
   {"visits/main.txt": "0901|Dr. Okafor|flu\n0901|Dr. Lindqvist|cast\n0902|Dr. Okafor|checkup\n",
    "visits/eastside/week1.txt": "0903|Dr. Lindqvist|cast\n0903|Dr. Reyes|sprain\n\n0904|Dr. Reyes|sprain\n",
    "visits/westside/week1.txt": "0905|Dr. Okafor|flu\n",
    "README.md": "One line per visit: date|doctor|reason.\n"},
   _o3, "subdir", "Path.glob('*.txt') is non-recursive.",
   "Read the script, list visits/, change glob to rglob, read back.",
   "rglob covers main.txt and every satellite folder.",
   hidden={"visits/southside/week2.txt": "0910|Dr. Reyes|sprain\n"})

# ------------------------------------------------------------ 4 subdir: photo storage size by event (zh)
def _o4(f):
    t = {}
    for p, c in f.items():
        if p.startswith("manifest/") and p.endswith(".tsv"):
            for l in c.splitlines()[1:]:
                a, b = l.split("\t")
                t[a] = t.get(a, 0) + int(b)
    return "\n".join("%s\t%d" % (k, t[k]) for k in sorted(t))


mk(4, "photomanifest", "Fix a photo manifest summary that skips nested manifest folders",
   "摄影社团的 size_sum.py 把各活动的照片总大小(KB)加起来，但 manifest 里按年份分了子文件夹，子文件夹里的清单好像没被加进去。麻烦修一下，让 python3 size_sum.py 的结果完整。",
   "size_sum.py",
   '''import os

totals = {}
for name in sorted(os.listdir("manifest")):
    path = os.path.join("manifest", name)
    if os.path.isdir(path):
        continue
    with open(path, encoding="utf-8") as f:
        for line in f.read().splitlines()[1:]:
            event, kb = line.split("\\t")
            totals[event] = totals.get(event, 0) + int(kb)
for event in sorted(totals):
    print(f"{event}\\t{totals[event]}")
''',
   [('''for name in sorted(os.listdir("manifest")):
    path = os.path.join("manifest", name)
    if os.path.isdir(path):
        continue
    with open(path, encoding="utf-8") as f:
        for line in f.read().splitlines()[1:]:
            event, kb = line.split("\\t")
            totals[event] = totals.get(event, 0) + int(kb)''',
     '''for root, _dirs, names in os.walk("manifest"):
    for name in sorted(names):
        with open(os.path.join(root, name), encoding="utf-8") as f:
            for line in f.read().splitlines()[1:]:
                event, kb = line.split("\\t")
                totals[event] = totals.get(event, 0) + int(kb)''')],
   {"manifest/2026.tsv": "event\tkb\n秋季外拍\t5200\n社团迎新\t3100\n",
    "manifest/2025/spring.tsv": "event\tkb\n春季外拍\t4800\n社团迎新\t2900\n",
    "manifest/2025/autumn.tsv": "event\tkb\n秋季外拍\t6100\n",
    "README.md": "清单为制表符分隔：活动、大小(KB)。往年的清单放在以年份命名的子文件夹里。\n"},
   _o4, "subdir", "isdir -> continue skips whole subfolders.",
   "Read script, list manifest/, switch to os.walk, read back.",
   "os.walk sums every manifest at any depth.",
   hidden={"manifest/2024/autumn.tsv": "event\tkb\n秋季外拍\t300\n"})

# ------------------------------------------------------------ 5 subdir: translation word counts (en)
def _o5(f):
    t = {}
    for p, c in f.items():
        if p.startswith("jobs/") and p.endswith("/words.csv"):
            lang = p.split("/")[1]
            for l in c.splitlines()[1:]:
                n = int(l.split(",")[1])
                t[lang] = t.get(lang, 0) + n
    return "\n".join("%s %d" % (k, t[k]) for k in sorted(t))


mk(5, "translatejobs", "Fix a translation word-count rollup that reads only one folder depth",
   "wordcount_rollup.py is supposed to total the words per target language from jobs/<lang>/ ..., but the totals only include the files at the top of each language folder. Some jobs are in dated subfolders. Fix it please.",
   "wordcount_rollup.py",
   '''import glob

totals = {}
for path in sorted(glob.glob("jobs/*/words.csv")):
    lang = path.split("/")[1]
    with open(path, encoding="utf-8") as f:
        for line in f.read().splitlines()[1:]:
            words = int(line.split(",")[1])
            totals[lang] = totals.get(lang, 0) + words
for lang in sorted(totals):
    print(lang, totals[lang])
''',
   [('glob.glob("jobs/*/words.csv")', 'glob.glob("jobs/*/**/words.csv", recursive=True)')],
   {"jobs/de/words.csv": "job,words\nJ-101,1200\nJ-102,800\n",
    "jobs/de/2026-09/words.csv": "job,words\nJ-140,950\n",
    "jobs/fr/2026-08/words.csv": "job,words\nJ-120,2000\n",
    "jobs/fr/2026-09/words.csv": "job,words\nJ-150,400\nJ-151,650\n",
    "README.md": "Each language has jobs/<lang>/; older batches sit in dated subfolders. Each folder holds a words.csv.\n"},
   _o5, "subdir", "Pattern jobs/*/words.csv requires the file to be directly in the language folder; fr has none there.",
   "Read script, list jobs/, adjust glob to recursive, read back. Note ** also matches zero dirs so jobs/de/words.csv still counted.",
   "Recursive pattern covers dated subfolders of each language.",
   hidden={"jobs/de/2026-10/words.csv": "job,words\nJ-160,100\n"})


def group_sum(f, prefix, suffix, key_i, val_i, skip=1, sep=","):
    t = {}
    for p, c in sorted(f.items()):
        if p.startswith(prefix) and p.endswith(suffix):
            for l in c.splitlines()[skip:]:
                if l.strip():
                    r = l.split(sep)
                    t[r[key_i]] = t.get(r[key_i], 0) + int(r[val_i])
    return t


# ------------------------------------------------------------ 6 unit: parcel weight g -> kg (zh)
def _o6(f):
    t = group_sum(f, "parcels/", ".csv", 0, 1)
    return "\n".join("%s %d.%02d kg" % (k, t[k] // 1000, t[k] % 1000 // 10) for k in sorted(t))


mk(6, "parcelweight", "Fix a parcel weight report that converts grams to kg with the wrong divisor",
   "驿站的 weight_report.py 打出来的各站点总重量(kg)大得离谱，数据里的重量是克。帮我把换算改对，运行 python3 weight_report.py 能给出正确的千克数。",
   "weight_report.py",
   '''import glob

totals = {}
for path in glob.glob("parcels/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            station, grams = line.strip().split(",")
            totals[station] = totals.get(station, 0) + int(grams)
for station in sorted(totals):
    print(f"{station} {totals[station] / 100:.2f} kg")
''',
   [('totals[station] / 100:.2f', 'totals[station] / 1000:.2f')],
   {"parcels/mon.csv": "station,grams\n东门站,1250\n南区站,3400\n东门站,780\n",
    "parcels/tue.csv": "station,grams\n南区站,2210\n北苑站,960\n东门站,4000\n",
    "README.md": "每行：站点、包裹重量（克）。\n"},
   _o6, "unit", "The divisor 100 should be 1000 (grams to kilograms).",
   "Read script, replace_lines the print line with / 1000, read back.",
   "Dividing by 1000 gives kg per station.",
   hidden={"parcels/wed.csv": "station,grams\n北苑站,540\n东门站,20\n"})


# ------------------------------------------------------------ 7 unit: miles -> km (en)
def _o7(f):
    t = group_sum(f, "trips/", ".csv", 0, 1)
    return "\n".join("%s %d km" % (k, t[k] * 1609344 // 1000000) for k in sorted(t))


mk(7, "fleetmiles", "Fix a fleet mileage report that converts miles to km with a wrong factor",
   "Our fleet_km.py prints each vehicle's total distance in km, but the totals look too small. The trip logs are in miles. Can you fix the conversion so python3 fleet_km.py is right?",
   "fleet_km.py",
   '''import glob

MILES_TO_KM = 1.06

totals = {}
for path in glob.glob("trips/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            van, miles = line.strip().split(",")
            totals[van] = totals.get(van, 0) + int(miles)
for van in sorted(totals):
    print(f"{van} {int(totals[van] * MILES_TO_KM)} km")
''',
   [('MILES_TO_KM = 1.06', 'MILES_TO_KM = 1.609344')],
   {"trips/week1.csv": "vehicle,miles\nvan-A,120\nvan-B,85\nvan-A,40\n",
    "trips/week2.csv": "vehicle,miles\nvan-B,200\nvan-C,60\nvan-A,15\n",
    "README.md": "Distances in the trip logs are in miles; the report must be in kilometres.\n"},
   _o7, "unit", "1.06 is not the miles to km factor; it is 1.609344.",
   "Read script, fix the constant, read back.",
   "Constant 1.609344, truncated to int km.",
   hidden={"trips/week3.csv": "vehicle,miles\nvan-C,75\nvan-A,5\n"})


# ------------------------------------------------------------ 8 unit: Fahrenheit -> Celsius (zh)
def _o8(f):
    t, n = {}, {}
    for p, c in sorted(f.items()):
        if p.startswith("sensors/") and p.endswith(".csv"):
            for l in c.splitlines()[1:]:
                r, v = l.split(",")
                t[r] = t.get(r, 0) + (int(v) - 32) * 5
                n[r] = n.get(r, 0) + 9
    return "\n".join("%s %.1f" % (k, t[k] / n[k]) for k in sorted(t))


mk(8, "coldroom", "Fix a cold-room temperature average whose Fahrenheit conversion has wrong precedence",
   "冷库的温度记录是华氏度，temp_avg.py 要按库房算平均摄氏度，现在算出来的数不对（冷冻库居然是正几十度）。帮我修好，python3 temp_avg.py 输出要对。",
   "temp_avg.py",
   '''import glob

sums = {}
counts = {}
for path in glob.glob("sensors/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            room, fahrenheit = line.strip().split(",")
            celsius = int(fahrenheit) - 32 * 5 / 9
            sums[room] = sums.get(room, 0) + celsius
            counts[room] = counts.get(room, 0) + 1
for room in sorted(sums):
    print(f"{room} {sums[room] / counts[room]:.1f}")
''',
   [('int(fahrenheit) - 32 * 5 / 9', '(int(fahrenheit) - 32) * 5 / 9')],
   {"sensors/am.csv": "room,f\n冷冻库,-4\n冷藏库,37\n冷冻库,-8\n冷藏库,39\n",
    "sensors/pm.csv": "room,f\n冷冻库,0\n冷藏库,41\n",
    "README.md": "每行：库房名、温度（华氏度）。\n"},
   _o8, "unit", "Missing parentheses: 32 * 5 / 9 is evaluated first.",
   "Read script, add parentheses around (f - 32), read back.",
   "Celsius = (F - 32) * 5 / 9, averaged per room.",
   hidden={"sensors/night.csv": "room,f\n冷冻库,-13\n冷藏库,35\n"})


# ------------------------------------------------------------ 9 unit: seconds -> hours (en)
def _o9(f):
    t = group_sum(f, "plays/", ".csv", 0, 1)
    return "\n".join("%s %.1f h" % (k, t[k] / 3600) for k in sorted(t))


mk(9, "podcasthours", "Fix a podcast listening report that converts seconds to hours with the wrong divisor",
   "podcast_hours.py is meant to print total listening hours per show, but a show with a few episodes already says 20+ hours. The play logs are in seconds. Please fix it.",
   "podcast_hours.py",
   '''import glob


def to_hours(seconds):
    return seconds / 360


totals = {}
for path in sorted(glob.glob("plays/*.csv")):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            show, seconds = line.strip().split(",")
            totals[show] = totals.get(show, 0) + int(seconds)
for show in sorted(totals):
    print(f"{show} {to_hours(totals[show]):.1f} h")
''',
   [('return seconds / 360\n', 'return seconds / 3600\n')],
   {"plays/jan.csv": "show,seconds\nNight Owls,5400\nCode Hour,3000\nNight Owls,7200\n",
    "plays/feb.csv": "show,seconds\nCode Hour,9000\nGardening Now,2700\nNight Owls,1800\n",
    "README.md": "plays: show name and seconds listened.\n"},
   _o9, "unit", "seconds / 360 should be / 3600.",
   "Read script, fix the divisor in to_hours, read back.",
   "Hours = seconds / 3600.",
   hidden={"plays/mar.csv": "show,seconds\nGardening Now,900\nCode Hour,1800\n"})


# ------------------------------------------------------------ 10 unit: fen -> yuan (zh)
def _o10(f):
    t = group_sum(f, "orders/", ".csv", 0, 1)
    return "\n".join("%s %d.%02d" % (k, t[k] // 100, t[k] % 100) for k in sorted(t))


mk(10, "shopfen", "Fix a shop revenue report whose cents-to-yuan conversion divides by 10",
   "网店的 shop_revenue.py 算各店铺营业额，订单文件里金额的单位是分，输出要的是元（保留两位）。现在店铺营业额大了十倍，帮我改对。",
   "shop_revenue.py",
   '''import glob

totals = {}
for path in glob.glob("orders/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            shop, cents = line.strip().split(",")
            totals[shop] = totals.get(shop, 0) + int(cents)
for shop in sorted(totals):
    print(f"{shop} {totals[shop] / 10:.2f}")
''',
   [('totals[shop] / 10:.2f', 'totals[shop] / 100:.2f')],
   {"orders/a.csv": "shop,fen\n旗舰店,12990\n书店,3550\n旗舰店,8800\n",
    "orders/b.csv": "shop,fen\n书店,2490\n旗舰店,1005\n",
    "README.md": "orders 每行：店铺、订单金额（分）。\n"},
   _o10, "unit", "Amounts are in fen (1/100 yuan); dividing by 10 is wrong.",
   "Read script, change 10 to 100, read back.",
   "Yuan = fen / 100 with two decimals.",
   hidden={"orders/c.csv": "shop,fen\n书店,1310\n"})


# ------------------------------------------------------------ 11 boundary: loyalty threshold (zh)
def _o11(f):
    names = []
    for p, c in sorted(f.items()):
        if p.startswith("members/") and p.endswith(".csv"):
            for l in c.splitlines()[1:]:
                n, pts = l.split(",")
                if int(pts) >= 100:
                    names.append(n)
    return "\n".join(sorted(names))


mk(11, "vipcutoff", "Fix a VIP list that excludes members sitting exactly at the point threshold",
   "咖啡店的 vip_list.py 要列出积分达到 100 分的会员（100 分当天就算），但刚好 100 分的人没出现。修一下，python3 vip_list.py 要把所有够格的人都列出来。",
   "vip_list.py",
   '''import glob

THRESHOLD = 100

vips = []
for path in glob.glob("members/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            name, points = line.strip().split(",")
            if int(points) > THRESHOLD:
                vips.append(name)
for name in sorted(vips):
    print(name)
''',
   [('int(points) > THRESHOLD', 'int(points) >= THRESHOLD')],
   {"members/east.csv": "name,points\n林夏,100\n周明,87\n赵晴,152\n",
    "members/west.csv": "name,points\n吴桐,99\n郑远,100\n孙悦,240\n",
    "README.md": "积分达到 100 分即为 VIP。\n"},
   _o11, "boundary", "Strict > excludes members with exactly 100 points.",
   "Read script, change > to >=, read back.",
   "Members with >= 100 points are listed in sorted order.",
   hidden={"members/south.csv": "name,points\n陈默,100\n"})


# ------------------------------------------------------------ 12 boundary: last 7 days slice (en)
def _o12(f):
    out = []
    for p, c in sorted(f.items()):
        if p.startswith("energy/") and p.endswith(".csv"):
            vals = [int(l.split(",")[1]) for l in c.splitlines()[1:]]
            out.append("%s %d" % (p.split("/")[1][:-4], sum(vals[-7:])))
    return "\n".join(out)


mk(12, "weeklykwh", "Fix a weekly energy total that sums only six days",
   "weekly_kwh.py should print the kWh used over the last 7 days for each meter, but the numbers seem to be one day short. Can you fix it so python3 weekly_kwh.py is right?",
   "weekly_kwh.py",
   '''import glob
import os

for path in sorted(glob.glob("energy/*.csv")):
    with open(path, encoding="utf-8") as f:
        rows = f.read().splitlines()[1:]
    values = [int(row.split(",")[1]) for row in rows]
    last_week = values[-6:]
    name = os.path.basename(path)[:-4]
    print(f"{name} {sum(last_week)}")
''',
   [('values[-6:]', 'values[-7:]')],
   {"energy/meter-a.csv": "day,kwh\n09-03,11\n09-04,15\n09-05,13\n09-06,16\n09-07,18\n09-08,17\n09-09,12\n",
    "energy/meter-b.csv": "day,kwh\n09-03,28\n09-04,31\n09-05,29\n09-06,33\n09-07,35\n09-08,27\n09-09,26\n",
    "README.md": "Rows are in date order, one row per day, oldest first.\n"},
   _o12, "boundary", "Slice [-6:] covers six days.",
   "Read script, change the slice to -7, read back.",
   "Last seven rows summed per meter.",
   hidden={"energy/meter-c.csv": "day,kwh\n09-01,5\n09-02,6\n09-03,7\n09-04,8\n09-05,9\n09-06,10\n09-07,11\n09-08,12\n"})


# ------------------------------------------------------------ 13 boundary: deadline inclusive (zh)
def _o13(f):
    t = {}
    for p, c in sorted(f.items()):
        if p.startswith("signup/") and p.endswith(".csv"):
            for l in c.splitlines()[1:]:
                course, day = l.split(",")
                if day <= "2026-10-15":
                    t[course] = t.get(course, 0) + 1
    return "\n".join("%s %d" % (k, t[k]) for k in sorted(t))


mk(13, "signupdeadline", "Fix a sign-up counter that drops registrations made on the deadline day",
   "社区课程的 signup_count.py 统计截止日(含 2026-10-15 当天)之前的报名人数，但 15 号当天报名的人都没算进去。帮我修好，python3 signup_count.py 输出每门课的有效报名数。",
   "signup_count.py",
   '''import glob

DEADLINE = "2026-10-15"

counts = {}
for path in glob.glob("signup/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            course, day = line.strip().split(",")
            if day < DEADLINE:
                counts[course] = counts.get(course, 0) + 1
for course in sorted(counts):
    print(f"{course} {counts[course]}")
''',
   [('if day < DEADLINE', 'if day <= DEADLINE')],
   {"signup/part1.csv": "course,date\n书法,2026-10-10\n陶艺,2026-10-15\n书法,2026-10-15\n",
    "signup/part2.csv": "course,date\n陶艺,2026-10-12\n书法,2026-10-16\n陶艺,2026-10-15\n",
    "README.md": "date 为 ISO 格式，字符串可直接比较；报名截止日当天仍然有效。\n"},
   _o13, "boundary", "Strict < loses same-day registrations.",
   "Read script, change < to <=, read back.",
   "Dates up to and including 2026-10-15 counted; 10-16 excluded.",
   hidden={"signup/part3.csv": "course,date\n陶艺,2026-10-15\n书法,2026-10-20\n"})


# ------------------------------------------------------------ 14 boundary: range excludes last shelf (en)
def _o14(f):
    tot = 0
    for p, c in f.items():
        if p.startswith("stock/shelf-"):
            tot += int(c.strip())
    return "total %d" % tot


mk(14, "shelfcount", "Fix a warehouse stock total whose loop stops one shelf early",
   "The warehouse has shelves 1 to 8, each with a count file in stock/. shelf_total.py is supposed to add them all up, but the total is missing the last shelf. Please fix it.",
   "shelf_total.py",
   '''SHELVES = 8

total = 0
for number in range(1, SHELVES):
    with open(f"stock/shelf-{number}.txt", encoding="utf-8") as f:
        total += int(f.read().strip())
print(f"total {total}")
''',
   [('range(1, SHELVES)', 'range(1, SHELVES + 1)')],
   {f"stock/shelf-{i}.txt": "%d\n" % v for i, v in enumerate([40, 25, 60, 18, 33, 71, 12, 54], 1)},
   _o14, "boundary", "range(1, 8) stops at shelf 7.",
   "Read script, change range end to SHELVES + 1, read back.",
   "All eight shelf files are summed.",
   hidden={})


# ------------------------------------------------------------ 15 boundary: top-3 slice (zh)
def _o15(f):
    rows = []
    for p, c in sorted(f.items()):
        if p.startswith("scores/") and p.endswith(".csv"):
            for l in c.splitlines()[1:]:
                n, s = l.split(",")
                rows.append((int(s), n))
    rows.sort(reverse=True)
    return "\n".join("%d. %s %d" % (i, n, s) for i, (s, n) in enumerate(rows[:3], 1))


mk(15, "quiztop3", "Fix a quiz leaderboard that prints only two of the top three",
   "知识竞赛的 top3.py 应该打印得分最高的前三名，可现在只出来两个人。帮我改一下，python3 top3.py 要列出前三名。",
   "top3.py",
   '''import glob

rows = []
for path in glob.glob("scores/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            name, score = line.strip().split(",")
            rows.append((int(score), name))
rows.sort(reverse=True)
for rank, (score, name) in enumerate(rows[:2], 1):
    print(f"{rank}. {name} {score}")
''',
   [('rows[:2]', 'rows[:3]')],
   {"scores/round1.csv": "name,score\n李强,91\n王芳,82\n张雨,77\n",
    "scores/round2.csv": "name,score\n刘洋,88\n陈静,95\n",
    "README.md": "每个选手只出现一次，分数不并列。\n"},
   _o15, "boundary", "Slice [:2] keeps two entries.",
   "Read script, change slice to 3, read back.",
   "Top three scores are printed.",
   hidden={"scores/round3.csv": "name,score\n赵磊,93\n"})


# ------------------------------------------------------------ 16 encoding: BOM csv DictReader (zh)
def _o16(f):
    t = {}
    for p, c in sorted(f.items()):
        if p.startswith("timesheet/") and p.endswith(".csv"):
            for l in c.lstrip("﻿").splitlines()[1:]:
                r = l.split(",")
                t[r[0]] = t.get(r[0], 0) + int(r[2])
    return "\n".join("%s %d 小时" % (k, t[k]) for k in sorted(t))


mk(16, "timesheetbom", "Fix a timesheet report that crashes on CSV files exported with a BOM",
   "设计院的 hours_report.py 按人汇总工时，上周开始一跑就报 KeyError，应该是 HR 换了导出方式。帮我修好，让 python3 hours_report.py 能正常汇总。",
   "hours_report.py",
   '''import csv
import glob

totals = {}
for path in glob.glob("timesheet/*.csv"):
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            dept = row["姓名"]
            totals[dept] = totals.get(dept, 0) + int(row["工时"])
for dept in sorted(totals):
    print(f"{dept} {totals[dept]} 小时")
''',
   [('with open(path, encoding="utf-8", newline="")', 'with open(path, encoding="utf-8-sig", newline="")')],
   {"timesheet/2026-09.csv": "﻿姓名,部门,工时\n钱程,结构,152\n孙敏,建筑,160\n李想,结构,148\n",
    "timesheet/2026-10.csv": "﻿姓名,部门,工时\n钱程,结构,40\n周岚,给排水,96\n",
    "README.md": "工时表由 HR 系统导出，列：姓名、部门、工时。\n"},
   _o16, "encoding", "A UTF-8 BOM is glued to the first header, so the key is '\\ufeff姓名' and row['姓名'] raises KeyError.",
   "Read script, change encoding to utf-8-sig, read back.",
   "utf-8-sig strips the BOM.",
   hidden={})


# ------------------------------------------------------------ 17 encoding: CRLF status column (en)
def _o17(f):
    t = {}
    for p, c in sorted(f.items()):
        if p.startswith("deliveries/") and p.endswith(".csv"):
            for l in c.splitlines()[1:]:
                region, status = l.split(",")
                if status == "OK":
                    t[region] = t.get(region, 0) + 1
    return "\n".join("%s %d" % (k, t[k]) for k in sorted(t))


mk(17, "crlfstatus", "Fix a delivery counter that matches nothing because the exports use CRLF line endings",
   "delivered_count.py should count the OK deliveries per region, but it now prints nothing at all. The export tool was switched to a Windows one last week. Can you get python3 delivered_count.py working again?",
   "delivered_count.py",
   '''import glob

counts = {}
for path in glob.glob("deliveries/*.csv"):
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().split("\\n")[1:]
    for line in lines:
        if not line:
            continue
        region, status = line.split(",")
        if status == "OK":
            counts[region] = counts.get(region, 0) + 1
for region in sorted(counts):
    print(f"{region} {counts[region]}")
''',
   [('f.read().split("\\n")[1:]', 'f.read().splitlines()[1:]')],
   {"deliveries/mon.csv": "region,status\r\nnorth,OK\r\nsouth,LATE\r\nnorth,OK\r\neast,OK\r\n",
    "deliveries/tue.csv": "region,status\r\nsouth,OK\r\neast,FAILED\r\nnorth,LATE\r\nsouth,OK\r\n",
    "README.md": "Columns: region, status (OK / LATE / FAILED). Files come from the Windows export tool.\n"},
   _o17, "encoding", "CRLF leaves '\\r' on the status, so status == 'OK' never matches.",
   "Read script, switch to splitlines() (or strip), read back.",
   "Lines are split correctly regardless of CRLF.",
   hidden={"deliveries/wed.csv": "region,status\r\neast,OK\r\nnorth,OK\r\n"})


# ------------------------------------------------------------ 18 encoding: BOM json (zh)
def _o18(f):
    import json as j
    t = {}
    for p, c in sorted(f.items()):
        if p.startswith("stores/") and p.endswith(".json"):
            d = j.loads(c.lstrip("﻿"))
            for k, v in d["库存"].items():
                t[k] = t.get(k, 0) + v
    return "\n".join("%s %d" % (k, t[k]) for k in sorted(t))


mk(18, "stockjson", "Fix a stock merger that fails on JSON files saved with a BOM",
   "仓库的 stock_merge.py 把各门店 json 里的库存按品名合并。其中一家门店用记事本改过文件，现在一跑就报 JSON 解析错误。帮我修好，python3 stock_merge.py 要能合并所有门店。",
   "stock_merge.py",
   '''import glob
import json

merged = {}
for path in glob.glob("stores/*.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for item, qty in data["库存"].items():
        merged[item] = merged.get(item, 0) + qty
for item in sorted(merged):
    print(f"{item} {merged[item]}")
''',
   [('with open(path, encoding="utf-8") as f:', 'with open(path, encoding="utf-8-sig") as f:')],
   {"stores/a.json": '{"门店": "A", "库存": {"毛巾": 30, "牙刷": 120}}\n',
    "stores/b.json": '﻿{"门店": "B", "库存": {"毛巾": 12, "拖鞋": 45}}\n',
    "README.md": "每个门店一个 json，库存是 品名 -> 数量。\n"},
   _o18, "encoding", "json.load rejects a UTF-8 BOM when the file is opened as plain utf-8.",
   "Read script, open with utf-8-sig, read back.",
   "BOM is tolerated; all stores are merged.",
   hidden={"stores/c.json": '﻿{"门店": "C", "库存": {"拖鞋": 5, "牙刷": 10}}\n'})


# ------------------------------------------------------------ 19 encoding: BOM TSV header (en)
def _o19(f):
    t = {}
    for p, c in sorted(f.items()):
        if p.startswith("scans/") and p.endswith(".tsv"):
            for l in c.lstrip("﻿").splitlines()[1:]:
                sku, q = l.split("\t")
                t[sku] = t.get(sku, 0) + int(q)
    return "\n".join("%s\t%d" % (k, t[k]) for k in sorted(t))


mk(19, "skuscan", "Fix a SKU scan tally that dies on a TSV exported with a BOM",
   "sku_tally.py adds up scanned quantities per SKU from the TSV files in scans/. It started failing with a KeyError after the handheld scanners got a firmware update. Could you fix it? python3 sku_tally.py should print every SKU again.",
   "sku_tally.py",
   '''import csv
import glob

totals = {}
for path in glob.glob("scans/*.tsv"):
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\\t"):
            totals[row["sku"]] = totals.get(row["sku"], 0) + int(row["qty"])
for sku in sorted(totals):
    print(f"{sku}\\t{totals[sku]}")
''',
   [('with open(path, encoding="utf-8", newline="")', 'with open(path, encoding="utf-8-sig", newline="")')],
   {"scans/dock1.tsv": "﻿sku\tqty\nA-100\t24\nB-220\t6\nA-100\t10\n",
    "scans/dock2.tsv": "﻿sku\tqty\nB-220\t14\nC-310\t3\n",
    "README.md": "Scanner export: sku and qty, tab separated.\n"},
   _o19, "encoding", "BOM glued to the first header makes row['sku'] a KeyError.",
   "Read script, change encoding to utf-8-sig, read back.",
   "utf-8-sig strips the BOM from the first header.",
   hidden={"scans/dock3.tsv": "﻿sku\tqty\nC-310\t7\n"})


# ------------------------------------------------------------ 20 encoding: CRLF whitelist (zh)
def _o20(f):
    allow = set(f["config/allow.txt"].splitlines())
    t = {}
    for p, c in sorted(f.items()):
        if p.startswith("events/") and p.endswith(".log"):
            for l in c.splitlines():
                u = l.split()[1]
                if u in allow:
                    t[u] = t.get(u, 0) + 1
    return "\n".join("%s %d" % (k, t[k]) for k in sorted(t))


mk(20, "allowlist", "Fix an access-event counter whose allow-list from a Windows editor never matches",
   "门禁的 allowed_events.py 只统计白名单里的人的刷卡次数，可白名单是行政用 Windows 记事本编辑的，现在输出一行都没有。帮我修好，python3 allowed_events.py 要打印每个白名单成员的次数。",
   "allowed_events.py",
   '''import glob

with open("config/allow.txt", encoding="utf-8", newline="") as f:
    allowed = set(f.read().split("\\n"))

counts = {}
for path in glob.glob("events/*.log"):
    with open(path, encoding="utf-8") as f:
        for line in f:
            user = line.split()[1]
            if user in allowed:
                counts[user] = counts.get(user, 0) + 1
for user in sorted(counts):
    print(f"{user} {counts[user]}")
''',
   [('set(f.read().split("\\n"))', 'set(f.read().splitlines())')],
   {"config/allow.txt": "zhangsan\r\nlisi\r\nwangwu\r\n",
    "events/0930.log": "08:01 zhangsan in\n08:05 guest01 in\n08:30 lisi in\n17:55 zhangsan out\n",
    "events/1001.log": "08:10 wangwu in\n08:12 zhangsan in\n09:00 guest02 in\n",
    "README.md": "每行：时间、卡号对应的用户名、动作。config/allow.txt 一行一个用户名。\n"},
   _o20, "encoding", "CRLF leaves '\\r' on each allow-list name, so no event matches.",
   "Read script, switch to splitlines(), read back.",
   "Names in the allow-list are matched properly.",
   hidden={"events/1002.log": "08:00 lisi in\n08:01 guest03 in\n"})


def read_rows(f, prefix, suffix, sep=","):
    rows = []
    for p, c in sorted(f.items()):
        if p.startswith(prefix) and p.endswith(suffix):
            for l in c.splitlines()[1:]:
                if l.strip():
                    rows.append(l.split(sep))
    return rows


# ------------------------------------------------------------ 21 sort: numeric strings (en)
def _o21(f):
    rows = read_rows(f, "invoices/", ".csv")
    rows.sort(key=lambda r: -int(r[1]))
    return "\n".join("%s %s" % (r[0], r[1]) for r in rows[:5])


mk(21, "bigbills", "Fix a largest-invoices list that sorts amounts as text",
   "top_invoices.py is supposed to list the five largest invoices, but the order is clearly off (a 900 is shown above a 12000). Please fix the sorting so python3 top_invoices.py is right.",
   "top_invoices.py",
   '''import glob

rows = []
for path in glob.glob("invoices/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            number, amount = line.strip().split(",")
            rows.append((number, amount))
rows.sort(key=lambda row: row[1], reverse=True)
for number, amount in rows[:5]:
    print(number, amount)
''',
   [('key=lambda row: row[1], reverse=True', 'key=lambda row: int(row[1]), reverse=True')],
   {"invoices/q1.csv": "number,amount\nINV-102,12000\nINV-101,900\nINV-103,450\nINV-104,7800\n",
    "invoices/q2.csv": "number,amount\nINV-201,3100\nINV-202,95000\nINV-203,640\n",
    "README.md": "Amounts are whole euros.\n"},
   _o21, "sort", "Amounts are strings, so '900' sorts above '12000'.",
   "Read script, convert key to int, read back.",
   "Numeric descending order, five rows.",
   hidden={"invoices/q3.csv": "number,amount\nINV-301,25000\nINV-302,80\n"})


# ------------------------------------------------------------ 22 sort: wrong column (zh)
def _o22(f):
    rows = read_rows(f, "loans/", ".csv")
    rows.sort(key=lambda r: r[2])
    return "\n".join("%s %s %s" % (r[2], r[0], r[1]) for r in rows)


mk(22, "libduedate", "Fix an overdue-books list sorted by title instead of due date",
   "图书馆的 due_list.py 应该按应还日期从早到晚列出借出的书，可现在是按书名在排。帮我修好，python3 due_list.py 输出顺序要对。",
   "due_list.py",
   '''import glob

rows = []
for path in glob.glob("loans/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            rows.append(line.strip().split(","))
rows.sort(key=lambda row: row[1])
for title, reader, due in rows:
    print(due, title, reader)
''',
   [('key=lambda row: row[1]', 'key=lambda row: row[2]')],
   {"loans/east.csv": "书名,读者,应还日期\n平凡的世界,赵一,2026-10-20\n活着,钱二,2026-10-08\n",
    "loans/west.csv": "书名,读者,应还日期\n三体,孙三,2026-10-12\n围城,李四,2026-10-25\n",
    "README.md": "应还日期为 ISO 格式 YYYY-MM-DD。\n"},
   _o22, "sort", "Sort key is the reader column rather than the due date.",
   "Read script, change key index to 2, read back.",
   "Sorted ascending by ISO due date.",
   hidden={"loans/south.csv": "书名,读者,应还日期\n红楼梦,周五,2026-10-10\n"})


# ------------------------------------------------------------ 23 sort: dd.mm.yyyy dates as text (en)
def _o23(f):
    rows = read_rows(f, "bookings/", ".csv")
    rows.sort(key=lambda r: tuple(int(x) for x in reversed(r[0].split("."))))
    return "\n".join("%s %s" % (r[0], r[1]) for r in rows)


mk(23, "ddmmsort", "Fix a booking list that sorts dd.mm.yyyy dates alphabetically",
   "booking_order.py should print the bookings in chronological order, but dates from different months are interleaved wrongly. The dates are written day.month.year. Can you fix it so python3 booking_order.py is correctly ordered?",
   "booking_order.py",
   '''import glob

rows = []
for path in glob.glob("bookings/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            rows.append(line.strip().split(","))
rows.sort(key=lambda row: row[0])
for date, guest in rows:
    print(date, guest)
''',
   [('key=lambda row: row[0]', 'key=lambda row: tuple(int(x) for x in reversed(row[0].split(".")))')],
   {"bookings/a.csv": "date,guest\n12.11.2026,Novak\n03.12.2026,Berg\n25.10.2026,Costa\n",
    "bookings/b.csv": "date,guest\n02.11.2026,Aydin\n18.12.2026,Moreau\n09.10.2026,Lund\n",
    "README.md": "Dates are day.month.year.\n"},
   _o23, "sort", "Alphabetical order of dd.mm.yyyy is not chronological.",
   "Read script, build a (year, month, day) key, read back.",
   "Chronological ascending order.",
   hidden={"bookings/c.csv": "date,guest\n01.01.2027,Weber\n30.09.2026,Silva\n"})


# ------------------------------------------------------------ 24 sort: tie-break direction (zh)
def _o24(f):
    rows = read_rows(f, "sales/", ".csv")
    rows.sort(key=lambda r: (-int(r[1]), r[0]))
    return "\n".join("%s %s" % (r[0], r[1]) for r in rows)


mk(24, "milkteaboard", "Fix a sales ranking that puts tied items in reverse name order",
   "奶茶店的 rank.py 按销量从高到低排名，销量相同的要按名称拼音/字典序从小到大排。现在并列的店品排反了。帮我修好，python3 rank.py 输出要对。",
   "rank.py",
   '''import glob

rows = []
for path in glob.glob("sales/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            name, cups = line.strip().split(",")
            rows.append((name, int(cups)))
rows.sort(key=lambda row: (row[1], row[0]), reverse=True)
for name, cups in rows:
    print(name, cups)
''',
   [('key=lambda row: (row[1], row[0]), reverse=True', 'key=lambda row: (-row[1], row[0])')],
   {"sales/a.csv": "name,cups\nberry,120\nmatcha,95\nmango,120\n",
    "sales/b.csv": "name,cups\njasmine,95\noolong,60\ncocoa,95\n",
    "README.md": "同销量按名称字典序从小到大。\n"},
   _o24, "sort", "reverse=True reverses the name tie-break as well.",
   "Read script, use key (-cups, name), read back.",
   "Descending by cups, ascending by name on ties.",
   hidden={"sales/c.csv": "name,cups\napple,120\nzesty,60\n"})


# ------------------------------------------------------------ 25 sort: version strings (en)
def _o25(f):
    vs = [l.strip() for l in f["releases.txt"].splitlines() if l.strip()]
    vs.sort(key=lambda v: tuple(int(x) for x in v.split(".")), reverse=True)
    return "\n".join(vs[:3])


mk(25, "latestversions", "Fix a latest-versions list that sorts version strings as text",
   "latest_versions.py should print the three newest releases from releases.txt, but it thinks 1.9.0 is newer than 1.10.0. Please fix the ordering so python3 latest_versions.py is right.",
   "latest_versions.py",
   '''with open("releases.txt", encoding="utf-8") as f:
    versions = [line.strip() for line in f if line.strip()]
versions.sort(reverse=True)
for version in versions[:3]:
    print(version)
''',
   [('versions.sort(reverse=True)', 'versions.sort(key=lambda v: tuple(int(p) for p in v.split(".")), reverse=True)')],
   {"releases.txt": "1.10.0\n1.8.2\n1.9.0\n1.9.1\n1.2.15\n1.10.1\n0.9.9\n",
    "README.md": "releases.txt lists released versions, one per line, in no particular order.\n"},
   _o25, "sort", "String comparison puts 1.9.x above 1.10.x.",
   "Read script, sort by tuple of ints, read back.",
   "Newest three: 1.10.1, 1.10.0, 1.9.1.",
   hidden={"extra.txt": "unused\n"})


# ------------------------------------------------------------ 26 sort: case-insensitive names (en)
def _o26(f):
    names = [r[0] for r in read_rows(f, "contacts/", ".csv")]
    names.sort(key=lambda s: s.lower())
    return "\n".join(names)


mk(26, "contactsorder", "Fix a contact list whose sort puts lowercase names after all capitals",
   "phone_book.py prints the contacts alphabetically, but names starting with lowercase letters (like 'de Vries') all end up at the bottom. Can you make python3 phone_book.py sort properly, ignoring case?",
   "phone_book.py",
   '''import glob

names = []
for path in glob.glob("contacts/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            names.append(line.strip().split(",")[0])
for name in sorted(names):
    print(name)
''',
   [('sorted(names)', 'sorted(names, key=str.lower)')],
   {"contacts/work.csv": "name,phone\nAbbott,555-0101\nde Vries,555-0102\nZhang,555-0103\n",
    "contacts/home.csv": "name,phone\nbrown,555-0201\nCarter,555-0202\nvan Dyke,555-0203\n",
    "README.md": "contacts: name, phone.\n"},
   _o26, "sort", "Default sort is by code point: capitals before lowercase.",
   "Read script, add key=str.lower, read back.",
   "Case-insensitive alphabetical order.",
   hidden={"contacts/club.csv": "name,phone\nEvans,555-0301\naldous,555-0302\n"})


# ------------------------------------------------------------ 27 unit: ms -> s (zh)
def _o27(f):
    t, n = {}, {}
    for r in read_rows(f, "latency/", ".csv"):
        t[r[0]] = t.get(r[0], 0) + int(r[1])
        n[r[0]] = n.get(r[0], 0) + 1
    return "\n".join("%s %.2f 秒" % (k, t[k] / n[k] / 1000) for k in sorted(t))


mk(27, "apilatency", "Fix an API latency report that multiplies milliseconds instead of dividing",
   "接口监控的 latency_report.py 要给出每个接口的平均耗时(秒，两位小数)，日志里的耗时是毫秒。现在平均值大得不对，帮我把换算改对。",
   "latency_report.py",
   '''import glob

sums = {}
counts = {}
for path in glob.glob("latency/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        for line in f:
            api, ms = line.strip().split(",")
            sums[api] = sums.get(api, 0) + int(ms)
            counts[api] = counts.get(api, 0) + 1
for api in sorted(sums):
    avg_seconds = sums[api] / counts[api] * 1000
    print(f"{api} {avg_seconds:.2f} 秒")
''',
   [('sums[api] / counts[api] * 1000', 'sums[api] / counts[api] / 1000')],
   {"latency/a.csv": "api,ms\n/login,320\n/search,1250\n/login,280\n",
    "latency/b.csv": "api,ms\n/search,1750\n/pay,860\n/pay,940\n",
    "README.md": "每行：接口、耗时（毫秒）。\n"},
   _o27, "unit", "Milliseconds multiplied by 1000 instead of divided.",
   "Read script, change * to /, read back.",
   "avg ms / 1000 = seconds.",
   hidden={"latency/c.csv": "api,ms\n/login,300\n"})


# ------------------------------------------------------------ 28 boundary: page slice (en)
def _o28(f):
    items = f["catalog.txt"].splitlines()
    return "\n".join(items[10:20])


mk(28, "catalogpage", "Fix a catalogue pager that prints the wrong page",
   "page.py is supposed to print page 2 of catalog.txt (10 items per page, pages start at 1), but it shows what looks like page 3. Please fix it.",
   "page.py",
   '''PAGE = 2
PAGE_SIZE = 10

with open("catalog.txt", encoding="utf-8") as f:
    items = f.read().splitlines()
start = PAGE * PAGE_SIZE
for item in items[start:start + PAGE_SIZE]:
    print(item)
''',
   [('start = PAGE * PAGE_SIZE', 'start = (PAGE - 1) * PAGE_SIZE')],
   {"catalog.txt": "".join("item-%02d %s\n" % (i, w) for i, w in enumerate(
        "lamp desk chair shelf rug clock mirror vase frame stool bench table sofa tray basket rack hook cart bin jar mug plate bowl fork spoon kettle pan pot".split(), 1)),
    "README.md": "catalog.txt: one item per line, pages are numbered from 1.\n"},
   _o28, "boundary", "Page numbering starts at 1 but the offset treats it as 0-based.",
   "Read script, use (PAGE - 1) * PAGE_SIZE, read back.",
   "Items 11-20 printed.",
   hidden={})


# ------------------------------------------------------------ 29 subdir: unfinished todos (zh)
def _o29(f):
    n = 0
    for p, c in f.items():
        if p.startswith("notes/") and p.endswith(".md"):
            n += sum(1 for l in c.splitlines() if l.startswith("- [ ]"))
    return "未完成 %d 项" % n


mk(29, "todonotes", "Fix a to-do counter that ignores project subfolders of notes",
   "我的 todo_count.py 统计 notes 里没勾掉的待办（以 - [ ] 开头的行），但各项目的笔记在子文件夹里，数出来明显偏少。帮我修好，python3 todo_count.py 要算上所有笔记。",
   "todo_count.py",
   '''import glob

open_items = 0
for path in glob.glob("notes/*.md"):
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("- [ ]"):
                open_items += 1
print(f"未完成 {open_items} 项")
''',
   [('glob.glob("notes/*.md")', 'glob.glob("notes/**/*.md", recursive=True)')],
   {"notes/inbox.md": "# 收件箱\n- [ ] 交电费\n- [x] 预约体检\n- [ ] 回邮件\n",
    "notes/reno/plan.md": "# 装修\n- [ ] 选瓷砖\n- [ ] 约水电\n- [x] 量尺寸\n",
    "notes/trip/list.md": "- [x] 订机票\n- [ ] 办签证\n",
    "notes/README.md": "- [ ] 把旧笔记整理进各自的项目文件夹（- [x] 表示已完成）\n"},
   _o29, "subdir", "glob('notes/*.md') is not recursive.",
   "Read script, make the glob recursive, read back.",
   "All open items under notes/ at any depth are counted.",
   hidden={"notes/trip/day2/extra.md": "- [ ] 订酒店\n"})


# ------------------------------------------------------------ 30 boundary: skips two lines (en)
def _o30(f):
    t = {}
    for r in read_rows(f, "tickets/", ".csv"):
        t[r[0]] = t.get(r[0], 0) + 1
    return "\n".join("%s %d" % (k, t[k]) for k in sorted(t))


mk(30, "ticketqueue", "Fix a ticket counter that drops the first data row of every file",
   "ticket_counts.py counts support tickets per queue, but every queue is short by one or two compared with the raw files. I think it's eating a row somewhere. Fix it so python3 ticket_counts.py is accurate.",
   "ticket_counts.py",
   '''import glob

counts = {}
for path in glob.glob("tickets/*.csv"):
    with open(path, encoding="utf-8") as f:
        next(f)
        next(f)
        for line in f:
            queue = line.strip().split(",")[0]
            counts[queue] = counts.get(queue, 0) + 1
for queue in sorted(counts):
    print(f"{queue} {counts[queue]}")
''',
   [('        next(f)\n        next(f)\n', '        next(f)\n')],
   {"tickets/oct1.csv": "queue,id\nbilling,T-1\nbilling,T-2\naccess,T-3\nbilling,T-4\n",
    "tickets/oct2.csv": "queue,id\naccess,T-5\naccess,T-6\nhardware,T-7\n",
    "README.md": "Each file has one header line followed by one ticket per row.\n"},
   _o30, "boundary", "A second next(f) skips the first ticket row.",
   "Read script, remove the extra next(f), read back.",
   "Every ticket row is counted.",
   hidden={"tickets/oct3.csv": "queue,id\nhardware,T-8\n"})
