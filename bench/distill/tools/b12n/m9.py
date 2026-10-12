"""M9 (bash) half of the v1.41 b12n batch: ids 9341-9360. Every case has two or three turns that mix a lookup or an
aggregate (turn 1, answer in the reply) with an edit that depends on the result (turn 2) and, in eight cases, a partial
undo (turn 3). Every edit touches two or more files or a pattern across a tree; README files protect some paths."""
from common import Random, chain_case, lines, ts

REFS = {}


def case(*a, **k):
    return chain_case(REFS, *a, **k)


# ---------------------------------------------------------------- cfg-9341: errors per service -> timeout


def cfg_9341():
    svcs = ["gateway", "orders", "payment", "stock", "notify"]

    def gen(rng):
        files = {}
        errs = rng.sample(range(9, 40), 5)
        for s, e in zip(svcs, errs):
            levels = ["ERROR"] * e + ["WARN"] * rng.randint(8, 14)
            levels += ["INFO"] * (rng.randint(70, 90) - len(levels))
            rng.shuffle(levels)
            rows = []
            for i, lv in enumerate(levels):
                msg = {"ERROR": rng.choice(["upstream timeout after 3000ms", "connection reset by peer", "pool exhausted"]),
                       "WARN": rng.choice(["slow response 2400ms", "retrying call"]),
                       "INFO": rng.choice(["request ok", "health check passed errors=0", "ERROR_RATE=0.00 window=5m"])}[lv]
                rows.append("%s %s %s" % (ts(i), lv, msg))
            files["logs/%s.log" % s] = lines(rows)
            for env in ("prod", "staging", "canary"):
                files["config/%s/%s.yaml" % (s, env)] = lines(["name: " + s, "timeout_ms: 3000", "connect_timeout_ms: 500", "retries: 2"])
        files["config/_base/defaults.yaml"] = lines(["timeout_ms: 3000", "retries: 2"])
        files["config/README.md"] = lines(["# 服务配置", "", "每个服务一个目录，里面有 prod.yaml、staging.yaml、canary.yaml。",
                                          "_base 是全局默认值，要走评审，不要改。connect_timeout_ms 是连接超时，和 timeout_ms 是两回事。"])
        return files

    logic = '''
def solve(files):
    counts = {}
    for p, t in files.items():
        if p.startswith("logs/") and p.endswith(".log"):
            counts[p[5:-4]] = sum(1 for r in t.splitlines() if r.split()[2] == "ERROR")
    top = max(counts, key=counts.get)
    assert sorted(counts.values())[-1] > sorted(counts.values())[-2]
    final = dict(files)
    for env in ("prod", "staging", "canary"):
        p = "config/%s/%s.yaml" % (top, env)
        final[p] = files[p].replace("\\ntimeout_ms: 3000\\n", "\\ntimeout_ms: 6000\\n")
        assert final[p] != files[p]
    final2 = dict(final)
    for env in ("staging", "canary"):
        p = "config/%s/%s.yaml" % (top, env)
        final2[p] = files[p]
    return [{"all": [top]}, None, None], final2, {"svc": top}
'''

    def cmds(i):
        s = i["svc"]
        return [
            ["""for f in logs/*.log; do echo "$f $(awk '$3=="ERROR"' $f | wc -l)"; done"""],
            ["sed -i 's/^timeout_ms: 3000$/timeout_ms: 6000/' config/%s/prod.yaml config/%s/staging.yaml config/%s/canary.yaml" % (s, s, s), "grep -rn '^timeout_ms' config/" + s],
            ["sed -i 's/^timeout_ms: 6000$/timeout_ms: 3000/' config/%s/staging.yaml config/%s/canary.yaml" % (s, s), "grep -rn '^timeout_ms' config/" + s],
        ]
    return case(
        "cfg-9341", desc="Three turns: finds the service with the most ERROR-level log lines, raises its timeout_ms in three config files, then restores two of them",
        task_type="edit_value", family="fam-cfg-b12n-errtimeout-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: INFO lines carry look-alikes (`ERROR_RATE=0.00`, `errors=0`), only the third field decides the level. TR-READONLY: config/_base/defaults.yaml and connect_timeout_ms stay (config/README.md); a global `s/3000/6000/` or `s/timeout_ms: .*/` hits the wrong lines.",
        prompts=["logs 目录里每个服务一个日志文件，每行第三个字段是日志级别。哪个服务级别为 ERROR 的行最多？只回答服务名。",
                 "这个服务的超时太短了：把它在 config 下 prod.yaml、staging.yaml、canary.yaml 里的 timeout_ms 都改成 6000，哪些不能动看 config/README.md。改完回复 DONE。",
                 "staging 和 canary 的流量小，不用这么长，这两个文件的 timeout_ms 改回 3000，prod 保持 6000。改完回复 DONE。"],
        alts=["哪个服务的 ERROR 日志最多？把它的超时翻倍，然后 staging 和 canary 再还原", "找出报错最多的服务，三套配置的 timeout_ms 提到 6000，之后只留 prod 的改动",
              "日志里 ERROR 行数最多的是谁？给它的 prod、staging、canary 加长超时，再把后两个撤回", "统计各服务 ERROR 行，对出错最多的服务调大 timeout_ms，随后 staging 与 canary 恢复原值",
              "Which service logs the most ERROR lines? Raise its timeout_ms to 6000 everywhere, then put staging and canary back to 3000."])


# ---------------------------------------------------------------- fs-9342: largest file -> archive


def fs_9342():
    stems = ["海报", "封面", "横幅", "头图", "插画", "图标集"]

    def gen(rng):
        ks = rng.sample([30, 45, 60, 75, 95, 120], 6)
        files = {}
        for stem, k in zip(stems, ks):
            files["素材/%s.png" % stem] = "".join("frame %04d data %s\n" % (i, "#" * 20) for i in range(k))
            files["素材/%s.png.meta" % stem] = lines(["作者: " + rng.choice(["小李", "老周", "阿青"]), "用途: " + rng.choice(["首页", "活动页", "公众号"])])
        files["素材/归档/旧封面.png"] = "".join("frame %04d data %s\n" % (i, "#" * 20) for i in range(200))
        files["素材/归档/旧封面.png.meta"] = lines(["作者: 老周", "用途: 首页"])
        files["素材/README.md"] = lines(["# 素材库", "", "素材/归档 里是已经处理过的旧素材，统计大小时不算。",
                                        "每个素材文件都有同名加 .meta 的说明文件，归档时两个要一起搬。"])
        return files

    logic = '''
def solve(files):
    sizes = {p: len(t.encode()) for p, t in files.items() if p.startswith("素材/") and p.endswith(".png") and "/归档/" not in p}
    top = max(sizes, key=sizes.get)
    assert sorted(sizes.values())[-1] > sorted(sizes.values())[-2]
    name = top[3:]
    final = {p: t for p, t in files.items() if p not in (top, top + ".meta")}
    final["素材/归档/" + name] = files[top]
    final["素材/归档/" + name + ".meta"] = files[top + ".meta"]
    return [{"all": [name]}, None], final, {"name": name}
'''

    def cmds(i):
        n = i["name"]
        return [["wc -c 素材/*.* | sort -rn | head -4"], ["mv 素材/%s 素材/%s.meta 素材/归档/" % (n, n), "ls 素材 素材/归档"]]
    return case(
        "fs-9342", desc="Two turns: finds the largest file in a folder while an archive subfolder does not count, then moves it and its .meta sidecar into the archive",
        task_type="bulk_edit", family="fam-fs-b12n-bigarchive-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: 素材/归档/旧封面.png is bigger than everything else but archived (素材/README.md). The move has two ends: the picture and its same-named .meta file, nothing else moves.",
        prompts=["素材 目录里（子目录归档里的旧素材不算）体积最大的 .png 文件是哪个？只回答文件名。",
                 "把它连同同名的 .meta 说明文件一起移到 素材/归档 里，别的不动。移完回复 DONE。"],
        alts=["素材里最大的图片是哪张？找到后和它的 .meta 一起归档", "不算归档，最大的 png 叫什么？把它和说明文件放进归档目录", "找出素材目录体积最大的那个 png，再把它与 .meta 都挪进归档",
              "素材库里哪个图片文件最大（归档除外）？归档它和对应的说明文件", "Which .png in 素材 is the biggest (not counting 归档)? Move it and its .meta file into 素材/归档."])


# ---------------------------------------------------------------- doc-9343: missing owner comment -> add it


