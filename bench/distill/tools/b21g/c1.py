"""b21g sub C (part 1): traversals over directories too big for one listing, 32223-32230 (filesystem)."""
import json
import re
from random import Random

from common import L, emit, reg


@reg
def c1(i):
    rng = Random(3222300 + i * 7919)
    files = {}
    for d in range(1, 13):
        for k in range(rng.randint(9, 16)):
            ext = rng.choices([".png", ".jpg", ".png.bak", ".webp", ".txt"], [6, 6, 2, 3, 1])[0]
            files["photos/2026-%02d/IMG_%04d%s" % (d, rng.randint(1000, 9999) + k * 10000, ext)] = "placeholder %d\n" % rng.randint(1, 9)
    files["photos/README.txt"] = "Exported from the phone gallery. .bak files are leftovers from a failed sync.\n"

    def solve(files):
        n = [p for p in files if p.endswith(".png")]
        b = [p for p in files if ".png" in p]
        return {"turns": [{"number": len(n), "items": []}], "decoys": {"TR-DECOY": len(b), "TR-TRUNC": 50}}
    emit("fs-32223", sub="multifile", task_type="count_by_type", desc="Counts .png photos across twelve monthly folders where .png.bak leftovers share the stem",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "photos 文件夹下按月份分了十二个子目录。一共有多少张 .png 图片？.png.bak 是同步失败留下的垃圾，不算。"}],
         ref=(["find photos -type f -name '*.png' | wc -l"], 0),
         notes_traps=["TR-DECOY: .png.bak names contain .png.", "TR-TRUNC: the tree has well over 100 files, one directory listing returns only 50."],
         notes_ref=["find photos -type f -name '*.png' | wc -l."], unique="Names ending exactly in .png.")


@reg
def c2(i):
    rng = Random(3222400 + i * 7919)
    files = {}
    dirs = ["inbox", "reports/q1", "reports/q2", "reports/q3", "scans", "contracts", "misc", "tmp"]
    w = [rng.randint(3, 40) for _ in dirs]
    for d, k in zip(dirs, w):
        for j in range(k):
            ext = rng.choice([".pdf", ".log", ".txt", ".pdf"])
            files["archive/%s/doc-%03d%s" % (d, j, ext)] = "x%d\n" % j
    def solve(files):
        c = {}
        for p in files:
            d = p.rsplit("/", 1)[0]
            c[d] = c.get(d, 0) + 1
        r = sorted(c.items(), key=lambda kv: -kv[1])
        assert r[0][1] > r[1][1]
        pdf = len([p for p in files if p.startswith(r[0][0] + "/") and p.endswith(".pdf")])
        logs = len([p for p in files if p.startswith(r[0][0] + "/") and p.endswith(".log")])
        assert pdf != r[0][1]
        return {"turns": [{"number": r[0][1], "items": [r[0][0]]}, {"number": pdf, "items": []}], "decoys": {"TR-TRUNC": 50, "TR-DECOY": r[1][1]}}
    emit("fs-32224", sub="multifile", task_type="count_by_type", desc="Finds the archive directory holding the most files, then how many of them are pdf",
         files=files, solve=solve, traps=["TR-TRUNC", "TR-DECOY"],
         turns=[{"prompt": "Under archive/, which single directory directly contains the most files, and how many files is that?"},
                {"prompt": "How many of the files in that directory are PDFs?"}],
         ref=(["find archive -type f -name '*.pdf' | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -3"], 0),
         notes_traps=["TR-TRUNC: over 150 files so a listing is cut at 50.", "TR-DECOY: the second-biggest directory is close behind."],
         notes_ref=["find archive -type f | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head.", "Then count .pdf in that directory."], unique="Direct children only; unique winner.")


@reg
def c3(i):
    rng = Random(3222500 + i * 7919)
    files = {}
    sizes = rng.sample(range(300, 9000), 90)
    for k, s in enumerate(sizes):
        name = "downloads/%s/%s-%02d.%s" % (rng.choice(["work", "personal", "misc"]), rng.choice(["report", "photo", "notes", "invoice", "draft"]), k, rng.choice(["pdf", "txt", "csv"]))
        files[name] = ("a" * (s - 1)) + "\n"
    def solve(files):
        r = sorted(files.items(), key=lambda kv: -len(kv[1].encode()))[:5]
        return {"turns": [{"number": len(r[0][1].encode()), "items": [p.rsplit("/", 1)[1] for p, _ in r]}], "decoys": {"TR-TRUNC": len(r[1][1].encode())}}
    emit("fs-32225", sub="multifile", task_type="largest", desc="Lists the five biggest files by byte size in a downloads tree with ninety files",
         files=files, solve=solve, traps=["TR-TRUNC"],
         turns=[{"prompt": "downloads 目录里文件很多，分在 work、personal、misc 三个子目录下。体积最大的 5 个文件是哪几个？告诉我文件名，以及最大的那个有多少字节。"}],
         ref=(["find downloads -type f -exec wc -c {} + | grep -v ' total$' | sort -rn | head -5"], 0),
         notes_traps=["TR-TRUNC: 90 files, one listing returns 50 and has no sizes anyway."], notes_ref=["find -exec wc -c {} + | sort -rn | head -5."], unique="All sizes distinct.")


