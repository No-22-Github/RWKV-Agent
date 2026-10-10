"""b10c (v1.4 §3.4) M4 part A: three-tool catalog (list_files, read_file, search_text).

70 cases: workspace cfg-8200..8211, doc-8200..8211, fs-8200..8210 (35) and
no-tool nt-8200..8234 (35). Each fixture is pinned by a sha256 in verify.py so
the sabotage test always notices, and the answer is recomputed from the files.
The reference answer of every case is checked against its own criteria here.

Run: cd bench/distill/tools/b10c && python3 m4a.py
"""
import hashlib
import json
import re

from common import revised
write_case = revised({
    "cfg-8210": "S5：去掉排除项 21:00——老师解释 winter.toml 是 21:00 属正确的解释性提及。",
    "doc-8202": "S5：题面加「诊所须知里」——原题面没有任何指向本地文件的线索，三遍老师都凭常识作答没读 FAQ。",
    "doc-8207": "S5：判据由 token「2」改为 any「2 approvals / two approvals」——老师写 Two approvals 被判挂。",
    "doc-8209": "S5：去掉排除项 30 kg——老师说明 Standard/Express 是 30 kg 属解释性提及。",
    "nt-8204": "S5：去掉排除项「那个」——老师在改动说明里引用原文「那个」被误判。",
})

THREE = ["list_files", "read_file", "search_text"]
NOCALL = {"tools": [], "require_active_no_call": True}
GEN = []  # (cid, zh) for the final tally


def _tok_ok(text, s):
    for m in re.finditer(re.escape(s), text):
        a = text[m.start() - 1] if m.start() > 0 else " "
        b = text[m.end()] if m.end() < len(text) else " "
        if not a.isalnum() and not b.isalnum():
            return True
    return False


def selfcheck(cid, ex, ref):
    for s in ex.get("output_contains", []):
        ok = _tok_ok(ref, s) if ex.get("output_contains_token") else s in ref
        assert ok, (cid, "contains", s)
    anyl = ex.get("output_contains_any")
    if anyl:
        assert any(s in ref for s in anyl), (cid, "any")
    for s in ex.get("output_excludes", []):
        assert s not in ref, (cid, "excludes", s)
    assert len(ref) <= ex.get("max_output_chars", 600), (cid, "len", len(ref))
    assert ex.get("max_output_chars", 600) <= 600


def _num(s):
    try:
        float(s.replace(",", ""))
        return True
    except ValueError:
        return False


def _tail(ex, expect_lit):
    """verify.py tail printing the one shape bank verify can match."""
    c = ex.get("output_contains", [])
    nums = [s for s in c if _num(s)]
    if nums:
        return 'print(json.dumps({"expected_number": %s}))\n' % nums[0].replace(",", "")
    if c:
        return 'print(json.dumps({"expected_string": %r}, ensure_ascii=False))\n' % c[0]
    return 'print(json.dumps({"expected_contains_any": %r}, ensure_ascii=False))\n' % (list(dict.fromkeys(ex["output_contains_any"])),)


def ws(cid, *, fam, desc, ttype, files, prompt, ref, contains=(), any_=(), excl=(), token=False,
       req=("read_file",), maxc=400, calls=1, ans_expr, ans, traps, unique, zh, level="L0"):
    ex = {}
    if contains:
        ex["output_contains"] = list(contains)
    if token:
        ex["output_contains_token"] = True
    if any_:
        ex["output_contains_any"] = list(any_)
    if excl:
        ex["output_excludes"] = list(excl)
    ex["required_tools"] = list(req)
    ex["max_output_chars"] = maxc
    selfcheck(cid, ex, ref)
    digest = hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    verify = ('import hashlib\nimport json\nimport re\n\ncase = json.load(open("case.json"))\nfiles = case["files"]\n'
              'assert hashlib.sha256(json.dumps(files, sort_keys=True, ensure_ascii=False).encode()).hexdigest() == %r\n'
              'ans = %s\nassert ans == %r\n' % (digest, ans_expr, ans)) + _tail(ex, ans)
    notes = ("## Traps\n%s\n\n## Reference solution\n%s\n终答示例：%s\n判据见 case.json（%s）。\n\n## Why the answer is unique\n%s\n"
             % (traps, "只提供 list_files / read_file / search_text 三个工具，正常检索后作答。", ref,
                "contains=%s any=%s excl=%s" % (list(contains), list(any_), list(excl)), unique))
    write_case(cid, desc=desc, task_type=ttype, family="fam-%s-b10c-%s" % (cid.split("-")[0], fam), level=level,
               ref_calls=calls, offered_tools=THREE, axes=[], files=files,
               turns=[{"prompt": prompt, "expect": ex}], verify=verify, notes=notes)
    GEN.append((cid, zh))


def nt(cid, *, fam, desc, ttype="concept", prompt, ref, contains=(), any_=(), excl=(), token=False, maxc=400,
       check, zh, axes=("DEC",)):
    """check: python source asserting the answer from literals; it may print nothing."""
    ex = dict(NOCALL)
    if contains:
        ex["output_contains"] = list(contains)
    if token:
        ex["output_contains_token"] = True
    if any_:
        ex["output_contains_any"] = list(any_)
    if excl:
        ex["output_excludes"] = list(excl)
    ex["max_output_chars"] = maxc
    selfcheck(cid, ex, ref)
    verify = ('import json\n\ncase = json.load(open("case.json"))\nprompt = case["turns"][0]["prompt"]\n'
              + check.strip("\n") + "\n" + _tail(ex, None))
    notes = ("## Traps\n- 无。清单里没有合适的工具、问题也不需要工作区，直接回答。\n\n## Reference solution\n不调用任何工具。终答示例：%s\n"
             "判据：零调用，%s。\n\n## Why the answer is unique\n%s\n"
             % (ref, "包含 %s %s" % (list(contains), list(any_)), desc))
    write_case(cid, desc=desc, task_type=ttype, family="fam-nt-b10c-%s" % fam, level="L0", ref_calls=0,
               offered_tools=THREE, axes=list(axes), files={}, turns=[{"prompt": prompt, "expect": ex}],
               verify=verify, notes=notes)
    GEN.append((cid, zh))


def z(n, *units):
    return [f"{n} {u}" for u in units] + [f"{n}{u}" for u in units]


# ================================================================ cfg
ws("cfg-8200", fam="inncheckin-01", zh=True, ttype="read_effective",
   desc="Read a guesthouse rules file for the latest check-in time, ignoring the archived 2025 rules",
   files={"规则/入住.yaml": "民宿: 山栖\n最晚入住时间: 22:00\n押金: 300\n早餐时段: 07:30-09:30\n",
          "规则/归档/入住-2025.yaml": "民宿: 山栖\n最晚入住时间: 21:00\n押金: 200\n早餐时段: 07:30-09:00\n",
          "README.md": "# 山栖民宿运营参数\n\n现行规则在 规则/ 下，归档/ 里是去年的旧版本。\n"},
   prompt="山栖民宿现在最晚几点之前要办完入住？",
   ref="山栖民宿现行规则是最晚 22:00 办完入住（规则/入住.yaml）；归档里去年的旧版是 21:00，已不适用。",
   any_=["22:00", "22 点", "22点", "晚上 10 点", "晚上10点", "十点"], excl=[], maxc=300,
   ans_expr='re.search(r"最晚入住时间: (\\S+)", files["规则/入住.yaml"]).group(1)', ans="22:00",
   traps="- 归档目录里有去年的旧规则（21:00），要用现行文件。",
   unique="现行文件只有一个最晚入住时间；归档文件的 21:00 是去年的旧值。")