def doc_9343():
    HDR = "<!-- owner: docs-team -->"
    names = ["安装", "使用", "排错", "备份", "权限", "升级", "术语", "命令表", "错误码", "计费"]

    def gen(rng):
        files = {}
        missing = set(rng.sample(range(10), rng.randint(4, 6)))
        decoy = rng.choice(sorted(missing))
        for i, n in enumerate(names):
            path = "手册/%s.md" % n if i < 7 else "手册/附录/%s.md" % n
            body = ["# " + n, "", "这一页说明" + n + "的做法。", "第二段：" + rng.choice(["先看前提条件。", "注意先备份。", "参见附录。"])]
            if i not in missing:
                rows = [rng.choice([HDR, "<!-- owner: ops-team -->"])] + body
            elif i == decoy:
                rows = ["# " + n, "", HDR] + body[2:]
            else:
                rows = body
            files[path] = lines(rows)
        for n in ("授权", "插件说明"):
            files["手册/_第三方/%s.md" % n] = lines(["# " + n, "", "来自外部项目的文档。"])
        files["手册/README.md"] = lines(["# 手册说明", "", "每页的第一行必须是 owner 注释「" + HDR + "」（ops-team 等其他组的写法也算）。",
                                        "README.md 本身和 _第三方 目录里的页面是外部文档，不用加。"])
        return files

    logic = '''
def solve(files):
    final = dict(files)
    bad = []
    for p, t in sorted(files.items()):
        if p.endswith(".md") and p != "手册/README.md" and "/_第三方/" not in p:
            if not t.splitlines()[0].startswith("<!-- owner"):
                bad.append(p)
                final[p] = "<!-- owner: docs-team -->" + chr(10) + t
    return [{"any": [str(len(bad))]}, None], final, {"n": len(bad)}
'''

    def cmds(i):
        loop = "for f in $(find 手册 -name '*.md' | grep -v _第三方 | grep -v README.md); do head -1 $f | grep -q '^<!-- owner' || %s; done"
        return [[(loop % "echo $f") + " | wc -l"], [loop % "sed -i '1i <!-- owner: docs-team -->' $f", "head -n 2 手册/*.md 手册/附录/*.md"]]
    return case(
        "doc-9343", desc="Two turns: counts manual pages whose first line is not the owner comment (README and third-party pages excluded), then adds the comment to each of them",
        task_type="write_structured", family="fam-doc-b12n-ownerhead-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: one page has the comment on line 3 (not the first line, so it counts), others use another group's comment (counts as present). TR-READONLY: README.md and 手册/_第三方 are not ours (手册/README.md).",
        prompts=["手册 下每个页面的第一行都应该是 owner 注释，哪些页面不用管，手册根目录的说明页里写了。现在有多少个页面的第一行不是这样的注释？只回答数字。",
                 "把「<!-- owner: docs-team -->」加到这些页面的第一行，页面其余内容保持原样。改完回复 DONE。"],
        alts=["手册里有几页没有在第一行写 owner 注释？给它们补上 docs-team 的注释", "统计第一行不是 owner 注释的页面数，然后在这些页面顶部插入那条注释", "手册页面中缺 owner 注释的有多少个？把它们的首行补齐",
              "数一数手册里首行缺 owner 注释的页面，再给这些页面加上「<!-- owner: docs-team -->」", "How many manual pages lack the owner comment on line 1? Add the docs-team comment to each."])


# ---------------------------------------------------------------- log-9344: 5xx per upstream -> rate limit


def log_9344():
    ups = ["api-a", "api-b", "api-c", "api-d"]

    def gen(rng):
        files = {}
        errs = rng.sample(range(14, 45), 4)
        for u, e in zip(ups, errs):
            sts = [rng.choice([500, 502, 503]) for _ in range(e)] + [rng.choice([404, 429]) for _ in range(rng.randint(8, 16))]
            sts += [rng.choice([200, 200, 201, 301]) for _ in range(rng.randint(100, 130))]
            rng.shuffle(sts)
            rows = []
            for i, st in enumerate(sts):
                path = rng.choice(["/v1/orders/%d" % rng.randint(100, 999), "/v1/items/500", "/v1/search", "/v1/users/%d" % rng.randint(10, 99)])
                rows.append("2026-10-%02d %02d:%02d:%02d GET %s %d %dms" % (1 + i % 7, (i * 3) % 24, (i * 7) % 60, (i * 11) % 60, path, st, rng.randint(8, 900)))
            files["access/%s.log" % u] = lines(rows)
            for kind in ("", ".canary", ".dr"):
                files["edge/%s/limits%s.conf" % (u, kind)] = lines(["upstream = " + u, "rate_limit_rps = 100", "burst_rps = 100", "timeout_s = 30"])
        files["edge/_shared/limits.conf"] = lines(["upstream = shared", "rate_limit_rps = 100", "burst_rps = 100"])
        files["edge/README.md"] = lines(["# Edge limits", "", "Each upstream has limits.conf, limits.canary.conf and limits.dr.conf. edge/_shared is common to all and is never edited.",
                                        "burst_rps is a separate knob: it only changes with a ticket."])
        return files

    logic = '''
def solve(files):
    counts = {}
    for p, t in files.items():
        if p.startswith("access/"):
            counts[p[7:-4]] = sum(1 for r in t.splitlines() if int(r.split()[4]) >= 500)
    top = max(counts, key=counts.get)
    assert sorted(counts.values())[-1] > sorted(counts.values())[-2]
    final = dict(files)
    for kind in ("", ".canary", ".dr"):
        p = "edge/%s/limits%s.conf" % (top, kind)
        final[p] = files[p].replace("rate_limit_rps = 100", "rate_limit_rps = 60")
    for kind in (".canary", ".dr"):
        p = "edge/%s/limits%s.conf" % (top, kind)
        final[p] = files[p]
    return [{"all": [top]}, None, None], final, {"up": top}
'''

    def cmds(i):
        u = i["up"]
        fs = " ".join("edge/%s/limits%s.conf" % (u, k) for k in ("", ".canary", ".dr"))
        return [["for f in access/*.log; do echo \"$f $(awk '$5>=500' $f | wc -l)\"; done"],
                ["sed -i 's/^rate_limit_rps = 100$/rate_limit_rps = 60/' " + fs, "grep -rn rate_limit edge/" + u],
                ["sed -i 's/^rate_limit_rps = 60$/rate_limit_rps = 100/' edge/%s/limits.canary.conf edge/%s/limits.dr.conf" % (u, u), "grep -rn rate_limit edge/" + u]]
    return case(
        "log-9344", desc="Three turns: finds the upstream with the most 5xx responses, lowers its rate_limit_rps in three limit files, then restores two of them",
        task_type="count_events", family="fam-log-b12n-upstream5xx-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: the path /v1/items/500 has status 200; 404/429 are not 5xx; the status is the 5th field. TR-READONLY: burst_rps = 100 is a look-alike line and edge/_shared is common (edge/README.md), so `s/= 100/= 60/` is wrong.",
        prompts=["The access directory has one log per upstream; the fifth field of each line is the HTTP status. Which upstream returned the most 5xx responses (status 500-599)? Answer with its name only.",
                 "That upstream is overloaded. Lower rate_limit_rps to 60 in its limits.conf, limits.canary.conf and limits.dr.conf under edge. edge/README.md lists what must stay as it is. Reply DONE when finished.",
                 "Canary and dr run on separate capacity, so put rate_limit_rps back to 100 in those two files; the main limits.conf keeps the cut. Reply DONE when finished."],
        alts=["Find the upstream with the most server errors and throttle it to 60 rps in all three limit files, then undo that for canary and dr.", "Which upstream has the most 5xx? Cut its rate limit to 60, afterwards restore canary and dr.",
              "Check the access logs for the worst upstream (5xx), set its rate_limit_rps to 60 in three files, then revert two of them.", "Highest 5xx count wins: reduce that upstream's rate_limit_rps to 60 and later bring the canary and dr limits back to 100.",
              "找出 5xx 最多的上游，把它三个限流文件的 rate_limit_rps 降到 60，然后恢复 canary 和 dr 的两份"])


# ---------------------------------------------------------------- tab-9345: refunds per store -> flag the store


def tab_9345():
    stores = ["东门店", "西湖店", "南站店", "高新店", "滨江店"]
    regions = ["华东", "华西", "华南", "华北", "华东"]

    def gen(rng):
        files = {}
        for s in stores:
            rows = ["日期,订单,金额,状态"]
            for i in range(rng.randint(35, 55)):
                rows.append("2026-09-%02d,SO%05d,%d,%s" % (1 + i % 28, rng.randint(10000, 99999), rng.randint(20, 900), rng.choice(["已退款", "已退款", "驳回", "处理中"])))
            files["退款/%s.csv" % s] = lines(rows)
        for w in range(1, 5):
            files["门店/看板/第%d周.txt" % w] = lines(["%s 区域：%s 关注：否 客流：%d" % (s, r, rng.randint(900, 5000)) for s, r in zip(stores, regions)])
        for s, r in zip(stores, regions):
            files["门店/档案/%s.md" % s] = lines(["# " + s, "", "区域：" + r, "关注：否", "店长：" + rng.choice(["赵", "钱", "孙", "李"]) + "经理"])
        files["门店/README.md"] = lines(["# 门店资料", "", "看板 每周一张表，每家门店一行；档案 每家门店一页。被点名的门店要在看板的每一周和它的档案里同时改，其他门店不动。"])
        return files

    logic = '''
def solve(files):
    tot = {}
    for p, t in files.items():
        if p.startswith("退款/"):
            tot[p[3:-4]] = sum(int(r.split(",")[2]) for r in t.splitlines()[1:] if r.split(",")[3] == "已退款")
    top = max(tot, key=tot.get)
    assert sorted(tot.values())[-1] - sorted(tot.values())[-2] > 150
    final = dict(files)
    for p, t in files.items():
        if p.startswith("门店/看板/"):
            final[p] = "".join((r.replace("关注：否", "关注：是") if r.startswith(top + " ") else r) + chr(10) for r in t.splitlines())
    final["门店/档案/%s.md" % top] = files["门店/档案/%s.md" % top].replace("关注：否", "关注：是")
    return [{"all": [top]}, None], final, {"store": top}
'''

    def cmds(i):
        s = i["store"]
        return [["for f in 退款/*.csv; do echo \"$f $(awk -F, '$4==\"已退款\" {s+=$3} END{print s}' $f)\"; done"],
                ["sed -i '/^%s /s/关注：否/关注：是/' 门店/看板/*.txt && sed -i 's/^关注：否$/关注：是/' 门店/档案/%s.md" % (s, s), "grep -rn %s 门店" % s]]
    return case(
        "tab-9345", desc="Two turns: finds the store with the largest refunded amount, then flags it as watched in four weekly board sheets and in its profile page",
        task_type="aggregate", family="fam-tab-b12n-refundwatch-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: only 状态=已退款 rows count (驳回 and 处理中 are not refunds). TR-READONLY: other stores keep 关注：否 in every sheet (门店/README.md); the board edit is one line per file, selected by store name.",
        prompts=["退款 目录里每家门店一个 CSV（列：日期,订单,金额,状态）。只算状态为「已退款」的金额，哪家门店合计最高？只回答门店名。",
                 "把这家门店标成重点关注：门店/看板 下每周表里它那一行的「关注：否」，和 门店/档案 里它的档案中的「关注：否」，都改成「关注：是」。其他门店不动。改完回复 DONE。"],
        alts=["已退款金额最高的是哪家店？在看板各周和它的档案里把关注改成是", "按已退款合计找出退款最多的门店，把它标为重点关注（看板四周的表与档案）", "哪家门店退款金额最大（只看已退款）？把看板每周表里它那一行和它的档案都改成关注：是",
              "统计各店已退款金额，对最高的那家把关注状态设为是，看板和档案要一致", "Which store has the highest total of refunded rows? Mark it as watched in every weekly board sheet and in its profile."])