@reg
def c4(i):
    rng = Random(3222600 + i * 7919)
    files = {}
    for k in range(rng.randint(110, 150)):
        body = ["# export %d" % k] + ["row %d status=%s" % (j, rng.choice(["ok", "retry", "ok"])) for j in range(rng.randint(8, 30))]
        files["exports/batch-%03d.txt" % k] = L(*body)
    tgt = "exports/batch-%03d.txt" % rng.randint(10, 100)
    lines = files[tgt].splitlines()
    ln = rng.randint(3, len(lines) - 1)
    lines[ln - 1] = "row %d status=error ref=ORDER-7731" % (ln - 1)
    files[tgt] = L(*lines)
    files["exports/batch-099.txt"] = files["exports/batch-099.txt"] + "note: see also ORDER-77310 pending\n" if tgt != "exports/batch-099.txt" else files["exports/batch-099.txt"]

    def solve(files):
        hits = [(p, n + 1) for p, t in files.items() for n, l in enumerate(t.splitlines()) if re.search(r"ORDER-7731(?!\d)", l)]
        assert len(hits) == 1
        return {"turns": [{"number": hits[0][1], "items": [hits[0][0].split("/")[1]]}], "decoys": {"TR-DECOY": len([1 for p, t in files.items() if "ORDER-7731" in t]), "TR-TRUNC": 50}}
    emit("fs-32226", sub="multifile", task_type="find_file", desc="Locates the single export file and line mentioning one order reference among 130 files where a longer reference shares the prefix",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "One of the files in exports/ mentions order ORDER-7731 (exactly that number; ORDER-77310 is another order). Which file is it, and on which line?"}],
         ref=(["grep -rnE 'ORDER-7731($|[^0-9])' exports"], 0),
         notes_traps=["TR-DECOY: ORDER-77310 is a longer reference in another file.", "TR-TRUNC: 100+ files."], notes_ref=["grep -rnE with a non-digit boundary."], unique="Boundary-checked match appears once.")


@reg
def c5(i):
    rng = Random(3222700 + i * 7919)
    files = {}
    for k in range(rng.randint(90, 130)):
        sec = rng.choice(["guide", "api", "faq", "notes"])
        ext = rng.choices([".md", ".txt", ".mdx", ".md.orig"], [8, 3, 2, 1])[0]
        files["docs/%s/page-%03d%s" % (sec, k, ext)] = L(*["line %d" % j for j in range(rng.randint(3, 40))])
    def solve(files):
        md = {p: t for p, t in files.items() if p.endswith(".md")}
        loose = {p: t for p, t in files.items() if ".md" in p}
        n = sum(len(t.splitlines()) for t in md.values())
        return {"turns": [{"number": len(md), "items": []}, {"number": n, "items": []}], "decoys": {"TR-DECOY": len(loose), "TR-TRUNC": 50}}
    emit("fs-32227", sub="multifile", task_type="count_by_type", desc="Counts Markdown pages in a docs tree with .mdx and .md.orig look-alikes, then totals their lines",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "docs 目录下一共有多少个 .md 文件？（.mdx 和 .md.orig 不是 Markdown 页面，不算。）"},
                {"prompt": "这些 .md 文件加起来一共多少行？"}],
         ref=(["find docs -type f -name '*.md' -exec cat {} + | wc -l"], 0),
         notes_traps=["TR-DECOY: .mdx and .md.orig contain .md.", "TR-TRUNC: ~110 files."], notes_ref=["find -name '*.md' | wc -l.", "find -name '*.md' -exec cat {} + | wc -l."], unique="Exact extension; lines by newline count.")


