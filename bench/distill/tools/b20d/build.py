"""b20d (v2.0 daily Q&A): pick 200 questions from the HF distill-zh-2k set and write them as notool cases.

Usage: python3 build.py            (run from anywhere; writes nt-21001..nt-21200 and the report)
Deterministic: fixed seed, no clock, no network; re-running rewrites identical bytes.
Only the `instruction` field of the source rows is used; the source thinking/response are ignored.
"""
import ast
import collections
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch  # noqa: E402
from distill_paths import REPO, version_dir  # noqa: E402

SRC = os.path.join(REPO, "local", "datasets", "hf-deepseek-v41-flash-distill-zh-2k", "data", "train.jsonl")
REPORT = version_dir("v2.0", "reports", "b20d-authoring.md")
DATASET = "dengxiaodi/deepseek-v4.1-flash-distill-zh-2k"
SEED = 20210
N_TOTAL = 200
CAP = 8              # per-category cap in the balanced fill
MAX_TOKENS = 2048    # source completion_tokens limit
N_CALC = 12          # target number of exact-calculation questions
FIRST_NO = 21001
NGRAM = 8
JACCARD_MAX = 0.4    # near-duplicate threshold on 8-char shingles

BATCH = Batch(salt="b20d", author="llm:claude-sonnet-b20d", version="v2.0", tool_catalog="agent-tool-v2.0")

TOOLS = ["list_files", "read_file", "search_text", "read_lines", "write_file", "replace_lines", "append_file",
         "calculator", "data_query", "datetime", "web_search", "web_fetch", "bash", "get_weather"]
TIME_RE = re.compile(r"最新|现在|目前|近期|当前|新闻|实时|最近|今年|去年|明年|本周|本月|今日|此刻|"
                     r"今天(?:的)?(?:价|天气|汇率|股|行情|日期|几号|星期)|明天(?:的)?(?:天气|价)|20[2-9]\d")
LOCAL_RE = re.compile(r"我的|我家|附件|上传|刚才|上文|上面的|本地|截图|图片|链接|https?://|这个文件|该文件|这份文件|当前目录|工作区")
CALC_RE = re.compile(r"计算|等于|多少|求")


def load():
    rows = []
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            u = r["usage"]
            u = ast.literal_eval(u) if isinstance(u, str) else u
            r["ct"] = u["completion_tokens"]
            rows.append(r)
    return rows


def exclusion(r):
    ins = r["instruction"]
    if r["ct"] > MAX_TOKENS:
        return "completion_tokens>2048"
    if TIME_RE.search(ins):
        return "time-sensitive"
    if LOCAL_RE.search(ins):
        return "needs local file/personal data"
    low = ins.lower()
    if any(t in low for t in TOOLS):
        return "mentions a tool name (lint prompt.tool_name)"
    return None


def is_calc(r):
    ins = r["instruction"]
    return r["category"] == "数学应用题" or bool(re.search(r"\d", ins) and CALC_RE.search(ins))


def grams(s):
    s = re.sub(r"\s+", "", s)
    return {s[i:i + NGRAM] for i in range(max(1, len(s) - NGRAM + 1))}


def jaccard(a, b):
    return len(a & b) / len(a | b)


def select(rows):
    rng = random.Random(SEED)
    reasons = collections.Counter()
    eligible = []
    for r in rows:
        why = exclusion(r)
        if why:
            reasons[why] += 1
        else:
            eligible.append(r)
    chosen, chosen_grams, per_cat = [], [], collections.Counter()
    dup_skipped = 0

    def try_take(r):
        nonlocal dup_skipped
        g = grams(r["instruction"])
        if any(jaccard(g, h) >= JACCARD_MAX for h in chosen_grams):
            dup_skipped += 1
            return False
        chosen.append(r)
        chosen_grams.append(g)
        per_cat[r["category"]] += 1
        return True

    # 1) exact-calculation quota, spread over categories (<= 4 per category here)
    pool = sorted((r for r in eligible if is_calc(r)), key=lambda r: r["id"])
    rng.shuffle(pool)
    calc_cat = collections.Counter()
    for r in pool:
        if sum(1 for c in chosen) >= N_CALC:
            break
        if calc_cat[r["category"]] >= 4:
            continue
        if try_take(r):
            calc_cat[r["category"]] += 1
    taken = {r["id"] for r in chosen}
    # 2) balanced round-robin fill, per-category cap
    cats = sorted({r["category"] for r in eligible})
    rng.shuffle(cats)
    by_cat = {c: sorted((r for r in eligible if r["category"] == c and r["id"] not in taken), key=lambda r: r["id"])
              for c in cats}
    for c in cats:
        rng.shuffle(by_cat[c])
    idx = {c: 0 for c in cats}
    while len(chosen) < N_TOTAL:
        progressed = False
        for c in cats:
            if len(chosen) >= N_TOTAL:
                break
            if per_cat[c] >= CAP:
                continue
            while idx[c] < len(by_cat[c]):
                r = by_cat[c][idx[c]]
                idx[c] += 1
                if try_take(r):
                    progressed = True
                    break
        if not progressed:
            sys.exit("cannot reach %d questions under cap %d (got %d)" % (N_TOTAL, CAP, len(chosen)))
    chosen.sort(key=lambda r: r["id"])
    return chosen, reasons, len(eligible), dup_skipped