# ---------------------------------------------------------------- scr-9346: scripts without shebang


def scr_9346():
    tops = ["build", "test", "lint", "deploy", "backup", "release", "cleanup", "ci-lint", "ci-test", "ci-deploy"]

    def gen(rng):
        files = {}
        for n in tops:
            body = ["set -e", "echo running %s" % n, "./tools/%s.sh \"$@\"" % n]
            if n.startswith("ci-"):
                rows = body
            else:
                rows = rng.choice([["#!/bin/sh"] + body, ["#!/bin/bash"] + body, body, ["# helper script"] + body, [""] + ["#!/bin/sh"] + body, ["# !/bin/sh"] + body])
            files["scripts/%s.sh" % n] = lines(rows)
        for n in ("fetch", "unpack"):
            files["scripts/vendor/%s.sh" % n] = lines(["set -e", "echo vendored %s" % n])
        files["scripts/README.md"] = lines(["# Scripts", "", "Only the top-level scripts in this folder count. scripts/vendor is third-party code and is never touched.",
                                           "A shebang is a first line starting with #!."])
        return files

    logic = '''
def solve(files):
    bad = [p for p, t in sorted(files.items()) if p.startswith("scripts/") and p.endswith(".sh") and "/vendor/" not in p and not t.splitlines()[0].startswith("#!")]
    assert sum(1 for p in bad if "/ci-" in p) == 3 and len(bad) >= 6
    final = dict(files)
    for p in bad:
        final[p] = "#!/bin/sh" + chr(10) + files[p]
    for p in bad:
        if "/ci-" in p:
            final[p] = files[p]
    return [{"any": [str(len(bad))]}, None, None], final, {"n": len(bad)}
'''
    loop = "for f in scripts/*.sh; do head -n 1 $f | grep -q '^#!' || %s; done"

    def cmds(i):
        return [[(loop % "echo $f") + " | wc -l"], [loop % "sed -i '1i #!/bin/sh' $f", "head -n 1 scripts/*.sh"],
                ["for f in scripts/ci-*.sh; do sed -i '1d' $f; done", "head -n 1 scripts/*.sh"]]
    return case(
        "scr-9346", desc="Three turns: counts top-level shell scripts without a shebang first line, adds the shebang to them, then removes it again from the ci-* scripts",
        task_type="add_flag", family="fam-scr-b12n-shebangadd-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: `# !/bin/sh` (space) and a shebang on line 2 are not shebangs; `#!/bin/bash` is one. TR-READONLY: scripts/vendor is untouched (scripts/README.md). Turn 3 removes exactly the first line of the three ci-* scripts, which had no shebang originally.",
        prompts=["How many shell scripts directly in scripts lack a shebang on their first line (the line must start with #!)? scripts/README.md says which ones are left out. Reply with a bare number.",
                 "Put #!/bin/sh as the first line of each of those scripts and leave the rest of every file as it is. Reply DONE when finished.",
                 "The scripts/ci-*.sh files are checked against fixed hashes, so take the line off those again; the other scripts keep it. Reply DONE when finished."],
        alts=["Count the scripts in scripts whose first line is not a shebang, give them #!/bin/sh, then undo it for the ci scripts.", "Which top-level .sh files have no #! line? Add one, but the ci-* files must end up as they were.",
              "How many scripts need a shebang? Insert #!/bin/sh at the top of each, afterwards strip it from ci-lint, ci-test and ci-deploy.", "Find shell scripts starting without #!, fix them with #!/bin/sh and revert the ci ones.",
              "scripts 下有多少个脚本第一行没有 #!？都补上 #!/bin/sh，再把 ci- 开头的撤掉"])


# ---------------------------------------------------------------- cfg-9347: env keys missing -> append


def cfg_9347():
    keys = ["DB_URL", "DB_POOL", "REDIS_URL", "SENTRY_DSN", "API_TOKEN", "LOG_LEVEL", "SMTP_HOST", "FEATURE_X"]

    def gen(rng):
        files = {"deploy/.env.example": lines(["%s=" % k for k in keys])}
        for env in ("prod", "staging", "dev", "test"):
            others = [k for k in keys if k != "SENTRY_DSN"]
            drop = set(rng.sample(others, rng.randint(1, 3)))
            rows = []
            for k in keys:
                if k == "SENTRY_DSN" and env != "test":
                    continue
                if k in drop:
                    if rng.random() < 0.5:
                        rows.append("# %s=old-value" % k)
                    continue
                rows.append("%s=%s-%s" % (k, env, rng.randint(1, 99)))
            files["deploy/env/%s.env" % env] = lines(rows)
        files["deploy/README.md"] = lines(["# Deploy", "", "deploy/.env.example lists every key each environment needs. A commented-out line (# KEY=...) counts as not set.",
                                          "test.env is generated by CI: it is neither counted nor edited."])
        return files

    logic = '''
def solve(files):
    keys = [r.split("=")[0] for r in files["deploy/.env.example"].splitlines()]
    final = dict(files)
    n = 0
    for env in ("prod", "staging", "dev"):
        p = "deploy/env/%s.env" % env
        have = {r.split("=")[0] for r in files[p].splitlines()}
        miss = [k for k in keys if k not in have]
        n += len(miss)
        final[p] = files[p] + "".join(k + "=CHANGE_ME" + chr(10) for k in miss)
    for env in ("staging", "dev"):
        p = "deploy/env/%s.env" % env
        final[p] = final[p].replace("SENTRY_DSN=CHANGE_ME" + chr(10), "")
    return [{"any": [str(n)]}, None, None], final, {"n": n}
'''
    loop = 'for e in prod staging dev; do for k in $(cut -d= -f1 deploy/.env.example); do grep -q "^$k=" deploy/env/$e.env || %s; done; done'

    def cmds(i):
        return [[(loop % 'echo "$e $k"') + " | wc -l"], [loop % 'echo "$k=CHANGE_ME" >> deploy/env/$e.env', "tail -n 4 deploy/env/prod.env deploy/env/staging.env deploy/env/dev.env"],
                ["sed -i '/^SENTRY_DSN=CHANGE_ME$/d' deploy/env/staging.env deploy/env/dev.env", "grep -n SENTRY deploy/env/*.env"]]
    return case(
        "cfg-9347", desc="Three turns: counts config keys that environment files lack compared with an example file, appends them with a placeholder, then removes one of them again from two files",
        task_type="missing_keys", family="fam-cfg-b12n-envkeys-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: `# REDIS_URL=old-value` is commented out, so the key is not set. TR-READONLY: deploy/env/test.env is generated by CI (deploy/README.md): neither counted nor edited. SENTRY_DSN is absent from prod, staging and dev, so turn 3 restores the original state of two files.",
        prompts=["deploy/.env.example 列出了每个环境都要有的配置项。deploy/env 下 prod、staging、dev 三个环境文件各自少了哪些项？把三个文件各自少的项数加起来（同一个键在两个文件里都没有，就算两项），注释掉的算没有；其他文件的说明看 deploy/README.md。只回答总数。",
                 "把少的项补到这三个文件的末尾，每项一行，写成 KEY=CHANGE_ME，顺序按 .env.example。改完回复 DONE。",
                 "SENTRY_DSN 在 staging 和 dev 里用不上，把刚补进去的那两行删掉，prod 里的保留。改完回复 DONE。"],
        alts=["对照 .env.example，三个环境一共缺几项？补成 CHANGE_ME，之后 staging 和 dev 的 SENTRY_DSN 再去掉", "统计 prod、staging、dev 比示例文件少的配置项总数，追加到文件末尾，再把 SENTRY_DSN 从后两个文件里删除",
              "各环境文件比 .env.example 缺多少个键？用 CHANGE_ME 补齐，然后只保留 prod 的 SENTRY_DSN", "数出三个环境缺少的配置项（注释不算），补上占位值，最后撤掉 staging 与 dev 的 SENTRY_DSN",
              "How many keys from .env.example are missing across prod, staging and dev? Append them as KEY=CHANGE_ME, then drop SENTRY_DSN from staging and dev again."])


# ---------------------------------------------------------------- fs-9348: most .tmp files -> clean that project


