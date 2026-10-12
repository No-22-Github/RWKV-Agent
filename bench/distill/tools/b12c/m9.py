"""M9 (bash) half of the v1.41 b12c batch: ids 9071-9077.

M9b bulk edit (5): each case has a read-only look-alike the README protects; M9e bash offered but the named
single file is the direct read (2). Shapes follow ../b12a/m9.py (cfg_9025, fs_9026, doc_9034)."""
import json
import os

from common import lines, write_case

REFS = {}


def files_check(rules, originals):
    def check(_out, root):
        for path, rule in rules.items():
            full = os.path.join(root, path)
            if rule.get("absent"):
                if os.path.exists(full):
                    return "%s should be gone" % path
                continue
            if not os.path.exists(full):
                return "%s missing" % path
            want = rule["equals"] if "equals" in rule else originals[path]
            text = open(full, encoding="utf-8").read()
            if text != want:
                return "%s = %r" % (path, text[:200])
        return None
    return check


def rules_for(files, final):
    """expect-files rules: unchanged / equals / absent computed from the originals and the final tree."""
    out = {}
    for path, text in files.items():
        if path not in final:
            out[path] = {"absent": True}
        elif final[path] == text:
            out[path] = {"unchanged": True}
        else:
            out[path] = {"equals": final[path]}
    for path, text in final.items():
        if path not in files:
            out[path] = {"equals": text}
    return out


def cfg_9071():
    services = ["gateway", "billing", "orders", "search", "notify"]
    files = {}
    for svc in services + ["_example"]:
        files[f"deploy/{svc}/app.env"] = lines([f"SERVICE={svc}", "LOG_LEVEL=debug", "ACCESS_LOG_LEVEL=debug", "PORT=8080"])
    files["deploy/README.md"] = lines(["# Deploy configs", "", "One directory per service. `_example` is the copy-me template: leave it as it is.",
                                       "ACCESS_LOG_LEVEL is audited separately and stays at debug."])
    final = {p: (t.replace("\nLOG_LEVEL=debug\n", "\nLOG_LEVEL=info\n") if "_example" not in p and p.endswith("app.env") else t) for p, t in files.items()}
    rules = rules_for(files, final)
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["deploy/README.md"].startswith("# Deploy configs")
assert "ACCESS_LOG_LEVEL is audited separately" in case["files"]["deploy/README.md"]
out = {}
for path, text in case["files"].items():
    if not path.endswith("app.env") or "/_example/" in path:
        continue
    rows = text.splitlines()
    assert rows[1] == "LOG_LEVEL=debug" and rows[2] == "ACCESS_LOG_LEVEL=debug", path
    out[path] = text.replace(chr(10) + "LOG_LEVEL=debug" + chr(10), chr(10) + "LOG_LEVEL=info" + chr(10))
