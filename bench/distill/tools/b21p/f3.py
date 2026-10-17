"""fs count_by_type 33713-33718, presence 33719-33723."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


def mk(r, names, lo=20, hi=90):
    return {p: blob(r, r.randint(lo, hi), p.split("/")[-1][:5]) for p in names}


def cnt(files, pred):
    return sum(1 for p in files if pred(p))


@reg
def c1():
    r = rng("c1")
    names = ["wiki/intro.md", "wiki/setup.md", "wiki/faq.MD", "wiki/guide/usage.md", "wiki/guide/tips.md", "wiki/guide/Advanced.Md",
             "wiki/guide/img/arch.png", "wiki/drafts/todo.md.bak", "wiki/drafts/plan.md", "wiki/index.html", "wiki/README"]
    f = mk(r, names)
    make("fs-33713", sub="ctype", task_type="count_by_type", desc="Count markdown files with mixed-case extensions and a .md.bak decoy",
         files=f, turns=[T("wiki 目录（含所有子目录）里一共有多少个 Markdown 文件？", ["7"], token=True),
                         T("其中直接放在 wiki 根目录下的有几个？", ["3"], token=True)],
         truth="n=[p for p in files if p.lower().endswith('.md')]\nanswers=[str(len(n)), str(len([p for p in n if p.count('/')==1]))]",
         ref=[("find wiki -type f | grep -ci '[.]md$'", "7")],
         lazy=[("find wiki -type f -name '*.md' | wc -l", "zero")] if False else [],
         notes={"traps": "faq.MD and Advanced.Md use other cases; todo.md.bak must not count.", "steps": "find | grep -ci '\\.md$'.", "unique": "7 md files, 3 at wiki root (intro, setup, faq)."},
         traps=("TR-DECOY",), rc=3)


@reg
def c2():
    r = rng("c2")
    names = ["data/raw/a.json", "data/raw/b.json", "data/raw/c.json", "data/clean/d.json", "data/clean/e.json", "data/clean/deep/f.json",
             "data/config.yaml", "data/clean/map.yml", "data/raw/seed.yaml", "data/raw/notes.txt", "data/schema.json.old", "data/out/g.jsonl"]
    f = mk(r, names)
    make("fs-33714", sub="ctype", task_type="count_by_type", desc="Count json files, then yaml and yml together",
         files=f, turns=[T("How many .json files are in the data folder, subfolders included?", ["6"], token=True),
                         T("And how many YAML files in total (.yaml and .yml together)?", ["3"], token=True)],
         truth="answers=[str(cnt(files, lambda p: p.endswith('.json'))), str(cnt(files, lambda p: p.endswith(('.yaml','.yml'))))]" if False else "answers=[str(len([p for p in files if p.endswith('.json')])), str(len([p for p in files if p.endswith(('.yaml','.yml'))]))]",
         ref=[("find data -type f -name '*.json' | wc -l", "6"), ("find data -type f \\( -name '*.yaml' -o -name '*.yml' \\) | wc -l", "3")],
         notes={"traps": "schema.json.old and .jsonl look like json; yaml has two spellings.", "steps": "find -name.", "unique": "6 json, 3 yaml/yml."},
         traps=("TR-DECOY",), rc=3)


@reg
def c3():
    r = rng("c3")
    names = ["album/2024/cat.jpg", "album/2024/dog.jpeg", "album/2024/sky.png", "album/2024/clip1.mp4", "album/2025/lake.JPG",
             "album/2025/city.webp", "album/2025/anim.gif", "album/2025/clip2.mov", "album/2025/clip3.mp4", "album/scan/doc1.pdf",
             "album/scan/doc2.png", "album/notes.txt", "album/thumbs/cat_thumb.jpg"]
    f = mk(r, names)
    make("fs-33715", sub="ctype", task_type="count_by_type", desc="Count images by the user's word, then videos",
         files=f, turns=[T("album 里一共有几张图片？jpg、jpeg、png、gif、webp 都算（不分大小写，所有子文件夹都算）。", ["8"], token=True),
                         T("视频文件（mp4、mov）有几个？", ["3"], token=True)],
         truth="answers=[str(len([p for p in files if p.lower().rsplit('.',1)[-1] in ('jpg','jpeg','png','gif','webp')])), str(len([p for p in files if p.lower().rsplit('.',1)[-1] in ('mp4','mov')]))]",
         ref=[("find album -type f | grep -ciE '[.](jpg|jpeg|png|gif|webp)$'", "8"), ("find album -type f | grep -ciE '[.](mp4|mov)$'", "3")],
         notes={"traps": "Upper-case .JPG, .jpeg spelling, png inside scan folder.", "steps": "find | grep -ciE.", "unique": "8 images, 3 videos."},
         traps=("TR-DEFN", "TR-DECOY"), rc=4)


@reg
def c4():
    r = rng("c4")
    names = ["proj/Makefile", "proj/LICENSE", "proj/src/main.c", "proj/src/util.c", "proj/src/util.h", "proj/docs/CHANGES",
             "proj/docs/guide.txt", "proj/build/Dockerfile", "proj/scripts/run", "proj/scripts/deploy.sh", "proj/NOTICE"]
    f = mk(r, names)
    make("fs-33716", sub="ctype", task_type="count_by_type", desc="Files with no extension at all",
         files=f, turns=[T("proj 里有多少个没有扩展名的文件？把它们的名字也列一下。", ["Makefile", "LICENSE", "CHANGES", "Dockerfile", "NOTICE", "run", "6"], token=True)],
         truth="n=[p.split('/')[-1] for p in files if '.' not in p.split('/')[-1]]\nanswers=['Makefile']",
         ref=[("find proj -type f | awk -F/ '$NF !~ /[.]/' | wc -l", "6")],
         notes={"traps": "Extensionless names are spread across subfolders; run (script) is easy to miss.", "steps": "find | awk on basename.", "unique": "Makefile LICENSE CHANGES Dockerfile run NOTICE = 6."},
         traps=("TR-DECOY",), rc=3)


@reg
def c5():
    r = rng("c5")
    names = ["lab/s1.csv", "lab/s2.csv", "lab/s3.csv", "lab/s4.csv", "lab/s5.csv", "lab/old/s0.csv", "lab/old/s6.csv", "lab/old/x.tsv",
             "lab/plots/p1.png", "lab/plots/p2.png", "lab/plots/p3.png", "lab/readme.txt", "lab/notes.txt"]
    f = mk(r, names)
    make("fs-33717", sub="ctype", task_type="count_by_type", desc="Most common extension and its count",
         files=f, turns=[T("Which file extension is the most common in lab/ (subfolders included), and how many files have it?", ["csv", "7"], token=True)],
         truth="answers=['csv']",
         ref=[("find lab -type f | awk -F'[.]' '{print $NF}' | sort | uniq -c | sort -rn | head -2", "7 csv")],
         notes={"traps": "csv files spread over lab/ and lab/old; tsv is a near type.", "steps": "extension histogram.", "unique": "csv 7, png 3, txt 2, tsv 1."},
         traps=("TR-DECOY",), rc=4)


@reg
def c6():
    r = rng("c6")
    names = ["home/.bashrc", "home/.profile", "home/.config/app/settings.json", "home/.config/app/cache.db", "home/.config/app/theme.css", "home/.ssh/config",
             "home/notes.txt", "home/todo.txt", "home/docs/cv.pdf", "home/docs/.draft.tmp", "home/pics/a.png"]
    f = mk(r, names)
    make("fs-33718", sub="ctype", task_type="count_by_type", desc="Hidden files (dot-prefixed names) anywhere under home",
         files=f, turns=[T("home 目录下面有多少个隐藏文件（文件名以点开头，不算目录，所有层级都算）？", ["3"], token=True),
                         T("那放在隐藏文件夹（.config、.ssh 这类以点开头的目录）里面的文件有几个？", ["4"], token=True)],
         truth="h=[p for p in files if p.split('/')[-1].startswith('.')]\nanswers=[str(len(h)), str(len([p for p in files if p.count('/')>=2 and p.split('/')[1].startswith('.')]))]",
         ref=[("find home -type f -name '.*' | wc -l", "3"), ("find home -type f -path '*/.*/*' | wc -l", "4")],
         notes={"traps": "Hidden files plus files inside a hidden directory (.config) whose own names are not dotted.", "steps": "find -name '.*'.", "unique": ".bashrc .profile .draft.tmp = 3; hidden dirs .config (3 files) and .ssh (1) = 4."},
         traps=("TR-DEFN",), rc=3)


@reg
def p1():
    r = rng("p1")
    names = ["shop/package.json", "shop/src/index.js", "shop/src/cart.js", "shop/legal/LICENSE", "shop/docs/CHANGES.txt", "shop/docs/usage.md", "shop/test/cart.test.js"]
    f = mk(r, names)
    make("fs-33719", sub="presence", task_type="presence", desc="A license file buried in a subfolder, then a changelog that does not exist",
         files=f, turns=[T("shop 项目里有 LICENSE 文件吗？在哪？", ["legal/LICENSE"]),
                         T("那 CHANGELOG 文件呢，项目里有吗？", any_=NEG)],
         truth="answers=['legal/LICENSE']",
         ref=[("find shop -name 'LICENSE'", "shop/legal/LICENSE"), ("find shop -iname 'CHANGELOG*'", "")],
         notes={"traps": "LICENSE is not at the top level; CHANGELOG is absent though docs/CHANGES.txt is close.", "steps": "find -name.", "unique": "LICENSE at shop/legal/LICENSE; no CHANGELOG."},
         traps=("TR-ABSENT", "TR-NEARNAME"), axes=("DEC", "ERR"), rc=4)


@reg
def p2():
    r = rng("p2")
    names = ["app/main.py", "app/.env.example", "app/lib/db.py", "app/lib/__init__.py", "app/tests/test_db.py", "app/README.md"]
    f = mk(r, names)
    make("fs-33720", sub="presence", task_type="presence", desc="A dot-file template that plain listing hides",
         files=f, turns=[T("Does the app folder include an example env file? If yes, tell me its path.", [".env.example"], token=False)],
         truth="answers=['.env.example']",
         ref=[("find app -name '.env*'", "app/.env.example")],
         notes={"traps": "Hidden file: ls without -a does not show it.", "steps": "find or ls -a.", "unique": "app/.env.example exists."},
         traps=("TR-DECOY",), rc=3)


@reg
def p3():
    r = rng("p3")
    names = ["svc/requirements-dev.txt", "svc/requirements.txt.bak", "svc/app/main.py", "svc/app/util.py", "svc/Dockerfile", "svc/docs/requirements.md"]
    f = mk(r, names)
    make("fs-33721", sub="presence", task_type="presence", desc="Requested requirements.txt does not exist; only lookalikes do",
         files=f, turns=[T("svc 里有 requirements.txt 这个文件吗？", any_=NEG)],
         truth="answers=[]",
         ref=[("find svc -name 'requirements*'", "requirements-dev.txt")],
         notes={"traps": "requirements-dev.txt, requirements.txt.bak and requirements.md are lookalikes; the exact file is absent.", "steps": "find -name requirements*; see none is exact.", "unique": "No file named requirements.txt."},
         traps=("TR-ABSENT", "TR-NEARNAME"), axes=("DEC", "ERR"), rc=3)


@reg
def p4():
    r = rng("p4")
    names = ["cfg/config.yaml", "cfg/config.local.yml", "cfg/config.prod.yaml", "cfg/base/defaults.yaml", "cfg/base/config.example.yaml", "cfg/notes.txt"]
    f = mk(r, names)
    make("fs-33722", sub="presence", task_type="presence", desc="Exact name config.local.yaml is absent while .yml spelling exists",
         files=f, turns=[T("Is there a file called config.local.yaml anywhere under cfg? Answer yes or no and point to the path if yes.", any_=NEG + ["not "]),
                         T("And config.prod.yaml?", ["cfg/config.prod.yaml"])],
         truth="answers=['cfg/config.prod.yaml']" if False else "answers=['cfg/config.prod.yaml']",
         ref=[("find cfg -name 'config.local*'", "config.local.yml")],
         notes={"traps": "config.local.yml (different extension) exists, config.local.yaml does not.", "steps": "find -name.", "unique": "No config.local.yaml; config.prod.yaml present."},
         traps=("TR-ABSENT", "TR-NEARNAME"), axes=("DEC", "ERR"), rc=4)


@reg
def p5():
    r = rng("p5")
    names = ["kit/docs/README.rst", "kit/src/a.c", "kit/src/b.c", "kit/src/README.txt.old", "kit/Makefile"]
    f = mk(r, names)
    make("fs-33723", sub="presence", task_type="presence", desc="README exists only in docs; the root has none",
         files=f, turns=[T("kit 里有 README 文件吗？", ["docs/README.rst"]),
                         T("我是说顶层目录（kit 根目录）下面，直接放着的那种。", any_=NEG)],
         truth="answers=['docs/README.rst']",
         ref=[("find kit -name 'README*'", "README.rst")],
         notes={"traps": "README.rst under docs only; root has none; README.txt.old is a stale lookalike.", "steps": "find, then ls root.", "unique": "docs/README.rst; none at root."},
         traps=("TR-ABSENT", "TR-NEARNAME"), axes=("DEC", "ERR"), rc=4)