def fs_9348():
    projs = ["alpha", "beta", "gamma", "delta", "omega"]

    def gen(rng):
        files = {}
        counts = rng.sample(range(5, 16), 5)
        for p, c in zip(projs, counts):
            files["projects/%s/src.txt" % p] = "main of %s\n" % p
            files["projects/%s/notes.tmp.bak" % p] = "backup of notes\n"
            files["projects/_trash/%s/README.txt" % p] = "moved temp files of %s\n" % p
            for i in range(c):
                name = "scratch%d.tmp" % i if i % 5 != 4 else "pin%d.keep.tmp" % i
                where = "cache/" if i % 2 else ""
                files["projects/%s/%s%s" % (p, where, name)] = "tmp %d\n" % i
            files["projects/%s/cache/index.txt" % p] = "cache index\n"
        files["projects/README.md"] = lines(["# Projects", "", "Each folder is one project (projects/_trash is not a project). Files named *.keep.tmp are pinned and never move.",
                                            "*.tmp.bak files are backups, not temp files. Moved temp files go to projects/_trash/<project>/ (flat, the folders exist)."])
        return files

    logic = '''
def solve(files):
    cnt = {}
    for p in files:
        if p.startswith("projects/") and p.endswith(".tmp") and not p.startswith("projects/_trash/"):
            cnt[p.split("/")[1]] = cnt.get(p.split("/")[1], 0) + 1
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] > sorted(cnt.values())[-2]
    final = {}
    for p, t in files.items():
        if p.startswith("projects/" + top + "/") and p.endswith(".tmp") and not p.endswith(".keep.tmp"):
            final["projects/_trash/%s/%s" % (top, p.split("/")[-1])] = t
        else:
            final[p] = t
    assert len(final) == len(files)
    return [{"all": [top]}, None], final, {"proj": top}
'''

    def cmds(i):
        t = i["proj"]
        return [["for p in alpha beta gamma delta omega; do echo \"$(find projects/$p -name '*.tmp' | wc -l) $p\"; done"],
                ["for f in $(find projects/%s -name '*.tmp' | grep -v '\\.keep\\.tmp$'); do mv $f projects/_trash/%s/; done" % (t, t), "find projects/%s projects/_trash/%s -type f" % (t, t)]]
    return case(
        "fs-9348", desc="Two turns: finds the project folder with the most .tmp files, then moves its unpinned .tmp files from the root and the cache subfolder into a trash folder while pinned files and other projects stay",
        task_type="scoped_delete", family="fam-fs-b12n-tmpproject-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: notes.tmp.bak ends in .bak, not .tmp; projects/_trash is not a project. TR-READONLY: *.keep.tmp stay (projects/README.md), other projects' .tmp files stay; turn 1 counts every file ending in .tmp, pinned ones included.",
        prompts=["Under projects each folder is one project (projects/_trash is not one). Which project has the most files whose name ends in .tmp (its cache subfolder included)? Reply with the project name only.",
                 "Clean up that project: move its .tmp files, from the project folder and from cache, into projects/_trash/<project>/, except the pinned ones described in projects/README.md. Other projects stay as they are. Reply DONE when finished."],
        alts=["Which project holds the most .tmp files? Move them (pinned ones excepted) into its folder under projects/_trash.", "Find the project with the biggest pile of .tmp files and sweep them into the trash folder, pinned files excepted.",
              "Count .tmp files per project; for the winner move every unpinned .tmp, cache ones included, to projects/_trash/<project>/.", "Pick the project with the most temp files and relocate them to its _trash folder, but leave *.keep.tmp and the other projects.",
              "projects 里哪个项目的 .tmp 文件最多？把它的 .tmp 挪进 projects/_trash 下对应目录，置顶的 .keep.tmp 留下"])


# ---------------------------------------------------------------- tab-9349: cheapest supplier -> update two files


def tab_9349():
    sups = ["星辰", "远航", "明达", "恒信"]

    def gen(rng):
        files = {}
        prices = rng.sample(range(31, 80), 4)
        for s, pr in zip(sups, prices):
            rows = ["货号,单价,起订量", "A-100,%d,%d" % (pr, rng.choice([50, 100, 200])), "A-1000,%d,100" % rng.randint(10, 80), "A-100X,%d,100" % rng.randint(10, 80),
                    "B-200,%d,50" % rng.randint(10, 90), "C-300,%d,20" % rng.randint(10, 90)]
            files["报价/%s.csv" % s] = lines(rows)
        order = sorted(range(4), key=lambda i: prices[i])
        cur = sups[order[2]]
        files["采购/默认供应商.csv"] = lines(["货号,供应商", "A-100," + cur, "B-200,远航", "C-300,明达"])
        for d in range(1, 6):
            files["采购/下单/2026-10-%02d.csv" % d] = lines(["货号,供应商,单价,数量", "B-200,远航,41,%d" % rng.randint(20, 90), "A-100,%s,%d,%d" % (cur, prices[order[2]], rng.choice([120, 240, 360])),
                                                          "A-1000,明达,%d,10" % rng.randint(10, 80), "C-300,明达,52,%d" % rng.randint(10, 40)])
        files["采购/README.md"] = lines(["# 采购", "", "默认供应商.csv 和 下单 里每天的单子，同一货号的供应商必须一致；下单单价取当前报价，数量是各天自己的。"])
        return files

    logic = '''
def solve(files):
    best = None
    for p, t in files.items():
        if p.startswith("报价/"):
            for r in t.splitlines()[1:]:
                f = r.split(",")
                if f[0] == "A-100" and (best is None or int(f[1]) < best[1]):
                    best = (p[3:-4], int(f[1]))
    s, price = best
    final = dict(files)
    final["采购/默认供应商.csv"] = "".join(("A-100," + s if r.startswith("A-100,") else r) + chr(10) for r in files["采购/默认供应商.csv"].splitlines())
    for p, t in files.items():
        if p.startswith("采购/下单/"):
            rows = []
            for r in t.splitlines():
                f = r.split(",")
                rows.append(",".join(["A-100", s, str(price), f[3]]) if f[0] == "A-100" else r)
            final[p] = "".join(r + chr(10) for r in rows)
    return [{"all": [s, str(price)]}, None], final, {"s": s, "price": price}
'''

    def cmds(i):
        s, pr = i["s"], i["price"]
        return [["grep '^A-100,' 报价/*.csv"],
                ["sed -i 's/^A-100,.*$/A-100,%s/' 采购/默认供应商.csv && sed -i 's/^A-100,[^,]*,[^,]*,/A-100,%s,%d,/' 采购/下单/*.csv" % (s, s, pr), "grep -rn '^A-100,' 采购"]]
    return case(
        "tab-9349", desc="Two turns: finds the supplier with the lowest quote for an exact part number among look-alike numbers, then switches the default-supplier table and five daily order sheets to that supplier and price",
        task_type="rank", family="fam-tab-b12n-cheapsupplier-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: A-1000 and A-100X are different part numbers that start with A-100 (a prefix grep returns them too). TR-READONLY: other part numbers and each day's order quantity stay (采购/README.md).",
        prompts=["报价 目录里每个供应商一个 CSV（列：货号,单价,起订量）。货号正好是 A-100 的行里，谁的单价最低？回答供应商名和单价。",
                 "A-100 改用这家供应商：采购/默认供应商.csv 里 A-100 的供应商，采购/下单 下每天的单子里 A-100 的供应商和单价，都按报价改过去，数量各天保持不变，其他货号不动。改完回复 DONE。"],
        alts=["A-100 哪家报价最低？把默认供应商表和每天的下单表都换成它", "找出 A-100 的最低单价供应商，默认供应商和下单目录里每天的 A-100 都改成这家和它的价格", "货号 A-100（不含 A-1000、A-100X）谁最便宜？更新默认供应商与各天下单表",
              "比较各家 A-100 的单价，选最低的，把采购目录下所有文件里 A-100 的供应商（和下单单价）更新", "Who quotes the lowest price for exactly A-100? Switch A-100 in the default-supplier file and every daily order sheet to that supplier and price."])


# ---------------------------------------------------------------- log-9350: day with most WARN -> copy logs


def log_9350():
    def gen(rng):
        files = {}
        warns = rng.sample(range(10, 34), 6)
        top_day = rng.choice([3, 4, 5, 6])
        days = list(range(1, 8))
        counts = {}
        pool = sorted(warns)
        counts[top_day] = pool.pop()
        rest = [d for d in days if d != top_day]
        for d, w in zip(rest, pool + [rng.randint(5, 9)]):
            counts[d] = w
        for d in days:
            levels = ["WARN"] * counts[d] + ["ERROR"] * rng.randint(2, 8)
            levels += ["INFO"] * (rng.randint(60, 80) - len(levels))
            rng.shuffle(levels)
            rows = []
            for i, lv in enumerate(levels):
                msg = {"WARN": rng.choice(["disk usage 82%", "slow query 1800ms", "retry scheduled"]),
                       "ERROR": rng.choice(["job failed", "write refused"]),
                       "INFO": rng.choice(["job started", "job done", "cache WARN-level=off"])}[lv]
                rows.append("2026-10-%02d %02d:%02d:%02d %s %s" % (d, (i * 3) % 24, (i * 7) % 60, (i * 11) % 60, lv, msg))
            files["logs/app-2026-10-%02d.log" % d] = lines(rows)
        files["待查/README.md"] = lines(["# 待查", "", "这里只放需要排查的日志副本；原日志留在 logs 里，不要移动。"])
        return files

    logic = '''
def solve(files):
    cnt = {}
    for p, t in files.items():
        if p.startswith("logs/"):
            cnt[p[9:19]] = sum(1 for r in t.splitlines() if r.split()[2] == "WARN")
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] > sorted(cnt.values())[-2]
    day = int(top[-2:])
    prev = "2026-10-%02d" % (day - 1)
    final = dict(files)
    for d in (top, prev):
        final["待查/app-%s.log" % d] = files["logs/app-%s.log" % d]
    return [{"all": [top]}, None], final, {"top": top, "prev": prev}
'''

    def cmds(i):
        return [["for f in logs/*.log; do echo \"$f $(awk '$3==\"WARN\"' $f | wc -l)\"; done"],
                ["cp logs/app-%s.log logs/app-%s.log 待查/" % (i["prev"], i["top"]), "ls 待查 logs"]]
    return case(
        "log-9350", desc="Two turns: finds the day whose log has the most WARN-level lines, then copies that day's log and the previous day's log into a review folder",
        task_type="count_events", family="fam-log-b12n-warnday-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: INFO lines contain `WARN-level=off`; only the third field is the level. TR-READONLY: the originals stay in logs (待查/README.md), so it is a copy, not a move; exactly two copies.",
        prompts=["logs 目录每天一个日志文件，每行第三个字段是日志级别。哪一天级别为 WARN 的行最多？只回答日期，写成 2026-10-04 这样的格式。",
                 "把那一天和前一天的日志各复制一份到 待查 目录，原文件留在 logs 里。复制完回复 DONE。"],
        alts=["哪天的 WARN 最多？把当天和前一天的日志复制到待查", "找出 WARN 行数最多的日期，拷贝这天和前一天的两份日志进 待查", "WARN 级别最密集的是哪一天？把它和前一天的日志各留一份副本在待查里",
              "按日志级别字段统计 WARN，最多的那天和它前一天的文件复制到待查目录", "Which day has the most WARN lines? Copy that day's log and the previous day's into 待查, leaving the originals."])


