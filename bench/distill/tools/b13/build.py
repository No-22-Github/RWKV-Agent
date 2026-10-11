"""Minimal corrective batch: 27 drafted, 23 live; no test seeds.

Run from the repo: python3 bench/distill/tools/b13/build.py
Only fixtures are generated. Teacher outputs must come from agent-eval k=3.
"""
import csv
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from casegen import Batch

B = Batch(salt="b13", author="llm:gpt-6-b13", version="v1.4")
NO = {"tools": [], "require_active_no_call": True, "max_output_chars": 600}
SHELVED = {
    "nt-8807": "v2 0/3: one spelling-contract failure and two unnecessary file searches; do not sample until lucky",
    "tab-8800": "0/3: whole-file read despite direct structured aggregation being sufficient",
    "tab-8802": "0/3: directory listing or whole-file read before aggregation",
    "tab-8804": "0/3: unnecessary discovery/whole read, or no query on the changed filter",
}


def shelve(cid, scenario):
    if cid not in SHELVED:
        return
    live = Path(B.cases) / scenario / cid
    shelf = Path(B.cases).parent / "cases-shelved" / scenario / cid
    if shelf.exists():
        shutil.rmtree(shelf)
    shelf.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(live), str(shelf))


def verify_files(files, answers, source_path=None):
    hashes = {p: hashlib.sha256(s.encode()).hexdigest() for p, s in files.items()}
    code = '''import hashlib, json
c = json.load(open("case.json"))
for p, h in %r.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
''' % (hashes,)
    if source_path:
        code += '''line = [s for s in c["files"][%r].splitlines() if s.strip()][-1]
separator = "=" if "=" in line else "：" if "：" in line else ":"
computed = line.split(separator, 1)[1].strip().strip('"')
for t in c["turns"]:
    assert t["expect"]["output_contains"] == [computed]
print(json.dumps({"expected_string": computed}, ensure_ascii=False))
''' % (source_path,)
        return code
    return code + '''
answers = %r
for t, a in zip(c["turns"], answers):
    assert t["expect"]["output_contains"] == a["expected_contains"]
print(json.dumps({"expected_string": answers[0]["expected_contains"][0]}, ensure_ascii=False))
''' % (answers,)


def notes(reference, unique):
    return "## Traps\n- None unless listed in tags; no test-bank source.\n\n## Reference solution\n" + reference + "\n\n## Why the answer is unique\n" + unique + "\n"


# Each item is independently drafted; supplied context, not live knowledge.
DIRECT = [
    ("把通知里的‘明早开门前检查投影仪’改成礼貌请求，保留时间和设备。", ["开门前", "投影仪"], "再压缩成一句，仍保留这两个信息。"),
    ("这条反馈只给了‘登录后页面白屏’，写一句追问，索取浏览器名称和版本。", ["浏览器", "版本"], "换成适合客服聊天的一句问话，信息要求保持一致。"),
    ("会议结论是‘周岚负责校对，郭越负责排版’，整理成一句交接说明。", ["周岚", "校对", "郭越", "排版"], "把同一分工改成两条清单。"),
    ("将‘展柜周二闭馆维护，周三恢复参观’改成访客通知。", ["周二", "维护", "周三"], "仍用这些信息，改成一条短信。"),
    ("海报草稿写着‘请自带水杯，现场提供饮水’，写一句报名提醒。", ["水杯", "饮水"], "按同一安排改成一句现场广播。"),
    ("登记说明规定‘青色标签放冷藏区，橙色标签放常温区’，复述两种标签的去向。", ["青色", "冷藏", "橙色", "常温"], "再将这两项去向写成一行提示。"),
    ("Turn this note into a visitor reminder: Cedar Room opens after lunch; visitors bring photo ID.", ["Cedar", "lunch", "ID"], "Keep those same details and make the reminder one sentence."),
    ("A handover says Mira handles captions and Soren handles sound. Restate the assignments for the production team.", ["Mira", "captions", "Soren", "sound"], "Put the same assignments into two bullets."),
    ("The workshop note says participants bring gloves; aprons are provided on arrival. Rewrite it as a signup reminder.", ["gloves", "aprons"], "Use the same arrangement in a brief arrival notice."),
    ("The support ticket says the export stops at the upload stage. Ask for the error message and the file type in one sentence.", ["error", "file type"], "Restate that request as a friendly chat message."),
    ("A courier note says the ceramic crate stays upright and the fabric bag stays dry. Turn it into a packing checklist.", ["ceramic", "upright", "fabric", "dry"], "Use the same instructions in a sentence for the driver."),
    ("Explain this label for attendees: Amber passes enter the balcony; Violet passes enter the courtyard.", ["Amber", "balcony", "Violet", "courtyard"], "Restate the same routing as two short signs."),
]

