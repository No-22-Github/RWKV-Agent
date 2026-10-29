"""B1 singletons (35021-35040): entity name in the prompt, our own data in the workspace; no B0 sibling."""
from common import *

S = []


def s(**kw):
    S.append(kw)


# ---- English (11)
s(cid="cfg-35021", tt="lookup_value", p="Which region did we pick for the Eastvale Systems VPN gateway in the internal runbook?",
  files={"network/eastvale-vpn-runbook.md": "# Eastvale VPN gateway runbook\n\nGateway region: ap-southeast-2 (chosen for latency to the Sydney office).\nStandby region: eu-west-1.\nTunnel MTU: 1380.\n",
         "network/office-subnets.txt": "sydney 10.20.0.0/16\nberlin 10.30.0.0/16\n"},
  inc=["ap-southeast-2"], exc=["us-east-1"], t2=("L", "And what MTU did we set on those tunnels?", ["1380"]))
s(cid="doc-35022", tt="lookup_value", p="What notice period does our Meridian Analytics agreement require to cancel?",
  files={"legal/meridian-analytics-subscription-signed.md": "# Meridian Analytics subscription\n\nTerm: 12 months from 2026-01-15, auto-renews.\nCancellation: 90 days written notice before the renewal date.\nSeats: 25\n",
         "legal/signature-log.txt": "signed by CFO 2026-01-14\n"},
  inc=["90"], exc=["30 days", "30-day"], trap="TR-WEBSTALE",
  web=[fx("Meridian Analytics", "https://www.meridiananalytics.io/legal/subscription-terms", "Subscription terms - Meridian Analytics", "Standard subscription terms.",
          "# Subscription terms\n\nCustomers may cancel with 30 days written notice before renewal.\n", "2026-03-30")])
s(cid="hyb-35023", tt="lookup_value", p="How many Tessera Cloud instances does our capacity plan say we run in production?",
  files={"capacity/tessera-capacity-plan-q3.md": "# Capacity plan Q3\n\nTessera Cloud production: 18 instances (m-class), 6 of them autoscaled.\nTessera Cloud staging: 4 instances.\nPlanned for Q4: +5 production.\n",
         "capacity/cost-sheet.csv": "item,monthly\ntessera-prod,9120\n"},
  inc=["18"], exc=["22 instances"], trap="TR-DECOY", t2=("L", "And how many more are planned for Q4?", ["5"]))
s(cid="cfg-35024", tt="lookup_value", p="What log level is set for the Vantage agent in our staging config?",
  files={"staging/vantage-agent-staging.ini": "[agent]\nname = staging-collector\nlog_level = debug\nflush_seconds = 15\n\n[output]\nendpoint = https://ingest.internal.local/v2\n",
         "staging/vantage-agent-prod.ini": "[agent]\nname = prod-collector\nlog_level = warn\nflush_seconds = 30\n"},
  inc=["debug"], exc=[], trap="TR-DECOY")
s(cid="doc-35025", tt="lookup_value", p="Per our onboarding wiki export, how many days of PTO does a new hire at Loomwright get in the first year?",
  files={"hr/onboarding-wiki-export-2026.md": "# Onboarding (wiki export)\n\n## Time off\n- New hires accrue 18 days of PTO in the first year, pro-rated by start month.\n- Sick leave is separate: 8 days.\n- Public holidays follow the Ontario calendar.\n",
         "hr/benefits-faq-draft.md": "TODO: add dental details\n"},
  inc=["18"], exc=["15 days", "20 days"], trap="TR-WEBSTALE",
  web=[fx("Loomwright", "https://www.loomwright.com/careers/benefits", "Benefits - Loomwright Careers", "What we offer.",
          "# Benefits\n\nLoomwright offers 20 days of paid time off per year to all full-time employees.\n", "2026-02-12")], t2=("L", "What about sick leave?", ["8"]))
s(cid="hyb-35026", tt="lookup_value", p="What's the support phone line for the Halvorsen copiers listed in our office handbook?",
  files={"office/office-handbook-2026.md": "# Office handbook\n\n## Equipment support\n- Halvorsen copiers (2nd and 4th floor): support line 555-0147, weekdays 8-18.\n- Badge printer: ask reception.\n",
         "office/floor-plan.txt": "2F: copier room next to kitchen\n"},
  inc=["555-0147"], exc=["555-0100"], trap="TR-DECOY")
s(cid="cfg-35027", tt="lookup_value", p="Which Redwick cache TTL did we set for product pages in our config?",
  files={"web/redwick-cache-rules.toml": "[rules.product_pages]\npath = \"/p/*\"\nttl_seconds = 900\n\n[rules.static]\npath = \"/assets/*\"\nttl_seconds = 86400\n",
         "web/deploy-log.txt": "2026-09-01 rules reloaded\n"},
  inc=["900"], exc=["3600"], trap="TR-WEBSTALE",
  web=[fx("Redwick", "https://docs.redwickcdn.com/caching/defaults", "Caching defaults - Redwick Docs", "Default TTLs.",
          "# Caching defaults\n\nHTML responses are cached for 3600 seconds by default; static assets for 7 days.\n", "2026-07-30")], t2=("L", "And the static assets TTL?", ["86400"]))