# ---------------------------------------------------------------- doc-9351: atlas pin -> bump -> partial revert


def doc_9351():
    def gen(rng):
        files = {}
        pins = lambda v: "pip install atlas==%s" % v
        guide = {"install": "2.3.4", "quickstart": "2.3.0", "upgrade": "2.2.9", "faq": None}
        for n, v in guide.items():
            rows = ["# " + n, "", "Steps for " + n + "."] + ([pins(v)] if v else ["No pinned versions here."])
            files["docs/guide/%s.md" % n] = lines(rows)
        files["docs/api/client.md"] = lines(["# client", "", pins("2.3.12"), "Also tested with atlas==2.30.1 in the lab."])
        files["docs/api/server.md"] = lines(["# server", "", "Server needs " + "atlas==2.4.0" + " or newer."])
        for n in ("runbook", "onboarding", "tools"):
            files["docs/internal/%s.md" % n] = lines(["# " + n, "", pins("2.3.1")] + (["pip install atlas==2.3.1 --upgrade"] if n == "tools" else []))
        files["docs/internal/notes.md"] = lines(["# notes", "", "Nothing pinned."])
        files["docs/CHANGELOG.md"] = lines(["# Changelog", "", "2.3.9: first release with " + "atlas==2.3.9", "2.2.0: older"])
        files["docs/archive/old-install.md"] = lines(["# old install", "", pins("2.3.2")])
        files["docs/README.md"] = lines(["# Docs", "", "docs/archive and docs/CHANGELOG.md are history: they never count and are never edited.",
                                        "A pin means the exact text atlas==2.3.N with N a number."])
        return files

    logic = '''
import re
def solve(files):
    pat = re.compile(r"atlas==2\\.3\\.[0-9]+")
    hit = [p for p, t in sorted(files.items()) if p.endswith(".md") and "/archive/" not in p and not p.endswith("CHANGELOG.md") and pat.search(t)]
    final = dict(files)
    for p in hit:
        final[p] = pat.sub("atlas==2.4.0", files[p])
    for p in hit:
        if p.startswith("docs/internal/"):
            final[p] = files[p]
    return [{"any": [str(len(hit))]}, None, None], final, {"n": len(hit)}
'''
    base = "grep -rlE 'atlas==2\\.3\\.[0-9]+' docs | grep -v archive | grep -v CHANGELOG"

    def cmds(i):
        return [[base + " | wc -l"], [base + " | xargs sed -i -E 's/atlas==2\\.3\\.[0-9]+/atlas==2.4.0/g'", "grep -rn 'atlas==' docs"],
                ["grep -rl 'atlas==2.4.0' docs/internal | xargs sed -i 's/atlas==2\\.4\\.0/atlas==2.3.1/g'", "grep -rn 'atlas==' docs/internal"]]
    return case(
        "doc-9351", desc="Three turns: counts pages that pin atlas==2.3.N, bumps those pins to 2.4.0 outside history pages, then reverts the internal pages to their old pin",
        task_type="extract_items", family="fam-doc-b12n-atlaspin-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: atlas==2.30.1 and atlas==2.2.9 are not 2.3.N pins; atlas==2.4.0 is already new. TR-READONLY: docs/archive and docs/CHANGELOG.md are history (docs/README.md). Internal pages all used 2.3.1, so turn 3 has one correct target text.",
        prompts=["How many pages under docs pin atlas to a 2.3.N version (the exact text atlas==2.3.N)? docs/README.md says which pages are history and left out. Reply with a bare number.",
                 "Bump those pins to atlas==2.4.0 in every page that counts, and leave every other line as it is. Reply DONE when finished.",
                 "The internal tooling is not ready for 2.4.0, so under docs/internal set the pins back to atlas==2.3.1. Reply DONE when finished."],
        alts=["Count the doc pages pinned to atlas 2.3.x, upgrade them to 2.4.0 (not history), then restore docs/internal to 2.3.1.", "How many pages use atlas==2.3.N? Move them to 2.4.0 and afterwards put the internal ones back on 2.3.1.",
              "Find pages pinned to atlas 2.3.something, switch the pin to 2.4.0 except archive and changelog, then revert internal.", "Number of non-history docs pinning atlas==2.3.N; update to 2.4.0; internal pages go back to 2.3.1.",
              "docs 里有多少页固定了 atlas==2.3.N？都改成 2.4.0（历史页除外），再把 docs/internal 改回 2.3.1"])


# ---------------------------------------------------------------- cfg-9352: low pool_size -> raise


def cfg_9352():
    svcs = ["billing", "search", "auth", "feed", "chat", "media", "push"]

    def gen(rng):
        files = {}
        low = set(rng.sample(range(7), 3))
        for i, s in enumerate(svcs):
            n = rng.randint(3, 9) if i in low else rng.randint(12, 40)
            files["svc/%s/config.toml" % s] = lines(["[pool]", "pool_size = %d" % n, "max_pool_size = 50", "pool_size_min = 2", "timeout = 30"])
            files["svc/%s/config.staging.toml" % s] = lines(["[pool]", "pool_size = %d" % rng.randint(2, 20), "max_pool_size = 50", "pool_size_min = 2", "timeout = 30"])
        files["svc/_template/config.toml"] = lines(["[pool]", "pool_size = 4", "max_pool_size = 50", "pool_size_min = 2", "timeout = 30"])
        files["svc/_template/config.staging.toml"] = lines(["[pool]", "pool_size = 4", "max_pool_size = 50", "pool_size_min = 2", "timeout = 30"])
        files["svc/README.md"] = lines(["# 服务配置", "", "每个服务目录里有 config.toml（生产）和 config.staging.toml。_template 是新服务的复制模板，保持原样。",
                                       "max_pool_size 和 pool_size_min 是别的参数，不要动。"])
        return files

    logic = '''
def solve(files):
    low = []
    for p, t in sorted(files.items()):
        if p.endswith("/config.toml") and "/_template/" not in p:
            n = int([r for r in t.splitlines() if r.startswith("pool_size = ")][0].split(" = ")[1])
            if n < 10:
                low.append(p.split("/")[1])
    final = dict(files)
    for s in low:
        for k in ("config.toml", "config.staging.toml"):
            p = "svc/%s/%s" % (s, k)
            final[p] = "".join(("pool_size = 10" if r.startswith("pool_size = ") else r) + chr(10) for r in files[p].splitlines())
    return [{"all": low}, None], final, {"low": low}
'''

    def cmds(i):
        fs = " ".join("svc/%s/config.toml svc/%s/config.staging.toml" % (s, s) for s in i["low"])
        return [["grep '^pool_size = ' svc/*/config.toml"], ["sed -i 's/^pool_size = .*$/pool_size = 10/' " + fs, "grep -rn '^pool_size = ' svc"]]
    return case(
        "cfg-9352", desc="Two turns: lists services whose production pool_size is below 10, then sets pool_size to 10 in both their production and staging TOML files",
        task_type="edit_value", family="fam-cfg-b12n-lowpool-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: max_pool_size and pool_size_min are different keys; svc/_template has pool_size = 4 but is a template (svc/README.md). Staging files may hold their own values; only low services' two files change.",
        prompts=["svc 下每个服务目录里的 config.toml 都有 pool_size。哪些服务的 pool_size 小于 10？把服务名都列出来，哪些目录不算看 svc/README.md。",
                 "把这几个服务的 config.toml 和 config.staging.toml 里的 pool_size 都改成 10，只改 pool_size 这一行，别的键和别的服务不动。改完回复 DONE。"],
        alts=["哪些服务的连接池太小（pool_size 低于 10）？把它们的生产和 staging 配置都调到 10", "找出 pool_size 不足 10 的服务，两份配置里的 pool_size 都设成 10", "svc 里 pool_size 小于 10 的有哪几个？统一改为 10（config.toml 与 config.staging.toml）",
              "列出池子小于 10 的服务，然后给它们的两份 toml 都把 pool_size 提到 10", "Which services have pool_size below 10 in config.toml? Set pool_size to 10 in their config.toml and config.staging.toml."])


# ---------------------------------------------------------------- code-9353: TODO per package -> tag owner -> partial revert