for i, (p, words, follow) in enumerate(DIRECT):
    cid = f"nt-{8800+i}"
    files = {"README.md": f"# Archive desk {chr(65+i)}\nThis workspace contains unrelated shift records.\n"}
    # v2: explicitly request reply text. v1 could be read as a file-edit request.
    lead = "请在聊天回复中给出文本：" if i < 6 else "Give the text in your chat reply: "
    if i >= 6:
        lead += "Keep the quoted terms with their original capitalization. "
    turns = [{"prompt": lead+p, "expect": dict(NO, output_contains=words)},
             {"prompt": lead+follow, "expect": dict(NO, output_contains=words)}]
    B.write_case(cid, desc="Restate supplied context and retain it in a follow-up", task_type="concept",
                 family=f"fam-nt-b13-context-{i//2+1:02}", level="L1", ref_calls=0,
                 files=files, turns=turns, version=2, traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": "unrelated shift records"}, axes=["DEC"],
                 verify=verify_files(files, [{"expected_contains": words}]*2),
                 notes="## Changelog\n- v2: specify reply text, not an unspecified file change; preserve quoted spelling for deterministic checks.\n\n"+notes("No calls on either turn; preserve every requested detail in natural language.",
                             "All needed details are explicitly supplied by the user; unrelated files add no evidence.").replace("- None unless listed in tags; no test-bank source.", "- TR-NOTOOLNEED: the user supplied the full content in chat; README.md has unrelated shift records and cannot improve the reply."))
    shelve(cid, "notool")

READ = [
    ("cfg", "read_effective", "设备/封口台.ini", "[seal]\nprofile=梨白\n", "设备/封口台.ini 里封口台的 profile 是什么？", "梨白", "将刚才查到的档位写成一句交班提示，不必再查。"),
    ("doc", "policy_lookup", "场馆/寄存说明.md", "# 寄存台\n领取凭证：栀子牌\n", "场馆/寄存说明.md 中领取寄存物要出示什么凭证？", "栀子牌", "用刚才的凭证名称写一句给访客的提醒。"),
    ("cfg", "read_effective", "灯光/台控.toml", 'scene = "Moonweave"\n', "What scene is set in 灯光/台控.toml?", "Moonweave", "Restate that scene in a handover sentence using the result already obtained."),
    ("doc", "extract_items", "studio/contact.md", "# Studio desk\nProof coordinator: Elowen\n", "Who is the proof coordinator in studio/contact.md?", "Elowen", "Use the coordinator name from your answer in a short routing note."),
    ("cfg", "read_effective", "包装/覆膜.yaml", "finish: 雾银\n", "包装/覆膜.yaml 中 finish 的设置是什么？", "雾银", "将这个设置改述成一句验收提醒。"),
    ("doc", "policy_lookup", "garden/entry.md", "# Garden access\nCollection point: Fern Gate\n", "Which collection point does garden/entry.md specify?", "Fern Gate", "Turn the result you already found into a visitor reminder."),
]
for i, (prefix, task, path, content, prompt, value, follow) in enumerate(READ):
    cid = f"{prefix}-{8800+i}"
    files = {path: content, "README.md": "# Shared reception workspace\nContact the duty desk for unrelated services.\n"}
    turns = [{"prompt": prompt, "expect": {"required_tools": ["read_file"], "forbidden_tools": ["list_files"], "output_contains": [value], "max_output_chars": 600}},
             {"prompt": follow, "expect": dict(NO, output_contains=[value])}]
    B.write_case(cid, desc="Read the named target, then reuse evidence without reopening it", task_type=task,
                 family=f"fam-{prefix}-b13-direct-{i+1:02}", level="L0", ref_calls=1,
                 files=files, turns=turns, axes=["OBS", "STP"],
                 verify=verify_files(files, [{"expected_contains": [value]}]*2, source_path=path),
                 notes=notes(f"Read {path} directly once; answer {value} with its source. On turn two use the existing result without calls.",
                             "The prompt names an existing exact file and the single relevant field; no directory discovery is needed."))

