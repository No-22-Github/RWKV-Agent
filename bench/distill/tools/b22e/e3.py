"""E3 big directories, cases fs-34441..34450."""
from common import *
from lg import pick

B = []
POL = {"must_offer": ["bash", "list_files"]}
WORDS = ("alpha river stone lamp cedar quartz maple orbit pixel ember harbor delta fjord grain hollow ivory juniper kettle lantern "
         "meadow nectar oyster pebble quill ridge saddle thistle umber velvet willow yarrow zephyr cobalt dune ferry glacier").split()


def reg(f):
    B.append(f)
    return f


def blob(r, nbytes, head=""):
    out, size = [], 0
    if head:
        out.append(head); size = len(head) + 1
    while size < nbytes:
        l = " ".join(pick(r, WORDS) for _ in range(r.randint(3, 9)))
        out.append(l); size += len(l) + 1
    return "\n".join(out) + "\n"


def tree(r, dirs, exts, n, stem, used=None):
    """n unique paths: dir/stem_NNNN.ext"""
    paths = set()
    while len(paths) < n:
        paths.add("%s/%s_%04d.%s" % (pick(r, dirs), stem, r.randint(0, 9999), pick(r, exts)))
    return sorted(paths)


@reg
def f01():
    r = rng("f01")
    exts = ["jpg"] * 8 + ["png"] * 5 + ["gif", "txt", "md", "json"]
    ps = tree(r, ["album/2024", "album/2025", "album/2026/spring", "album/2026/summer", "album/raw", "album/exports"], exts, 340, "img")
    f = {p: blob(r, r.randint(40, 700)) for p in ps}
    make("fs-34441", sub="E3", task_type="count_by_type", desc="Count png files in a 340-file album tree",
         files=f, shape="dir", rc=3, policy=POL, deep=False,
         turns=[T("album 目录里（包括所有子目录）一共有多少个 png 文件？", "i")],
         truth="answers = [len([p for p in files if p.endswith('.png')])]\n",
         ref=[("find album -name '*.png' | wc -l", lambda a: str(a[0]))],
         notes={"traps": "The tree is six directories deep; a single directory listing shows only part of the files and may be cut off.", "steps": "find album -name '*.png' | wc -l.", "unique": "Recomputed from the file names."})


@reg
def f02():
    r = rng("f02")
    ps = tree(r, ["data/raw", "data/clean", "data/archive/2025", "data/archive/2026", "tmp", "exports"], ["csv", "csv", "log", "bin", "txt"], 310, "part")
    sizes = r.sample(range(60, 1800), len(ps))
    f = {p: blob(r, s) for p, s in zip(ps, sizes)}
    big = [ps[5], ps[100], ps[222]]
    for p, s in zip(big, (4300, 3900, 3500)):
        f[p] = blob(r, s)
    make("fs-34442", sub="E3", task_type="largest", desc="Three largest files in a 310-file data tree",
         files=f, shape="dir", rc=3, policy=POL, deep=False,
         turns=[T("Which three files under data/ (and the tmp and exports folders next to it) take up the most space? Give the file names from biggest to smallest.", "s")],
         truth="s = sorted(files, key=lambda p: -len(files[p].encode()))[:3]\nassert len(files[s[2]].encode()) > 3400 and len(files[sorted(files, key=lambda p: -len(files[p].encode()))[3]].encode()) < 1900\nanswers = [[p.split('/')[-1] for p in s]]\n",
         ref=[("find . -type f -printf '%s %p\\n' | sort -rn | head -4", lambda a: a[0][0])],
         notes={"traps": "Large files hide in different subfolders; the other 307 files are all below 1800 bytes.", "steps": "find -printf '%s %p' | sort -rn | head -3.", "unique": "The three planted files exceed 3400 bytes, all others are below 1900."})