ws("cfg-8201", fam="coopirrig-01", zh=True, ttype="read_effective",
   desc="Read a farm cooperative irrigation config where the greenhouse file overrides the default duration",
   files={"灌溉/默认.yaml": "单次时长分钟: 20\n每日次数: 3\n水压: 0.25\n",
          "灌溉/大棚B.yaml": "单次时长分钟: 12\n每日次数: 4\n",
          "灌溉/大棚C.yaml": "单次时长分钟: 15\n",
          "README.md": "# 合作社灌溉参数\n\n各大棚文件只写与默认不同的项，没写的沿用 默认.yaml。\n"},
   prompt="大棚 B 每次灌溉多长时间？",
   ref="大棚 B 每次灌溉 12 分钟：灌溉/大棚B.yaml 覆盖了默认的 20 分钟，一天灌 4 次。",
   any_=z(12, "分钟", "min", "分"), maxc=300,
   ans_expr='int(re.search(r"单次时长分钟: (\\d+)", files["灌溉/大棚B.yaml"]).group(1))', ans=12,
   traps="- 默认文件里是 20 分钟，大棚 B 自己覆盖为 12 分钟。",
   unique="大棚 B 文件显式写了单次时长，覆盖默认值；大棚 C 的 15 分钟属于另一个大棚。")

ws("cfg-8202", fam="gymcap-01", zh=True, ttype="read_effective",
   desc="Read a gym class settings file for the cap of the evening spin class, with a rejected draft beside it",
   files={"课程/团课.yaml": "瑜伽:\n  人数上限: 25\n  时长分钟: 60\n单车:\n  人数上限: 18\n  时长分钟: 45\n普拉提:\n  人数上限: 12\n  时长分钟: 50\n",
          "课程/团课-草稿.yaml": "单车:\n  人数上限: 30\n  时长分钟: 45\n",
          "README.md": "团课以 团课.yaml 为准，草稿未通过评审。\n"},
   prompt="晚上那节单车团课最多能约多少人？",
   ref="单车团课人数上限是 18 人（课程/团课.yaml）；草稿里的 30 人没有通过评审，不作数。",
   any_=z(18, "人", "位", "个人"), excl=["上限是 30", "上限为 30", "最多 30", "最多30"], maxc=300,
   ans_expr='int(re.search(r"单车:\\n  人数上限: (\\d+)", files["课程/团课.yaml"]).group(1))', ans=18,
   traps="- 草稿文件写了 30 人，但 README 说明未通过评审。",
   unique="团课.yaml 是唯一正式文件；单车的上限在其中写明为 18。")

ws("cfg-8203", fam="parkrate-01", zh=True, ttype="read_effective",
   desc="Read parking lot pricing where the weekend file overrides the hourly rate",
   files={"停车场/费率.toml": "[weekday]\n每小时 = 6\n封顶 = 40\n\n[weekend]\n每小时 = 9\n封顶 = 60\n",
          "停车场/节假日.toml": "[holiday]\n每小时 = 12\n封顶 = 80\n",
          "README.md": "# 万丰广场停车场\n\n费率分工作日、周末、节假日三套。\n"},
   prompt="万丰广场停车场周末停车每小时多少钱？",
   ref="周末每小时 9 元（停车场/费率.toml 的 weekend 段），封顶 60 元；工作日是 6 元、节假日是 12 元。",
   any_=z(9, "元", "块"), maxc=300,
   ans_expr='int(re.search(r"\\[weekend\\]\\n每小时 = (\\d+)", files["停车场/费率.toml"]).group(1))', ans=9,
   traps="- 工作日和节假日费率不同，要取 weekend 段。",
   unique="周末费率只有 weekend 段一个值 9；6 和 12 分别是工作日和节假日。")

ws("cfg-8204", fam="beekeep-01", zh=True, ttype="read_effective",
   desc="Read an apiary env file for the honey harvest interval, with a staging file as decoy",
   files={"养蜂场/prod.env": "取蜜间隔天=9\n蜂箱数=64\n预警温度=36\n",
          "养蜂场/试验.env": "取蜜间隔天=5\n蜂箱数=6\n预警温度=34\n",
          "README.md": "# 养蜂场参数\n\nprod.env 是正式蜂场，试验.env 只用于新蜂种试验。\n"},
   prompt="正式蜂场隔几天取一次蜜？",
   ref="正式蜂场每 9 天取一次蜜（养蜂场/prod.env）；试验蜂场的 5 天只用于新蜂种试验。",
   any_=z(9, "天", "日"), maxc=300,
   ans_expr='int(re.search(r"取蜜间隔天=(\\d+)", files["养蜂场/prod.env"]).group(1))', ans=9,
   traps="- 试验.env 是另一个蜂场，取蜜间隔不同。",
   unique="题问正式蜂场，对应 prod.env 的 9 天。")

ws("cfg-8205", fam="dancestudio-01", zh=True, ttype="read_effective",
   desc="Read a dance studio JSON config for the late-cancellation fee",
   files={"studio/policy.json": json.dumps({"cancel_free_hours": 12, "late_cancel_fee": 35, "no_show_fee": 60, "trial_price": 49}, ensure_ascii=False, indent=2) + "\n",
          "studio/prices.md": "# 价目\n\n体验课 49 元，月卡 580 元，次卡 10 次 420 元。\n"},
   prompt="舞蹈教室里，晚于规定时间取消预约要扣多少钱？",
   ref="晚取消要扣 35 元（studio/policy.json 的 late_cancel_fee）；爽约不到场是 60 元。",
   any_=z(35, "元", "块"), maxc=300,
   ans_expr='json.loads(files["studio/policy.json"])["late_cancel_fee"]', ans=35,
   traps="- no_show_fee 是爽约费，不是晚取消费。",
   unique="晚取消对应 late_cancel_fee = 35。")

ws("cfg-8206", fam="solarinv-01", zh=True, ttype="read_effective",
   desc="Read a solar plant ini file for the inverter alarm temperature, with a per-site override",
   files={"电站/全局.ini": "[inverter]\n报警温度 = 75\n采样秒 = 30\n",
          "电站/西坡站.ini": "[inverter]\n报警温度 = 68\n",
          "电站/东滩站.ini": "[inverter]\n采样秒 = 10\n",
          "README.md": "站点 ini 只写覆盖项，缺的项沿用 全局.ini。\n"},
   prompt="东滩站逆变器的报警温度是多少度？",
   ref="东滩站没有单独设置，沿用全局的 75 度（电站/全局.ini）；西坡站才是 68 度。",
   any_=["75 度", "75度", "75 ℃", "75℃", "75°C", "75 °C"], maxc=300,
   ans_expr='int(re.search(r"报警温度 = (\\d+)", files["电站/全局.ini"]).group(1))', ans=75,
   traps="- 东滩站文件只覆盖采样秒，报警温度要回退到全局。",
   unique="东滩站无报警温度项，取全局 75；西坡站的 68 属于另一站点。")

ws("cfg-8207", fam="devpool-01", zh=False, ttype="read_effective",
   desc="Read a service config where the production file overrides the default connection pool size",
   files={"config/default.yaml": "pool:\n  size: 10\n  timeout_s: 30\nretries: 3\n",
          "config/production.yaml": "pool:\n  size: 40\n",
          "config/development.yaml": "pool:\n  size: 4\n",
          "README.md": "Environment files override only the keys they set.\n"},
   prompt="What connection pool size does production use?",
   ref="Production uses a pool size of 40: config/production.yaml overrides the default of 10.",
   contains=["40"], token=True, excl=["size of 10", "size is 10"], maxc=300,
   ans_expr='int(re.search(r"size: (\\d+)", files["config/production.yaml"]).group(1))', ans=40,
   traps="- default.yaml says 10; production overrides it.",
   unique="Only production.yaml sets the production pool size.")