def write_cases(chosen, cat_index):
    out = []
    for i, r in enumerate(chosen):
        cid = "nt-%d" % (FIRST_NO + i)
        ins = r["instruction"]
        desc = ("Daily Q&A answered inside the agent environment with no workspace; source %s id %d, category %s"
                % (DATASET, r["id"], r["category"]))
        notes = (
            "## Traps\n- None. Everyday question from %s (id %d, category %s, CC BY 4.0, teacher DeepSeek-V4.1-Flash); "
            "only the instruction is used.\n\n"
            "## Reference solution\nNo fixed answer. The expected shape is a direct natural-language reply; a "
            "calculator call is fine when the question needs exact arithmetic. Quality is decided by the "
            "post-run filter, not by this case.\n\n"
            "## Why the answer is unique\nIt is not: open-ended Q&A with no scored expectation (the only expect is output_excludes [UNKNOWN], see the batch README).\n"
            % (DATASET, r["id"], r["category"]))
        verify = (
            "import json\n"
            "case = json.load(open(\"case.json\"))\n"
            "assert case[\"files\"] == {} and case[\"web_fixture\"] == []\n"
            "assert len(case[\"turns\"]) == 1 and case[\"turns\"][0][\"prompt\"].strip()\n"
            "assert case[\"turns\"][0][\"expect\"] == {\"output_excludes\": [\"UNKNOWN\"]} and \"expect\" not in case\n"
            "assert \"tool_policy\" not in case and \"offered_tools\" not in case\n"
            "t = case[\"tags\"]\n"
            "assert t[\"batch\"] == \"b20d\" and t[\"license\"] == \"CC-BY-4.0\" and t[\"source_dataset\"] == %r\n"
            "assert t[\"source_id\"] == %d and t[\"source_category\"] == %r\n"
            "print(json.dumps({\"files\": case[\"files\"]}))  # no answer to recompute; echo the (empty) fixture so gate --strict-shape recognises the shape\n" % (DATASET, r["id"], r["category"]))
        BATCH.write_case(
            cid, desc=desc, task_type="concept", family="fam-nt-b20d-c%02d-01" % cat_index[r["category"]],
            level="L0", ref_calls=0, files={}, turns=[{"prompt": ins, "expect": {"output_excludes": ["UNKNOWN"]}}], verify=verify, notes=notes,
            extra_tags={"batch": "b20d", "source_dataset": DATASET, "source_id": r["id"],
                        "source_category": r["category"], "license": "CC-BY-4.0"})
        out.append((cid, r))
    return out