@reg
def f03():
    r = rng("f03")
    ps = tree(r, ["notes/team", "notes/personal", "notes/projects/a", "notes/projects/b", "notes/archive"], ["md", "md", "txt"], 320, "memo")
    f = {}
    for p in ps:
        m = r.choice([6, 6, 7, 7, 8, 8, 9]) if r.random() < 0.9 else 9
        d = "2026-%02d-%02d" % (m, r.randint(1, 28))
        f[p] = blob(r, r.randint(60, 500), "updated: " + d)
    make("fs-34443", sub="E3", task_type="find_file", desc="Count notes whose updated header is in September 2026 or later",
         files=f, shape="dir", rc=4, policy=POL, deep=False,
         turns=[T("notes 目录里每个文件第一行都写着 updated: 日期。有多少个文件的更新日期在 2026-09-01 或之后？", "i")],
         truth="answers = [len([p for p in files if files[p].split('\\n')[0] >= 'updated: 2026-09-01'])]\n",
         ref=[("grep -rh '^updated: 2026-09' notes | wc -l", lambda a: str(a[0]))],
         notes={"traps": "File modification times are meaningless here; the date lives in the first line of each of 320 files.", "steps": "grep -rh '^updated: 2026-09' notes | wc -l.", "unique": "Dates are only in months 6-9."})


@reg
def f04():
    r = rng("f04")
    names = set()
    while len(names) < 330:
        m, d = r.choice([7, 8, 8, 9]), r.randint(1, 28)
        names.add("backups/%s/db-2026-%02d-%02d-%s.sql.gz" % (pick(r, ["nightly", "weekly", "adhoc"]), m, d, pick(r, ["a", "b", "c", "d"])))
    f = {p: blob(r, r.randint(30, 400)) for p in sorted(names)}
    make("fs-34444", sub="E3", task_type="find_file", desc="Backups dated on or after 2026-08-20 judged from file names",
         files=f, shape="dir", rc=4, policy=POL, deep=False,
         turns=[T("backups 目录里的备份文件名里带着日期（db-2026-MM-DD-…）。日期在 2026-08-20 及以后的有多少个？", "i")],
         truth="import re\nanswers = [len([p for p in files if re.search(r'db-(\\d{4}-\\d\\d-\\d\\d)-', p).group(1) >= '2026-08-20'])]\n",
         ref=[("find backups -type f | sed 's/.*db-\\(2026-[0-9-]*\\)-[a-d]\\.sql\\.gz/\\1/' | awk '$1 >= \"2026-08-20\"' | wc -l", lambda a: str(a[0]))],
         notes={"traps": "Three subfolders and 330 names; filenames, not modification times, carry the date. 08-20 itself counts.", "steps": "find | sed extract date | awk compare | wc -l.", "unique": "Recomputed from the file names."})


@reg
def f05():
    r = rng("f05")
    ps = tree(r, ["site/pages", "site/posts/2025", "site/posts/2026", "site/assets/css", "site/assets/js", "site/drafts"], ["html", "html", "md", "css", "js"], 315, "f")
    empties = set(r.sample(ps, 29))
    f = {p: ("" if p in empties else blob(r, r.randint(40, 600))) for p in ps}
    make("fs-34445", sub="E3", task_type="find_file", desc="Count zero-byte files in a 315-file site tree",
         files=f, shape="dir", rc=3, policy=POL, deep=False,
         turns=[T("site 目录里有一些空文件（0 字节）。一共有多少个？", "i"), T("其中放在 drafts 文件夹里的有几个？", "i")],
         truth="answers = [len([p for p in files if files[p] == '']), len([p for p in files if files[p] == '' and p.startswith('site/drafts/')])]\n",
         ref=[("find site -type f -size 0 | wc -l", lambda a: str(a[0])), ("find site/drafts -type f -size 0 | wc -l", lambda a: str(a[1]))],
         notes={"traps": "Empty files are scattered; a directory listing is long and cut off by its default limit.", "steps": "find -size 0 | wc -l.", "unique": "Recomputed from the fixture."})


