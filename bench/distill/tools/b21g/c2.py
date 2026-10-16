"""b21g sub C (part 2): config trees with many small files, 32231-32234."""
import json
import re
from random import Random

from common import L, emit, reg


@reg
def c9(i):
    rng = Random(3223100 + i * 7919)
    files = {}
    for k in range(rng.randint(110, 150)):
        rows = ["name: svc-%03d" % k]
        if rng.random() < 0.15:
            rows.append("# enabled: true  (old default)")
        rows.append("enabled: %s" % rng.choice(["true", "true", "false"]))
        rows.append("replicas: %d" % rng.randint(1, 6))
        if rng.random() < 0.6:
            rows += ["tls:", "  enabled: %s" % rng.choice(["true", "false"]), "  cert: /etc/ssl/svc-%03d.pem" % k]
        files["services/%s/svc-%03d.yaml" % (rng.choice(["core", "edge", "batch"]), k)] = L(*rows)
    def solve(files):
        def top(t):
            return {m.group(1): m.group(2) for m in re.finditer(r"^([a-z]+): (\S+)\s*$", t, re.M)}
        on = [t for t in files.values() if top(t).get("enabled") == "true"]
        b = [t for t in on if int(top(t)["replicas"]) > 3]
        loose = [t for t in files.values() if "enabled: true" in t]
        return {"turns": [{"number": len(on), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-DECOY": len(loose), "TR-TRUNC": 50}}
    emit("cfg-32231", sub="multifile", task_type="read_effective", desc="Counts service yaml files with top-level enabled true while nested tls.enabled and commented lines look the same",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "services 目录下按 core、edge、batch 分了很多服务的 yaml。顶层 enabled 是 true 的服务有多少个？（tls 里面的 enabled 和注释掉的行都不算。）"},
                {"prompt": "这些服务里 replicas 大于 3 的有几个？"}],
         ref=(["grep -rl '^enabled: true' services | xargs grep -h '^replicas:' | awk '$2>3' | wc -l"], 0),
         notes_traps=["TR-DECOY: tls.enabled and a commented line also contain enabled: true.", "TR-TRUNC: ~130 files."],
         notes_ref=["grep -rl '^enabled: true' services | wc -l.", "xargs grep -h '^replicas:' | awk '$2>3' | wc -l."], unique="Anchored top-level key.")


@reg
def c10(i):
    rng = Random(3223200 + i * 7919)
    files = {}
    teams = ["payments", "search", "growth", "infra"]
    tw = [rng.randint(8, 40) for _ in teams]
    for t, n in zip(teams, tw):
        for k in range(n):
            rows = ["APP=%s-%02d" % (t, k), "PORT=%d" % rng.randint(3000, 9000)]
            v = rng.choices(["info", "debug", "warn", "debug-sql"], [5, 4, 2, 1])[0]
            if rng.random() < 0.15:
                rows.append("#LOG_LEVEL=debug")
            rows.append("LOG_LEVEL=%s" % v)
            files["envs/%s/%s-%02d.env" % (t, t, k)] = L(*rows)
    def solve(files):
        hit = {}
        for p, t in files.items():
            if re.search(r"^LOG_LEVEL=debug$", t, re.M):
                hit[p.split("/")[1]] = hit.get(p.split("/")[1], 0) + 1
        r = sorted(hit.items(), key=lambda kv: -kv[1])
        assert r[0][1] > r[1][1]
        return {"turns": [{"number": sum(hit.values()), "items": []}, {"number": r[0][1], "items": [r[0][0]]}],
                "decoys": {"TR-DECOY": len([1 for t in files.values() if "LOG_LEVEL=debug" in t]), "TR-TRUNC": 50}}
    emit("cfg-32232", sub="multifile", task_type="read_effective", desc="Counts env files whose active LOG_LEVEL is exactly debug among commented and debug-sql look-alikes, then ranks teams",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "envs/ has one folder per team full of .env files. How many files actually run with LOG_LEVEL=debug? A commented-out line or a value like debug-sql doesn't count."},
                {"prompt": "Which team folder has the most of them, and how many?"}],
         ref=(["grep -rlx 'LOG_LEVEL=debug' envs | cut -d/ -f2 | sort | uniq -c | sort -rn | head -4"], 0),
         notes_traps=["TR-DECOY: '#LOG_LEVEL=debug' and 'LOG_LEVEL=debug-sql' contain the text.", "TR-TRUNC: ~90 files."],
         notes_ref=["grep -rlx 'LOG_LEVEL=debug' envs | wc -l.", "cut -d/ -f2 | sort | uniq -c | sort -rn."], unique="Whole-line match.")