ws("cfg-8208", fam="brewtemp-01", zh=False, ttype="read_effective",
   desc="Read a brewery recipe config for the mash temperature of the stout",
   files={"recipes/stout.cfg": "name=Harbour Stout\nmash_temp_c=67\nboil_minutes=75\nferment_days=14\n",
          "recipes/pale.cfg": "name=Pale Ale\nmash_temp_c=65\nboil_minutes=60\nferment_days=10\n",
          "README.md": "Recipe parameters, one file per beer.\n"},
   prompt="At what temperature do we mash the Harbour Stout?",
   ref="The Harbour Stout is mashed at 67 degrees C (recipes/stout.cfg); the pale ale uses 65.",
   contains=["67"], token=True, maxc=300,
   ans_expr='int(re.search(r"mash_temp_c=(\\d+)", files["recipes/stout.cfg"]).group(1))', ans=67,
   traps="- The pale ale recipe has a similar mash temperature.",
   unique="Only stout.cfg belongs to Harbour Stout.")

ws("cfg-8209", fam="ciretry-01", zh=False, ttype="read_effective",
   desc="Read a CI config for the number of retries on flaky integration tests",
   files={".ci/pipeline.yml": "stages:\n  - build\n  - test\ntest:\n  timeout_minutes: 25\n  integration_retries: 2\n  unit_retries: 0\n",
          ".ci/nightly.yml": "test:\n  timeout_minutes: 90\n  integration_retries: 5\n",
          "README.md": "pipeline.yml runs on every push; nightly.yml only at night.\n"},
   prompt="How many times is a failing integration test retried on a normal push?",
   ref="On a normal push a failing integration test is retried 2 times (.ci/pipeline.yml); the nightly run allows 5.",
   contains=["2"], token=True, excl=["retried 5", "5 times on a normal"], maxc=300,
   ans_expr='int(re.search(r"integration_retries: (\\d+)", files[".ci/pipeline.yml"]).group(1))', ans=2,
   traps="- nightly.yml has a different retry count.",
   unique="Normal pushes use pipeline.yml, which sets 2.")

ws("cfg-8210", fam="campsite-01", zh=False, ttype="read_effective",
   desc="Read a campground settings file with a seasonal override of the quiet hours start",
   files={"site/base.toml": "quiet_start = \"22:00\"\nquiet_end = \"07:00\"\nfire_ban = false\n",
          "site/summer.toml": "quiet_start = \"23:00\"\n",
          "site/winter.toml": "quiet_start = \"21:00\"\n",
          "README.md": "Season files override base.toml. We are in the summer season.\n"},
   prompt="When do quiet hours start at the campground at the moment?",
   ref="Quiet hours start at 23:00 now: site/summer.toml overrides the base 22:00.",
   any_=["23:00", "11 pm", "11 PM", "11pm", "11:00 pm", "11:00 PM"], maxc=300,
   ans_expr='re.search(r"quiet_start = \\"(\\S+)\\"", files["site/summer.toml"]).group(1)', ans="23:00",
   traps="- README says summer season, so summer.toml applies, not winter.toml.",
   unique="Current season is summer; its override gives 23:00.")

ws("cfg-8211", fam="labfreezer-01", zh=False, ttype="read_effective",
   desc="Read a lab equipment json for the alarm threshold of the minus-80 freezer",
   files={"equipment/freezers.json": json.dumps({"F-01": {"set_c": -20, "alarm_c": -15}, "F-80A": {"set_c": -80, "alarm_c": -70}, "F-80B": {"set_c": -80, "alarm_c": -65}}, indent=2) + "\n",
          "README.md": "Freezer F-80A is the one in room 204.\n"},
   prompt="What is the alarm threshold of the freezer in room 204?",
   ref="The freezer in room 204 is F-80A, and its alarm threshold is -70 C (equipment/freezers.json).",
   contains=["-70"], maxc=300,
   ans_expr='json.loads(files["equipment/freezers.json"])["F-80A"]["alarm_c"]', ans=-70,
   traps="- Two -80 freezers with different thresholds; the README maps room 204 to F-80A.",
   unique="Room 204 is F-80A, whose alarm_c is -70; F-80B is -65.")


# ================================================================ doc
ws("doc-8200", fam="movingclaim-01", zh=True, ttype="policy_lookup",
   desc="Look up in a moving company terms document the deadline for damage claims",
   files={"条款/服务条款.md": "# 搬家服务条款\n\n## 一、预约\n提前 2 天预约，临时加单收加急费。\n\n## 二、理赔\n物品损坏须在签收后 48 小时内提出理赔，逾期不再受理。贵重物品需事先申报。\n\n## 三、取消\n搬家前 1 天取消免费。\n",
          "条款/价目.md": "# 价目\n\n小型车 280 元起，中型车 420 元起。\n",
          "README.md": "# 顺心搬家 客服资料\n"},
   prompt="顺心搬家的东西搬坏了，签收后多久之内还能申请理赔？",
   ref="签收后 48 小时内要提出理赔，超过就不再受理（条款/服务条款.md 第二章）；贵重物品需事先申报。",
   any_=z(48, "小时", "个小时", "h"), maxc=300,
   ans_expr='re.search(r"签收后 (\\d+) 小时", files["条款/服务条款.md"]).group(1)', ans="48",
   traps="- 预约和取消条款里也有天数，不是理赔时限。",
   unique="理赔时限只在第二章写了一次：48 小时。")

ws("doc-8201", fam="campfee-01", zh=True, ttype="policy_lookup",
   desc="Look up the refund rule in a camping reservation document",
   files={"营地/预订须知.md": "# 云岭营地预订须知\n\n## 退订\n入住前 7 天以上退订，全额退款；入住前 3 到 7 天，退 50%；入住前 3 天内不退。\n\n## 入营\n下午 2 点后入营，次日中午 12 点前离营。\n",
          "营地/装备租赁.md": "帐篷每晚 60 元，睡袋每晚 15 元。\n",
          "README.md": "云岭营地资料。\n"},
   prompt="云岭营地如果我入住前 5 天退订，能退多少？",
   ref="入住前 5 天退订属于「3 到 7 天」档，退 50%（营地/预订须知.md）。",
   any_=["50%", "50 %", "五成", "一半", "50％", "百分之五十"], maxc=300,
   ans_expr='re.search(r"3 到 7 天，退 (\\d+)%", files["营地/预订须知.md"]).group(1)', ans="50",
   traps="- 三档退款比例，5 天落在中间档。",
   unique="5 天介于 3 到 7 天之间，只对应 50%。")

ws("doc-8202", fam="clinicwait-01", zh=True, ttype="policy_lookup",
   desc="Look up a dental clinic FAQ for how long to avoid eating after a filling",
   files={"常见问题/补牙后.md": "# 补牙后的注意事项\n\n- 局麻消退前（约 2 小时）不要进食，以免咬伤脸颊。\n- 24 小时内避免过硬、过黏的食物。\n- 如出现持续疼痛，请回诊。\n",
          "常见问题/洁牙后.md": "# 洁牙后\n\n当天不要吃深色饮食；牙龈出血 1 到 2 天内属正常。\n",
          "README.md": "# 康乐口腔 患者须知\n"},
   prompt="诊所须知里说补完牙以后多久之内最好别吃东西？",
   ref="补牙后局麻没退之前别吃东西，大约要等 2 小时（常见问题/补牙后.md）；24 小时内还要避开过硬过黏的食物。",
   any_=z(2, "小时", "个小时"), maxc=300,
   ans_expr='re.search(r"约 (\\d+) 小时", files["常见问题/补牙后.md"]).group(1)', ans="2",
   traps="- 24 小时是避免硬食物的时间，不是禁食时间。",
   unique="禁食只到局麻消退，约 2 小时。")