@reg
def f06():
    r = rng("f06")
    dirs = [("reports/q1", 4), ("reports/q2", 6), ("reports/q3", 12), ("reports/q4", 5), ("reports/misc", 3), ("reports/old", 2)]
    ps = set()
    while len(ps) < 305:
        d = None
        tot = sum(w for _, w in dirs); x = r.uniform(0, tot)
        for dd, w in dirs:
            x -= w
            if x <= 0:
                d = dd; break
        ps.add("%s/rep%04d.txt" % (d or dirs[-1][0], r.randint(0, 9999)))
    f = {p: blob(r, r.randint(30, 500)) for p in sorted(ps)}
    make("fs-34446", sub="E3", task_type="count_by_type", desc="Folder holding the most files in a reports tree",
         files=f, shape="dir", rc=4, policy=POL, deep=False,
         turns=[T("Which subfolder of reports holds the most files, and how many?")],
         truth="import collections\nc = collections.Counter(p.rsplit('/', 1)[0] for p in files)\nd, k = c.most_common(1)[0]\nassert c.most_common(2)[1][1] < k - 5\nanswers = [[d, str(k)]]\n",
         ref=[("find reports -type f | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -3", lambda a: a[0][1])],
         notes={"traps": "Six folders of different sizes; the biggest is not the first listed.", "steps": "find -type f | sed dir | sort | uniq -c | sort -rn.", "unique": "The leader is ahead by more than five files."})


@reg
def f07():
    r = rng("f07")
    ps = tree(r, ["code/core", "code/api", "code/utils", "code/tests/unit", "code/tests/e2e", "code/scripts"], ["py", "py", "py", "md", "txt", "cfg"], 320, "mod")
    f = {}
    for p in ps:
        f[p] = blob(r, r.randint(20, 380))
    f["code/core/mod_big.py"] = blob(r, 2600)
    make("fs-34447", sub="E3", task_type="count_by_type", desc="Total lines of all .py files in a 321-file code tree, then the longest .py file",
         files=f, shape="dir", rc=4, policy=POL, deep=False,
         turns=[T("code 目录下所有 .py 文件加起来一共有多少行？", "i"), T("哪个 .py 文件行数最多？只要文件名。", "s")],
         truth="py = {p: files[p].count('\\n') for p in files if p.endswith('.py')}\nm = sorted(py, key=lambda p: -py[p])\nassert py[m[0]] > py[m[1]] + 5\nanswers = [sum(py.values()), [m[0].split('/')[-1]]]\n",
         ref=[("find code -name '*.py' | xargs cat | wc -l", lambda a: str(a[0])), ("find code -name '*.py' | xargs wc -l | sort -rn | head -3", lambda a: "mod_big.py")],
         notes={"traps": "Hundreds of small files and one longer file; only a combined count gives the total.", "steps": "find code -name '*.py' | xargs cat | wc -l; xargs wc -l | sort -rn.", "unique": "mod_big.py is the longest by a wide margin."})


@reg
def f08():
    r = rng("f08")
    ps = tree(r, ["share/docs", "share/img", "share/downloads", "share/old"], ["txt", "md", "dat"], 312, "item")
    f = {p: blob(r, r.randint(40, 700), "id %d" % (i + 1)) for i, p in enumerate(ps)}
    src = r.sample(ps, 14)
    for j, s in enumerate(src):
        for k in range(1 + j % 3):
            tgt = ps[(ps.index(s) * 7 + 31 * (k + 1)) % len(ps)]
            if tgt not in src:
                f[tgt] = f[s]
    make("fs-34448", sub="E3", task_type="duplicates", desc="Number of files whose content is an exact copy of another file",
         files=f, shape="dir", rc=5, policy=POL, deep=False,
         turns=[T("share 目录里有些文件内容是完全一样的拷贝。去掉重复之后，一共有多少份不同内容的文件？", "i")],
         truth="answers = [len(set(files.values()))]\n",
         ref=[("find share -type f -exec md5sum {} + | awk '{print $1}' | sort -u | wc -l", lambda a: str(a[0]))],
         notes={"traps": "Names differ and copies sit in different folders; only content hashes show the duplicates.", "steps": "find -exec md5sum | awk hash | sort -u | wc -l.", "unique": "Number of distinct contents, recomputed."})