s(cid="doc-35028", tt="lookup_value", p="In the Brackenridge lease we signed, what's the monthly rent?",
  files={"facilities/brackenridge-lease-signed-2025.md": "# Lease - Brackenridge Tower, floor 7\n\nTerm: 5 years from 2025-04-01.\nRent: 31,400 per month.\nRent review: 1 April 2028, capped at 4% increase.\nBreak option: none.\n",
         "facilities/parking-allocation.csv": "bay,holder\n12,CEO\n"},
  inc=["31,400"], exc=["28,000"], trap="TR-WEBSTALE",
  web=[fx("Brackenridge", "https://www.brackenridgetower.com/leasing", "Leasing - Brackenridge Tower", "Available space.",
          "# Leasing\n\nFloor 7 asking rent: 28,000 per month for suites of this size.\n", "2026-06-14")], t2=("L", "When is the first rent review?", ["2028"]))
s(cid="hyb-35029", tt="lookup_value", p="How many licences of Pixelforge Studio does our asset register show for the design team?",
  files={"it/software-asset-register.csv": "product,team,licences,renewal\nPixelforge Studio,design,12,2026-11-30\nPixelforge Studio,marketing,3,2026-11-30\nMailpath,all,140,2027-01-12\n",
         "it/renewal-reminders.txt": "send Pixelforge renewal quote request by Oct 15\n"},
  inc=["12"], exc=[], trap="TR-DECOY")
s(cid="cfg-35030", tt="lookup_value", p="What heap size do we give the Sablewood indexer in production?",
  files={"search/sablewood-indexer-prod.env": "SABLEWOOD_HEAP=6g\nSABLEWOOD_SHARDS=12\nSABLEWOOD_REFRESH=5s\n",
         "search/sablewood-indexer-dev.env": "SABLEWOOD_HEAP=1g\nSABLEWOOD_SHARDS=2\n"},
  inc=["6g"], exc=["2g", "4g"], trap="TR-WEBSTALE",
  web=[fx("Sablewood", "https://docs.sablewood.dev/indexer/memory", "Memory sizing - Sablewood Docs", "Heap recommendations.",
          "# Memory sizing\n\nThe default heap for the indexer is 2g. For production workloads, 4g is a common starting point.\n", "2026-08-08")],
  t2=("L", "How many shards is that set up with?", ["12"]))
s(cid="doc-35031", tt="lookup_value", p="By what date did we say we'd move everything off the Corvid v2 API, per our architecture decision record?",
  files={"adr/adr-0017-corvid-api-migration.md": "# ADR-0017: Corvid API migration\n\nStatus: accepted 2026-07-09\n\nDecision: migrate all callers to Corvid v3 by 2026-12-15, with the v2 fallback removed in January.\nOwner: payments team.\n",
         "adr/adr-0016-queue-choice.md": "Status: accepted\nUse the managed queue.\n"},
  inc=["2026-12-15"], exc=["2027-04-30"], trap="TR-WEBSTALE",
  web=[fx("Corvid", "https://developers.corvidapi.io/v2-sunset", "v2 sunset - Corvid API", "Retirement schedule.",
          "# v2 sunset\n\nCorvid v2 shuts down on 2027-04-30.\n", "2026-06-01")])

# ---- Chinese (9)
s(cid="doc-35032", tt="lookup_value", p="我们和曜石科技签的保密协议，保密期限是几年？",
  files={"法务/曜石科技-保密协议-已签.md": "# 保密协议\n\n双方：本公司、曜石科技\n签署日期：2026-03-03\n保密期限：自签署之日起 5 年，期满后商业秘密继续保密。\n违约金：50 万元。\n",
         "法务/协议台账.csv": "协议,状态\n曜石科技保密协议,生效\n"},
  inc=["5"], exc=["3 年", "3年"], trap="TR-WEBSTALE",
  web=[fx("曜石科技", "https://www.yaoshi-tech.cn/legal/nda-template", "保密协议范本 - 曜石科技", "合作伙伴保密协议范本。",
          "# 保密协议范本\n\n保密期限：自签署之日起 3 年。双方可协商延长。\n", "2026-04-22")], t2=("L", "违约金是多少？", ["50"]))
s(cid="cfg-35033", tt="lookup_value", p="咱们的飞渡网关限流现在配的是每秒多少个请求？",
  files={"网关/飞渡网关-限流配置.yaml": "gateway: feidu\nrate_limit:\n  per_second: 800\n  burst: 1200\nroutes:\n  /pay: 200\n  /search: 600\n",
         "网关/变更记录.txt": "2026-08-19 限流从 500 调到 800\n"},
  inc=["800"], exc=["100 个", "1000 个"], trap="TR-DECOY")