TABLES = [
    ("维修/工单.csv", ["ticket", "team", "minutes"], ["机修", "电检"], "minutes", "aggregate", 31,
     "维修/工单.csv 中机修组累计登记了多少分钟？", "同一份记录里，电检组累计登记了多少分钟？", "把刚才两个组的总分钟数汇总成一句交班说明。"),
    ("library/returns.csv", ["slip", "desk", "books"], ["West", "East"], "books", "aggregate", 37,
     "How many books were returned at West in library/returns.csv?", "What is the book total for East in that record?", "Summarize the two desk totals from your previous answers."),
    ("仓储/收货.csv", ["receipt", "zone", "crates"], ["南仓", "北仓"], "crates", "aggregate", 43,
     "仓储/收货.csv 里南仓累计收了多少箱？", "按同一份记录报出北仓累计箱数。", "复述两个仓的箱数，给收货员一条交接说明。"),
    ("museum/visits.csv", ["entry", "wing", "visitors"], ["Glass", "Stone"], "visitors", "aggregate", 47,
     "What is the visitor total for Glass in museum/visits.csv?", "Give the visitor total for Stone from that record.", "Turn those two totals into a short front-desk note."),
    ("剧场/签收.csv", ["sheet", "section", "pieces"], ["服装", "道具"], "pieces", "filter_count", 53,
     "剧场/签收.csv 中服装组有多少条签收记录？", "这份登记中道具组有多少条签收记录？", "把两组的记录条数复述成一句归档说明。"),
    ("harbor/checks.csv", ["inspection", "berth", "checks"], ["Reed", "Slate"], "checks", "filter_count", 59,
     "How many inspection records belong to Reed in harbor/checks.csv?", "How many records belong to Slate in that file?", "Restate the record counts for the two berths in a handover note."),
    ("诊所/配药.csv", ["batch", "柜台", "盒数"], ["东柜", "西柜"], "盒数", "aggregate", 61,
     "诊所/配药.csv 的列是 batch、柜台、盒数，柜台取值为东柜或西柜。东柜登记的总盒数是多少？", "这份记录中，西柜登记的总盒数是多少？", "在聊天回复里复述刚才两个柜台的总盒数。"),
    ("bindery/sheets.csv", ["job", "press", "sheets"], ["Birch", "Maple"], "sheets", "aggregate", 67,
     "bindery/sheets.csv has job, press and sheets columns; Birch and Maple are press names. What is the sheet total for Birch?", "What is the sheet total for Maple in that file?", "Give a chat reply that recaps the two press totals you obtained."),
    ("育苗/入盘.csv", ["登记", "棚区", "盘数"], ["甲棚", "乙棚"], "盘数", "filter_count", 71,
     "育苗/入盘.csv 的列是登记、棚区、盘数，棚区取值为甲棚或乙棚。甲棚共有多少条登记？", "同一份记录里乙棚有多少条登记？", "在聊天回复里复述两座棚各自的登记条数。"),
]
for i, (path, hdr, groups, field, task, count, p, follow, recap) in enumerate(TABLES):
    revised = i in (3, 5, 6)
    if i in (3, 5):
        recap = "Give the note in your chat reply using the two previous results. " + recap
    if i == 3:
        # Keep all required values (AND), rather than weakening the recap to
        # an ANY list that would accept only one group's correct total.
        p += " Write numeric totals as digits with no thousands separator."
        follow += " Write numeric totals as digits with no thousands separator."
        recap += " Write numeric totals as digits with no thousands separator."
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(hdr)
    records = [[f"{chr(75+i)}-{1001*(i+1)+j*7}", groups[(j*j+j//3)%2],
                17+i*101+(j*13)%71 if i < 6 else 1+(j*17+i)%9] for j in range(count)]
    w.writerows(records)
    files = {path: buf.getvalue(), "README.md": "# Intake archive\nEach row records one completed entry.\n"}
    vals = [sum(int(r[2]) for r in records if r[1] == g) if task == "aggregate" else sum(r[1] == g for r in records) for g in groups]
    turns = []
    for prompt, val in zip((p, follow), vals):
        turns.append({"prompt": prompt, "expect": {"required_tools": ["data_query"], "forbidden_tools": ["list_files", "read_file"],
                      "output_contains": [str(val)], "output_contains_token": True, "max_output_chars": 600}})
    turns.append({"prompt": recap, "expect": dict(NO, output_contains=list(map(str, vals)), output_contains_token=True)})
    if i == 6:
        # v2: a first-turn group_by can already return the second cabinet's
        # total. Requiring another query would teach redundant evidence work.
        # First turn still requires data_query; values/forbidden tools unchanged.
        del turns[1]["expect"]["required_tools"]
    hashes = {k: hashlib.sha256(v.encode()).hexdigest() for k, v in files.items()}
    verify = '''import csv, io, json, hashlib
c = json.load(open("case.json"))
for p,h in %r.items():
    assert hashlib.sha256(c["files"][p].encode()).hexdigest() == h
rows = list(csv.DictReader(io.StringIO(c["files"][%r])))
vals = [sum(int(r[%r]) for r in rows if r[%r] == g) if %r == "aggregate" else sum(r[%r] == g for r in rows) for g in %r]
for t, want in zip(c["turns"], [[str(vals[0])], [str(vals[1])], list(map(str, vals))]):
    assert t["expect"]["output_contains"] == want
print(json.dumps({"expected_number": vals[0]}))
''' % (hashes, path, field, hdr[1], task, hdr[1], groups)
    cid = f"tab-{8800+i}"
    B.write_case(cid, desc="Aggregate the named structured table, change group, then retain both answers", task_type=task,
                 family=f"fam-tab-b13-query-{i//2+1:02}", level="L0", ref_calls=2,
                 files=files, turns=turns, version=2 if revised else 1, case_expect={"max_calls": {"read_lines": 2}}, axes=["OBS", "STP"], verify=verify,
                 notes=("## Changelog\n- v2: allow turn two to use a first-turn grouped result; first-turn query and exact values remain required.\n\n" if i == 6 else "## Changelog\n- v2: clarify reply-only recap and numeric spelling; tool restrictions and all result values unchanged.\n\n" if revised else "")+notes(f"Query {path}, filter {hdr[1]}={groups[0]}, aggregate {'sum '+field if task == 'aggregate' else 'count'}: {vals[0]}. Repeat for {groups[1]}: {vals[1]} (or reuse an already returned grouped total in tab-8806). Recap with no calls.",
                             "Every row is a completed record; numbers are plain integers, equality filtering and sum/count are supported. Full-file reading is unnecessary."))
    shelve(cid, "tabular")

print("b13: 27 drafted, 23 live, 4 shelved; 52 live turns (before teacher path selection / QA)")