ws("doc-8203", fam="schoolbus-01", zh=True, ttype="policy_lookup",
   desc="Look up in a school bus handbook the maximum number of seated students for the small bus",
   files={"校车/运行手册.md": "# 校车运行手册\n\n## 车型与载客\n- 大巴：核载 45 人。\n- 小巴：核载 19 人，其中学生座位 16 个，其余为随车教师和司机。\n\n## 发车\n早班 6:50 发车。\n",
          "校车/路线.md": "一号线经过 12 站，二号线经过 9 站。\n",
          "README.md": "# 校车资料\n"},
   prompt="小巴最多能坐几个学生？",
   ref="小巴学生座位是 16 个（校车/运行手册.md）；核载 19 人里还包含随车教师和司机。",
   any_=z(16, "个", "名", "位"), excl=["最多 19", "最多能坐 19", "19 个学生"], maxc=300,
   ans_expr='re.search(r"学生座位 (\\d+) 个", files["校车/运行手册.md"]).group(1)', ans="16",
   traps="- 核载 19 人包括教师和司机，学生只有 16 个座位。",
   unique="题问学生，手册明确学生座位 16。")

ws("doc-8204", fam="florist-01", zh=True, ttype="policy_lookup",
   desc="Look up in a flower shop care guide how often to change the water for roses",
   files={"养护/鲜切花.md": "# 鲜切花养护\n\n- 玫瑰：每 2 天换一次水，斜剪 1 厘米茎底。\n- 百合：每 3 天换水，及时摘除花粉。\n- 满天星：每 4 天换水。\n",
          "养护/盆栽.md": "盆栽绿萝每周浇水 1 次。\n",
          "README.md": "# 花间小铺 养护卡片\n"},
   prompt="买回去的玫瑰要隔几天换一次水？",
   ref="玫瑰每 2 天换一次水，换水时斜剪 1 厘米茎底（养护/鲜切花.md）。",
   any_=["每 2 天", "每2天", "2 天换", "2天换", "隔 2 天", "两天"], maxc=300,
   ans_expr='re.search(r"玫瑰：每 (\\d+) 天", files["养护/鲜切花.md"]).group(1)', ans="2",
   traps="- 百合 3 天、满天星 4 天，别串花种。",
   unique="玫瑰一行写明 2 天。")

ws("doc-8205", fam="repairphone-01", zh=True, ttype="policy_lookup",
   desc="Look up in a phone repair shop notice the warranty length for screen replacement",
   files={"店规/保修.md": "# 保修说明\n\n- 换屏：保修 90 天，人为摔坏、进水不在保修内。\n- 换电池：保修 180 天。\n- 主板维修：保修 30 天。\n",
          "店规/价格.md": "换屏 280 元起。\n",
          "README.md": "# 小马手机维修\n"},
   prompt="在小马手机维修换了屏，保修多少天？",
   ref="换屏保修 90 天，但人为摔坏和进水不在保修范围（店规/保修.md）。",
   any_=z(90, "天", "日"), maxc=300,
   ans_expr='re.search(r"换屏：保修 (\\d+) 天", files["店规/保修.md"]).group(1)', ans="90",
   traps="- 电池和主板的保修期不同。",
   unique="换屏一行写明 90 天。")

ws("doc-8206", fam="bandroom-01", zh=True, ttype="policy_lookup",
   desc="Look up in a rehearsal room guide the cancellation notice period for bookings",
   files={"排练室/使用说明.md": "# 排练室使用说明\n\n## 预约\n每次最少订 2 小时，最长 4 小时。\n\n## 取消\n开始前 24 小时以上取消，不收费；不足 24 小时，收取 50% 场地费。\n\n## 设备\n鼓组、两台音箱免费使用。\n",
          "排练室/价格.md": "工作日 80 元/小时，周末 120 元/小时。\n",
          "README.md": "# 回声排练室\n"},
   prompt="回声排练室要提前多久取消预约才不收费？",
   ref="开始前 24 小时以上取消不收费；不足 24 小时要收 50% 场地费（排练室/使用说明.md）。",
   any_=z(24, "小时", "个小时"), maxc=300,
   ans_expr='re.search(r"开始前 (\\d+) 小时以上", files["排练室/使用说明.md"]).group(1)', ans="24",
   traps="- 2 小时、4 小时是预约时长，不是取消期限。",
   unique="取消条款只写了 24 小时。")

ws("doc-8207", fam="releasepolicy-01", zh=False, ttype="policy_lookup",
   desc="Look up in a contributing guide how many approvals a pull request needs",
   files={"guides/review-rules.md": "# Contributing\n\n## Reviews\nEvery pull request needs 2 approvals. Changes under `security/` need 3 approvals, one of them from the security team.\n\n## Merging\nSquash merge only.\n",
          "guides/release-calendar.md": "Releases are cut on the first Monday of each month.\n",
          "OVERVIEW.txt": "Tidewater, a small parsing library.\n"},
   prompt="How many approvals does an ordinary pull request need before merging?",
   ref="An ordinary pull request needs 2 approvals (guides/review-rules.md); only changes under security/ need 3.",
   any_=["2 approvals", "two approvals", "Two approvals"], maxc=300,
   ans_expr='re.search(r"Every pull request needs (\\d+) approvals", files["guides/review-rules.md"]).group(1)', ans="2",
   traps="- The security/ exception needs 3.",
   unique="The word ordinary points at the general rule: 2.")

ws("doc-8208", fam="trainingrefund-01", zh=False, ttype="policy_lookup",
   desc="Look up in a training academy handbook the minimum attendance for a certificate",
   files={"handbook/certificates.md": "# Certificates\n\nA certificate is issued to learners who attend at least 80% of sessions and pass the final assessment. Learners below 60% attendance are withdrawn from the cohort.\n",
          "handbook/fees.md": "Fees are due 14 days before the cohort starts.\n",
          "README.md": "Academy handbook.\n"},
   prompt="What attendance do I need to get the course certificate?",
   ref="You need at least 80% attendance and a pass in the final assessment (handbook/certificates.md).",
   any_=["80%", "80 %", "80 percent", "eighty percent"], excl=["at least 60%", "need 60%"], maxc=300,
   ans_expr='re.search(r"attend at least (\\d+)%", files["handbook/certificates.md"]).group(1)', ans="80",
   traps="- 60% is the withdrawal threshold, not the certificate threshold.",
   unique="The certificate line says 80%.")

ws("doc-8209", fam="vetfast-01", zh=False, ttype="policy_lookup",
   desc="Look up in a shipping guide the maximum parcel weight for the economy service",
   files={"guide/services.md": "# Services\n\n| Service | Max weight | Delivery |\n|---|---|---|\n| Economy | 20 kg | 5-7 days |\n| Standard | 30 kg | 3-4 days |\n| Express | 30 kg | next day |\n",
          "guide/packing.md": "Use boxes rated for at least twice the parcel weight.\n",
          "README.md": "Parcel shipping help.\n"},
   prompt="What is the heaviest parcel I can send with the economy service?",
   ref="The economy service takes parcels up to 20 kg (guide/services.md).",
   contains=["20"], token=True, maxc=300,
   ans_expr='re.search(r"\\| Economy \\| (\\d+) kg", files["guide/services.md"]).group(1)', ans="20",
   traps="- Standard and Express allow 30 kg.",
   unique="The Economy row says 20 kg.")

