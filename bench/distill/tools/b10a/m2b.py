"""M2 (v1.4 §3.2) b10a scale-up, part B: target absent with a near-match decoy.

16 cases: fs-8004..fs-8011 (filesystem) and log-8010..log-8017 (logs).
Chinese topics: pet hospitals and photography studios; English topic: aquarium
stores / aquarium systems. Question shapes follow the b10 pilot cases
fs-8001 / tab-8001 / doc-8001; wording rules follow b10-pilot.md §5-§6.
"""
import json

from common import revised

write_case = revised({'fs-8004': '去掉对另一只宠物名「椰果」的排除：老师列出证件目录里有哪些文件时提到它，属于「查了哪些地方」，不是把它当答案。', 'fs-8005': '去掉对「汤圆」的排除：老师说明「10 月 8 日那份是汤圆的，不是旺财的」，是点明诱饵，不是把它当答案。', 'fs-8006': '去掉对「周叙」的排除：同 fs-8005，点明目录里另一位客户的精修包不是她的。', 'fs-8007': '去掉对 proforma 金额与 INV-2198 的排除：问的是正式发票到没到，老师说明「只有一份估价 2,480.00 的 proforma」是背景信息，不是答案。', 'log-8011': '必含项「3号影棚」改为「影棚」：老师写「3 号影棚」（中间有空格）被误判。'})

# The sabotage test (bank verify) either increments the first fixture number
# matching a scored value, or deletes the first non-empty line of the
# first-sorted fixture file (verify.go extOrder). These cases score no numbers
# (output_contains items are words), so the delete-first-line path applies and
# every verify.py asserts the exact first line of that target file.
EXT_ORDER = [".csv", ".tsv", ".txt", ".jsonl", ".log", ".json", ".yaml", ".yml", ".md"]


def _ext_rank(path):
    base = path.rsplit("/", 1)[-1].lower()
    for i, ext in enumerate(EXT_ORDER):
        if base.endswith(ext):
            return i
    return len(EXT_ORDER)


def _guard(files):
    """Assert line for the file bank verify corrupts first."""
    for path in sorted(files, key=lambda p: (_ext_rank(p), p)):
        for line in files[path].split("\n"):
            if line.strip():
                return ("# sabotage guard: bank verify deletes the first non-empty line of this file first\n"
                        "assert files[%s].splitlines()[0] == %s\n"
                        % (json.dumps(path, ensure_ascii=False), json.dumps(line, ensure_ascii=False)))
    return ""


def V(body, files, words):
    """Fill the @@GUARD@@ and @@WORDS@@ placeholders of a verify body."""
    out = body.replace("@@GUARD@@", _guard(files)).replace("@@WORDS@@", json.dumps(words, ensure_ascii=False))
    assert "@@" not in out
    return out


_PILOT_SLUGS = {"ferrypier", "coldroom", "signedbundle", "retiredwh", "oncallrota", "collectorgap",
                "retrybackoff", "berthfee", "geocodeprice", "warrantytickets", "labledger", "ratelimit",
                "nightlybackup", "storesales", "stocktakeloss", "fivexxwindow", "poolsizepair"}
_FAMILY_COUNT = {}


def fam(abbrev, slug):
    assert slug not in _PILOT_SLUGS, slug
    assert slug not in _FAMILY_COUNT, "slug reused: " + slug
    _FAMILY_COUNT[slug] = 1
    return "fam-%s-b10-%s-01" % (abbrev, slug)


def check_no_numeric_contains(turns):
    """A scored value that parses as a number would switch the sabotage test to
    number+1 on possibly unrelated literals. M2B scores words only."""
    import re
    for t in turns:
        for s in t["expect"]["output_contains"]:
            assert re.fullmatch(r"-?\d+(\.\d+)?", s.replace(",", "").strip()) is None, s