s(cid="hyb-35034", tt="lookup_value", p="我们团建预算表里，山岚度假村的人均标准是多少？",
  files={"行政/团建预算表-Q4.md": "# 团建预算 Q4\n\n- 山岚度假村两天一夜：人均 860 元（含住宿、两餐、门票），共 32 人。\n- 市内桌游：人均 120 元。\n",
         "行政/报名名单.csv": "姓名,部门\n陈晨,研发\n"},
  inc=["860"], exc=["980", "1080"], trap="TR-WEBSTALE",
  web=[fx("山岚度假村", "https://www.shanlan-resort.com/packages/team", "团队套餐 - 山岚度假村", "团建套餐价格。",
          "# 团队套餐\n\n两天一夜团建套餐：人均 980 元起，30 人以上可咨询优惠。\n", "2026-08-07")], t2=("L", "一共多少人参加？", ["32"]))
s(cid="doc-35035", tt="lookup_value", p="按我们的内部规定，使用朗致会议系统开周会，录制文件要保留多久？",
  files={"信息安全/会议录制管理规定.md": "# 会议录制管理规定\n\n- 朗致会议系统的录制文件保存 90 天后自动删除。\n- 涉及客户数据的会议不得录制。\n- 如需长期保存须经部门负责人批准。\n",
         "信息安全/会议室预约规则.txt": "提前一天预约\n"},
  inc=["90"], exc=["30 天", "30天"], trap="TR-WEBSTALE",
  web=[fx("朗致会议", "https://www.langzhi-meeting.com/help/recording", "云录制说明 - 朗致会议", "录制文件保存规则。",
          "# 云录制说明\n\n云录制文件默认保存 30 天，到期自动清理。\n", "2026-06-30")], t2=("L", "涉及客户数据的会议能录吗？", ["不得"]))
s(cid="cfg-35036", tt="lookup_value", p="我们的苍梧监控告警，CPU 超过多少百分比会发给值班？",
  files={"监控/苍梧告警规则.yaml": "rules:\n  - name: cpu_high\n    threshold_percent: 85\n    duration: 5m\n    notify: oncall\n  - name: disk_full\n    threshold_percent: 90\n    notify: oncall\n",
         "监控/值班轮换.csv": "周,人\n38,赵宇\n"},
  inc=["85"], exc=["80%", "80 %", "95%"], trap="TR-DECOY", t2=("L", "磁盘告警的阈值呢？", ["90"]))
s(cid="hyb-35037", tt="lookup_value", p="内部手册里写的暖阳打印机卡纸报修电话是多少？",
  files={"行政/设备报修手册.md": "# 设备报修\n\n- 暖阳打印机卡纸、缺粉：分机 8021\n- 网络故障：分机 8000\n- 空调：物业 400-820-3366\n",
         "行政/楼层分布.txt": "三楼打印间在东侧\n"},
  inc=["8021"], exc=["8000"], trap="TR-DECOY")
s(cid="doc-35038", tt="lookup_value", p="我们和采芝林的供货合同，质保期写的多久？",
  files={"采购/采芝林-供货合同-2026.md": "# 供货合同\n\n供方：采芝林食品\n质保期：自收货之日起 18 个月。\n退换货：开箱 7 日内凭质检报告办理。\n",
         "采购/验收记录.csv": "日期,批次\n2026-06-01,B-0601\n"},
  inc=["18"], exc=["12 个月", "12个月", "一年"], trap="TR-WEBSTALE",
  web=[fx("采芝林", "https://www.caizhilin-foods.cn/service/warranty", "售后与质保 - 采芝林食品", "质保政策。",
          "# 售后与质保\n\n标准质保期 12 个月。\n", "2026-05-05")], t2=("L", "退换货的时限呢？", ["7"]))
s(cid="cfg-35039", tt="lookup_value", p="咱们的云杉对象存储桶，生命周期规则设的是多少天转冷存储？",
  files={"存储/云杉存储桶-生命周期.json": "{\n  \"bucket\": \"logs-archive\",\n  \"rules\": [\n    {\"id\": \"to-cold\", \"after_days\": 45, \"class\": \"cold\"},\n    {\"id\": \"expire\", \"after_days\": 400}\n  ]\n}\n",
         "存储/桶清单.txt": "logs-archive\nmedia-raw\n"},
  inc=["45"], exc=["30 天", "30天", "60 天", "60天"], trap="TR-DECOY")
s(cid="doc-35040", tt="lookup_value", p="我们和百川翻译社约定的千字翻译单价是多少？",
  files={"采购/百川翻译社-服务确认单.md": "# 服务确认单\n\n服务方：百川翻译社\n中译英：千字 280 元；英译中：千字 220 元。\n交付：5000 字以内 3 天。\n",
         "采购/稿件登记.csv": "稿件,字数\n产品手册,12000\n"},
  inc=["280"], exc=["350 元", "350元"], trap="TR-WEBSTALE",
  web=[fx("百川翻译社", "https://www.baichuan-translation.cn/price", "翻译报价 - 百川翻译社", "公开报价。",
          "# 翻译报价\n\n中译英：千字 350 元起。英译中：千字 260 元起。\n", "2026-07-11")], t2=("L", "英译中的呢？", ["220"]))