ws("doc-8210", fam="coworkdesk-01", zh=False, ttype="policy_lookup",
   desc="Look up in a coworking space handbook the guest pass limit per month",
   files={"handbook/guests.md": "# Guests\n\nMembers may bring up to 3 guests per month on a free guest pass. Extra guests cost $12 per day. Guests must be signed in at the front desk.\n",
          "handbook/hours.md": "The space is open 7:00 to 22:00 on weekdays.\n",
          "README.md": "Member handbook.\n"},
   prompt="How many guests can I bring to the coworking space each month for free?",
   ref="You can bring up to 3 guests a month for free (handbook/guests.md); extra guests cost $12 a day.",
   contains=["3"], token=True, maxc=300,
   ans_expr='re.search(r"up to (\\d+) guests per month", files["handbook/guests.md"]).group(1)', ans="3",
   traps="- The $12 fee is for extra guests beyond the free ones.",
   unique="Free guests are capped at 3 per month.")

ws("doc-8211", fam="ferrylug-01", zh=False, ttype="policy_lookup",
   desc="Look up in a ferry FAQ the check-in closing time before departure",
   files={"faq/boarding.md": "# Boarding\n\nCheck-in closes 45 minutes before departure for vehicles and 30 minutes before departure for foot passengers.\n",
          "faq/pets.md": "Pets must stay in the vehicle deck kennel area.\n",
          "README.md": "Ferry FAQ.\n"},
   prompt="How long before departure does check-in close for foot passengers?",
   ref="Check-in closes 30 minutes before departure for foot passengers (faq/boarding.md); for vehicles it is 45 minutes.",
   any_=["30 minutes", "30 min", "half an hour", "half hour", "30-minute"], maxc=300,
   ans_expr='re.search(r"(\\d+) minutes before departure for foot", files["faq/boarding.md"]).group(1)', ans="30",
   traps="- Vehicles have a different cutoff (45).",
   unique="The question names foot passengers: 30.")


# ================================================================ fs
ws("fs-8200", fam="warehouseinv-01", zh=True, ttype="count_by_type", req=("list_files",),
   desc="Count the pallet inventory csv files in a warehouse folder, excluding archived and readme files",
   files={"盘点/2026-07.csv": "sku,qty\n", "盘点/2026-08.csv": "sku,qty\n", "盘点/2026-09.csv": "sku,qty\n",
          "盘点/归档/2025-12.csv": "sku,qty\n", "盘点/说明.md": "每月月底盘点一次。\n", "README.md": "# 北仓库\n"},
   prompt="北仓库的 盘点 目录下现在有几个月度盘点的 csv 文件？不算归档里的。",
   ref="盘点目录下有 3 个月度盘点 csv：2026-07、2026-08 和 2026-09；归档里的 2025-12 不算。",
   any_=z(3, "个", "份", "张") + ["三个", "三份"], maxc=300,
   ans_expr='len([p for p in files if p.startswith("盘点/") and p.count("/") == 1 and p.endswith(".csv")])', ans=3,
   traps="- 归档子目录里还有一个 csv，不应计入。",
   unique="盘点/ 一级目录下 csv 共 3 个，归档里的 1 个排除。")

ws("fs-8201", fam="photoshoot-01", zh=True, ttype="find_file", req=("search_text",),
   desc="Find which meeting note mentions the lighthouse booking among several notes",
   files={"纪要/0902-选址.md": "讨论了三处备选：老码头、旧船厂、红砖仓库。\n",
          "纪要/0909-预算.md": "预算上限 1.8 万元，摄影师费用单列。\n",
          "纪要/0916-订场.md": "确认订下灯塔公园的场地，周六上午 9 点进场。\n",
          "纪要/0923-收尾.md": "回收道具，结算尾款。\n",
          "README.md": "# 海岸系列拍摄 纪要\n"},
   prompt="哪一份纪要里确定订了灯塔公园的场地？",
   ref="是 纪要/0916-订场.md：里面写明确认订下灯塔公园的场地，周六上午 9 点进场。",
   contains=["0916-订场"], maxc=300, calls=1,
   ans_expr='[p for p, t in sorted(files.items()) if "灯塔公园" in t][0]', ans="纪要/0916-订场.md",
   traps="- 其他纪要只讨论选址、预算、收尾，没有提灯塔公园。",
   unique="只有 0916-订场.md 含「灯塔公园」。")

ws("fs-8202", fam="routefile-01", zh=True, ttype="count_by_type", req=("list_files",),
   desc="Count the gpx route files in a hiking club folder while ignoring photos",
   files={"线路/九溪.gpx": "<gpx/>\n", "线路/龙井.gpx": "<gpx/>\n", "线路/天目山.gpx": "<gpx/>\n", "线路/清凉峰.gpx": "<gpx/>\n",
          "线路/九溪.jpg": "x\n", "线路/龙井.jpg": "x\n", "线路/备注.txt": "轨迹均为 2026 年实测。\n", "README.md": "# 山友会线路库\n"},
   prompt="山友会线路库里一共有多少条 gpx 轨迹文件？",
   ref="线路目录里一共有 4 条 gpx 轨迹：九溪、龙井、天目山和清凉峰；照片和备注不算。",
   any_=z(4, "条", "个", "份") + ["四条", "四个"], maxc=300,
   ans_expr='len([p for p in files if p.endswith(".gpx")])', ans=4,
   traps="- 同名的 jpg 照片不是轨迹文件。",
   unique="gpx 文件共 4 个。")

ws("fs-8203", fam="fishfarm-01", zh=True, ttype="find_file", req=("search_text",),
   desc="Find which log file reports the aerator failure in a fish farm logs folder",
   files={"日志/塘A.log": "08:10 溶氧 5.2 正常\n18:30 溶氧 4.9 正常\n",
          "日志/塘B.log": "07:50 溶氧 5.0 正常\n13:20 增氧机停转，已报修\n",
          "日志/塘C.log": "09:00 溶氧 5.5 正常\n",
          "README.md": "# 渔场日志，每塘一份\n"},
   prompt="哪个塘的日志里记了增氧机停转？",
   ref="是塘 B：日志/塘B.log 里 13:20 记了增氧机停转并已报修。",
   any_=["塘B", "塘 B", "B 塘", "B塘"], maxc=300,
   ans_expr='[p for p, t in sorted(files.items()) if "增氧机停转" in t][0]', ans="日志/塘B.log",
   traps="- 三个日志格式相同，只有一个含停转记录。",
   unique="只有 塘B.log 含「增氧机停转」。")

ws("fs-8204", fam="bikeshare-01", zh=True, ttype="find_file", req=("list_files",),
   desc="Find the latest dated station report in a bike share reports folder",
   files={"报表/站点-20260830.csv": "id\n", "报表/站点-20260906.csv": "id\n", "报表/站点-20260913.csv": "id\n",
          "报表/站点-20260920.csv": "id\n", "报表/站点-汇总.md": "周报按日期命名。\n", "README.md": "# 单车站点周报\n"},
   prompt="站点周报里日期最新的是哪一天的？",
   ref="最新的是 2026-09-20 那份（报表/站点-20260920.csv）。",
   any_=["20260920", "2026-09-20", "9 月 20 日", "9月20日", "9 月 20 号", "9月20号"], maxc=300,
   ans_expr='max(re.findall(r"站点-(\\d{8})\\.csv", " ".join(files)))', ans="20260920",
   traps="- 汇总.md 不带日期，不参与比较。",
   unique="四份周报里最大的日期是 20260920。")