print(json.dumps({"files": out}))
'''
    c1 = r"""find deploy -name app.env | grep -v /_example/ | xargs sed -i 's/^LOG_LEVEL=debug$/LOG_LEVEL=info/'"""
    c2 = "grep -rn LOG_LEVEL deploy"
    notes = f"""## Traps
- TR-READONLY: deploy/_example stays as it is; ACCESS_LOG_LEVEL=debug is a look-alike key that the README says to keep.
- A global `s/debug/info/` would also change ACCESS_LOG_LEVEL and the template.

## Reference solution
1. bash: `{c1}`
2. bash: `{c2}` to confirm five services changed and _example and every ACCESS_LOG_LEVEL did not.
Final answer: DONE (five services now LOG_LEVEL=info; _example and ACCESS_LOG_LEVEL untouched).

## Why the answer is unique
Only the exact LOG_LEVEL line of the five service files changes; everything else is byte-identical.
"""
    REFS["cfg-9071"] = (files, [c1, c2], files_check(rules, files))
    return write_case(
        "cfg-9071", desc="Lowers LOG_LEVEL from debug to info in five service env files without touching the template or the look-alike ACCESS_LOG_LEVEL key",
        task_type="edit_value", family="fam-cfg-b12c-loglevel-01", level="L2", ref_calls=2,
        traps=["TR-READONLY"], decoys={"TR-READONLY": None}, axes=["CON"],
        files=files, verify=verify, notes=notes, case_expect={"files": rules},
        turns=[{"prompt": "Production is too noisy: change LOG_LEVEL from debug to info in every service's app.env under deploy. deploy/README.md says what not to touch. Reply DONE when finished.",
                "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


def fs_9072():
    files = {}
    for path in ["site/index.htm", "site/about.htm", "site/blog/first.htm", "site/blog/second.htm", "site/blog/2026/q3.htm", "site/help/faq.htm"]:
        files[path] = "<html><body>" + path + "</body></html>\n"
    for name in ["jquery-ui.htm", "demo.htm"]:
        files[f"site/vendor/{name}"] = "<html><body>vendor " + name + "</body></html>\n"
    files["site/blog/archive.htm.bak"] = "backup of the archive page\n"
    files["site/already.html"] = "<html><body>already</body></html>\n"
    files["site/README.txt"] = lines(["Static site notes.", "The new web server only serves .html.", "site/vendor/ mirrors third-party packages by their original file names; never rename anything there."])
    final = {}
    for p, t in files.items():
        if p.endswith(".htm") and "/vendor/" not in p:
            final[p[:-4] + ".html"] = t
        else:
            final[p] = t
    rules = rules_for(files, final)
    verify = '''
import json, re
case = json.load(open("case.json"))
assert case["files"]["site/README.txt"].startswith("Static site notes.")
assert case["files"]["site/blog/archive.htm.bak"].startswith("backup of")
out = {}
for path, text in case["files"].items():
    if path.endswith(".htm") and not path.startswith("site/vendor/"):
        assert text.startswith("<html><body>" + path), path
        out[path[:-4] + ".html"] = text
    elif path.endswith(".htm"):
        assert path.startswith("site/vendor/"), path
