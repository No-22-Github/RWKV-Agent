"""fs duplicates 33707-33712."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


DUPS = ("find . -type f | xargs sha256sum | sort | awk '{c[$1]++; n[$1]=n[$1] \" \" $2} "
        "END{for(h in c) if(c[h]>1) print c[h] \":\" n[h]}'")


def tweak(s):
    """same size, one character different"""
    i = s.index("a") if "a" in s else 0
    return s[:i] + ("e" if s[i] != "e" else "i") + s[i + 1:]


@reg
def d1():
    r = rng("d1")
    a = blob(r, 1420, "sunset"); b = blob(r, 2260, "market")
    f = {"photos/IMG_2041.txt": a, "photos/trip/IMG_2041_copy.txt": a, "photos/IMG_2042.txt": tweak(a),
         "photos/IMG_2050.txt": b, "photos/trip/IMG_2051.txt": blob(r, 980, "pier"), "photos/trip/notes.txt": blob(r, 350, "note")}
    make("fs-33707", sub="dup", task_type="duplicates", desc="One pair of identical files plus a same-size one-character decoy",
         files=f, turns=[T("photos 里有没有内容完全一样的文件？有的话只列出文件名，不要别的。", ["IMG_2041.txt", "IMG_2041_copy.txt"], exc=["IMG_2042.txt", "IMG_2050.txt"])],
         truth="import collections\ng=collections.defaultdict(list)\nfor p,t in files.items(): g[t].append(p)\nd=[v for v in g.values() if len(v)>1]\nassert len(d)==1\nanswers=[sorted(d[0])[0].split('/')[-1]]" if False else "import collections\ng=collections.defaultdict(list)\nfor p,t in files.items(): g[t].append(p)\nd=[v for v in g.values() if len(v)>1]\nassert len(d)==1\nanswers=['IMG_2041.txt']",
         ref=[(DUPS, "IMG_2041_copy.txt")],
         notes={"traps": "IMG_2042 has the same size as IMG_2041 and differs in one character; comparing by size or name gives a false pair.", "steps": "sha256sum on all files, group equal hashes.", "unique": "Only IMG_2041.txt and IMG_2041_copy.txt match."},
         traps=("TR-DECOY",), rc=4)


@reg
def d2():
    r = rng("d2")
    c = blob(r, 610, "[server]")
    f = {"conf/prod/app.ini": c, "conf/staging/app.ini": c, "conf/backup/app.ini.bak": c, "conf/dev/app.ini": tweak(c),
         "conf/prod/db.ini": blob(r, 480, "[db]"), "conf/staging/db.ini": blob(r, 480, "[db]")}
    make("fs-33708", sub="dup", task_type="duplicates", desc="Triple of identical configs under different names and directories",
         files=f, turns=[T("Which files under conf/ are byte-for-byte identical? Give me the paths of every file in the identical group.",
                           ["conf/prod/app.ini", "conf/staging/app.ini", "conf/backup/app.ini.bak"], exc=["conf/dev/app.ini is identical", "conf/prod/db.ini is identical"])],
         truth="answers=['conf/prod/app.ini']",
         ref=[(DUPS, "3:")],
         notes={"traps": "Same file name in several directories with different content (db.ini, dev app.ini); a .bak copy under another name.", "steps": "sha256sum, group.", "unique": "Three files share one hash."},
         traps=("TR-DECOY", "TR-NEARNAME"), axes=("OBS", "ERR"), rc=4)


@reg
def d3():
    r = rng("d3")
    x = blob(r, 1710, "invoice"); y = blob(r, 760, "receipt")
    f = {"scans/jan/inv_0113.txt": x, "scans/feb/inv_0113_dup.txt": x, "scans/mar/receipt_77.txt": y, "scans/mar/receipt_77_b.txt": y,
         "scans/mar/receipt_78.txt": blob(r, 760, "receipt"), "scans/apr/misc.txt": blob(r, 300, "misc")}
    make("fs-33709", sub="dup", task_type="duplicates", desc="Two duplicate groups, then the bytes wasted by extra copies",
         files=f, turns=[T("scans 目录下有哪几组内容重复的文件？每组列出文件名。", ["inv_0113.txt", "inv_0113_dup.txt", "receipt_77.txt", "receipt_77_b.txt"], exc=["receipt_78.txt"]),
                         T("这些重复文件多占了多少字节？（每组只保留一份，其余算多占）", [], any_=["2470", "2,470"], anytoken=True)],
         truth="answers=['inv_0113.txt','2470']",
         ref=[(DUPS, "2:")],
         notes={"traps": "receipt_78 has the same size as receipt_77 but different content.", "steps": "sha256sum, group; wasted = 1710 + 760.", "unique": "1710+760=2470."},
         traps=("TR-DECOY",), rc=5)


@reg
def d4():
    r = rng("d4")
    f = {"drop/v1/report.txt": blob(r, 900, "q3"), "drop/v2/report.txt": tweak(blob(rng("d4b"), 900, "q3")),
         "drop/v3/report.txt": blob(r, 900, "q3"), "drop/readme.txt": blob(r, 210, "readme")}
    f["drop/v2/report.txt"] = tweak(f["drop/v1/report.txt"])
    make("fs-33710", sub="dup", task_type="duplicates", desc="Same file name in three folders but no identical content",
         files=f, turns=[T("Are any two files under drop/ identical in content? If so name them; if not, say so plainly.", any_=NEG, exc=["identical copy of"]),
                         ],
         truth="import collections\ng=collections.Counter(files.values())\nassert max(g.values())==1\nanswers=[]",
         ref=[(DUPS, "")],
         notes={"traps": "Three report.txt of equal size with tiny differences; no duplicates exist.", "steps": "sha256sum, no repeated hash.", "unique": "No identical pair."},
         traps=("TR-ABSENT", "TR-DECOY"), axes=("DEC", "OBS"), rc=4)


@reg
def d5():
    r = rng("d5")
    a = blob(r, 2040, "chapter"); b = blob(r, 1180, "outline")
    f = {"draft/ch1.txt": a, "draft/old/ch1_final.md": a, "draft/old/outline.txt": b, "draft/outline_v2.md": b,
         "draft/outline_v3.md": tweak(b), "draft/old/ch2.txt": blob(r, 1500, "chapter"), "draft/ch2.txt": blob(r, 1500, "chapter")}
    make("fs-33711", sub="dup", task_type="duplicates", desc="Duplicates hidden behind different extensions; count of redundant files",
         files=f, turns=[T("draft 里有多少个文件是别的文件的完全重复（内容一样）？每组保留一份，其余算重复。", [], any_=["2 个","2个","两个","2 files","two files","2 redundant","2 duplicate","2 extra","two redundant","two duplicate","2 copies","two extra"]),
                         T("具体是哪几个文件重复了？", ["ch1_final.md", "outline_v2.md"], exc=["outline_v3.md 和", "ch2.txt 和"])],
         truth="import collections\ng=collections.Counter(files.values())\nanswers=['2 个' if sum(v-1 for v in g.values() if v>1)==2 else 'x','ch1_final.md']",
         ref=[(DUPS, "2:")],
         notes={"traps": "ch1 copy is saved with .md extension; ch2.txt in both folders has same size but different content; outline_v3 one char off.", "steps": "sha256sum grouping.", "unique": "Two groups, each of 2 -> 2 redundant files."},
         traps=("TR-DECOY", "TR-NEARNAME"), axes=("OBS", "ERR"), rc=5)


@reg
def d6():
    r = rng("d6")
    p = blob(r, 700, "pad"); q = blob(r, 1260, "mesh")
    f = {"old/models/pad.dat": p, "old/models/mesh.dat": q, "old/models/sky.dat": blob(r, 840, "sky"),
         "new/models/pad_v2.dat": p, "new/models/mesh_v2.dat": tweak(q), "new/models/tree.dat": blob(r, 840, "tree"),
         "new/readme.txt": blob(r, 150, "new")}
    make("fs-33712", sub="dup", task_type="duplicates", desc="Which files in new/ are unchanged copies of files in old/",
         files=f, turns=[T("new 目录里哪些文件其实是 old 里文件的原样拷贝（内容一模一样，只是换了名字）？只回答 new 里的文件名。", ["pad_v2.dat"], exc=["mesh_v2.dat", "tree.dat"])],
         truth="answers=['pad_v2.dat']",
         ref=[(DUPS, "2:")],
         notes={"traps": "mesh_v2 differs by one char, tree.dat is the same size as sky.dat but different.", "steps": "sha256sum over both trees.", "unique": "pad_v2.dat only."},
         traps=("TR-DECOY",), rc=4)