ws("fs-8205", fam="repoapi-01", zh=False, ttype="find_file", req=("search_text",),
   desc="Find which file defines the rate limit constant in a small service repo",
   files={"src/limits.py": "RATE_LIMIT_PER_MIN = 120\nBURST = 20\n",
          "src/server.py": "from limits import RATE_LIMIT_PER_MIN\n\ndef check(n):\n    return n <= RATE_LIMIT_PER_MIN\n",
          "tests/test_server.py": "from server import check\n\ndef test_check():\n    assert check(5)\n",
          "README.md": "A tiny API server.\n"},
   prompt="Which file defines RATE_LIMIT_PER_MIN?",
   ref="RATE_LIMIT_PER_MIN is defined in src/limits.py (set to 120); src/server.py only imports it.",
   contains=["src/limits.py"], maxc=300,
   ans_expr='[p for p, t in sorted(files.items()) if re.search(r"^RATE_LIMIT_PER_MIN =", t, re.M)][0]', ans="src/limits.py",
   traps="- server.py mentions the name but only imports it.",
   unique="Only limits.py has an assignment line.")

ws("fs-8206", fam="photoarchive-01", zh=False, ttype="count_by_type", req=("list_files",),
   desc="Count the raw photo files of one shoot in an archive folder with other formats mixed in",
   files={"shoot-0412/IMG_001.cr2": "x", "shoot-0412/IMG_002.cr2": "x", "shoot-0412/IMG_003.cr2": "x",
          "shoot-0412/IMG_004.cr2": "x", "shoot-0412/IMG_005.cr2": "x", "shoot-0412/IMG_001.jpg": "x",
          "shoot-0412/IMG_002.jpg": "x", "shoot-0412/notes.txt": "Overcast, ISO 400.\n",
          "shoot-0503/IMG_101.cr2": "x", "shoot-0503/IMG_102.cr2": "x", "README.md": "Photo archive.\n"},
   prompt="How many RAW (.cr2) files are in the shoot-0412 folder?",
   ref="There are 5 .cr2 files in shoot-0412 (IMG_001 to IMG_005); the jpg copies and notes.txt are not RAW.",
   contains=["5"], token=True, maxc=300,
   ans_expr='len([p for p in files if p.startswith("shoot-0412/") and p.endswith(".cr2")])', ans=5,
   traps="- shoot-0503 has two more cr2 files; jpg copies share names.",
   unique="Five .cr2 files live under shoot-0412.")

ws("fs-8207", fam="plantcal-01", zh=False, ttype="find_file", req=("search_text",),
   desc="Find the calibration record that mentions a failed pressure gauge",
   files={"calibration/2026-03.txt": "Gauge G-11: pass\nGauge G-12: pass\n",
          "calibration/2026-06.txt": "Gauge G-11: pass\nGauge G-12: FAILED, replaced\n",
          "calibration/2026-09.txt": "Gauge G-11: pass\nGauge G-12: pass\n",
          "README.md": "Quarterly calibration records.\n"},
   prompt="In which quarterly calibration record did a gauge fail?",
   ref="The failure is in calibration/2026-06.txt: gauge G-12 failed and was replaced.",
   contains=["2026-06"], maxc=300,
   ans_expr='[p for p, t in sorted(files.items()) if "FAILED" in t][0]', ans="calibration/2026-06.txt",
   traps="- Other records only list passes.",
   unique="Only 2026-06.txt contains FAILED.")

ws("fs-8208", fam="podcastep-01", zh=False, ttype="count_by_type", req=("list_files",),
   desc="Count the published episode scripts in a podcast folder, skipping drafts",
   files={"scripts/ep01.md": "x", "scripts/ep02.md": "x", "scripts/ep03.md": "x", "scripts/ep04.md": "x",
          "scripts/drafts/ep05.md": "x", "scripts/drafts/ep06.md": "x", "README.md": "Episode scripts. Drafts are unpublished.\n"},
   prompt="How many episode scripts have been published so far?",
   ref="Four scripts are published (ep01 to ep04); ep05 and ep06 are still drafts.",
   any_=["4 ", "four", "Four", "4.", "4 episode", "4 script"], excl=["6 episode", "six"], maxc=300,
   ans_expr='len([p for p in files if re.fullmatch(r"scripts/ep\\d+\\.md", p)])', ans=4,
   traps="- The drafts subfolder holds two unpublished scripts.",
   unique="README says drafts are unpublished; four scripts sit outside drafts/.")

ws("fs-8209", fam="vineyardtask-01", zh=False, ttype="find_file", req=("search_text",),
   desc="Find which task file is assigned to Priya in a vineyard task folder",
   files={"tasks/pruning.md": "Owner: Tomas\nDue: 2026-02-14\n", "tasks/irrigation.md": "Owner: Priya\nDue: 2026-03-01\n",
          "tasks/bottling.md": "Owner: Lena\nDue: 2026-05-20\n", "README.md": "One file per task.\n"},
   prompt="Which task is Priya the owner of?",
   ref="Priya owns the irrigation task (tasks/irrigation.md), due 2026-03-01.",
   contains=["irrigation"], maxc=300,
   ans_expr='[p for p, t in sorted(files.items()) if "Owner: Priya" in t][0]', ans="tasks/irrigation.md",
   traps="- None beyond picking the right owner line.",
   unique="Only irrigation.md has Owner: Priya.")

ws("fs-8210", fam="stagelist-01", zh=False, ttype="count_by_type", req=("list_files",),
   desc="Count the top-level folders in a theatre production directory",
   files={"lighting/cues.txt": "x", "sound/cues.txt": "x", "costumes/list.md": "x", "props/list.md": "x",
          "props/photos/a.jpg": "x", "scripts/final.md": "x", "README.md": "Production files.\n"},
   prompt="How many top-level folders does the production directory have?",
   ref="There are 5 top-level folders: lighting, sound, costumes, props and scripts (README.md is a file).",
   contains=["5"], token=True, maxc=300,
   ans_expr='len({p.split("/")[0] for p in files if "/" in p})', ans=5,
   traps="- props/photos is nested, not top-level.",
   unique="Five distinct first path segments among files inside folders.")


# ================================================================ nt (no tool needed)
nt("nt-8200", fam="orchardbox-01", ttype="unit_convert", zh=True,
   desc="Multiply boxes by jin per box in an orchard harvest, mental arithmetic",
   prompt="果园今年摘了 38 箱苹果，每箱 24 斤，一共多少斤？",
   ref="38 × 24 = 912，一共 912 斤。", any_=z(912, "斤"), maxc=300,
   check='assert "38 箱" in prompt and "24 斤" in prompt\nassert 38 * 24 == 912')

nt("nt-8201", fam="lunchbox-01", ttype="unit_convert", zh=True,
   desc="Change from a 200 yuan note after buying 16 boxed lunches at 7.5 each",
   prompt="一份盒饭 7.5 元，订了 16 份，我给了 200 元，应该找回多少？",
   ref="7.5 × 16 = 120 元，200 − 120 = 80，应该找回 80 元。", any_=["找回 80 元", "找回80元", "找 80 元", "找80元", "80 元", "80元", "80 块", "80块"], maxc=300,
   check='assert "7.5 元" in prompt and "16 份" in prompt\nassert 200 - 7.5 * 16 == 80')