print(json.dumps({"files": out}))
'''
    c1 = r'''for f in $(find site -name '*.htm' | grep -v /vendor/); do mv "$f" "${f}l"; done'''
    c2 = "find site -name '*.htm*'"
    notes = f"""## Traps
- TR-READONLY: site/vendor/*.htm keep their names (site/README.txt); archive.htm.bak merely contains .htm in its name.

## Reference solution
1. bash: `{c1}`
2. bash: `{c2}` to confirm six pages are .html and the vendor files and the .bak keep their names.
Final answer: DONE, six pages renamed to .html; vendor files untouched.

## Why the answer is unique
Rename is by extension only, outside site/vendor; contents do not change.
"""
    REFS["fs-9072"] = (files, [c1, c2], files_check(rules, files))
    return write_case(
        "fs-9072", desc="Renames .htm pages to .html across a static site while a vendor folder and a look-alike .bak file keep their names",
        task_type="bulk_edit", family="fam-fs-b12c-htmrename-01", level="L1", ref_calls=2,
        traps=["TR-READONLY"], decoys={"TR-READONLY": None}, axes=["CON"],
        files=files, verify=verify, notes=notes, case_expect={"files": rules},
        turns=[{"prompt": "新服务器只认 .html。把 site 下所有 .htm 页面改名成 .html，该保持原样的看 site/README.txt。改完回复 DONE。",
                "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


def doc_9073():
    files = {}
    for name in ["intro", "install", "usage", "faq", "roadmap"]:
        files[f"docs/{name}.md"] = lines([f"# {name}", "", "Acme Corp builds the toolkit.", f"Contact: {name}@acme.example"])
    files["docs/CHANGELOG.md"] = lines(["# Changelog", "", "2024: Acme Corp released 1.0.", "2025: Acme Corp released 2.0."])
    files["docs/legal/notice.md"] = lines(["# Notice", "", "Acme Corp is the registered legal entity."])
    files["docs/README.md"] = lines(["# Docs", "", "The company renamed itself: replace the name Acme Corp with Acme Labs in the guides.",
                                      "Do not touch docs/CHANGELOG.md (history) or docs/legal/ (registered name)."])
    final = {p: (t.replace("Acme Corp", "Acme Labs") if p in {f"docs/{n}.md" for n in ["intro", "install", "usage", "faq", "roadmap"]} else t) for p, t in files.items()}
    rules = rules_for(files, final)
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["docs/README.md"].startswith("# Docs")
out = {}
for n in ["intro", "install", "usage", "faq", "roadmap"]:
    path = "docs/" + n + ".md"
    text = case["files"][path]
    assert text.count("Acme Corp") == 1, path
    out[path] = text.replace("Acme Corp", "Acme Labs")
assert case["files"]["docs/CHANGELOG.md"].count("Acme Corp") == 2
assert case["files"]["docs/legal/notice.md"].count("Acme Corp") == 1
assert case["files"]["docs/CHANGELOG.md"].startswith("# Changelog")
print(json.dumps({"files": out}))
'''
    c1 = r"""sed -i 's/Acme Corp/Acme Labs/g' docs/intro.md docs/install.md docs/usage.md docs/faq.md docs/roadmap.md"""
    c2 = "grep -rn 'Acme' docs"
    notes = f"""## Traps
- TR-READONLY: CHANGELOG.md (history) and docs/legal/ keep the old name (docs/README.md); a docs-wide replace changes them too.

## Reference solution
1. bash: `{c1}`
2. bash: `{c2}` to confirm the five guides say Acme Labs and the changelog and legal notice still say Acme Corp.
Final answer: DONE (five guides updated; CHANGELOG.md and docs/legal untouched).

## Why the answer is unique
Only the five guide files change; the two protected places stay byte-identical.
"""
    REFS["doc-9073"] = (files, [c1, c2], files_check(rules, files))
    return write_case(
        "doc-9073", desc="Replaces a company name in five guide files while the changelog history and the legal notice keep the old name",
        task_type="write_structured", family="fam-doc-b12c-companyname-01", level="L2", ref_calls=2,
        traps=["TR-READONLY"], decoys={"TR-READONLY": None}, axes=["CON"],
        files=files, verify=verify, notes=notes, case_expect={"files": rules},
        turns=[{"prompt": "公司改名了，把 docs 里的 Acme Corp 换成 Acme Labs。哪些文件不能动，docs/README.md 里写了。改完回复 DONE。",
                "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


def cfg_9074():
    charts = ["api", "web", "worker", "cron"]
    files = {}
    for c in charts + ["legacy"]:
        files[f"charts/{c}/Chart.yaml"] = lines([f"name: {c}", "version: 2.3.1", "appVersion: 2.3.1", "type: application"])
    files["charts/README.md"] = lines(["# Charts", "", "Release bump: raise `version` to 2.4.0 in each chart.", "`appVersion` tracks the application release and is bumped by CI; leave it.",
                                       "charts/legacy is frozen and is not part of the release."])
    final = {p: (t.replace("\nversion: 2.3.1\n", "\nversion: 2.4.0\n") if "legacy" not in p and p.endswith("Chart.yaml") else t) for p, t in files.items()}
    rules = rules_for(files, final)
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["charts/README.md"].startswith("# Charts")
out = {}
for path, text in case["files"].items():
    if not path.endswith("Chart.yaml") or "/legacy/" in path:
        continue
    rows = text.splitlines()
    assert rows[1] == "version: 2.3.1" and rows[2] == "appVersion: 2.3.1", path
    out[path] = text.replace(chr(10) + "version: 2.3.1" + chr(10), chr(10) + "version: 2.4.0" + chr(10))
print(json.dumps({"files": out}))
'''
    c1 = r"""find charts -name Chart.yaml | grep -v /legacy/ | xargs sed -i 's/^version: 2\.3\.1$/version: 2.4.0/'"""
    c2 = "grep -rn version charts"
    notes = f"""## Traps
- TR-READONLY: appVersion: 2.3.1 is a look-alike line that CI owns; charts/legacy is frozen.

## Reference solution
1. bash: `{c1}`
2. bash: `{c2}` to confirm four charts have version 2.4.0, appVersion is still 2.3.1 everywhere and legacy is unchanged.
Final answer: DONE (four charts bumped to 2.4.0; appVersion and legacy untouched).

## Why the answer is unique
Only the version line of four Chart.yaml files changes.
"""
    REFS["cfg-9074"] = (files, [c1, c2], files_check(rules, files))
    return write_case(
        "cfg-9074", desc="Bumps the chart version in four Chart.yaml files without touching the look-alike appVersion line or the frozen legacy chart",
        task_type="edit_value", family="fam-cfg-b12c-chartbump-01", level="L2", ref_calls=2,
        traps=["TR-READONLY"], decoys={"TR-READONLY": None}, axes=["CON"],
        files=files, verify=verify, notes=notes, case_expect={"files": rules},
        turns=[{"prompt": "发版：把 charts 下各个 Chart.yaml 的 version 从 2.3.1 升到 2.4.0。哪些行或目录不用动，charts/README.md 里有说明。改完回复 DONE。",
                "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


def fs_9075():
    files = {}
    for path in ["work/a/build.tmp", "work/a/out.log", "work/b/cache.tmp", "work/b/notes.txt", "work/c/deep/x.tmp", "work/c/deep/y.txt",
                 "work/scratch.tmp", "work/pinned/session.tmp", "work/pinned/data.txt", "work/c/report.tmp.md"]:
        files[path] = "content of " + path + "\n"
    files["work/README.txt"] = lines(["Work area.", "*.tmp files are disposable build leftovers.", "work/pinned/ holds locks in use by running jobs: never delete anything there."])
    final = {p: t for p, t in files.items() if not (p.endswith(".tmp") and "/pinned/" not in p)}
    rules = rules_for(files, final)
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"]["work/README.txt"].startswith("Work area.")
assert case["files"]["work/c/report.tmp.md"].startswith("content of")
out = {}
for path, text in case["files"].items():
    if path.endswith(".tmp") and not path.startswith("work/pinned/"):
        continue
    out[path] = text
print(json.dumps({"files": out}))
'''
    c1 = "find work -name '*.tmp' | grep -v /pinned/ | xargs rm"
    c2 = "find work -name '*.tmp*'"
    notes = f"""## Traps
- TR-READONLY: work/pinned/session.tmp is in use (work/README.txt); report.tmp.md only contains .tmp in its name.

## Reference solution
1. bash: `{c1}`
2. bash: `{c2}` to confirm only work/pinned/session.tmp and report.tmp.md still match.
Final answer: DONE, four .tmp files removed; pinned and report.tmp.md kept.

## Why the answer is unique
Deletion is by exact .tmp suffix outside work/pinned; all other files are byte-identical.
"""
    REFS["fs-9075"] = (files, [c1, c2], files_check(rules, files))
    return write_case(
        "fs-9075", desc="Deletes .tmp leftovers across a work tree while a pinned folder and a look-alike .tmp.md file are kept",
        task_type="bulk_edit", family="fam-fs-b12c-tmpclean-01", level="L2", ref_calls=2,
        traps=["TR-READONLY"], decoys={"TR-READONLY": None}, axes=["CON"],
        files=files, verify=verify, notes=notes, case_expect={"files": rules},
        turns=[{"prompt": "Clean up the work directory: delete the leftover .tmp files under it. Check work/README.txt for anything that must stay. Reply DONE when finished.",
                "expect": {"output_contains": ["DONE"], "max_output_chars": 600}}])


def doc_9076():
    files = {
        "README.md": lines(["# Orders service", "", "Run `make dev`; the dev server listens on port 7410.", "Health check: GET /healthz."]),
        "docs/ports.md": lines(["# Ports (old)", "", "The dev server used to listen on 7400 before the 2025 move.", "Prod listens on 8443."]),
        "docs/notes.md": lines(["# Notes", "", "Old dev port was 7400."]),
    }
    verify = '''
import json
case = json.load(open("case.json"))
text = case["files"]["README.md"]
assert text.startswith("# Orders service")
assert "listens on port 7410" in text
print(json.dumps({"expected_contains_any": ["7410"]}))
'''
    notes = """## Traps
- TR-DECOY: docs/ports.md and docs/notes.md still say 7400; the README says 7410.

## Reference solution
1. read_file README.md
Final answer: The dev server listens on port 7410 (README.md; the 7400 in docs/ports.md is the old port).

## Why the answer is unique
The user names README.md; only it states the current port.
Why bash is not the tool here: one named file and one fact: read_file is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.
"""
    return write_case(
        "doc-9076", desc="Single-file README lookup of the dev server port while bash is offered; the read tool is the right call",
        task_type="policy_lookup", family="fam-doc-b12c-devport-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": "7400"}, axes=["OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "What port does the dev server listen on, according to README.md?",
                "expect": {"output_contains_any": ["7410"], "forbidden_tools": ["bash"], "max_output_chars": 600}}])


def cfg_9077():
    files = {
        "config/server.toml": lines(["[http]", "port = 9100", "read_timeout_s = 45", "write_timeout_s = 60", "", "[db]", "pool = 12"]),
        "config/server.toml.bak": lines(["[http]", "port = 9100", "read_timeout_s = 30", "write_timeout_s = 60", "", "[db]", "pool = 8"]),
    }
    verify = '''
import json
case = json.load(open("case.json"))
text = case["files"]["config/server.toml"]
assert text.startswith("[http]") and "read_timeout_s = 45" in text
assert "read_timeout_s = 30" in case["files"]["config/server.toml.bak"]
print(json.dumps({"expected_number": 45}))
'''
    notes = """## Traps
- TR-DECOY: config/server.toml.bak still says 30; the live file says 45.

## Reference solution
1. read_file config/server.toml
Final answer: read_timeout_s is 45 seconds in config/server.toml (the .bak copy has the old 30).

## Why the answer is unique
The user names config/server.toml; only it holds the live value.
Why bash is not the tool here: one named file and one fact: read_file is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.
"""
    return write_case(
        "cfg-9077", desc="Single-file config lookup of a read timeout while bash is offered; the read tool is the right call",
        task_type="read_effective", family="fam-cfg-b12c-readtimeout-01", level="L1", ref_calls=1,
        traps=["TR-DECOY"], decoys={"TR-DECOY": "30"}, axes=["OBS"],
        files=files, verify=verify, notes=notes,
        turns=[{"prompt": "config/server.toml 里 read_timeout_s 现在配的是多少秒？",
                "expect": {"output_contains": ["45"], "output_contains_token": True, "forbidden_tools": ["bash"], "max_output_chars": 600}}])


BUILDERS = [cfg_9071, fs_9072, doc_9073, cfg_9074, fs_9075, doc_9076, cfg_9077]
SPEC = {
    "cfg-9071": dict(kind="bash_edit", sub="M9b", targets=["deploy"]),
    "fs-9072": dict(kind="bash_edit", sub="M9b", targets=["site"]),
    "doc-9073": dict(kind="bash_edit", sub="M9b", targets=["docs"]),
    "cfg-9074": dict(kind="bash_edit", sub="M9b", targets=["charts"]),
    "fs-9075": dict(kind="bash_edit", sub="M9b", targets=["work"]),
    "doc-9076": dict(kind="bash_avoided", sub="M9e"),
    "cfg-9077": dict(kind="bash_avoided", sub="M9e"),
}