def code_9353():
    pkgs = ["ingest", "export", "auth", "billing", "search"]

    def gen(rng):
        files = {}
        totals = rng.sample(range(4, 13), 5)
        for p, tot in zip(pkgs, totals):
            split = [1, 1, 1]
            for _ in range(tot - 3):
                split[rng.randrange(3)] += 1
            for name, k in zip(("main", "utils", "io"), split):
                rows = ["import os", ""]
                for j in range(k):
                    rows += ["def step_%d():" % j, "    # TODO: %s" % rng.choice(["handle timeouts", "validate input", "log the failure", "add a retry"]), "    return os.getcwd()", ""]
                rows.append("# todo: lowercase notes are not tracked")
                files["src/%s/%s.py" % (p, name)] = lines(rows)
            files["src/%s/test_main.py" % p] = lines(["def test_x():", "    # TODO: more cases", "    # TODO: slow test", "    assert True"])
        files["src/README.md"] = lines(["# src", "", "Each folder is a package. Only the .py files that are not test_*.py count; test files are never edited.",
                                       "The marker is the exact text '# TODO:'."])
        return files

    logic = '''
def solve(files):
    cnt = {}
    for p, t in files.items():
        if p.startswith("src/") and p.endswith(".py") and "/test_" not in p:
            cnt[p.split("/")[1]] = cnt.get(p.split("/")[1], 0) + t.count("# TODO:")
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] > sorted(cnt.values())[-2]
    final = dict(files)
    for n in ("main",):
        p = "src/%s/%s.py" % (top, n)
        final[p] = files[p].replace("# TODO:", "# TODO(maya):")
    return [{"all": [top]}, None, None], final, {"pkg": top}
'''

    def cmds(i):
        p = i["pkg"]
        return [["for p in $(ls src); do [ -d src/$p ] && echo \"$(cat src/$p/main.py src/$p/utils.py src/$p/io.py | grep -c '# TODO:') $p\"; done"],
                ["sed -i 's/# TODO:/# TODO(maya):/' src/%s/main.py src/%s/utils.py src/%s/io.py" % (p, p, p), "grep -rn 'TODO' src/" + p],
                ["sed -i 's/# TODO(maya):/# TODO:/' src/%s/utils.py src/%s/io.py" % (p, p), "grep -rn 'TODO' src/" + p]]
    return case(
        "code-9353", desc="Three turns: finds the package with the most TODO markers outside tests, tags those markers with an owner in its three modules, then removes the tag from two of them",
        task_type="count_markers", family="fam-code-b12n-todoowner-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: test_main.py files hold two TODOs each (not counted, never edited per src/README.md) and `# todo:` in lowercase is not a marker. Turn 3 touches only utils.py and io.py; main.py keeps the owner tag.",
        prompts=["Under src each folder is a package. Which package has the most '# TODO:' markers? src/README.md says which files count. Reply with the package name only.",
                 "In that package, tag its TODO comments with the owner: turn '# TODO:' into '# TODO(maya):' in its .py files, leaving the test files as src/README.md says. Reply DONE when finished.",
                 "maya only owns main.py, so put plain '# TODO:' back in utils.py and io.py of that package. Reply DONE when finished."],
        alts=["Which package has the most TODO markers (tests excluded)? Tag them TODO(maya), then un-tag utils.py and io.py.", "Find the package with the most '# TODO:' lines and assign them to maya, except in utils.py and io.py afterwards.",
              "Count TODO comments per package without test files; add (maya) to the winner's TODOs and then restore utils.py and io.py.", "Top TODO package? Mark its TODOs as maya's, then maya hands back utils.py and io.py.",
              "src 里哪个包的 '# TODO:' 最多（测试文件不算）？给它的 TODO 标上 maya，之后把 utils.py 和 io.py 的标记去掉"])


# ---------------------------------------------------------------- fs-9354: duplicate photos -> delete copies


def fs_9354():
    def gen(rng):
        files = {}
        orig = ["IMG_%03d.jpg" % (101 + i) for i in range(8)]
        body = {n: lines(["EXIF %s" % n, "taken 2026-09-%02d" % rng.randint(1, 28), "pixels %d" % rng.randint(1000, 9000), "hash-seed %d" % rng.randint(100000, 999999)]) for n in orig}
        for n in orig:
            files["照片/原始/" + n] = body[n]
        dup = rng.sample(orig, 4)
        for i, n in enumerate(dup):
            files["照片/副本/" + rng.choice(["复制_", "backup_", "拷贝-"]) + str(i) + "_" + n] = body[n]
        for n in rng.sample([x for x in orig if x not in dup], 3):
            files["照片/副本/修图_" + n] = body[n].replace("pixels", "retouched pixels")
        files["照片/副本/" + orig[0]] = body[orig[1]].replace("EXIF", "EXIF edited")
        files["照片/README.md"] = lines(["# 照片库", "", "原始 是底片库。副本 里内容和 原始 中某个文件逐字相同的是重复文件，可以删；内容有差别的是修图版本，要保留。",
                                        "比较看内容，不看文件名。"])
        return files

    logic = '''
def solve(files):
    origs = {t for p, t in files.items() if p.startswith("照片/原始/")}
    dups = [p for p, t in sorted(files.items()) if p.startswith("照片/副本/") and t in origs]
    final = {p: t for p, t in files.items() if p not in dups}
    return [{"any": [str(len(dups))]}, None], final, {"n": len(dups)}
'''
    loop = 'for f in 照片/副本/*; do h=$(md5sum $f | cut -d" " -f1); md5sum 照片/原始/* | grep -q "^$h" && %s; done'

    def cmds(i):
        return [[(loop % "echo $f") + " | wc -l"], [loop % "rm $f", "ls 照片/副本"]]
    return case(
        "fs-9354", desc="Two turns: counts files in a copies folder whose content equals some original, then deletes exactly those while edited versions and the originals stay",
        task_type="duplicates", family="fam-fs-b12n-photodups-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: names do not tell: copies have new names, and 副本/IMG_101.jpg shares a name with an original but has different content; retouched versions differ by one line. TR-READONLY: 原始 stays untouched (照片/README.md).",
        prompts=["照片/副本 里有几个文件的内容和 照片/原始 里某个文件逐字相同？比较看内容，不看文件名。只回答数字。",
                 "把这些内容相同的副本删掉，内容不同的副本和 原始 里的文件都保留。删完回复 DONE。"],
        alts=["副本目录里有多少文件是原始文件的逐字拷贝？把它们删除", "统计内容与原始完全一致的副本个数，然后删掉这些副本，修图版本留着", "照片/副本 中有几个文件和原始里的某个文件内容一样？删去这些，其余不动",
              "按内容比对副本和原始，数出重复的副本并清理掉", "How many files in 照片/副本 are byte-identical to some file in 照片/原始? Delete exactly those copies."])


# ---------------------------------------------------------------- tab-9355: category totals -> write two files


def tab_9355():
    cats = ["饮料", "零食", "日用", "生鲜", "数码"]

    def gen(rng):
        files = {}
        for m in (7, 8, 9, 10):
            rows = ["品类,金额"]
            for _ in range(rng.randint(40, 60)):
                c = rng.choice(cats)
                rows.append("%s,%d" % (c, rng.randint(50, 900) * (1 if rng.random() > 0.08 else -1)))
            files["订单/2026-%02d.csv" % m] = lines(rows)
        files["汇总/2025年.csv"] = lines(["品类,金额", "饮料,100000", "零食,80000"])
        files["汇总/README.md"] = lines(["# 汇总", "", "按品类拆分：每个品类一个文件 汇总/<品类>.csv，第一行表头「品类,金额」，其后是该品类在 订单 四个月文件里的行，保持原来的先后顺序（先 7 月后 10 月，月内顺序不变）。",
                                        "结论.txt：只有一行，格式「最大品类：X」。2025年.csv 是去年的文件，不动。"])
        return files

    logic = '''
def solve(files):
    tot, rows = {}, {}
    for p, t in sorted(files.items()):
        if p.startswith("订单/"):
            for r in t.splitlines()[1:]:
                c, v = r.split(",")
                tot[c] = tot.get(c, 0) + int(v)
                rows.setdefault(c, []).append(r)
    order = sorted(tot, key=lambda c: -tot[c])
    assert tot[order[0]] > tot[order[1]]
    final = dict(files)
    for c in tot:
        final["汇总/%s.csv" % c] = "品类,金额" + chr(10) + "".join(r + chr(10) for r in rows[c])
    final["汇总/结论.txt"] = "最大品类：" + order[0] + chr(10)
    return [{"all": [order[0]]}, None], final, {"top": order[0], "cats": sorted(tot)}
'''

    def cmds(i):
        loop = "for c in %s; do (echo '品类,金额'; cat 订单/*.csv | grep \"^$c,\") > 汇总/$c.csv; done" % " ".join(i["cats"])
        return [["cat 订单/*.csv | grep -v '^品类' | awk -F, '{s[$1]+=$2} END{for(k in s) print k\",\"s[k]}' | sort -t, -k2 -nr"],
                [loop + " && echo '最大品类：%s' > 汇总/结论.txt" % i["top"], "ls 汇总; cat 汇总/结论.txt"]]
    return case(
        "tab-9355", desc="Two turns: finds the product category with the largest signed total over four monthly order files, then splits the rows into one CSV per category and writes the winner into a conclusion file",
        task_type="write_summary", family="fam-tab-b12n-categorysplit-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-MULTISRC", "TR-READONLY"],
        trap_note="- TR-MULTISRC: four monthly files, every one has its own header line. Negative amounts are returns and count in the total (汇总/README.md). TR-READONLY: 汇总/2025年.csv is last year's file and stays.",
        prompts=["订单 目录里 7 到 10 月各有一个文件（列：品类,金额），金额里的负数是退货冲减，要算进去。这四个月合计下来，哪个品类金额最大？只回答品类名。",
                 "按 汇总/README.md 的格式，把订单按品类拆开，每个品类写一个 汇总/<品类>.csv，再把最大品类写进 汇总/结论.txt。写完回复 DONE。"],
        alts=["四个月订单按品类汇总，谁最大？再把每个品类的行拆成单独文件并写结论", "统计 7 到 10 月各品类金额（负数计入），找出最大的，然后按品类生成 csv 和结论.txt", "哪个品类四个月加起来最多？按 README 的格式拆分出各品类文件并写结论文件",
              "把订单目录的四个月数据按品类求和，最大品类回答出来，并把各品类的行分别写入汇总里的文件", "Which category has the largest total over the four monthly order files (negatives count)? Then split the rows into one CSV per category in 汇总 and write 结论.txt."])


# ---------------------------------------------------------------- log-9356: OOM hosts -> restart queue