nt("nt-8202", fam="roadtrip-01", ttype="unit_convert", zh=True,
   desc="Distance from speed and time with a decimal number of hours",
   prompt="高速上匀速 90 公里每小时，开了 2.5 小时，大概跑了多远？",
   ref="90 × 2.5 = 225，大约跑了 225 公里。", any_=["225 公里", "225公里", "225 km", "225km", "225 千米", "225千米"], maxc=300,
   check='assert "90 公里" in prompt and "2.5 小时" in prompt\nassert 90 * 2.5 == 225')

nt("nt-8203", fam="expensetrans-01", ttype="concept", zh=True,
   desc="Translate a short Chinese office notice into English",
   prompt="帮我把这句话翻成英文：请在周三之前提交报销单据。",
   ref="Please submit your expense receipts by Wednesday.", contains=["Wednesday"], any_=["expense", "reimbursement", "receipt"], maxc=300,
   check='assert "周三" in prompt')

nt("nt-8204", fam="formalrewrite-01", ttype="concept", zh=True,
   desc="Rewrite a casual sentence into formal written Chinese keeping the key facts",
   prompt="把这句话改成正式一点的书面语：那个，我们这周五之前大概能把报告弄完吧。",
   ref="我们预计本周五前完成报告。", contains=["周五", "报告"], maxc=300,
   check='assert "周五" in prompt and "报告" in prompt')

nt("nt-8205", fam="marathon-01", ttype="unit_convert", zh=True,
   desc="Convert marathon distance in kilometres to miles with a decimal result",
   prompt="马拉松全程 42.195 公里，折合多少英里？",
   ref="42.195 ÷ 1.609 ≈ 26.2，约 26.2 英里。", any_=["26.2"], maxc=300,
   check='assert "42.195" in prompt\nassert round(42.195 / 1.609344, 1) == 26.2')

nt("nt-8206", fam="boilingf-01", ttype="unit_convert", zh=True,
   desc="Convert the boiling point of water from Celsius to Fahrenheit",
   prompt="水在标准大气压下 100 摄氏度沸腾，换成华氏温度是多少？",
   ref="100 × 9/5 + 32 = 212，即 212 华氏度。", any_=["212 华氏", "212华氏", "212°F", "212 °F", "212℉", "212 度", "212度", "212 F", "212F"], maxc=300,
   check='assert "100 摄氏度" in prompt\nassert 100 * 9 / 5 + 32 == 212')

nt("nt-8207", fam="floorarea-01", ttype="unit_convert", zh=True,
   desc="Floor area of a rectangular living room with decimal sides",
   prompt="客厅长 5.4 米、宽 3.5 米，铺地板要按多少平方米买？",
   ref="5.4 × 3.5 = 18.9，要按 18.9 平方米算，实际买料可再留几个点损耗。", any_=["18.9"], maxc=300,
   check='assert "5.4 米" in prompt and "3.5 米" in prompt\nassert round(5.4 * 3.5, 1) == 18.9')

nt("nt-8208", fam="revgrowth-01", ttype="unit_convert", zh=True,
   desc="Percentage growth of monthly revenue from 48 to 54 wan yuan",
   prompt="我们店上个月营业额 48 万，这个月 54 万，增长了百分之几？",
   ref="(54 − 48) ÷ 48 = 0.125，增长了 12.5%。", any_=["12.5"], maxc=300,
   check='assert "48 万" in prompt and "54 万" in prompt\nassert (54 - 48) / 48 == 0.125')

nt("nt-8209", fam="photosyn-01", ttype="concept", zh=True,
   desc="General knowledge: which gas plants absorb in photosynthesis",
   prompt="植物光合作用主要从空气里吸收哪种气体？",
   ref="主要吸收二氧化碳，并释放氧气。", any_=["二氧化碳", "CO2", "CO₂"], maxc=300,
   check='assert "光合作用" in prompt')

nt("nt-8210", fam="nationalday-01", ttype="concept", zh=True,
   desc="General knowledge: date of China's National Day",
   prompt="我们国家的国庆节是哪一天？",
   ref="国庆节是每年的 10 月 1 日。", any_=["10 月 1 日", "10月1日", "十月一日", "10 月 1 号", "10月1号", "10 月 1 日"], maxc=300,
   check='assert "国庆节" in prompt')

nt("nt-8211", fam="pcpower-01", ttype="unit_convert", zh=True,
   desc="Electricity used by a 150 W device over 8 hours in kWh",
   prompt="一台电脑功率 150 瓦，连续开 8 小时，大概用掉多少度电？",
   ref="150 W × 8 h = 1200 Wh = 1.2 度，约用 1.2 度电。", any_=["1.2 度", "1.2度", "1.2 千瓦时", "1.2千瓦时", "1.2 kWh", "1.2kWh", "1.2 kwh"], maxc=300,
   check='assert "150 瓦" in prompt and "8 小时" in prompt\nassert 150 * 8 / 1000 == 1.2')

nt("nt-8212", fam="workhours-01", ttype="unit_convert", zh=True,
   desc="Elapsed time between 8:40 and 14:15 in hours and minutes",
   prompt="我早上 8:40 开始值班，下午 2:15 交班，一共值了多久？",
   ref="8:40 到 14:15，共 5 小时 35 分钟。", any_=["5 小时 35", "5小时35", "5 小时35", "5 个小时 35", "5个小时35", "335 分钟", "335分钟", "5 h 35"], maxc=300,
   check='assert "8:40" in prompt\nassert (14 * 60 + 15) - (8 * 60 + 40) == 335')

nt("nt-8213", fam="receipttrans-01", ttype="concept", zh=True,
   desc="Translate an English warranty sentence into Chinese",
   prompt="这句话用中文怎么说：Please keep the receipt until the warranty expires.",
   ref="请保留好收据，直到保修期结束。", any_=["收据", "小票", "发票", "凭证", "购物凭证"], maxc=300,
   check='assert "warranty" in prompt')

nt("nt-8214", fam="leapfeb-01", ttype="concept", zh=True,
   desc="General knowledge: days in February of a leap year",
   prompt="闰年的二月有多少天？",
   ref="闰年的二月有 29 天。", any_=["29 天", "29天", "29 日", "29日"], maxc=300,
   check='assert "闰年" in prompt')

nt("nt-8215", fam="splitbill-01", ttype="unit_convert", zh=True,
   desc="Split a dinner bill evenly among six people",
   prompt="六个人聚餐一共花了 468 元，AA 的话每人付多少？",
   ref="468 ÷ 6 = 78，每人付 78 元。", any_=["78 元", "78元", "78 块", "78块"], maxc=300,
   check='assert "468 元" in prompt\nassert 468 / 6 == 78')

nt("nt-8216", fam="coatdiscount-01", ttype="unit_convert", zh=True,
   desc="Price after a 7.5-zhe discount on a 320 yuan coat",
   prompt="原价 320 元的外套打七五折，现价多少钱？",
   ref="七五折就是 75%，320 × 0.75 = 240，现价 240 元。", any_=["240 元", "240元", "240 块", "240块"], maxc=300,
   check='assert "320 元" in prompt and "七五折" in prompt\nassert 320 * 0.75 == 240')

nt("nt-8217", fam="kgtog-01", ttype="unit_convert", zh=True,
   desc="Convert 2.5 kilograms of flour into grams",
   prompt="2.5 公斤面粉等于多少克？",
   ref="1 公斤 = 1000 克，2.5 公斤 = 2500 克。", any_=["2500 克", "2500克", "2,500 克", "2,500克", "2500 g", "2500g"], maxc=300,
   check='assert "2.5 公斤" in prompt\nassert 2.5 * 1000 == 2500')