@reg
def c6(i):
    rng = Random(3222800 + i * 7919)
    files = {}
    need = ["deploy/%s.yml" % x for x in ["api", "web", "worker", "cron", "queue", "cache", "db", "proxy", "auth", "search", "mail", "metrics"]]
    absent = set(rng.sample(need, rng.randint(3, 5)))
    for p in need:
        if p not in absent:
            files[p] = "name: %s\n" % p.split("/")[1][:-4]
    for k in range(rng.randint(70, 100)):
        files["deploy/archive/old-%03d.yml" % k] = "name: old%d\n" % k
    files["deploy/REQUIRED.txt"] = L(*need)
    for a in sorted(absent)[:1]:
        files["deploy/archive/" + a.split("/")[1]] = "name: archived copy\n"

    def solve(files):
        req = files["deploy/REQUIRED.txt"].split()
        miss = [r for r in req if r not in files]
        return {"turns": [{"number": len(miss), "items": [m.split("/")[1] for m in miss]}], "decoys": {"TR-DECOY": len(req), "TR-TRUNC": 50}}
    emit("fs-32228", sub="multifile", task_type="presence", desc="Checks which required deploy files are absent from a directory of 100 where an archived copy of one exists",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "deploy/REQUIRED.txt lists the deployment files every environment must have directly under deploy/. Which of them are absent? Give the count and the file names. (Copies under deploy/archive don't count.)"}],
         ref=(["m=$(for f in $(cat deploy/REQUIRED.txt); do [ -f \"$f\" ] || echo $f; done); echo \"$m\"; echo \"$m\" | wc -l"], 0),
         notes_traps=["TR-DECOY: an archived copy of one file exists under archive/.", "TR-TRUNC: ~100 files so the listing hides the top-level ones."], notes_ref=["loop over REQUIRED.txt with test -f."], unique="Presence is exact path.")


@reg
def c7(i):
    rng = Random(3222900 + i * 7919)
    files = {}
    for k in range(rng.randint(80, 110)):
        sec = rng.choice(["2026-07", "2026-08", "2026-09", "archive"])
        rows = ["id,qty"] + ["%d,%d" % (j, rng.randint(1, 99)) for j in range(rng.randint(5, 60))]
        files["data/%s/part-%03d.csv" % (sec, k)] = L(*rows)
    for k in range(10):
        files["data/2026-09/notes-%d.txt" % k] = "x" * rng.randint(100, 2000) + "\n"
    def solve(files):
        t = sum(len(v.encode()) for p, v in files.items() if p.endswith(".csv") and "/archive/" not in p)
        a = sum(len(v.encode()) for p, v in files.items() if p.endswith(".csv"))
        return {"turns": [{"number": t, "items": []}], "decoys": {"TR-DECOY": a, "TR-TRUNC": 50}}
    emit("fs-32229", sub="multifile", task_type="largest", desc="Totals the bytes of all csv parts outside the archive folder in a 100-file data tree",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "data 目录下所有 .csv 文件（archive 子目录里的不算，txt 也不算）加起来一共多少字节？"}],
         ref=(["find data -type f -name '*.csv' -not -path '*/archive/*' -exec cat {} + | wc -c"], 0),
         notes_traps=["TR-DECOY: archive csv files add bytes.", "TR-TRUNC: ~100 files."], notes_ref=["find -name '*.csv' -not -path '*/archive/*' -exec cat {} + | wc -c."], unique="Byte counts of exact files.")


@reg
def c8(i):
    rng = Random(3223000 + i * 7919)
    files = {}
    for d in range(1, 31):
        s = rng.choice([300, 700, 1400, 2200, 3100, 4800]) + rng.randint(0, 80) + d
        files["logs/app-2026-09-%02d.log" % d] = ("e" * (s - 1)) + "\n"
    for d in range(1, 31):
        files["logs/db-2026-09-%02d.log" % d] = ("d" * (rng.randint(100, 6000) - 1)) + "\n"
    def solve(files):
        a = {p: len(v.encode()) for p, v in files.items() if p.startswith("logs/app-")}
        big = [p for p, s in a.items() if s > 1000]
        top = max(a.items(), key=lambda kv: kv[1])
        assert sorted(a.values())[-1] != sorted(a.values())[-2]
        return {"turns": [{"number": len(big), "items": []}, {"number": top[1], "items": [top[0].split("/")[1]]}], "decoys": {"TR-DECOY": len([p for p, v in files.items() if len(v) > 1000]), "TR-TRUNC": 50}}
    emit("fs-32230", sub="multifile", task_type="largest", desc="Counts app log files over 1000 bytes among app and db logs, then names the biggest app log",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "How many of the app-*.log files in logs/ are bigger than 1000 bytes? (db-*.log files are a different thing.)"},
                {"prompt": "Which app log is the biggest, and how many bytes is it?"}],
         ref=(["find logs -name 'app-*.log' -exec wc -c {} + | grep -v ' total$' | sort -rn | head -3"], 0),
         notes_traps=["TR-DECOY: db logs also exceed 1000 bytes.", "TR-TRUNC: 60 files."], notes_ref=["find -name 'app-*.log' -size +1000c | wc -l.", "wc -c sort -rn."], unique="Distinct maximum.")