def log_9356():
    hosts = ["web-1", "web-2", "web-3", "web-4", "db-1", "db-2", "cache-1", "job-1"]

    def gen(rng):
        files = {}
        oom = set(rng.sample(range(7), 3))
        for i, h in enumerate(hosts):
            rows = []
            hit = [rng.randrange(40, 70)] if i in oom else []
            for j in range(rng.randint(80, 110)):
                if j in hit:
                    rows.append("2026-10-05 03:%02d:%02d %s kernel: Out of memory: Killed process %d (java) OOM-killed" % (j % 60, (j * 7) % 60, h, rng.randint(1000, 9999)))
                else:
                    rows.append("2026-10-05 03:%02d:%02d %s %s" % (j % 60, (j * 7) % 60, h, rng.choice(
                        ["kernel: oom_score_adj=0 for pid 411", "systemd: Started session", "app: request ok", "kernel: memory cgroup stats ok", "app: gc pause 40ms"])))
            files["logs/%s.log" % h] = lines(rows)
            files["inventory/%s.yaml" % h] = lines(["host: " + h, "restart: none", "zone: " + rng.choice(["a", "b"])])
        files["inventory/restart.list"] = lines(["job-1"])
        files["inventory/README.md"] = lines(["# Inventory", "", "restart.list is the restart queue: one host per line, append only, alphabetical within one batch.",
                                             "A host that is queued also gets restart: pending in its own yaml."])
        return files

    logic = '''
def solve(files):
    oom = sorted(p[5:-4] for p, t in files.items() if p.startswith("logs/") and "OOM-killed" in t)
    final = dict(files)
    final["inventory/restart.list"] = files["inventory/restart.list"] + "".join(h + chr(10) for h in oom)
    for h in oom:
        p = "inventory/%s.yaml" % h
        final[p] = files[p].replace("restart: none", "restart: pending")
    return [{"all": oom}, None], final, {"oom": oom}
'''

    def cmds(i):
        o = i["oom"]
        loop = "; ".join("echo %s >> inventory/restart.list; sed -i 's/^restart: none$/restart: pending/' inventory/%s.yaml" % (h, h) for h in o)
        return [["grep -c 'OOM-killed' logs/*.log"], [loop, "cat inventory/restart.list; grep -n restart: inventory/*.yaml"]]
    return case(
        "log-9356", desc="Two turns: lists the hosts whose logs contain an OOM-killed line, then queues them in a restart list and flips their inventory status",
        task_type="locate_error", family="fam-log-b12n-oomhosts-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: `oom_score_adj=0` lines are not OOM kills; only the exact text OOM-killed counts. TR-READONLY: hosts without a kill keep restart: none; job-1 is already queued and stays the first line (inventory/README.md: append only).",
        prompts=["The logs folder has one log per host. Which hosts logged at least one OOM-killed line? List their names.",
                 "Queue those hosts for a restart: append each name to inventory/restart.list (alphabetical order, one per line, the existing line stays), and change restart: none to restart: pending in each of those hosts' files under inventory. Other hosts stay as they are. Reply DONE when finished."],
        alts=["Which hosts were hit by the OOM killer? Add them to the restart list and set restart: pending on their inventory files.", "Find hosts with an OOM-killed message, append them to restart.list and mark them pending in inventory.",
              "List hosts whose logs show OOM-killed; queue them (restart.list plus restart: pending in their yaml).", "Check the logs for OOM kills; the affected hosts go onto the restart queue and get restart: pending.",
              "哪些主机的日志里出现了 OOM-killed？把它们加进 restart.list，并在 inventory 里把 restart 改成 pending"])


# ---------------------------------------------------------------- doc-9357: dead links -> rename -> partial revert


def doc_9357():
    def gen(rng):
        files = {}
        ren = [("安装指南.md", "安装.md"), ("常见问题.md", "FAQ.md"), ("快速入门.md", "入门.md")]
        live = ["安装.md", "FAQ.md", "入门.md", "概览.md", "排错.md", "使用.md", "附录.md"]
        for n in live:
            files["知识库/" + n] = ""
        pages = {
            "概览.md": ["# 概览", "", "先看[快速入门](快速入门.md)，再看[使用](使用.md)。", "安装见[安装指南](安装指南.md)，遇到问题看[常见问题](常见问题.md)。"],
            "使用.md": ["# 使用", "", "回到[概览](概览.md)。", "详细步骤在[快速入门](快速入门.md)。"],
            "排错.md": ["# 排错", "", "先看[常见问题](常见问题.md)，再看[安装指南](安装指南.md)。", "也可以直接去[使用](使用.md)。"],
            "安装.md": ["# 安装", "", "装完后看[入门](入门.md)。"],
            "入门.md": ["# 入门", "", "概览在[这里](概览.md)。"],
            "附录.md": ["# 附录", "", "参见[安装指南](安装指南.md)和[快速入门](快速入门.md)，旧版叫[常见问题](常见问题.md)。"],
            "FAQ.md": ["# FAQ", "", "安装问题见[安装指南](安装指南.md)，入门见[快速入门](快速入门.md)。"],
        }
        for n, rows in pages.items():
            files["知识库/" + n] = lines(rows)
        files["知识库/改名表.txt"] = lines(["%s -> %s" % r for r in ren])
        return files

    logic = '''
import re
def solve(files):
    ren = dict(r.split(" -> ") for r in files["知识库/改名表.txt"].splitlines())
    dead = 0
    final = dict(files)
    for p, t in sorted(files.items()):
        if p.endswith(".md"):
            for tgt in re.findall(r"\\]\\(([^()]*\\.md)\\)", t):
                if "知识库/" + tgt not in files:
                    dead += 1
            new = t
            for old, nw in ren.items():
                new = new.replace("(" + old + ")", "(" + nw + ")")
            final[p] = new
    for p in ("知识库/附录.md", "知识库/FAQ.md"):
        final[p] = files[p]
    return [{"any": [str(dead)]}, None, None], final, {"ren": ren}
'''

    def cmds(i):
        r = list(i["ren"].items())
        fwd = "; ".join("sed -i 's/(%s)/(%s)/g' 知识库/*.md" % (a, b) for a, b in r)
        back = "; ".join("sed -i 's/(%s)/(%s)/g' 知识库/附录.md 知识库/FAQ.md" % (b, a) for a, b in r)
        return [["grep -ho '([^()]*\\.md)' 知识库/*.md | tr -d '()' | while read t; do [ -e 知识库/$t ] || echo $t; done | wc -l"], [fwd, "grep -rn '](' 知识库"], [back, "grep -n '](' 知识库/附录.md 知识库/FAQ.md"]]
    return case(
        "doc-9357", desc="Three turns: counts links to renamed pages that no longer exist, rewrites them using a rename table, then restores the old names in two pages",
        task_type="link_check", family="fam-doc-b12n-deadlinks-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-MULTISRC", "TR-READONLY"],
        trap_note="- TR-MULTISRC: the dead links are spread over seven pages and one page can hold two of them; every occurrence counts. 改名表.txt is data, not a page. Turn 3 only works on 附录.md and FAQ.md, whose links to renamed targets were all dead originally.",
        prompts=["知识库 里的页面用 [文字](文件.md) 互相链接。有多少个链接指向的文件已经不存在了？每个失效链接算一个，只回答数字。",
                 "知识库/改名表.txt 记着文件的改名对照（旧名 -> 新名）。把页面里失效的链接按对照表改成新名字，别的内容不动。改完回复 DONE。",
                 "附录.md 和 FAQ.md 暂时不跟着改名，把这两页里刚改过的链接恢复成旧名字，其他页面保持现在的样子。改完回复 DONE。"],
        alts=["知识库里有几个链接已经失效？按改名表修好，之后附录和 FAQ 两页再改回旧名", "数一下指向不存在文件的链接，用改名表替换成新文件名，然后让附录.md 和 FAQ.md 恢复原状",
              "统计知识库里的失效链接，对照改名表批量更新，最后把附录与 FAQ 的改动撤销", "失效链接有多少个？修复它们，但附录.md 和 FAQ.md 要保留旧链接", "How many links in 知识库 point to files that no longer exist? Fix them with the rename table, then put the old names back in 附录.md and FAQ.md."])


# ---------------------------------------------------------------- cfg-9358: debug services -> info + delete overrides


def cfg_9358():
    svcs = ["api", "cart", "mailer", "pay", "report", "sync", "ui"]

    def gen(rng):
        files = {}
        dbg = set(rng.sample(range(7), 3))
        for i, s in enumerate(svcs):
            lv = "debug" if i in dbg else rng.choice(["info", "warn", "info"])
            rows = ["name: " + s, "log_level: " + lv, "port: %d" % rng.randint(8000, 8999)]
            if i not in dbg and rng.random() < 0.6:
                rows.append("log_level_file: debug")
            files["config/services/%s.yaml" % s] = lines(rows)
            if i in dbg or rng.random() < 0.4:
                files["config/overrides/%s.debug.yaml" % s] = lines(["log_level: trace", "sample_rate: 1.0"])
        files["config/README.md"] = lines(["# Config", "", "services/<name>.yaml is the real config. overrides/<name>.debug.yaml is a temporary debug override that may only be deleted",
                                          "together with the service going back to info. log_level_file is a different key."])
        return files

    logic = '''
def solve(files):
    dbg = sorted(p.split("/")[2][:-5] for p, t in files.items() if p.startswith("config/services/") and "log_level: debug" in t.splitlines())
    final = dict(files)
    for s in dbg:
        p = "config/services/%s.yaml" % s
        final[p] = files[p].replace("log_level: debug", "log_level: info")
        final.pop("config/overrides/%s.debug.yaml" % s, None)
    return [{"all": dbg}, None], final, {"dbg": dbg}
'''

    def cmds(i):
        d = i["dbg"]
        return [["grep -n '^log_level: debug$' config/services/*.yaml"],
                ["; ".join("sed -i 's/^log_level: debug$/log_level: info/' config/services/%s.yaml; rm config/overrides/%s.debug.yaml" % (s, s) for s in d), "ls config/overrides; grep -n '^log_level' config/services/*.yaml"]]
    return case(
        "cfg-9358", desc="Two turns: lists services that log at debug in their own config, then sets them to info and deletes their temporary debug override files",
        task_type="edit_value", family="fam-cfg-b12n-debugoff-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: `log_level_file: debug` lines are a different key, so those services are not at debug. TR-READONLY: override files of non-debug services stay (config/README.md), and so does every other key.",
        prompts=["Under config/services each service has its own log_level. Which services run at debug? List their names.",
                 "Put those services back to info: set log_level: info in each one's file under config/services and delete its overrides/<name>.debug.yaml. Other services and overrides stay as they are. Reply DONE when finished."],
        alts=["Which services are at log_level debug? Return them to info and remove their debug override files.", "List the services whose own config says debug, then switch them to info and delete the matching overrides/<name>.debug.yaml.",
              "Find services logging at debug; for each, change the level to info and remove its temporary debug override.", "Debug-level services: name them, then lower them to info and clean up their debug overrides.",
              "哪些服务的日志级别是 debug？改回 info，并删掉它们的 overrides 文件"])