# ---------------------------------------------------------------- fs-8004
FILES_FSA = {
    "README.md": "# 安和宠物诊所 客户证件库\n\n证件/ 只存放已出具并交付客户的电子证件。是否出具以 疫苗/接种登记.csv 的状态为准：预约中、待观察的犬猫不走发证流程。\n",
    "疫苗/接种登记.csv": "宠物名,类别,疫苗,剂次,状态,登记日期\n麦芽,犬,狂犬疫苗,第3针,预约中,2026-10-08\n麦芽,犬,犬四联,第2针,已完成,2026-09-06\n椰果,猫,猫三联,年度加强,已完成,2026-09-30\n",
    "证件/麦芽-驱虫记录.pdf": "安和宠物诊所 体外驱虫记录\n宠物：麦芽（犬）\n项目：体外驱虫滴剂\n执行日期：2026-09-21\n下次驱虫：2026-10-21\n",
    "证件/椰果-猫三联免疫证.pdf": "安和宠物诊所 免疫证\n宠物：椰果（猫）\n疫苗：猫三联 年度加强\n接种日期：2026-09-30\n执业兽医师：贺兰\n",
    "前台/交付登记.md": "# 证件交付登记\n\n| 日期 | 证件 | 交付方式 |\n|---|---|---|\n| 2026-09-30 | 椰果-猫三联免疫证.pdf | 客户自取 |\n| 2026-09-21 | 麦芽-驱虫记录.pdf | 电子发送 |\n",
}
WORDS_FSA = ["预约", "未接种", "没接种", "还没接种", "尚未接种", "待接种", "还没打", "没打", "没法出证", "无法出证", "不能出证"]
TURNS_FSA = [{
    "prompt": "麦芽的主人下周要带它出境，来电找麦芽的电子免疫证。帮我看看有没有这份证。",
    "expect": {
        "output_contains": ["麦芽"],
        "output_contains_any": WORDS_FSA,
        "output_excludes": ["免疫证是 证件/麦芽-驱虫记录", "免疫证就是 证件/麦芽-驱虫记录", "免疫证在 证件/麦芽-驱虫记录", "免疫证：证件/麦芽-驱虫记录"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_FSA)
write_case(
    "fs-8004",
    desc="A client asks for a dog's electronic immunization certificate; only a deworming record under the same name exists and the rabies booster is still booked, so no certificate was issued",
    task_type="find_file", family=fam("fs", "immunecert"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "证件/麦芽-驱虫记录.pdf"},
    axes=["DEC", "ERR"],
    files=FILES_FSA, turns=TURNS_FSA,
    verify=V('''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
rows = {r["宠物名"] + "|" + r["疫苗"]: r for r in csv.DictReader(io.StringIO(files["疫苗/接种登记.csv"]))}
# The rabies booster for 麦芽 is still booked, so no immunization certificate was issued.
assert rows["麦芽|狂犬疫苗"]["状态"] == "预约中"
assert not any("麦芽" in p and "免疫证" in p for p in files)
# The only document under 麦芽's name is the deworming record, not a certificate.
assert "证件/麦芽-驱虫记录.pdf" in files
assert "免疫证" not in files["证件/麦芽-驱虫记录.pdf"]
assert "麦芽-免疫证" not in files["前台/交付登记.md"]
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_FSA, WORDS_FSA),
    notes='''
## Traps
- TR-ABSENT: 证件/ 下没有麦芽的免疫证；疫苗/接种登记.csv 写明麦芽的狂犬疫苗第 3 针状态是「预约中」（2026-10-08 登记，10-14 上午才打），按 README 的流程没到出证这一步；前台/交付登记.md 里也没有它的免疫证。
- TR-NEARNAME: 证件/麦芽-驱虫记录.pdf 是麦芽名下唯一的证件文件，名字同在「证件/」下、同属麦芽，但它是驱虫用药记录，不是免疫证。把它当免疫证交付就是诱饵答案。

## Reference solution
1. 列出证件库：证件/ 下有麦芽-驱虫记录、椰果-猫三联免疫证，另有 README 和 疫苗/、前台/ 目录。
2. 读 疫苗/接种登记.csv：麦芽狂犬第 3 针预约中，未接种。
3. 读 前台/交付登记.md：交付记录里没有麦芽的免疫证。
终答（2–4 句）：证件库里没有麦芽的免疫证——接种登记里麦芽的狂犬第三针还是预约中，按流程没到出证这一步；麦芽名下只有一份驱虫记录，那是驱虫用药记录，不是免疫证，交付登记里也没有它的免疫证。等 14 日接种完成、诊所出证后我提醒你交付。判据：包含「麦芽」和一个「预约/未接种」说法，不得把驱虫记录当免疫证。

## Why the answer is unique
诱饵错在文件性质不同：麦芽-驱虫记录.pdf 的标题和内容都是体外驱虫记录，不含免疫证应有的疫苗、接种日期、执业兽医师字段，README 也写明证件库只放已出具证件、出证以接种登记状态为准。登记表证实第三针未接种，交付登记里无免疫证，所以「麦芽的免疫证」在工作区不存在，唯一站得住的回答是说明未出证并给出接种后的下一步。
''',
)

# ---------------------------------------------------------------- fs-8005
FILES_FSB = {
    "README.md": "# 贝贝康动物医院 检验报告库\n\n化验/ 按宠物名加采样日期存放已出的报告；未出报告的样本在 化验/采样登记.md 里登记状态。\n",
    "化验/采样登记.md": "# 化验采样登记\n\n| 日期 | 宠物 | 项目 | 状态 |\n|---|---|---|---|\n| 2026-10-01 | 旺财 | 血常规 | 已出报告 |\n| 2026-10-08 | 旺财 | 血常规 | 样本溶血作废，需重新采样，报告未出 |\n| 2026-10-08 | 汤圆 | 血常规 | 已出报告 |\n",
    "化验/旺财-血常规-2026-10-01.pdf": "贝贝康动物医院 血常规检验报告\n宠物：旺财（犬）\n采样日期：2026-10-01\n白细胞 12.4 ×10^9/L（参考 6.0-17.0）\n红细胞 6.8 ×10^12/L\n检验者：检验科\n",
    "化验/汤圆-血常规-2026-10-08.pdf": "贝贝康动物医院 血常规检验报告\n宠物：汤圆（猫）\n采样日期：2026-10-08\n白细胞 9.6 ×10^9/L（参考 5.5-19.5）\n检验者：检验科\n",
}
WORDS_FSB = ["溶血", "作废", "重新采样", "重采", "未出", "没有出", "还没出", "尚未出", "没出来", "还没出来", "未生成", "没有生成", "还没生成"]
TURNS_FSB = [{
    "prompt": "旺财主人来问 10 月 8 日那次体检的血常规报告好了没有，好了他就过来取。帮我查一下。",
    "expect": {
        "output_contains": ["旺财"],
        "output_contains_any": WORDS_FSB,
        "output_excludes": ["报告是 化验/旺财-血常规-2026-10-01", "报告在 化验/旺财-血常规-2026-10-01", "报告是 化验/汤圆", "报告已出"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_FSB)
write_case(
    "fs-8005",
    desc="Asks for a dog's complete blood count report from Oct 8; that sample was voided for hemolysis, only an older report of the same dog and another pet's same-day report exist",
    task_type="find_file", family=fam("fs", "labreport"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "化验/旺财-血常规-2026-10-01.pdf"},
    axes=["DEC", "OBS"],
    files=FILES_FSB, turns=TURNS_FSB,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
reg = files["化验/采样登记.md"]
assert reg.splitlines()[0] == "# 化验采样登记"
rows = [l for l in reg.splitlines() if l.startswith("| 2026-10-08 | 旺财")]
assert len(rows) == 1 and "溶血" in rows[0] and "未出" in rows[0]
assert not any(p.startswith("化验/旺财") and "2026-10-08" in p for p in files)
# Decoys: the dog's older report and another pet's same-day report both exist.
assert "化验/旺财-血常规-2026-10-01.pdf" in files
assert "化验/汤圆-血常规-2026-10-08.pdf" in files
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_FSB, WORDS_FSB),
    notes='''
## Traps
- TR-ABSENT: 化验/采样登记.md 写明 2026-10-08 旺财的血常规样本「溶血作废，需重新采样，报告未出」，报告库里没有 10 月 8 日的旺财报告。
- TR-DECOY: 化验/旺财-血常规-2026-10-01.pdf 同名同项目，只是日期是 10 月 1 日；同日还有汤圆的血常规报告。把旧报告或别只宠物的报告当成 10 月 8 日的结果交付，就是诱饵答案。

## Reference solution
1. 列出 化验/：两份报告和采样登记。
2. 读 化验/采样登记.md：10-08 旺财样本溶血作废，报告未出。
3. 读 README 确认报告库存放规则。
终答（2–4 句）：10 月 8 日旺财的血常规报告还没出——采样登记里写着当天的样本溶血作废，需要重新采样。化验目录里只有旺财 10 月 1 日的旧报告和当天另一只宠物的报告，都不能当这次的报告。建议联系主人重新采样，采完我再看登记状态。判据：包含「旺财」和一个「溶血/作废/未出」说法，不得把旧报告或别的报告当答案。

## Why the answer is unique
两份诱饵都错在对象或日期不符：10-01 的报告是旺财一周前的结果，采样登记明确 10-08 那次样本作废；汤圆的报告同日但宠物不同，血常规数值没有可比性。登记状态是报告是否出具的权威口径（README 写明），报告库里也确实没有 10-08 的旺财文件，所以唯一站得住的回答是说明样本作废、需重新采样。
''',
)

# ---------------------------------------------------------------- fs-8006
FILES_FSC = {
    "README.md": "# 拾光映画 交付目录\n\n交付/ 只放已上传给客户的成品包；修图中的场次在 上传登记.md 里跟踪。\n",
    "交付/上传登记.md": "# 交付包上传登记\n\n| 客户 | 包 | 状态 | 备注 |\n|---|---|---|---|\n| 林晚棠 | 海景婚纱-初选包 | 已交付 | 2026-10-07 上传 |\n| 林晚棠 | 海景婚纱-精修包 | 返修中 | 客户 10-08 提出精修意见，修好后重新上传 |\n| 周叙 | 城市旅拍-精修包 | 已交付 | 2026-10-09 上传 |\n",
    "交付/林晚棠-海景婚纱-初选包.zip": "初选包（未修原图精选 120 张）\n场次：2026-10-05 海景婚纱\n客户：林晚棠、沈亦白\n状态：初选已交付 2026-10-07\n",
    "交付/周叙-城市旅拍-精修包.zip": "精修包（36 张）\n场次：2026-10-05 城市旅拍\n客户：周叙\n状态：已交付 2026-10-09\n",
}
WORDS_FSC = ["返修", "修图", "修改", "重传", "重新上传", "未上传", "没有上传", "还没上传", "尚未上传", "暂无", "未交付", "还没交付", "尚未交付"]
TURNS_FSC = [{
    "prompt": "林晚棠问 10 月 5 日海景婚纱那场的精修包什么时候能下载，你帮我看看现在出了没有。",
    "expect": {
        "output_contains": ["林晚棠"],
        "output_contains_any": WORDS_FSC,
        "output_excludes": ["精修包是 交付/林晚棠-海景婚纱-初选包", "精修包在 交付/林晚棠-海景婚纱-初选包", "精修包已上传", "精修包已经出了", "现在就能下载"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_FSC)
write_case(
    "fs-8006",
    desc="Asks for the retouched deliverable pack of an Oct 5 wedding shoot; it is back in retouching, only the unretouched selection pack of the same client and another client's pack from the same day exist",
    task_type="find_file", family=fam("fs", "retouchpack"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "交付/林晚棠-海景婚纱-初选包.zip"},
    axes=["DEC", "OBS"],
    files=FILES_FSC, turns=TURNS_FSC,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
reg = files["交付/上传登记.md"]
assert reg.splitlines()[0] == "# 交付包上传登记"
rows = [l for l in reg.splitlines() if l.startswith("| 林晚棠 | 海景婚纱-精修包")]
assert len(rows) == 1 and "返修" in rows[0]
assert not any(p.startswith("交付/林晚棠") and "精修包" in p for p in files)
# Decoys: the same client's selection pack and another client's pack exist.
assert "交付/林晚棠-海景婚纱-初选包.zip" in files
assert "交付/周叙-城市旅拍-精修包.zip" in files
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_FSC, WORDS_FSC),
    notes='''
## Traps
- TR-ABSENT: 交付/上传登记.md 写明林晚棠的海景婚纱-精修包状态是「返修中」，客户 10-08 提出精修意见，修好后重新上传；交付/ 目录里没有她的精修包。
- TR-DECOY: 交付/林晚棠-海景婚纱-初选包.zip 同客户同场次，只差「初选/精修」两个字；同日还有周叙的精修包。把初选包或别人的精修包当成她的精修包，就是诱饵答案。

## Reference solution
1. 列出 交付/：两个 zip 和上传登记。
2. 读 交付/上传登记.md：林晚棠精修包返修中。
3. 读 README 确认目录只放已上传成品。
终答（2–4 句）：林晚棠那场海景婚纱的精修包还没上传——上传登记里她的精修包状态是返修中，10-08 客户提了精修意见，修好后会重新上传。交付目录里只有她的初选包和同日另一位客户的精修包，都不是这份。可以先回复客户返修中，包上传后我提醒你。判据：包含「林晚棠」和一个「返修/修图/未上传」说法，不得把初选包当精修包。

## Why the answer is unique
初选包错在阶段不同：文件内容自述是未修原图精选，登记表也把它标成已交付的初选包，与「精修包」是两个交付物；周叙的精修包错在客户不同。上传登记是成品包是否上传的权威口径（README 写明目录只放已上传成品），其中林晚棠精修包明确返修中，所以唯一站得住的回答是说明返修中并给出上传后的下一步。
''',
)

# ---------------------------------------------------------------- fs-8007
FILES_FSD = {
    "README.md": "Driftwood Aquatics accounts folder. invoices/ holds invoice documents that have actually arrived; INVOICE-LOG.md records the status of each one.\n",
    "invoices/INVOICE-LOG.md": "# Invoice log\n\n| Invoice | Order | Status | Note |\n|---|---|---|---|\n| INV-2198 | PO-1154 | settled | final invoice received 2026-09-02 |\n| INV-2214 | PO-1187 | proforma only | final invoice pending the arrival stock count; the supplier issues it once the delivery is checked in |\n",
    "invoices/INV-2214-proforma.pdf": "Driftwood Aquatics - proforma invoice INV-2214\nSupplier: Coral Mesa Exports\nOrder PO-1187, live rock and invertebrates\nEstimated amount: USD 2,480.00, subject to the arrival stock count\nIssued 2026-09-28\n",
    "invoices/INV-2198.pdf": "Driftwood Aquatics - invoice INV-2198\nSupplier: Coral Mesa Exports\nOrder PO-1154, filtration media\nAmount: USD 612.40\nSettled 2026-09-02\n",
}
WORDS_FSD = ["proforma", "pending", "not arrived", "hasn't arrived", "has not arrived", "not been issued",
             "hasn't been issued", "has not been issued", "not yet issued", "no final invoice",
             "not received", "hasn't been received", "has not been received", "not yet received"]
TURNS_FSD = [{
    "prompt": "Accounts wants to settle the Coral Mesa order PO-1187 this week and is asking for the final invoice. Can you check whether it has reached us yet?",
    "expect": {
        "output_contains": ["INV-2214"],
        "output_contains_any": WORDS_FSD,
        "output_excludes": ["final invoice is invoices/INV-2214-proforma", "final invoice is INV-2214-proforma", "final invoice has arrived", "has reached us"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_FSD)
write_case(
    "fs-8007",
    desc="Asks for the final invoice of supplier order PO-1187; only the proforma under the same invoice number exists and the log says the final invoice is pending the arrival stock count",
    task_type="find_file", family=fam("fs", "finalinvoice"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "invoices/INV-2214-proforma.pdf"},
    axes=["DEC", "ERR"],
    files=FILES_FSD, turns=TURNS_FSD,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
log = files["invoices/INVOICE-LOG.md"]
rows = [l for l in log.splitlines() if l.startswith("| INV-2214 ")]
assert len(rows) == 1 and "proforma" in rows[0] and "pending" in rows[0]
assert not any(p.endswith("/INV-2214.pdf") for p in files)
# The proforma under the same number and an older settled invoice both exist.
assert "invoices/INV-2214-proforma.pdf" in files
assert "invoices/INV-2198.pdf" in files
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_FSD, WORDS_FSD),
    notes='''
## Traps
- TR-ABSENT: invoices/INVOICE-LOG.md 把 INV-2214（订单 PO-1187）记为「proforma only」，最终发票 pending 到货清点，供应商验收后才开具；目录里没有 INV-2214 的正式发票文件。
- TR-NEARNAME: invoices/INV-2214-proforma.pdf 与最终发票同号，只差 proforma 一个词；把 proforma 形式发票当最终发票交给付款，就是诱饵答案。

## Reference solution
1. 列出 invoices/：proforma、一张旧发票和 INVOICE-LOG.md。
2. 读 invoices/INVOICE-LOG.md：INV-2214 proforma only，final invoice pending。
3. 读 proforma 文件确认它自述是估价、以到货清点为准。
终答（2–4 句）：The final invoice for PO-1187 (INV-2214) hasn't arrived: the invoice log lists it as proforma only, pending the arrival stock count, and only the proforma document is in the folder. The supplier issues the final invoice once the delivery is checked in. Tell accounts to hold payment until then, or ask Coral Mesa for the expected date. 判据：包含 INV-2214 和一个 proforma/pending 说法，不得把 proforma 当最终发票。

## Why the answer is unique
The proforma is the closest match by name, but it calls itself an estimated amount subject to the stock count, and the log states the final invoice is only issued after the delivery is checked in, so paying on it would be wrong. INV-2198 belongs to a different order. No other file claims a final INV-2214 invoice, so the only defensible reply is that it has not arrived and what to do meanwhile.
''',
)

# ---------------------------------------------------------------- fs-8008
FILES_FSE = {
    "README.md": "Lanternfish Pets service office. Only sign-off sheets marked signed in commissioning/SIGNOFF-LOG.txt count as warranty documents.\n",
    "commissioning/SIGNOFF-LOG.txt": "system | document | status | date\nreef-350 | reef-350-signoff.pdf | signed | 2026-08-14\nreef-700 | reef-700-checklist-draft.pdf | draft, unsigned | -\nreef-700 | reef-700-signoff.pdf | not generated; sign-off visit scheduled for 2026-10-14 | -\n",
    "commissioning/reef-700-checklist-draft.pdf": "Lanternfish Pets - commissioning checklist, reef display 700 (DRAFT)\nSystem: reef-700, installed 2026-09-25\nAll checklist items ticked by the installer\nStatus: draft, unsigned; the sign-off visit has not taken place\n",
    "commissioning/reef-350-signoff.pdf": "Lanternfish Pets - commissioning sign-off, reef display 350\nSystem: reef-350, signed 2026-08-14 by M. Okafor (service lead)\nWarranty start: 2026-08-14\n",
}
WORDS_FSE = ["not generated", "unsigned", "draft", "not signed", "isn't signed", "hasn't been signed",
             "has not been signed", "not yet signed", "scheduled", "awaiting", "pending"]
TURNS_FSE = [{
    "prompt": "The reef-700 display is part of the shop tour next week. Where is its signed commissioning sign-off sheet?",
    "expect": {
        "output_contains": ["reef-700"],
        "output_contains_any": WORDS_FSE,
        "output_excludes": ["sign-off sheet is commissioning/reef-", "sign-off is commissioning/reef-", "sign-off sheet is at commissioning/reef-", "sign-off is at commissioning/reef-", "is filed at commissioning/reef-"],
        "required_tools": ["list_files"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_FSE)
write_case(
    "fs-8008",
    desc="Asks where the signed commissioning sign-off for the reef-700 display is; only an unsigned draft checklist and another system's signed sheet exist, and the log says the sign-off visit is scheduled",
    task_type="find_file", family=fam("fs", "reefsignoff"), level="L2", ref_calls=2,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "commissioning/reef-700-checklist-draft.pdf"},
    axes=["DEC", "OBS"],
    files=FILES_FSE, turns=TURNS_FSE,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
log = files["commissioning/SIGNOFF-LOG.txt"].splitlines()
assert log[0] == "system | document | status | date"
status = {l.split(" | ")[1]: l.split(" | ")[2] for l in log[1:] if l.strip()}
assert status["reef-700-signoff.pdf"].startswith("not generated")
assert status["reef-700-checklist-draft.pdf"].startswith("draft")
assert status["reef-350-signoff.pdf"] == "signed"
assert not any(p.endswith("reef-700-signoff.pdf") for p in files)
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_FSE, WORDS_FSE),
    notes='''
## Traps
- TR-ABSENT: commissioning/SIGNOFF-LOG.txt 把 reef-700-signoff.pdf 记为「not generated; sign-off visit scheduled for 2026-10-14」，目录里没有这份文件。
- TR-DECOY: commissioning/reef-700-checklist-draft.pdf 是同一个系统的文件，只是未签字的 draft checklist；同目录还有 reef-350 的已签字 sign-off。把 draft 当签收单、或把 350 系统的签收单拿来应付，都是诱饵答案。

## Reference solution
1. 列出 commissioning/：两份 pdf、SIGNOFF-LOG.txt 和 README。
2. 读 commissioning/SIGNOFF-LOG.txt：reef-700 的 sign-off 未生成，10-14 安排签收；draft 未签字。
终答（2–4 句）：There is no signed sign-off sheet for reef-700 yet: the log marks the reef-700 sign-off as not generated, with the sign-off visit scheduled for Oct 14, and the only reef-700 document is the unsigned draft checklist. The signed reef-350 sheet belongs to a different system. The draft can be shown as provisional, but the warranty paperwork waits for the visit. 判据：包含 reef-700 和一个 not generated/unsigned 说法，不得把 draft 或 reef-350 的签收单当答案。

## Why the answer is unique
The draft is the nearest artefact by name and system, but it labels itself DRAFT and unsigned, and the README allows only sheets marked signed in the log to count as warranty documents; the log itself lists the signed sheet as not generated with a scheduled visit. The reef-350 sheet is a different system. Nothing else in the workspace claims a signed reef-700 sheet, so the only defensible reply is that it does not exist yet.
''',
)

# ---------------------------------------------------------------- fs-8009
FILES_FSF = {
    "README.md": "# 芝麻开门儿童摄影 对账目录\n\n对账/ 存放供应商往来的正式单据；核对以对账单为准，报价单不能当对账依据。\n",
    "对账/往来登记.md": "# 雅映制品 往来登记\n\n| 单据 | 状态 | 备注 |\n|---|---|---|\n| 9 月对账单 | 已对账 | 2026-10-06 双方确认 |\n| 10 月对账单 | 未收到 | 厂家 10-09 答复：10 月订单还在出货，月底统一出具对账单 |\n| 10 月报价单 | 已收到 | 仅供报价参考 |\n",
    "对账/雅映制品-2026-09-对账单.pdf": "雅映制品 对账单（2026 年 9 月）\n客户：芝麻开门儿童摄影\n相册制作费合计：8620 元\n双方已确认\n",
    "对账/雅映制品-2026-10-报价单.pdf": "雅映制品 报价单（2026 年 10 月）\n客户：芝麻开门儿童摄影\n10 月相册单价与折扣预估，不作为对账依据\n",
}
WORDS_FSF = ["未收到", "没有收到", "还没收到", "尚未收到", "没收到", "月底", "未出具", "没有出具", "还没出具", "尚未出具", "还没出", "尚未出"]
TURNS_FSF = [{
    "prompt": "财务在做月度对账，让我找一下十月份相册厂家雅映制品的对账单，帮我看看收到没有。",
    "expect": {
        "output_contains": ["雅映制品"],
        "output_contains_any": WORDS_FSF,
        "output_excludes": ["对账单是 对账/雅映制品-2026-10-报价单", "对账单在 对账/雅映制品-2026-10-报价单", "对账单已收到", "8620", "8,620"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_FSF)
write_case(
    "fs-8009",
    desc="Asks for the October statement from the album vendor; only September's statement and an October quotation exist, and the ledger says the statement comes at month end",
    task_type="find_file", family=fam("fs", "albumrecon"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "对账/雅映制品-2026-10-报价单.pdf"},
    axes=["DEC", "ERR"],
    files=FILES_FSF, turns=TURNS_FSF,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
reg = files["对账/往来登记.md"]
rows = [l for l in reg.splitlines() if l.startswith("| 10 月对账单")]
assert len(rows) == 1 and "未收到" in rows[0] and "月底" in rows[0]
assert not any("2026-10-对账单" in p for p in files)
# Near-name decoys: the October quotation and September's statement exist.
assert "对账/雅映制品-2026-10-报价单.pdf" in files
assert "对账/雅映制品-2026-09-对账单.pdf" in files
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_FSF, WORDS_FSF),
    notes='''
## Traps
- TR-ABSENT: 对账/往来登记.md 写明 10 月对账单「未收到」，厂家 10-09 答复 10 月订单还在出货、月底统一出具；对账/ 目录里没有 10 月的对账单文件。
- TR-NEARNAME: 对账/雅映制品-2026-10-报价单.pdf 同厂家同月份，只差「报价单/对账单」；9 月对账单同名同种类但月份不同。拿报价单或 9 月对账单当 10 月对账依据，就是诱饵答案。

## Reference solution
1. 列出 对账/：9 月对账单、10 月报价单、往来登记、README。
2. 读 对账/往来登记.md：10 月对账单未收到，月底出具。
3. 读 README 确认报价单不能当对账依据。
终答（2–4 句）：十月份雅映制品的对账单还没收到——往来登记里写着厂家 10-09 答复 10 月订单还在出货，月底统一出具。对账目录里只有 9 月的对账单和 10 月的报价单，报价单按目录说明不能当对账依据。月底拿到对账单后我再帮你核对。判据：包含「雅映制品」和一个「未收到/月底」说法，不得把报价单或 9 月对账单当 10 月对账单。

## Why the answer is unique
报价单错在性质不同：文件自述是单价与折扣预估、不作为对账依据，README 也写明核对以对账单为准；9 月对账单错在期间不同，对应的是 9 月业务。往来登记是单据收发状态的权威记录，写明 10 月对账单未收到且月底出具，所以唯一站得住的回答是说明未收到并等月底。
''',
)

# ---------------------------------------------------------------- fs-8010
FILES_FSG = {
    "README.md": "# 暖窝动物医院 手术档案\n\n手术/ 只存放已扫描归档的手术文件；归档状态以 手术/手术登记.csv 为准。\n",
    "手术/手术登记.csv": "日期,宠物,手术,同意书状态\n2026-10-07,雪球,绝育,客户带回补充签字，10-09 交回，待扫描\n2026-10-09,阿福,洁牙,已扫描归档\n",
    "手术/归档说明.md": "# 手术档案归档说明\n\n签字同意书由客户带回补充签字，交回前台后由前台扫描归档；未扫描的手术以手术登记.csv 的状态为准。\n",
    "手术/雪球-麻醉知情同意书-签字版.pdf": "暖窝动物医院 麻醉知情同意书（已签字）\n宠物：雪球（布偶猫）\n手术：绝育\n客户签字日期：2026-10-07\n",
}
WORDS_FSG = ["待扫描", "未扫描", "没有扫描", "还没扫描", "尚未扫描", "未归档", "没有归档", "还没归档", "尚未归档", "交回"]
TURNS_FSG = [{
    "prompt": "雪球主人想确认她那份绝育手术同意书的扫描件是不是已经放进档案了，她自己也要一份复印件。",
    "expect": {
        "output_contains": ["雪球"],
        "output_contains_any": WORDS_FSG,
        "output_excludes": ["扫描件是 手术/雪球-麻醉知情同意书", "扫描件在 手术/雪球-麻醉知情同意书", "手术同意书已归档", "手术同意书已经归档", "已经放进档案了"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_FSG)
write_case(
    "fs-8010",
    desc="Asks whether the signed surgical consent scan for a cat's spay is archived; the registry says the form is back and awaiting scanning, only the signed anesthesia consent under the same name exists",
    task_type="presence", family=fam("fs", "consentscan"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "手术/雪球-麻醉知情同意书-签字版.pdf"},
    axes=["DEC", "ERR"],
    files=FILES_FSG, turns=TURNS_FSG,
    verify=V('''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
rows = {r["宠物"]: r for r in csv.DictReader(io.StringIO(files["手术/手术登记.csv"]))}
# The consent form is back from the client but has not been scanned yet.
assert "待扫描" in rows["雪球"]["同意书状态"]
assert not any("雪球" in p and "手术同意书" in p for p in files)
# Near-name decoy: the signed anesthesia consent for the same pet.
assert "手术/雪球-麻醉知情同意书-签字版.pdf" in files
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_FSG, WORDS_FSG),
    notes='''
## Traps
- TR-ABSENT: 手术/手术登记.csv 写明雪球 10-07 绝育的同意书「客户带回补充签字，10-09 交回，待扫描」，手术/ 目录里没有她的手术同意书扫描件。
- TR-NEARNAME: 手术/雪球-麻醉知情同意书-签字版.pdf 同宠物同手术已签字，但它是麻醉知情同意书，不是手术同意书。把麻醉同意书扫描件当成手术同意书答复「已归档」，就是诱饵答案。

## Reference solution
1. 读 手术/手术登记.csv：雪球的同意书 10-09 交回、待扫描。
2. 读 手术/归档说明.md：交回后由前台扫描归档。
3. 列出 手术/：雪球名下只有麻醉知情同意书。
终答（2–4 句）：手术档案里还没有雪球同意书的扫描件——手术登记写明 10-09 已交回、待扫描。目录里雪球名下只有已签字的麻醉知情同意书，那是麻醉那份，不是手术同意书的扫描件。等前台扫描归档后就有，到时可以复印一份给主人。判据：包含「雪球」和一个「待扫描/未归档」说法，不得把麻醉同意书当手术同意书。

## Why the answer is unique
诱饵错在文书种类不同：麻醉知情同意书的标题和内容都是麻醉事项，手术同意书是另一份需要客户补充签字的文书，归档说明写明交回后由前台扫描、未扫描的以手术登记为准。登记表证实雪球那份还在待扫描，目录里也没有手术同意书文件，所以「扫描件已归档」不成立，唯一站得住的回答是说明待扫描并给出归档后的下一步。
''',
)

# ---------------------------------------------------------------- fs-8011
FILES_FSH = {
    "README.md": "Fin & Frond Aquatics husbandry binder. Only charts marked current in husbandry/HUSBANDRY-LOG.txt are in force.\n",
    "husbandry/HUSBANDRY-LOG.txt": "document | status | note\njellyfish-feeding-chart-2025.pdf | superseded | pre-renovation stocking, do not use\njellyfish-feeding-chart-2026.pdf | not generated | new chart in review with the curator, expected after the moon jelly census\nseahorse-feeding-chart.pdf | current | -\n",
    "husbandry/jellyfish-feeding-chart-2025.pdf": "Fin & Frond Aquatics - jellyfish display feeding chart (2025)\nKreisel tank, pre-renovation stocking\nFeeds: 3 per day, brine shrimp only\nSuperseded by the 2026-08 renovation\n",
    "husbandry/seahorse-feeding-chart.pdf": "Fin & Frond Aquatics - seahorse display feeding chart (current)\nFeeds: 4 per day, mysis\n",
}
WORDS_FSH = ["in review", "under review", "not generated", "not been issued", "hasn't been issued",
             "has not been issued", "not yet issued", "superseded", "no current", "isn't current",
             "is not current", "old chart", "curator"]
TURNS_FSH = [{
    "prompt": "A weekend volunteer needs the feeding chart for the jellyfish display. Where do I find the current one?",
    "expect": {
        "output_contains": ["jellyfish"],
        "output_contains_any": WORDS_FSH,
        "output_excludes": ["current one is husbandry/", "current chart is husbandry/", "find it at husbandry/",
                            "find the current one at husbandry/", "3 per day", "brine shrimp", "mysis"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_FSH)
write_case(
    "fs-8011",
    desc="Asks for the current feeding chart of the jellyfish display; the 2025 chart was superseded by the renovation and the replacement is still in review with the curator",
    task_type="find_file", family=fam("fs", "jellychart"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "husbandry/jellyfish-feeding-chart-2025.pdf"},
    axes=["DEC", "OBS"],
    files=FILES_FSH, turns=TURNS_FSH,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
log = files["husbandry/HUSBANDRY-LOG.txt"].splitlines()
assert log[0] == "document | status | note"
status = {l.split(" | ")[0]: l.split(" | ")[1] for l in log[1:] if l.strip()}
assert status["jellyfish-feeding-chart-2026.pdf"] == "not generated"
assert status["jellyfish-feeding-chart-2025.pdf"] == "superseded"
assert status["seahorse-feeding-chart.pdf"] == "current"
assert not any(p.endswith("jellyfish-feeding-chart-2026.pdf") for p in files)
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_FSH, WORDS_FSH),
    notes='''
## Traps
- TR-ABSENT: husbandry/HUSBANDRY-LOG.txt 把 jellyfish-feeding-chart-2026.pdf 记为「not generated」，新图表还在 curator 那里评审，目录里没有 2026 年的水母缸喂食表。
- TR-DECOY: husbandry/jellyfish-feeding-chart-2025.pdf 同一 display、只差年份，但已被 2026-08 改造 superseded；同目录还有海马缸的现行喂食表。把 2025 旧表或海马表当现行喂食表，就是诱饵答案。

## Reference solution
1. 读 husbandry/HUSBANDRY-LOG.txt：水母缸 2026 图表 not generated、in review；2025 图表 superseded。
2. 列出 husbandry/：只有 2025 水母表和海马表。
3. 读 README 确认只有 current 的图表有效。
终答（2–4 句）：There is no current jellyfish feeding chart yet: the log marks the 2026 chart as not generated while it is in review with the curator, and the 2025 chart in the binder is superseded by the renovation. The seahorse chart belongs to a different display. The volunteer should wait for the curator's sign-off, and I can chase it after the moon jelly census. 判据：包含 jellyfish 和一个 in review/not generated 说法，不得把 2025 旧表或海马表当现行喂食表。

## Why the answer is unique
The 2025 chart is the nearest match by display, but it self-describes as pre-renovation stocking and the log marks it superseded with a note not to use it; the seahorse chart is a different tank with different prey. The README says only charts marked current are in force, and the log lists the jellyfish 2026 chart as not generated, so no current jellyfish chart exists and the only defensible reply points to the review.
''',
)

# ---------------------------------------------------------------- log-8010
FILES_LGA = {
    "README.md": "# 安宁宠物医院 运维日志库\n\nlogs/ 按网关、按天存放告警日志。\n",
    "logs/监护网关-M1-2026-10-06.log": "安宁宠物医院 监护网关 M1 告警日志（手术室）\n2026-10-06T22:14:00+08:00 WARN 传感器脱落 手术台B\n2026-10-06T23:05:41+08:00 WARN 传感器脱落 手术台A\n2026-10-07T01:22:33+08:00 WARN 传感器脱落 手术台B\n2026-10-07T04:40:09+08:00 WARN 传感器脱落 手术台A\n",
    "logs/监护网关-M2-2026-10-06.log": "安宁宠物医院 监护网关 M2 告警日志（住院部）\n2026-10-06T19:12:05+08:00 WARN 输液低流量 3 号住院笼 持续 45 秒\n2026-10-06T20:41:22+08:00 WARN 输液低流量 5 号住院笼 持续 60 秒\n2026-10-06T21:58:47+08:00 INFO 网关进入升级窗口，告警暂停采集\n2026-10-06T21:59:02+08:00 INFO 升级窗口内告警不落盘、不补录，恢复后从实时数据继续\n2026-10-07T06:02:10+08:00 INFO 网关升级完成，采集恢复\n2026-10-07T06:35:18+08:00 WARN 输液低流量 3 号住院笼 持续 30 秒\n",
    "运维/值班交接-2026-10-06.md": "# 值班交接（10 月 6 日夜班）\n\n住院部监护网关 M2 今夜 22 点前后做固件升级，升级窗口内告警不落盘、不补录；手术室的 M1 不在升级范围，正常记录。原始数据只保留在网关本机，保留 7 天。\n",
}
WORDS_LGA = ["不落盘", "不补录", "没有补录", "未补录", "暂停采集", "没有采集", "未采集", "没有记录",
             "没有日志", "缺失", "缺口", "空白", "升级窗口", "没法统计", "无法统计", "不完整"]
TURNS_LGA = [{
    "prompt": "住院部 10 月 6 日夜里到 7 日早上，输液低流量告警一共触发了多少次？",
    "expect": {
        "output_contains": ["M2"],
        "output_contains_any": WORDS_LGA,
        "output_excludes": ["0 次", "零次", "共 0", "为 0", "一共 0", "4 次", "一共 4 次", "共 4 次"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_LGA)
write_case(
    "log-8010",
    desc="Asks how many low-flow infusion alarms fired overnight; the ward gateway was in a firmware upgrade window, alarms were not persisted and the nearby operating-room gateway did log alarms",
    task_type="time_window", family=fam("log", "monitorgap"), level="L1", ref_calls=3,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"},
    axes=["DEC"],
    files=FILES_LGA, turns=TURNS_LGA,
    verify=V('''
import json
import re

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
m2 = files["logs/监护网关-M2-2026-10-06.log"]
assert "告警暂停采集" in m2 and "不落盘、不补录" in m2 and "采集恢复" in m2
# No infusion low-flow alarm line falls inside the upgrade window 21:58-06:02.
for line in m2.splitlines():
    m = re.match(r"2026-10-(\\d\\d)T(\\d\\d):(\\d\\d)", line)
    if not m or "输液低流量" not in line:
        continue
    day, hh, mm = int(m.group(1)), int(m.group(2)), int(m.group(3))
    t = hh * 60 + mm
    if day == 6:
        assert t <= 21 * 60 + 58, line
    else:
        assert t >= 6 * 60 + 2, line
# The operating-room gateway did log through the night, but different alarms.
m1 = files["logs/监护网关-M1-2026-10-06.log"]
warns = [l for l in m1.splitlines() if " WARN " in l]
assert warns and all("传感器脱落" in l for l in warns)
assert "不补录" in files["运维/值班交接-2026-10-06.md"]
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_LGA, WORDS_LGA),
    notes='''
## Traps
- TR-ABSENT: logs/监护网关-M2-2026-10-06.log 在 21:58 记录「网关进入升级窗口，告警暂停采集」，并注明「升级窗口内告警不落盘、不补录」，到 7 日 06:02 才恢复。夜里这一段一行都没有。把「没有告警行」读成 0 次、或把手术室 M1 的告警数拿来充数，都是诱饵答案（0）。

## Reference solution
1. 列出 logs/：M1、M2 两份日志。
2. 读 M2 日志：21:58 进升级窗口、不落盘不补录，06:02 恢复；可见的低流量告警只有窗口前两条和恢复后一条。
3. 读 运维/值班交接-2026-10-06.md：确认升级窗口、M1 不受影响。
终答（2–4 句）：这个数统计不出来：住院部的 M2 网关 10 月 6 日 21:58 进入固件升级窗口，窗口内告警不落盘、不补录，到 7 日早上 06:02 才恢复采集。日志里只能看到升级前的输液低流量告警和恢复后的一次，夜里的部分是空白，不能当成没有发生。值班交接确认了这一点；原始数据只在网关本机保留 7 天，需要的话尽快去取。判据：包含「M2」和一个「不落盘/缺口/没法统计」说法，不得报 0 次。

## Why the answer is unique
诱饵 0 错在把「没有记录」当成「没有发生」：日志自己写明升级窗口内告警不落盘、不补录，值班交接也确认。M1 是另一台网关（手术室），夜里记录的是传感器脱落告警，与住院部输液低流量无关，拿它计数是张冠李戴。工作区没有其他来源覆盖这一夜，所以次数无法确定，只能说明缺口并指向网关本机的原始数据。
''',
)

# ---------------------------------------------------------------- log-8011
FILES_LGB = {
    "README.md": "# 岚山影像工作室 运维记录\n\nlogs/ 存放影棚设备日志。\n",
    "logs/灯光同步-2026-10-08.log": "岚山影像工作室 灯光控制器同步日志（2026-10-08）\n2026-10-08T09:12:40+08:00 2号影棚 WARN 同步失败 触发器未响应 重试成功\n2026-10-08T09:47:15+08:00 2号影棚 WARN 同步失败 触发器未响应 重试成功\n2026-10-08T10:05:12+08:00 2号影棚 WARN 同步失败 触发器未响应 重试成功\n2026-10-08T11:33:26+08:00 2号影棚 WARN 同步失败 通道拥塞 重试成功\n2026-10-08T13:21:54+08:00 2号影棚 WARN 同步失败 触发器未响应 重试成功\n2026-10-08T15:48:07+08:00 2号影棚 WARN 同步失败 触发器未响应 重试成功\n2026-10-08T17:02:39+08:00 2号影棚 WARN 同步失败 通道拥塞 重试成功\n2026-10-08T18:30:00+08:00 INFO 3号影棚控制器当日固件升级，未接入同步采集\n",
    "运维/影棚设备台账.md": "# 影棚设备台账\n\n- 2号影棚：灯光控制器 LC-2h，正常接入同步采集。\n- 3号影棚：灯光控制器 LC-3h，2026-10-08 固件升级，当日不接入同步采集，10-09 起恢复记录。\n",
}
WORDS_LGB = ["未接入", "没有接入", "没接入", "不接入", "未采集", "没有采集", "没有记录", "无记录",
             "没有日志", "无日志", "未记录", "升级", "没有失败"]
TURNS_LGB = [{
    "prompt": "10 月 8 日 3 号影棚的灯光同步失败一共有几条？",
    "expect": {
        "output_contains": ["影棚"],
        "output_contains_any": WORDS_LGB,
        "output_excludes": ["7 条", "共 7", "一共 7", "7 次"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_LGB)
write_case(
    "log-8011",
    desc="Asks how many lighting sync failures studio 3 logged on Oct 8; that controller was off the sync bus for a firmware upgrade, only studio 2's failures are in the log",
    task_type="count_events", family=fam("log", "lightssync"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"], decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "7"},
    axes=["DEC", "ERR"],
    files=FILES_LGB, turns=TURNS_LGB,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
log = files["logs/灯光同步-2026-10-08.log"].splitlines()
fails = [l for l in log if "同步失败" in l]
assert fails and all("2号影棚" in l for l in fails)
assert len(fails) == 7
assert any("3号影棚" in l and "未接入" in l for l in log)
ledger = files["运维/影棚设备台账.md"]
assert "3号影棚" in ledger and "不接入同步采集" in ledger
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_LGB, WORDS_LGB),
    notes='''
## Traps
- TR-ABSENT: logs/灯光同步-2026-10-08.log 末行写明「3号影棚控制器当日固件升级，未接入同步采集」，运维/影棚设备台账.md 也写明它当日不接入、10-09 起恢复记录。3 号棚当天一条记录都没有。
- TR-NEARNAME: 同一份日志里有 2号影棚的同步失败记录（触发器未响应、通道拥塞）。把 2 号棚的失败数当成 3 号棚的，就是诱饵答案。

## Reference solution
1. 列出 logs/：一份灯光同步日志和设备台账。
2. 读 logs/灯光同步-2026-10-08.log：同步失败全标着 2号影棚，末行注明 3 号棚未接入。
3. 读 运维/影棚设备台账.md：3 号棚当日固件升级、不接入同步采集。
终答（2–4 句）：3号影棚一条同步失败记录都没有：设备台账写明它的控制器 10 月 8 日固件升级，当天未接入同步采集，10-09 才恢复记录。日志里那几条同步失败全是 2号影棚的，不是 3 号棚的。要看 3 号棚的失败情况得等升级后的日志，或者查一下当天的现场记录。判据：包含「3号影棚」和一个「未接入/没有记录」说法，不得报 2 号棚的失败数。

## Why the answer is unique
诱饵错在对象不同：同步失败行的影棚字段都是 2号影棚，3 号棚在日志里只出现在「未接入同步采集」的说明行；设备台账确认它当天不接入、次日恢复。「未接入」意味着没有采集而不是没有失败，所以任何计数都站不住，唯一站得住的回答是说明没有记录及原因，并指向恢复后的日志。
''',
)

# ---------------------------------------------------------------- log-8012
FILES_LGC = {
    "README.md": "Tidepool Corner maintenance binder. logs/ holds daily equipment event logs; maintenance/PUMP-LEDGER.md tracks pump service.\n",
    "logs/kalk-dosing-2026-10-09.log": "Tidepool Corner - dosing pump event log, 2026-10-09\n2026-10-09T08:02:11Z INFO KD-2 removed for impeller rebuild; KD-2 spare installed in its place\n2026-10-09T08:40:05Z WARN KD-2 spare calibration drift 4 ml\n2026-10-09T13:15:47Z WARN KD-2 spare calibration drift 6 ml\n2026-10-09T19:02:30Z WARN KD-2 spare calibration drift 5 ml\n",
    "maintenance/PUMP-LEDGER.md": "# Dosing pump ledger\n\n- KD-2 (kalkwasser, display system): removed for impeller rebuild 2026-10-09, reinstalled 2026-10-10. It ran no doses on 2026-10-09 and logged nothing itself.\n- KD-2 spare: backup pump, covered the schedule on 2026-10-09. Its calibration warnings are its own and are not KD-2's.\n",
}
WORDS_LGC = ["rebuild", "removed", "out of service", "didn't run", "did not run", "logged nothing",
             "no events", "no entries", "not in service", "offline", "reinstalled", "no warnings"]
TURNS_LGC = [{
    "prompt": "How many calibration warnings did the KD-2 kalkwasser pump log on October 9?",
    "expect": {
        "output_contains": ["KD-2"],
        "output_contains_any": WORDS_LGC,
        "output_excludes": ["3 calibration", "three calibration", "3 warnings", "three warnings",
                            "total of 3", "3 times", "three times"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_LGC)
write_case(
    "log-8012",
    desc="Asks how many calibration warnings the KD-2 kalkwasser pump logged on Oct 9; the pump was out for an impeller rebuild and the three warnings that day belong to its spare",
    task_type="count_events", family=fam("log", "dosingpump"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "3"},
    axes=["DEC", "OBS"],
    files=FILES_LGC, turns=TURNS_LGC,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
log = files["logs/kalk-dosing-2026-10-09.log"].splitlines()
warns = [l for l in log if " WARN " in l]
assert warns and all("KD-2 spare" in l for l in warns)
assert len(warns) == 3
assert any("removed for impeller rebuild" in l for l in log)
ledger = files["maintenance/PUMP-LEDGER.md"]
assert "rebuild 2026-10-09" in ledger and "reinstalled 2026-10-10" in ledger
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_LGC, WORDS_LGC),
    notes='''
## Traps
- TR-ABSENT: KD-2 当天 08:02 被「removed for impeller rebuild」，10-10 才回装；台账写明它 10-09 一剂没跑、自己一条日志都没有，所以它的告警数无法统计，也不能报 0。
- TR-DECOY: 当天日志里的三条 calibration drift 全是顶班的 KD-2 spare 的。把 spare 的告警数当成 KD-2 的，就是诱饵答案。

## Reference solution
1. 列出 logs/：一份 dosing 事件日志和泵台账。
2. 读 logs/kalk-dosing-2026-10-09.log：KD-2 被拆下重建，spare 顶班；WARN 全标着 spare。
3. 读 maintenance/PUMP-LEDGER.md：KD-2 当天没跑、没日志；spare 的告警归 spare。
终答（2–4 句）：KD-2 logged nothing on Oct 9: it was removed that morning for an impeller rebuild and reinstalled the next day, so the pump never ran. The calibration warnings in that day's log all belong to KD-2 spare, which covered the schedule. If you need the spare's drift trend, say so and I will pull its numbers. 判据：包含 KD-2 和一个 removed/rebuild/did not run 说法，不得把 spare 的告警数报成 KD-2 的。

## Why the answer is unique
The three warnings are the nearest-looking data, but every WARN line names KD-2 spare as the source, and both the log's INFO line and the ledger state KD-2 was removed for a rebuild and ran no doses. Counting them for KD-2 would attribute another pump's calibration behaviour to it. Nothing else logs KD-2 events that day, so the only defensible reply is that KD-2 logged nothing and why.
''',
)

# ---------------------------------------------------------------- log-8013
FILES_LGD = {
    "README.md": "# 青芷宠物诊所 疫苗收货\n\nlogs/ 下按月存放冷链入库日志。\n",
    "logs/冷链入库-2026-10.csv": "日期,批次,品名,数量,到货时间,运输最高温度℃,记录人\n2026-10-06,MS-2609C,猫三联,24 盒,09:40,,郑护士\n2026-10-06,QK-2609A,犬四联,12 盒,09:55,7.8,郑护士\n2026-10-06,DN-2609B,犬瘟热,8 盒,10:20,6.2,郑护士\n",
    "运维/冷链收货说明.md": "# 冷链收货说明\n\n运输最高温度取自随货温控条，由扫描仪读出后填入入库日志。\n10 月 6 日 MS-2609C 的温控条因扫描仪故障未能读出，原始温控条已寄回厂家核对，厂家回传后再补填。\n",
}
WORDS_LGD = ["未读出", "没读出", "读不出", "未扫描", "没有扫描", "未填", "没填", "没有填", "空白", "缺失",
             "待回传", "未回传", "没有回传", "还没回传", "寄回", "扫描仪"]
TURNS_LGD = [{
    "prompt": "帮我查一下 10 月 6 日入库的那批猫三联，运输途中最高温度是多少？",
    "expect": {
        "output_contains": ["猫三联"],
        "output_contains_any": WORDS_LGD,
        "output_excludes": ["7.8", "6.2"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_LGD)
write_case(
    "log-8013",
    desc="Asks the maximum transport temperature of a cat vaccine batch received Oct 6; its temperature field is blank because the strip reader failed, other batches that day have values",
    task_type="root_cause", family=fam("log", "vaxtempfield"), level="L2", ref_calls=3,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "7.8"},
    axes=["DEC"],
    files=FILES_LGD, turns=TURNS_LGD,
    verify=V('''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
rows = {r["批次"]: r for r in csv.DictReader(io.StringIO(files["logs/冷链入库-2026-10.csv"]))}
# The cat vaccine batch has no transport temperature recorded.
assert rows["MS-2609C"]["品名"] == "猫三联"
assert rows["MS-2609C"]["运输最高温度℃"] == ""
# Same-day batches do have values, which are the decoys.
assert rows["QK-2609A"]["运输最高温度℃"] == "7.8"
assert rows["DN-2609B"]["运输最高温度℃"] == "6.2"
doc = files["运维/冷链收货说明.md"]
assert "扫描仪故障" in doc and "补填" in doc
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_LGD, WORDS_LGD),
    notes='''
## Traps
- TR-ABSENT: logs/冷链入库-2026-10.csv 里 MS-2609C（猫三联）一行的「运输最高温度℃」是空的；运维/冷链收货说明.md 写明当天扫描仪故障未读出温控条，原始温控条已寄回厂家，回传后再补填。拿同日别的批次的温度值（7.8、6.2）来填，就是诱饵答案。

## Reference solution
1. 列出 logs/：入库 CSV 和收货说明。
2. 读 logs/冷链入库-2026-10.csv：MS-2609C 行温度列为空，同日 QK-2609A、DN-2609B 有值。
3. 读 运维/冷链收货说明.md：扫描仪故障、待厂家回传补填。
终答（2–4 句）：查不到这个温度：入库日志里猫三联（MS-2609C）那行的运输最高温度是空的，冷链收货说明写明当天扫描仪故障没读出温控条，原始温控条已寄回厂家，回传后才补填。同日另外两个批次的温度值都有，但那是别的批次，不能拿来填这批。可以先问厂家要核对结果。判据：包含「猫三联」和一个「未读出/空白/待回传」说法，不得报别的批次的温度。

## Why the answer is unique
诱饵 7.8 和 6.2 错在批次不同：它们分别属于 QK-2609A（犬四联）和 DN-2609B（犬瘟热），疫苗运输温度按批次记录，不同批次不能互相替代。收货说明解释了空值的原因（扫描仪故障）并给出补填流程，所以唯一站得住的回答是说明字段缺失、等厂家回传。
''',
)

# ---------------------------------------------------------------- log-8014
FILES_LGE = {
    "README.md": "# 小橡树亲子摄影 运维日志\n\nlogs/ 存放云相册归档日志。\n",
    "logs/云归档-2026-10.log": "小橡树亲子摄影 云相册归档日志\n2026-10-04T23:30:12+08:00 TASK 自动归档完成 上传客片包 6 个\n2026-10-05T09:00:00+08:00 INFO 云相册平台迁移，自动归档任务暂停，恢复时间另行通知\n2026-10-05T14:22:41+08:00 MANUAL 客片包-十一外景-段家 上传成功（员工手动）\n2026-10-05T15:07:03+08:00 MANUAL 客片包-周岁照-曲家 上传成功（员工手动）\n2026-10-05T16:45:29+08:00 MANUAL 原片备份-十月第二批 上传成功（员工手动）\n2026-10-05T17:31:58+08:00 MANUAL 客片包-全家福-华家 上传成功（员工手动）\n",
    "运维/云相册迁移说明.md": "# 云相册平台迁移说明\n\n自动归档任务 10 月 5 日起暂停，迁移完成前不再夜间自动上传；期间的上传一律由员工在后台手动执行，日志记为 MANUAL。\n",
}
WORDS_LGE = ["暂停", "迁移", "手动", "MANUAL", "没有运行", "未运行", "没运行", "没有跑", "没跑",
             "停用", "没有执行", "未执行", "不再", "没有自动"]
TURNS_LGE = [{
    "prompt": "10 月 5 日晚上自动归档任务往云相册传了几个客片包？",
    "expect": {
        "output_contains": ["自动归档"],
        "output_contains_any": WORDS_LGE,
        "output_excludes": ["4 个", "四个", "4 条", "共 4", "一共 4", "上传了 4"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_LGE)
write_case(
    "log-8014",
    desc="Asks how many photo packages the auto-archive job uploaded on Oct 5; the job was paused for a platform migration and the uploads that day were staff manual uploads",
    task_type="count_events", family=fam("log", "cloudupload"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "4"},
    axes=["DEC", "OBS"],
    files=FILES_LGE, turns=TURNS_LGE,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
log = files["logs/云归档-2026-10.log"].splitlines()
task = [l for l in log if " TASK " in l]
assert len(task) == 1 and task[0].startswith("2026-10-04")
manual = [l for l in log if l.startswith("2026-10-05") and " MANUAL " in l]
assert len(manual) == 4
assert any("自动归档任务暂停" in l for l in log)
doc = files["运维/云相册迁移说明.md"]
assert "暂停" in doc and "手动" in doc
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_LGE, WORDS_LGE),
    notes='''
## Traps
- TR-ABSENT: logs/云归档-2026-10.log 在 10-05 09:00 记录「云相册平台迁移，自动归档任务暂停，恢复时间另行通知」，当天没有任何 TASK 行（上一条 TASK 是 10-04 的）。
- TR-DECOY: 当天日志里有四条 MANUAL 上传记录（员工手动）。把这几条手动上传数当成自动归档任务的上传数，就是诱饵答案。

## Reference solution
1. 列出 logs/：一份云归档日志和迁移说明。
2. 读 logs/云归档-2026-10.log：10-05 无 TASK 行，只有 MANUAL 上传和暂停说明。
3. 读 运维/云相册迁移说明.md：任务暂停期间上传一律手动、记为 MANUAL。
终答（2–4 句）：10 月 5 日自动归档任务没有运行：云相册平台从当天起迁移，任务暂停，迁移说明写明恢复时间另行通知。日志里 10-05 的几条上传都是员工手动执行的（记为 MANUAL），不是自动任务传的，所以「自动传了几个」答不出来。等平台迁移完成、任务恢复后我再帮你对数。判据：包含「自动归档」和一个「暂停/手动/MANUAL」说法，不得把手动上传数报成自动任务的。

## Why the answer is unique
诱饵错在执行主体不同：四条上传记录的级别都是 MANUAL，迁移说明明确期间上传一律员工手动执行；自动任务的记录级别是 TASK，当天没有。把「有上传」当成「任务在跑」就答错了主体，唯一站得住的回答是说明任务暂停、区分手动与自动，并等恢复。
''',
)

# ---------------------------------------------------------------- log-8015
FILES_LGF = {
    "README.md": "Barnacle Bay Pets quarantine room records. logs/ holds the daily water test log for the quarantine tanks.\n",
    "logs/quarantine-2026-10.csv": "date,tank,ammonia_ppm,nitrite_ppm,note\n2026-10-07,Q1,0.10,0.02,\n2026-10-08,Q1,,0.02,ammonia test kit expired mid-test; retest due with the new kit\n2026-10-08,Q2,0.50,0.00,\n2026-10-09,Q1,0.15,0.02,\n",
    "quarantine/TESTING-SOP.md": "# Water testing SOP\n\nAmmonia and nitrite are tested for every quarantine tank each morning and logged the same day. A blank ammonia cell means the test did not complete; never copy the previous day's reading into the log. Retests are backfilled with the tester's initials.\n",
}
WORDS_LGF = ["expired", "no reading", "not recorded", "wasn't recorded", "was not recorded", "missing",
             "retest", "blank", "empty", "not tested", "wasn't tested", "was not tested",
             "did not complete", "didn't complete", "backfilled"]
TURNS_LGF = [{
    "prompt": "What was the ammonia reading for tank Q1 on October 8?",
    "expect": {
        "output_contains": ["Q1"],
        "output_contains_any": WORDS_LGF,
        "output_excludes": ["0.50", "0.25", "0.10", "0.15"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_LGF)
write_case(
    "log-8015",
    desc="Asks the ammonia reading of quarantine tank Q1 on Oct 8; the cell is blank because the test kit expired mid-test, other tanks and days have values",
    task_type="root_cause", family=fam("log", "ammoniafield"), level="L2", ref_calls=3,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0.10"},
    axes=["DEC"],
    files=FILES_LGF, turns=TURNS_LGF,
    verify=V('''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
rows = {(r["date"], r["tank"]): r for r in csv.DictReader(io.StringIO(files["logs/quarantine-2026-10.csv"]))}
# Tank Q1 on Oct 8 has no ammonia value; the note explains why.
assert rows[("2026-10-08", "Q1")]["ammonia_ppm"] == ""
assert "expired" in rows[("2026-10-08", "Q1")]["note"]
# Adjacent days and the other tank do have values, which are the decoys.
assert rows[("2026-10-07", "Q1")]["ammonia_ppm"] == "0.10"
assert rows[("2026-10-08", "Q2")]["ammonia_ppm"] == "0.50"
assert rows[("2026-10-09", "Q1")]["ammonia_ppm"] == "0.15"
sop = files["quarantine/TESTING-SOP.md"]
assert "never copy" in sop and "did not complete" in sop
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_LGF, WORDS_LGF),
    notes='''
## Traps
- TR-ABSENT: logs/quarantine-2026-10.csv 里 (2026-10-08, Q1) 的 ammonia_ppm 是空格前后的空单元格，note 写明「ammonia test kit expired mid-test; retest due with the new kit」。相邻日子（0.10、0.15）和同日 Q2（0.50）都有值，拿任何一个来答，都是诱饵答案。

## Reference solution
1. 列出日志目录：检疫缸水测 CSV 和 TESTING-SOP。
2. 读 logs/quarantine-2026-10.csv：Q1 在 10-08 的氨氮列为空，note 写明试剂盒过期、需换新重测。
3. 读 quarantine/TESTING-SOP.md：空白代表检测未完成，不得抄前一天的值。
终答（2–4 句）：Tank Q1 has no ammonia reading for Oct 8: the cell is blank, and the note says the test kit expired mid-test with a retest due once the new kit arrived. The SOP says a blank means the test did not complete, so the neighbouring days' values and tank Q2's reading are not substitutes. The retest should be backfilled with the tester's initials; I can check whether that happened. 判据：包含 Q1 和一个 expired/blank/retest 说法，不得报相邻日子或别的缸的读数。

## Why the answer is unique
The blank cell is not a zero or a lost value: the row's own note says the kit expired mid-test, and the SOP states a blank means the test did not complete and must never be filled by copying the previous day. The 0.10 belongs to Oct 7, the 0.15 to Oct 9, and the 0.50 to tank Q2 on the same date - different days or a different tank, none of which substitutes for Q1 on Oct 8. The only defensible reply is that the reading is missing and a retest is pending.
''',
)

# ---------------------------------------------------------------- log-8016
FILES_LGG = {
    "README.md": "# 拾野宠物医院 设备日志\n\nlogs/ 存放新风机组压差日志，按机组分文件。\n",
    "logs/新风压差-手术室-2026-10.csv": "日期,机组,滤网状态,压差Pa,备注\n2026-10-05,手术室新风,初效滤网,78,\n2026-10-06,手术室新风,初效滤网,92,更换前偏高\n2026-10-07,手术室新风,已换新滤网,,记录仪随更换断开\n2026-10-08,手术室新风,新滤网,,记录仪仍未接回\n2026-10-09,手术室新风,新滤网,41,记录仪 10-09 上午重新接回\n",
    "logs/新风压差-犬舍-2026-10.csv": "日期,机组,滤网状态,压差Pa,备注\n2026-10-07,犬舍新风,初效滤网,66,\n2026-10-08,犬舍新风,初效滤网,69,\n2026-10-09,犬舍新风,初效滤网,71,\n",
    "运维/机组维护记录.md": "# 新风机组维护记录\n\n- 手术室新风：2026-10-07 更换初效滤网，压差记录仪随更换断开，10-09 上午重新接回；7 日、8 日无压差读数。\n- 犬舍新风：滤网未动，读数正常。\n",
}
WORDS_LGG = ["断开", "未接回", "没接回", "重新接回", "无读数", "没有读数", "没有记录", "无记录",
             "缺失", "没有数据", "无数据", "10-09", "10 月 9 日"]
TURNS_LGG = [{
    "prompt": "手术室的新风机组 10 月 8 日的压差读数是多少？",
    "expect": {
        "output_contains": ["手术室"],
        "output_contains_any": WORDS_LGG,
        "output_excludes": ["92", "78", "41", "66", "69", "71"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_LGG)
write_case(
    "log-8016",
    desc="Asks the differential pressure of the surgery-room air unit on Oct 8; the gauge was disconnected for a filter change and reconnected Oct 9, only pre-change and kennel-unit readings exist",
    task_type="time_window", family=fam("log", "airpresslog"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "92"},
    axes=["DEC", "OBS"],
    files=FILES_LGG, turns=TURNS_LGG,
    verify=V('''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
surg = {r["日期"]: r for r in csv.DictReader(io.StringIO(files["logs/新风压差-手术室-2026-10.csv"]))}
# No pressure reading on Oct 7-8: the gauge was disconnected for the filter change.
assert surg["2026-10-07"]["压差Pa"] == "" and surg["2026-10-08"]["压差Pa"] == ""
assert "断开" in surg["2026-10-07"]["备注"] and "未接回" in surg["2026-10-08"]["备注"]
assert surg["2026-10-09"]["压差Pa"] == "41"
# Decoys: pre-change readings of the same unit and the kennel unit's Oct 8 value.
assert surg["2026-10-06"]["压差Pa"] == "92"
kennel = {r["日期"]: r for r in csv.DictReader(io.StringIO(files["logs/新风压差-犬舍-2026-10.csv"]))}
assert kennel["2026-10-08"]["压差Pa"] == "69"
doc = files["运维/机组维护记录.md"]
assert "断开" in doc and "重新接回" in doc
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_LGG, WORDS_LGG),
    notes='''
## Traps
- TR-ABSENT: logs/新风压差-手术室-2026-10.csv 里 10-07、10-08 两行的压差列为空，备注写明「记录仪随更换断开」「仍未接回」；运维/机组维护记录.md 确认 10-09 上午才重新接回，7、8 两日无读数。
- TR-DECOY: 同一机组 10-06 更换前的读数（92）和同日犬舍新风的读数（69）都在日志里。拿更换前的读数或别的机组的读数来答，都是诱饵答案。

## Reference solution
1. 列出 logs/：手术室、犬舍两份压差 CSV 和维护记录。
2. 读 logs/新风压差-手术室-2026-10.csv：10-08 行压差为空，备注「记录仪仍未接回」。
3. 读 运维/机组维护记录.md：10-07 换滤网时断开，10-09 重新接回。
终答（2–4 句）：手术室新风 10 月 8 日没有压差读数：维护记录写明 10-07 换初效滤网时记录仪断开，10-09 上午才重新接回，7 日、8 日都是空白。日志里 10-08 有读数的是犬舍新风那台机组，更换前的读数也代表不了换滤网之后的状态。要看当天的实际压差，只能看机组本地表盘有没有抄表。判据：包含「手术室」和一个「断开/未接回/无读数」说法，不得报更换前或犬舍的读数。

## Why the answer is unique
两个诱饵都错在状态不同：92 是滤网更换前一天的读数，换滤网后压差必然改变，不能代表 10-08；69 是犬舍机组的读数，机组不同。日志备注和维护记录一致写明记录仪 10-07 断开、10-09 才接回，所以 10-08 在工作区里没有任何来源，唯一站得住的回答是说明断开区间并指向本地表盘。
''',
)

# ---------------------------------------------------------------- log-8017
FILES_LGH = {
    "README.md": "Reeftide Pet Supply back-office records. logs/ holds daily job logs; the sync runbook lives in ops/.\n",
    "logs/order-sync-2026-10-11.log": "Reeftide Pet Supply - online order sync log, 2026-10-11\n2026-10-11T03:00:00Z INFO sync job skipped: MantaCart migration window, auto-import paused this week\n2026-10-11T10:12:44Z MANUAL import batch B-1182, 7 orders (staff, web back office)\n2026-10-11T16:40:19Z MANUAL import batch B-1183, 4 orders (staff, web back office)\n",
    "ops/SYNC-RUNBOOK.md": "# Order sync runbook\n\nThe sync job normally imports MantaCart orders every night at 03:00. During the migration week (Oct 6-12) auto-import is paused; the log shows only staff manual imports, which are not sync runs.\n",
}
WORDS_LGH = ["paused", "migration", "manual", "no run", "did not run", "didn't run", "skipped",
             "no sync run", "no import", "staff"]
TURNS_LGH = [{
    "prompt": "How many orders did the MantaCart sync import during the night of October 11?",
    "expect": {
        "output_contains": ["sync"],
        "output_contains_any": WORDS_LGH,
        "output_excludes": ["11 orders", "imported 11", "total of 11", "11 new"],
        "required_tools": ["read_file"],
        "max_output_chars": 600,
    },
}]
check_no_numeric_contains(TURNS_LGH)
write_case(
    "log-8017",
    desc="Asks how many orders the store sync imported overnight; auto-import was paused for the platform migration and the only imports that day were staff manual batches",
    task_type="count_events", family=fam("log", "ordersync"), level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "11"},
    axes=["DEC", "OBS"],
    files=FILES_LGH, turns=TURNS_LGH,
    verify=V('''
import json

case = json.load(open("case.json"))
files = case["files"]
@@GUARD@@
log = files["logs/order-sync-2026-10-11.log"].splitlines()
# The scheduled sync run was skipped; the only imports are staff manual batches.
assert any("sync job skipped" in l for l in log)
manual = [l for l in log if " MANUAL " in l]
assert len(manual) == 2 and all("(staff" in l for l in manual)
runbook = files["ops/SYNC-RUNBOOK.md"]
assert "paused" in runbook and "not sync runs" in runbook
words = @@WORDS@@
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''', FILES_LGH, WORDS_LGH),
    notes='''
## Traps
- TR-ABSENT: logs/order-sync-2026-10-11.log 在 03:00 记录「sync job skipped: MantaCart migration window, auto-import paused this week」，当晚没有 sync 运行记录。
- TR-DECOY: 当天的两条 MANUAL 导入批次（B-1182、B-1183）共 11 单，是员工在后台手动导的。把这 11 单当成 sync 导入数，就是诱饵答案。

## Reference solution
1. 列出 logs/：一份订单同步日志和 runbook。
2. 读 logs/order-sync-2026-10-11.log：sync job skipped，只有两条 MANUAL 批次。
3. 读 ops/SYNC-RUNBOOK.md：迁移周自动导入暂停，手动导入不算 sync 运行。
终答（2–4 句）：The sync did not run that night: the log shows the 03:00 job skipped because the MantaCart migration window has auto-import paused this week, and the runbook confirms imports go manual for Oct 6-12. The import batches that day were staff manual imports, not sync runs, so there is no sync import count to give. Once the migration week ends the job resumes on its own. 判据：包含 sync 和一个 skipped/paused/manual 说法，不得把手动批次的单量报成 sync 导入数。

## Why the answer is unique
The manual batches are the nearest-looking numbers, but every one is labelled MANUAL with a staff note, and both the log's skip line and the runbook state auto-import is paused for the migration week and that manual imports are not sync runs. Counting them would attribute staff back-office work to the scheduled job. No other log covers that night, so the only defensible reply is that the sync did not run and why.
''',
)

print("b10a m2b: wrote 16 cases (fs-8004..fs-8011, log-8010..log-8017)")
for slug in sorted(_FAMILY_COUNT):
    assert _FAMILY_COUNT[slug] <= 3