nt("nt-8218", fam="weekday100-01", ttype="concept", zh=True,
   desc="Day of the week 100 days after a Wednesday using modulo 7",
   prompt="今天是周三，100 天以后是周几？",
   ref="100 ÷ 7 余 2，周三往后数 2 天，是周五。", any_=["周五", "星期五"], maxc=300,
   check='assert "周三" in prompt and "100 天" in prompt\nassert 100 % 7 == 2')

nt("nt-8219", fam="recipescale-01", ttype="unit_convert", zh=True,
   desc="Scale a recipe from 4 servings to 10 servings",
   prompt="食谱写的是 4 人份用 300 克面粉，我要做 10 人份，面粉要多少克？",
   ref="300 ÷ 4 × 10 = 750，需要 750 克。", any_=["750 克", "750克", "750 g", "750g"], maxc=300,
   check='assert "4 人份" in prompt and "10 人份" in prompt\nassert 300 / 4 * 10 == 750')

nt("nt-8220", fam="solarterm-01", ttype="concept", zh=True,
   desc="General knowledge: the solar term right after the winter solstice",
   prompt="二十四节气里，冬至的下一个节气是什么？",
   ref="冬至之后是小寒。", any_=["小寒"], maxc=300,
   check='assert "冬至" in prompt')

nt("nt-8221", fam="canberra-01", ttype="concept", zh=True,
   desc="General knowledge: the capital of Australia",
   prompt="澳大利亚的首都是哪座城市？",
   ref="澳大利亚的首都是堪培拉，不是悉尼。", any_=["堪培拉", "Canberra"], excl=["首都是悉尼", "首都是墨尔本"], maxc=300,
   check='assert "澳大利亚" in prompt')

nt("nt-8222", fam="fractions-01", ttype="unit_convert", zh=True,
   desc="Add two fractions 3/4 and 5/8",
   prompt="3/4 加 5/8 等于多少？",
   ref="3/4 = 6/8，6/8 + 5/8 = 11/8，也就是 1 又 3/8，约 1.375。", any_=["11/8", "1又3/8", "1 又 3/8", "1.375", "1 3/8", "八分之十一"], maxc=300,
   check='from fractions import Fraction\nassert Fraction(3, 4) + Fraction(5, 8) == Fraction(11, 8)')

nt("nt-8223", fam="brickstrips-01", ttype="unit_convert", zh=True,
   desc="Number of truck trips needed to carry 250 bricks at 48 per trip",
   prompt="工地要运 250 块砖，一辆车一趟最多拉 48 块，至少要跑几趟？",
   ref="250 ÷ 48 ≈ 5.2，不能跑半趟，向上取整，至少 6 趟。", any_=["6 趟", "6趟", "六趟", "6 次", "6次", "跑 6", "6 车", "6车"], maxc=300,
   check='import math\nassert "250 块" in prompt and "48 块" in prompt\nassert math.ceil(250 / 48) == 6')

nt("nt-8224", fam="avgscore-01", ttype="unit_convert", zh=True,
   desc="Mean of five test scores",
   prompt="小李五次测验分别考了 82、90、76、88、94 分，平均多少分？",
   ref="总分 82 + 90 + 76 + 88 + 94 = 430，430 ÷ 5 = 86，平均 86 分。", any_=["86 分", "86分", "平均 86", "是 86", "为 86", "= 86", "=86"], maxc=300,
   check='assert "82、90、76、88、94" in prompt\nassert sum([82, 90, 76, 88, 94]) / 5 == 86')

nt("nt-8225", fam="fixeddeposit-01", ttype="unit_convert", zh=True,
   desc="One-year simple interest on a fixed deposit",
   prompt="我存了 2 万元定期，年利率 2.5%，存满一年利息大概多少？",
   ref="20000 × 2.5% = 500，一年利息约 500 元。", any_=["500 元", "500元", "500 块", "500块"], maxc=300,
   check='assert "2 万元" in prompt\nassert 20000 * 0.025 == 500')

nt("nt-8226", fam="thankstrans-01", ttype="concept", zh=False,
   desc="Translate a short Chinese thank-you phrase into English",
   prompt="How do you say '谢谢你的耐心等待' in English?",
   ref="Thank you for your patience.", contains=["patience"], token=True, maxc=300,
   check='assert "耐心等待" in prompt')

nt("nt-8227", fam="trainarrive-01", ttype="unit_convert", zh=False,
   desc="Arrival time from departure time and a trip duration crossing the hour",
   prompt="A train leaves at 9:25 and the trip takes 3 hours 50 minutes. What time does it arrive?",
   ref="9:25 + 3:50 = 13:15, so it arrives at 1:15 pm.", any_=["13:15", "1:15 pm", "1:15 PM", "1:15pm", "1:15 p.m."], maxc=300,
   check='assert (9 * 60 + 25 + 3 * 60 + 50) == 13 * 60 + 15')

nt("nt-8228", fam="percentof-01", ttype="unit_convert", zh=False,
   desc="Compute a simple percentage of a number",
   prompt="What is 15% of 240?",
   ref="15% of 240 is 0.15 x 240 = 36.", contains=["36"], token=True, maxc=300,
   check='assert 0.15 * 240 == 36.0')

nt("nt-8229", fam="litresml-01", ttype="unit_convert", zh=False,
   desc="Convert 3.5 litres to millilitres",
   prompt="How many millilitres are in 3.5 litres?",
   ref="1 litre is 1000 ml, so 3.5 litres is 3,500 ml.", any_=["3500", "3,500"], maxc=300,
   check='assert 3.5 * 1000 == 3500')

nt("nt-8230", fam="nearestplanet-01", ttype="concept", zh=False,
   desc="General knowledge: the planet closest to the sun",
   prompt="Which planet is closest to the sun?",
   ref="Mercury is the closest planet to the sun.", contains=["Mercury"], token=True, maxc=300,
   check='assert "closest" in prompt')

nt("nt-8231", fam="passivevoice-01", ttype="concept", zh=False,
   desc="Rewrite an active sentence in the passive voice",
   prompt="Rewrite this sentence in the passive voice: The committee approved the budget.",
   ref="The budget was approved by the committee.", contains=["was approved"], maxc=300,
   check='assert "committee approved" in prompt')

nt("nt-8232", fam="fahrenheit72-01", ttype="unit_convert", zh=False,
   desc="Convert 72 Fahrenheit to Celsius roughly",
   prompt="Roughly what is 72 degrees Fahrenheit in Celsius?",
   ref="(72 - 32) x 5/9 is about 22.2, so roughly 22 degrees Celsius.", any_=["22.2", "22 °C", "22°C", "22 C", "22 degrees", "about 22", "approximately 22"], maxc=300,
   check='assert round((72 - 32) * 5 / 9, 1) == 22.2')

nt("nt-8233", fam="waterpack-01", ttype="unit_convert", zh=False,
   desc="Unit price of a 12-pack of water bottles at $9.60",
   prompt="A 12-pack of water costs $9.60. What is the price per bottle?",
   ref="$9.60 / 12 = $0.80 per bottle.", any_=["0.80", "80 cents", "$0.8"], maxc=300,
   check='assert round(9.60 / 12, 2) == 0.80')

nt("nt-8234", fam="canadacapital-01", ttype="concept", zh=False,
   desc="General knowledge: the capital of Canada",
   prompt="What is the capital of Canada?",
   ref="The capital of Canada is Ottawa.", contains=["Ottawa"], token=True, maxc=300,
   check='assert "Canada" in prompt')


if __name__ == "__main__":
    pass
zh = sum(1 for _, v in GEN if v)
print("generated %d cases, zh %d" % (len(GEN), zh))