# ---------------------------------------------------------------- scr-9359: python -> python3


def scr_9359():
    names = ["构建", "测试", "发布", "备份", "清理", "迁移", "体检", "同步", "导出"]

    def gen(rng):
        files = {}
        for n in names:
            rows = ["set -e", "echo 开始" + n]
            kind = rng.choice(["py", "py", "py3", "none", "comment", "echo"])
            if kind == "py":
                rows += [rng.choice(["python manage.py migrate", "python -m http.server 8000", "  python tools/%s.py --fast" % "gen"]), "echo 完成"]
            elif kind == "py3":
                rows += ["python3 tools/run.py", "echo 完成"]
            elif kind == "comment":
                rows += ["# 需要 python 环境", "echo 完成"]
            elif kind == "echo":
                rows += ['echo "python ready"', "echo 完成"]
            else:
                rows += ["echo 完成"]
            files["脚本/%s.sh" % n] = lines(rows)
        files["脚本/备份.sh"] = lines(["set -e", "echo 开始备份", "python backup.py --full", "if [ -f lock ]; then", "  python backup.py --check", "fi"])
        for n in ("钩子", "校验"):
            files["脚本/第三方/%s.sh" % n] = lines(["set -e", "python vendor.py"])
        files["脚本/README.md"] = lines(["# 脚本", "", "只看 脚本 目录下直接放的 .sh；第三方 是外部代码，不改。",
                                        "「调用 python」指某一行去掉前面的空格后以 python 加空格开头；注释和 echo 里的 python 字样不算。"])
        return files

    logic = '''
import re
def solve(files):
    pat = re.compile(r"^(\\s*)python ", re.M)
    hit = [p for p, t in sorted(files.items()) if p.startswith("脚本/") and p.endswith(".sh") and "/第三方/" not in p and pat.search(t)]
    assert len(hit) >= 4
    final = dict(files)
    for p in hit:
        final[p] = pat.sub(lambda m: m.group(1) + "python3 ", files[p])
    return [{"any": [str(len(hit))]}, None], final, {"n": len(hit)}
'''

    def cmds(i):
        return [["grep -lE '^[[:space:]]*python ' 脚本/*.sh | wc -l"],
                ["grep -lE '^[[:space:]]*python ' 脚本/*.sh | xargs sed -i -E 's/^([[:space:]]*)python /\\1python3 /'", "grep -n 'python' 脚本/*.sh"]]
    return case(
        "scr-9359", desc="Two turns: counts shell scripts that call python (not python3) at the start of a line, then rewrites those calls to python3 while comments, echo text and third-party scripts stay",
        task_type="fix_output", family="fam-scr-b12n-pythonbin-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: `# 需要 python 环境` and `echo \"python ready\"` mention python but do not call it; python3 lines are already right. TR-READONLY: 脚本/第三方 is untouched (脚本/README.md); indented calls keep their indentation.",
        prompts=["脚本 目录下直接放的 .sh 里，有几个脚本含有调用 python 的行（命令名正好是 python，不是 python3）？第三方目录和判定口径看 脚本/README.md。只回答数字。",
                 "把这些脚本里调用 python 的命令都改成 python3，缩进和别的行保持原样。改完回复 DONE。"],
        alts=["有多少个脚本直接用 python 命令？把它们都改成 python3", "统计以 python 命令开头的脚本个数，然后把这些命令换成 python3", "脚本目录里调用 python（而非 python3）的 .sh 有几个？替换成 python3",
              "数一数还在用 python 命令的脚本，再把这些行里的 python 改成 python3（注释和 echo 不动）", "How many scripts call plain python at the start of a line? Switch those calls to python3."])


# ---------------------------------------------------------------- fs-9360: most common extension -> move -> partial move back


def fs_9360():
    def gen(rng):
        files = {}
        npdf = rng.randint(8, 10)
        for i in range(npdf):
            files["下载/" + ("keep_" if i < 3 else "") + rng.choice(["合同", "报告", "发票", "简历", "手册"]) + "%02d.pdf" % i] = "pdf %d\n" % i
        for ext, k in (("jpg", rng.randint(4, 6)), ("zip", rng.randint(3, 5)), ("txt", rng.randint(3, 5)), ("docx", rng.randint(2, 4))):
            for i in range(k):
                files["下载/%s%02d.%s" % (rng.choice(["图", "资料", "备份", "笔记"]), i, ext)] = "%s %d\n" % (ext, i)
        files["下载/旧报告.pdf.bak"] = "backup\n"
        files["下载/旧合同.pdf.bak"] = "backup\n"
        for e in ("pdf", "jpg", "zip", "txt", "docx"):
            files["下载/%s/说明.txt" % e] = "这里放 %s 文件\n" % e
        files["下载/README.md"] = lines(["# 下载", "", "扩展名以最后一个点后面的部分为准：.pdf.bak 的扩展名是 bak。", "按扩展名整理时，文件放进 下载/<扩展名>/ 子目录，各类子目录已经建好。"])
        return files

    logic = '''
def solve(files):
    cnt = {}
    for p in files:
        if p.startswith("下载/") and p.count("/") == 1 and "." in p[3:] and not p.endswith("README.md"):
            e = p.rsplit(".", 1)[1]
            cnt[e] = cnt.get(e, 0) + 1
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] > sorted(cnt.values())[-2]
    final = {}
    for p, t in files.items():
        name = p[3:]
        if p.startswith("下载/") and p.count("/") == 1 and p.endswith("." + top) and not name.startswith("keep_"):
            final["下载/" + top + "/" + name] = t
        else:
            final[p] = t
    return [{"all": [top]}, None, None], final, {"ext": top}
'''

    def cmds(i):
        e = i["ext"]
        return [["ls 下载 | grep '\\.' | sed 's/.*\\.//' | sort | uniq -c | sort -rn | head -3"],
                ["mv 下载/*.%s 下载/%s/" % (e, e), "ls 下载 下载/" + e],
                ["mv 下载/%s/keep_*.%s 下载/" % (e, e), "ls 下载 下载/" + e]]
    return case(
        "fs-9360", desc="Three turns: finds the most common file extension in a downloads folder, moves those files into an extension subfolder, then moves the keep_ files back",
        task_type="count_by_type", family="fam-fs-b12n-extsort-01", gen=gen, logic=logic, cmds=cmds, traps=["TR-DECOY", "TR-READONLY"],
        trap_note="- TR-DECOY: 旧报告.pdf.bak and 旧合同.pdf.bak have extension bak (下载/README.md), so they neither count as pdf nor move. Turn 3 moves exactly the keep_* files back; all other pdf files stay in the subfolder.",
        prompts=["下载 目录里（只看直接放在里面的文件）数量最多的是哪种扩展名？扩展名以最后一个点后面的部分为准。只回答扩展名，不带点。",
                 "把这种扩展名的文件都整理到 下载/<扩展名>/ 子目录里（子目录已经建好），别的文件不动。整理完回复 DONE。",
                 "名字以 keep_ 开头的那几个还要留在 下载 根目录，把它们从子目录移回来，其余保持现在的样子。移完回复 DONE。"],
        alts=["下载里哪种扩展名的文件最多？把它们归到同名子目录，再把 keep_ 开头的搬回根目录", "找出数量最多的扩展名，整理进 下载/<扩展名>，keep_ 前缀的文件之后放回原处", "按扩展名统计下载目录，最多的那类移进子目录，然后把 keep_ 开头的移回来",
              "最常见的文件类型是什么？把这类文件收进子目录（keep_ 开头的除外，需要再移回）", "Which extension is most common in 下载? Move those files into a subfolder named after it, then move the keep_ ones back."])


BUILDERS = [cfg_9341, fs_9342, doc_9343, log_9344, tab_9345, scr_9346, cfg_9347, fs_9348, tab_9349, log_9350,
            doc_9351, cfg_9352, code_9353, fs_9354, tab_9355, log_9356, doc_9357, cfg_9358, scr_9359, fs_9360]

SPEC = {
    "cfg-9341": dict(kind="bash_edit", sub="M9b", targets=["config"]),
    "fs-9342": dict(kind="bash_edit", sub="M9b", targets=["素材"]),
    "doc-9343": dict(kind="bash_edit", sub="M9b", targets=["手册"]),
    "log-9344": dict(kind="bash_edit", sub="M9b", targets=["edge"]),
    "tab-9345": dict(kind="bash_edit", sub="M9b", targets=["门店"]),
    "scr-9346": dict(kind="bash_edit", sub="M9b", targets=["scripts"]),
    "cfg-9347": dict(kind="bash_edit", sub="M9b", targets=["deploy"]),
    "fs-9348": dict(kind="bash_edit", sub="M9b", targets=["projects"]),
    "tab-9349": dict(kind="bash_edit", sub="M9b", targets=["采购"]),
    "log-9350": dict(kind="bash_edit", sub="M9b", targets=["待查"]),
    "doc-9351": dict(kind="bash_edit", sub="M9b", targets=["docs"]),
    "cfg-9352": dict(kind="bash_edit", sub="M9b", targets=["svc"]),
    "code-9353": dict(kind="bash_edit", sub="M9b", targets=["src"]),
    "fs-9354": dict(kind="bash_edit", sub="M9b", targets=["照片"]),
    "tab-9355": dict(kind="bash_edit", sub="M9b", targets=["汇总"]),
    "log-9356": dict(kind="bash_edit", sub="M9b", targets=["inventory"]),
    "doc-9357": dict(kind="bash_edit", sub="M9b", targets=["知识库"]),
    "cfg-9358": dict(kind="bash_edit", sub="M9b", targets=["config"]),
    "scr-9359": dict(kind="bash_edit", sub="M9b", targets=["脚本"]),
    "fs-9360": dict(kind="bash_edit", sub="M9b", targets=["下载"]),
}