def report(chosen, written, reasons, n_elig, dup_skipped, cat_index, total):
    per_cat = collections.Counter(r["category"] for r in chosen)
    calc = [cid for cid, r in written if is_calc(r)]
    gl = [grams(r["instruction"]) for r in chosen]
    mx, pairs = 0.0, 0
    for a in range(len(gl)):
        for b in range(a + 1, len(gl)):
            if gl[a] & gl[b]:
                pairs += 1
            mx = max(mx, jaccard(gl[a], gl[b]))
    L = ["# b20d 日常问答批：出题报告", "",
         "批次 b20d，题号 nt-%d – nt-%d，共 %d 题；生成脚本 `bench/distill/tools/b20d/build.py`（种子 %d，重跑逐字节一致）。"
         % (FIRST_NO, FIRST_NO + len(chosen) - 1, len(chosen), SEED), "",
         "## 来源与署名", "",
         "题面（instruction）取自 Hugging Face 数据集 `%s`（CC BY 4.0，教师模型 DeepSeek-V4.1-Flash），"
         "每题 tags 带 source_dataset / source_id / source_category / license。原数据集的 thinking 与 response 一律不使用；"
         "回答由我们的环境里的老师重新生成。署名：dengxiaodi, \"DeepSeek-V4.1-Flash-Distill-ZH-2K\", CC BY 4.0, "
         "https://huggingface.co/datasets/%s 。" % (DATASET, DATASET), "",
         "## 选题规则（确定性，无手工挑选）", "",
         "1. 排除 completion_tokens > %d。" % MAX_TOKENS,
         "2. 排除时效题（正则 TIME_RE：最新/现在/目前/近期/当前/新闻/实时/最近/今年/本周/20xx 年等）。",
         "3. 排除需要本地文件或个人数据的题（LOCAL_RE：我的/附件/上传/刚才/上面的/截图/链接/这个文件等）。",
         "4. 排除题面含工具名的题（lint 规则 prompt.tool_name，例如“写一个 bash 命令”）。",
         "5. 先从剩余题里抽 %d 道精确计算类（数学应用题，或含数字且含 计算/等于/多少/求），每类不超过 4 道；"
         "再按 category 轮转补满到 %d，每类封顶 %d；顺序由种子 %d 的 shuffle 决定。" % (N_CALC, N_TOTAL, CAP, SEED),
         "6. 互相去重：8 字符片段（去空白）集合的 Jaccard ≥ %.1f 视为近似重复，后到者跳过（共跳过 %d 次）。"
         % (JACCARD_MAX, dup_skipped),
         "7. 选中后按源 id 升序编号为 nt-%d…。" % FIRST_NO, "",
         "## 被排除原因计数（源 %d 题，按判断顺序，每题只计第一个原因）" % total, ""]
    for k, v in reasons.most_common():
        L.append("- %s：%d" % (k, v))
    L.append("- 合格候选：%d；其中被选中 %d" % (n_elig, len(chosen)))
    L += ["", "## 计算类题数", "",
          "按 is_calc 规则（数学应用题，或含数字且含 计算/等于/多少/求）判定，选中里共 %d 道（其中配额抽取 %d 道，"
          "其余为轮转时碰巧命中）。题号：%s。" % (len(calc), N_CALC, " ".join(calc)), "",
          "## 去重自检", "",
          "200 题两两比较：存在至少一个共同 8 字符片段的题对 %d 个；最大 Jaccard %.3f（阈值 %.1f）。" % (pairs, mx, JACCARD_MAX),
          "同一模板句式（如“和我们的日常生活有什么关系”）的题允许出现，只要主题不同。", "",
          "## 各 category 题数（family 编号 cNN 对应）", "", "| family | category | 题数 |", "|---|---|---|"]
    for c in sorted(cat_index, key=cat_index.get):
        L.append("| c%02d | %s | %d |" % (cat_index[c], c, per_cat.get(c, 0)))
    L += ["", "## 题目形态", "",
          "- 场景 notool，files {}，web_fixture []，单轮；turns[0].prompt = instruction 原文；expect 只有一条 output_excludes [\"UNKNOWN\"]（见下“与规格的两处偏差”），不写 tools、tool_policy、max_output_chars。",
          "- task_type=concept，level=L0，ref_calls=0，traps 为空（TR-NOTOOLNEED 要求 trap_decoys 非 null，对无确定答案的题不适用，故不挂）。",
          "", "## 与规格的两处偏差（均不改 Go 代码）", "",
          "1. 加载器（caseio.go）要求每轮至少声明一种工具期望或结果期望，完全空的 expect 会让 `corpus loadcheck` 报错。"
          "最小处理：每轮写 `output_excludes: [\"UNKNOWN\"]`。它不约束工具，也不限长度，只排除裸 UNKNOWN 弃权（日常问答里本就不该出现）。",
          "2. `gate.sh` 的 verify 用 --strict-shape，对没有任何答案期望的题会报 verify_shape_unknown。最小处理：verify.py 输出 "
          "`{\"files\": {}}`（空夹具快照，已知形状），并断言题面、标签、署名字段自洽。lint 的 TR-NOTOOLNEED 要求 trap_decoys 非 null，"
          "不适用于无确定答案的题，所以不挂 trap（traps 为空，level L0）。", "",
          "- 全部中文题；answer_style=natural，不带英文答题契约。", ""]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def main():
    rows = load()
    chosen, reasons, n_elig, dup_skipped = select(rows)
    cat_index = {c: i + 1 for i, c in enumerate(sorted({r["category"] for r in rows}))}
    written = write_cases(chosen, cat_index)
    report(chosen, written, reasons, n_elig, dup_skipped, cat_index, len(rows))
    print("wrote %d cases, %d eligible" % (len(written), n_elig))


if __name__ == "__main__":
    main()