@reg
def f09():
    r = rng("f09")
    ps = tree(r, ["srv/logs/app", "srv/logs/web", "srv/logs/db", "srv/vendor/lib", "srv/vendor/cache"], ["log", "log", "gz"], 308, "run")
    f = {p: blob(r, r.randint(60, 1500)) for p in ps}
    f["srv/vendor/cache/run_blob.gz"] = blob(r, 4700)
    f["srv/logs/web/run_peak.log"] = blob(r, 3900)
    make("fs-34449", sub="E3", task_type="largest", desc="Largest file outside the vendor folder, then its size in bytes",
         files=f, shape="dir", rc=4, policy=POL, deep=False,
         turns=[T("srv 下面除了 vendor 目录之外，最大的文件是哪个？"), T("它有多少字节？", "i")],
         truth="c = [p for p in files if '/vendor/' not in p]\nm = max(c, key=lambda p: len(files[p].encode()))\nassert len(files[m].encode()) > 1700 and len(files[sorted(c, key=lambda p: -len(files[p].encode()))[1]].encode()) < 1700\nanswers = [[m.split('/')[-1]], len(files[m].encode())]\n",
         ref=[("find srv -type f -not -path '*/vendor/*' -printf '%s %p\\n' | sort -rn | head -2", lambda a: a[0][0]), ("find srv -type f -not -path '*/vendor/*' -printf '%s %p\\n' | sort -rn | head -1", lambda a: str(a[1]))],
         notes={"traps": "The overall largest file lives under vendor/cache and must be excluded.", "steps": "find with -not -path | sort -rn | head.", "unique": "run_peak.log is the largest outside vendor."})


@reg
def f10():
    r = rng("f10")
    ps = tree(r, ["app/auth", "app/billing", "app/search", "app/ui", "app/jobs"], ["py", "py", "js", "md"], 318, "unit")
    f = {}
    wts = {"app/billing": 0.30, "app/auth": 0.12, "app/search": 0.08, "app/ui": 0.05, "app/jobs": 0.1}
    for p in ps:
        txt = blob(r, r.randint(60, 500))
        if r.random() < wts[p.split("/")[0] + "/" + p.split("/")[1]]:
            ls = txt.split("\n"); ls.insert(r.randint(0, len(ls) - 1), "# TODO: " + pick(r, WORDS) + " " + pick(r, WORDS)); txt = "\n".join(ls)
        f[p] = txt
    make("fs-34450", sub="E3", task_type="find_file", desc="Files containing a TODO marker, then the module folder with the most of them",
         files=f, shape="dir", rc=4, policy=POL, deep=False,
         turns=[T("How many files under app/ contain the text TODO?", "i"), T("Which module folder (app/<name>) has the most of them?")],
         truth="import collections\nh = [p for p in files if 'TODO' in files[p]]\nc = collections.Counter(p.split('/')[1] for p in h)\nassert c.most_common(2)[1][1] < c.most_common(1)[0][1] - 3\nanswers = [len(h), [c.most_common(1)[0][0]]]\n",
         ref=[("grep -rl TODO app | wc -l", lambda a: str(a[0])), ("grep -rl TODO app | cut -d/ -f2 | sort | uniq -c | sort -rn | head -2", lambda a: a[1][0])],
         notes={"traps": "Only a content search over all 318 files gives the total; billing leads.", "steps": "grep -rl TODO app | wc -l; cut -d/ -f2 | sort | uniq -c.", "unique": "billing has the most TODO files."})