@reg
def c11(i):
    rng = Random(3223300 + i * 7919)
    files = {}
    for k in range(rng.randint(90, 130)):
        c = {"service": "w%03d" % k, "timeout_ms": rng.choice([500, 1000, 3000])}
        if rng.random() < 0.8:
            c["retry"] = {"max": rng.randint(0, 7), "backoff_ms": rng.choice([100, 250, 500])}
        files["conf/w%03d.json" % k] = json.dumps(c, indent=2) + "\n"
    def solve(files):
        cs = [json.loads(t) for t in files.values()]
        a = [c for c in cs if c.get("retry", {}).get("max", 0) > 3]
        b = [c for c in cs if "retry" in c]
        return {"turns": [{"number": len(a), "items": []}], "decoys": {"TR-MISSING": len(b), "TR-TRUNC": 50}}
    emit("cfg-32233", sub="multifile", task_type="read_effective", desc="Counts json config files with retry.max above 3 when a fifth of the files have no retry block",
         files=files, solve=solve, traps=["TR-MISSING"],
         turns=[{"prompt": "conf 目录里每个 worker 一个 json 配置。retry.max 大于 3 的有多少个？没配 retry 的按没有重试处理。"}],
         ref=(["jq -s 'map(select((.retry.max//0)>3))|length' conf/*.json"], 0),
         notes_traps=["TR-MISSING: ~20% have no retry block."], notes_ref=["jq -s over conf/*.json select (.retry.max//0)>3 | length."], unique="Strict greater than 3.")


@reg
def c12(i):
    rng = Random(3223400 + i * 7919)
    files = {}
    for k in range(rng.randint(80, 120)):
        rows = ["[app]", "name=tenant%03d" % k, "port=%d" % rng.choice([80, 8080]), "", "[db]", "host=db%d.internal" % rng.randint(1, 5),
                "port=%d" % rng.choices([5432, 5433, 6432], [8, 1, 1])[0], "", "[cache]", "port=6379"]
        files["tenants/t%03d.ini" % k] = L(*rows)
    def solve(files):
        n = 0
        for t in files.values():
            sec = None
            for l in t.splitlines():
                if l.startswith("["):
                    sec = l
                elif sec == "[db]" and l.startswith("port=") and l != "port=5432":
                    n += 1
        al = len([1 for t in files.values() for l in t.splitlines() if l.startswith("port=") and l != "port=5432"])
        return {"turns": [{"number": n, "items": []}], "decoys": {"TR-DECOY": al, "TR-TRUNC": 50}}
    emit("cfg-32234", sub="multifile", task_type="read_effective", desc="Counts tenant ini files whose [db] port differs from 5432 while app and cache sections also define ports",
         files=files, solve=solve, traps=["TR-DECOY", "TR-TRUNC"],
         turns=[{"prompt": "tenants 目录里每个租户一个 ini 文件。有多少个租户的 [db] 段里 port 不是 5432？别把 [app] 和 [cache] 段的 port 算进去。"}],
         ref=(["awk '/^\\[/{s=$0} s==\"[db]\" && /^port=/ && $0!=\"port=5432\"{n++} END{print n}' tenants/*.ini"], 0),
         notes_traps=["TR-DECOY: every file also has port= in [app] and [cache].", "TR-TRUNC: ~100 files."], notes_ref=["awk tracking the current section over all files."], unique="Section-aware match.")
