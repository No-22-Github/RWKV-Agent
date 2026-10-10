"""b10e M5 part A (v1.4 §3.5): in-place value edits that keep trailing comments, alignment and indentation. cfg-8600..8649."""
import json
from common import write_case

CASES = []


def C(cid, lang, slug, desc, path, content, old, ov, nv, prompt, section=None, ticket=None, tv=None,
      done=False, decoy=None, extra=None):
    """One case. old = exact target line; ov/nv = old/new value inside it.
    ticket = (path, text) holding the new value tv; decoy = one-line note for the trap."""
    CASES.append(dict(cid=cid, lang=lang, slug=slug, desc=desc, path=path, content=content, old=old, ov=ov,
                      nv=nv, prompt=prompt, section=section, ticket=ticket, tv=tv, done=done, decoy=decoy,
                      extra=extra or {}))


# ====================================================================== 中文
C("cfg-8600", "zh", "bnbsync", "Change a sync interval in a guesthouse channel-sync config, keep the trailing comment aligned",
  "配置/房态同步.yaml",
  """# 民宿房态同步
渠道: 携程
同步间隔分钟: 15      # 2026-06 与平台对账后调整
失败重试次数: 3       # 超过后发钉钉告警
房态来源: 前台系统
""",
  "同步间隔分钟: 15      # 2026-06 与平台对账后调整", "15", "10",
  "把 配置/房态同步.yaml 的同步间隔分钟改成 10，注释和对齐不要动。改完回复 DONE。", done=True)

C("cfg-8601", "zh", "drivebook", "Set the daily booking cap of a driving school from a change ticket, TOML with trailing comment",
  "配置/约车.toml",
  """[排班]
教练人数 = 12
每日最大约车数 = 40  # 教练反馈上限
最早开始 = "07:30"
最晚结束 = "18:00"
""",
  "每日最大约车数 = 40  # 教练反馈上限", "40", "36",
  "按 变更单/BG-2209.txt 把 配置/约车.toml 里的每日最大约车数改掉，其他保持原样。",
  ticket=("变更单/BG-2209.txt", "变更项: 每日最大约车数\n新值: 36\n原因: 两名教练休假\n申请: 教务处 钱慧敏 2026-09-18\n"), tv="36")

C("cfg-8602", "zh", "dentalremind", "Change the reminder lead time in a dental clinic INI that uses semicolon comments",
  "设置/预约提醒.ini",
  """[短信]
提前提醒小时 = 24   ; 患者反馈太早
发送时段 = 09:00-20:00
模板 = 复诊提醒

[微信]
提前提醒小时 = 24   ; 与短信一致
模板 = 复诊提醒
""",
  "提前提醒小时 = 24   ; 患者反馈太早", "24", "12",
  "诊所决定短信渠道提前 12 小时提醒就够了，在 设置/预约提醒.ini 里改一下，微信那边不变。改完回复 DONE。",
  section="[短信]", done=True, decoy="[微信] 段有同名键且同值 24，只能改 [短信]。")

C("cfg-8603", "zh", "parcelhold", "Raise a parcel-station overdue threshold nested under a rule block; cold-chain block has a similar key",
  "站点/驿站规则.yaml",
  """取件规则:
  普通件:
    超期天数: 3        # 超期转退回
    短信提醒次数: 2
  冷链件:
    超期天数: 1        # 生鲜不留存
    短信提醒次数: 3
""",
  "    超期天数: 3        # 超期转退回", "3", "5",
  "驿站普通件的超期天数要从 3 天放宽到 5 天，改 站点/驿站规则.yaml，冷链件那条别碰。",
  decoy="冷链件段也有「超期天数」键，不能误改。")

C("cfg-8604", "zh", "nursepatrol", "Change a nursing-home patrol interval inside an indented block with no comments, value from a ticket",
  "护理/巡房.yaml",
  """巡房计划:
  白班:
    间隔分钟: 60
    重点楼层: [2, 3]
  夜班:
    间隔分钟: 45
    重点楼层: [3]
""",
  "    间隔分钟: 45", "45", "30",
  "照 护理/通知-0921.txt 里说的，把 护理/巡房.yaml 的夜班巡房间隔改了。改完回复 DONE。", section="  夜班:", done=True,
  ticket=("护理/通知-0921.txt", "通知: 即日起夜班巡房间隔缩短为 30 分钟，白班不变。\n发布: 护理部 方淑贞\n"), tv="30",
  decoy="白班同样有「间隔分钟」键，通知只改夜班。")

C("cfg-8605", "zh", "pvpoll", "Lower a PV inverter polling period in an env file, keep the hint comment",
  "采集/inverter.env",
  """SITE_ID=PV-0317
INVERTER_POLL_SEC=20     # 厂商建议不低于 10
METER_POLL_SEC=60
UPLOAD_URL=http://scada.internal:7001/push
""",
  "INVERTER_POLL_SEC=20     # 厂商建议不低于 10", "20", "15",
  "光伏站这边逆变器轮询周期想调到 15 秒，在 采集/inverter.env 里改，别的变量不动。")

C("cfg-8606", "zh", "busdepart", "Change a quoted departure time in a school-bus route file, keep the quotes and note",
  "校车/路线三.yaml",
  """路线: 三号线
发车时间: "06:50"   # 冬令时
末站: 实验小学
站点数: 9
""",
  '发车时间: "06:50"   # 冬令时', "06:50", "07:05",
  "三号线校车发车时间改为 07:05，文件是 校车/路线三.yaml，引号和后面的注释保留。改完回复 DONE。", done=True)

C("cfg-8607", "zh", "parkrate", "Change the hourly rate of the daytime tier in a parking TOML; night tier has the same value",
  "停车场/费率.toml",
  """[白天]
每小时 = 6      # 单位 元
封顶 = 40

[夜间]
每小时 = 6      # 单位 元
封顶 = 20
""",
  "每小时 = 6      # 单位 元", "6", "8",
  "停车场白天时段每小时费率涨到 8 元，改 停车场/费率.toml，夜间保持。",
  section="[白天]", decoy="[夜间] 段有完全相同的一行，只能改 [白天]。")

C("cfg-8608", "zh", "kinderpass", "Shorten a pickup-code validity in a kindergarten INI from a ticket table",
  "园务/接送.ini",
  """[接送码]
有效分钟 = 30     ; 过期需重新生成
长度 = 6
允许代接 = 是
""",
  "有效分钟 = 30     ; 过期需重新生成", "30", "20",
  "园务/工单-117.md 里批的接送码有效期，请落到 园务/接送.ini，改完回复 DONE。", done=True,
  ticket=("园务/工单-117.md", "# 工单 117\n\n| 项 | 新值 |\n|---|---|\n| 接送码有效分钟 | 20 |\n\n批准: 园长 梁雅琴\n"), tv="20")

C("cfg-8609", "zh", "printdry", "Set the dryer temperature of a print shop line, same-width value, aligned comment",
  "车间/烘干线.yaml",
  """烘干线:
  编号: 二线
  温度: 85       # 80g 纸对应 ℃
  风速档位: 2
  传送速度: 14   # 米/分
""",
  "  温度: 85       # 80g 纸对应 ℃", "85", "82",
  "二线烘干温度改成 82，在 车间/烘干线.yaml 里改。")

C("cfg-8610", "zh", "cinemahall", "Change the show cap of hall 3 in a cinema scheduling file; other halls share the same line text",
  "排片/厅配置.yaml",
  """影厅:
  一号厅:
    每日最大场次: 8   # 含午夜场
    座位数: 180
  三号厅:
    每日最大场次: 8   # 含午夜场
    座位数: 96
""",
  "    每日最大场次: 8   # 含午夜场", "8", "6",
  "三号厅座位少、清场慢，每日最大场次降到 6 场，改 排片/厅配置.yaml。改完回复 DONE。",
  section="  三号厅:", done=True, decoy="一号厅有一行完全相同的内容，只能改三号厅。")

C("cfg-8611", "zh", "evpower", "Reduce the power cap of a charging station in TOML from a ticket; value changes width but comment gap is two spaces",
  "充电站/站点-07.toml",
  """站点 = "滨江路站"
桩数 = 8
功率上限kW = 120  # 变压器限制
故障自动重启 = true
""",
  "功率上限kW = 120  # 变压器限制", "120", "90",
  "供电局来函后的新限值写在 充电站/来函摘要.txt，请把 充电站/站点-07.toml 的功率上限改成那个数。",
  ticket=("充电站/来函摘要.txt", "来函: 滨江路站变压器检修期间，充电功率上限不得超过 90 kW。\n日期: 2026-09-20\n"), tv="90")

C("cfg-8612", "zh", "fishoxy", "Raise the oxygen-start threshold of a fish pond aerator from a note with decoy item",
  "鱼塘/增氧机.yaml",
  """增氧机:
  启动溶氧阈值: 4.5    # mg/L，低于即启动
  停止溶氧阈值: 6.5    # mg/L
  夜间强制启动: 是
""",
  "  启动溶氧阈值: 4.5    # mg/L，低于即启动", "4.5", "5.0",
  "按 鱼塘/农技员记录.txt 最新的建议改 鱼塘/增氧机.yaml。改完回复 DONE。", done=True,
  ticket=("鱼塘/农技员记录.txt", "9月18日 建议启动溶氧阈值提到 5.0 mg/L，停止阈值先不动。\n9月11日 曾提议停止阈值 7.0，已否决。\n"), tv="5.0",
  decoy="记录里还有已否决的停止阈值 7.0，不能写进去。")

C("cfg-8613", "zh", "florist", "Change the delivery buffer in a florist env file, keep the inline comment",
  "订单/提醒.env",
  """SHOP=花信子
DELIVERY_BUFFER_MIN=45   # 节假日需手动加长
REMIND_BEFORE_MIN=20
""",
  "DELIVERY_BUFFER_MIN=45   # 节假日需手动加长", "45", "60",
  "七夕前后配送缓冲时间要放宽到 60 分钟，改 订单/提醒.env，提醒时间别动。")

C("cfg-8614", "zh", "hotelout", "Change the checkout time in a hotel config (quoted string), keep the comment; value in prompt",
  "前台/客房规则.yaml",
  """客房规则:
  入住时间: "14:00"
  退房时间: "12:00"   # 2025 起统一
  延迟退房费率: 0.5
""",
  '  退房时间: "12:00"   # 2025 起统一', "12:00", "11:30",
  "前台/客房规则.yaml 里的退房时间改成 11:30，其余原样。改完回复 DONE。", done=True,
  decoy="入住时间一行同属时间字段，不能改。")

C("cfg-8615", "zh", "grouppick", "Change a self-pickup retention period of a community group-buy point in INI",
  "团购/自提点.ini",
  """[自提点-柳岸花园]
保留天数 = 2     ; 超期退回团长
开放时段 = 17:00-21:00

[自提点-紫荆苑]
保留天数 = 2     ; 超期退回团长
开放时段 = 16:30-20:30
""",
  "保留天数 = 2     ; 超期退回团长", "2", "3",
  "紫荆苑自提点的货放得久一点，保留天数改成 3，改 团购/自提点.ini，柳岸花园不动。",
  section="[自提点-紫荆苑]", decoy="柳岸花园段的保留天数同值同注释，不能改。")

C("cfg-8616", "zh", "earlyclass", "Change a trial-class quota inside a nested block of an early-education centre config from a ticket",
  "早教/课程.yaml",
  """课程:
  音乐启蒙:
    试听名额: 6
    年龄段: 1-2岁
  感统训练:
    试听名额: 6
    年龄段: 2-3岁
""",
  "    试听名额: 6", "6", "8",
  "早教/排课单.txt 里提到感统训练的试听名额调整了，请把 早教/课程.yaml 同步。改完回复 DONE。", section="  感统训练:", done=True,
  ticket=("早教/排课单.txt", "10月起: 感统训练 试听名额 8 个；音乐启蒙维持现状。\n"), tv="8",
  decoy="音乐启蒙的试听名额与感统训练原值相同，只能改感统训练。")

C("cfg-8617", "zh", "rainstn", "Change the sampling period of a rain gauge station with a calibration comment",
  "雨量站/采集.yaml",
  """站号: YL-204
采样间隔秒: 30   # 2026-07 校准后调整
上传间隔秒: 300
传感器型号: TB-3
""",
  "采样间隔秒: 30   # 2026-07 校准后调整", "30", "20",
  "雨季到了，YL-204 的采样间隔秒调到 20，文件 雨量站/采集.yaml，注释留着。")

C("cfg-8618", "zh", "lifttour", "Change the inspection cycle of one elevator in a property config from a work order",
  "物业/电梯.yaml",
  """电梯:
  1号楼A梯:
    巡检周期天: 30     # 国标要求不超过 30 天
    维保单位: 恒升电梯
  1号楼B梯:
    巡检周期天: 30     # 国标要求不超过 30 天
    维保单位: 恒升电梯
""",
  "    巡检周期天: 30     # 国标要求不超过 30 天", "30", "15",
  "物业/工单-0925.txt 是对 B 梯的要求，按它改 物业/电梯.yaml。改完回复 DONE。", section="  1号楼B梯:", done=True,
  ticket=("物业/工单-0925.txt", "1号楼B梯 近期故障频发，巡检周期缩短为 15 天，维保单位不变。\n"), tv="15",
  decoy="A 梯那行文字完全一样，只能改 B 梯。")

C("cfg-8619", "zh", "labincub", "Change the incubator temperature in a lab config, keep alignment",
  "实验室/恒温箱.yaml",
  """设备: 恒温箱-02
设定温度: 37.0    # ℃，细胞培养
温度报警偏差: 0.5 # ℃
CO2: 5            # %
""",
  "设定温度: 37.0    # ℃，细胞培养", "37.0", "36.5",
  "恒温箱-02 的设定温度要改成 36.5，在 实验室/恒温箱.yaml，温度报警偏差不要动。")

C("cfg-8620", "zh", "greenhouse", "Change the roll-up opening temperature of a vegetable greenhouse, near-name key",
  "大棚/卷帘.toml",
  """[卷帘]
开启温度 = 28      # ℃
关闭温度 = 18      # ℃
开启温度滞后 = 2   # ℃
""",
  "开启温度 = 28      # ℃", "28", "26",
  "大棚卷帘的开启温度降到 26，改 大棚/卷帘.toml。改完回复 DONE。", done=True,
  decoy="「开启温度滞后」键名以「开启温度」开头，不能改错行。")

C("cfg-8621", "zh", "scenicgate", "Change the per-minute gate limit of a scenic spot from a ticket in a table",
  "景区/闸机.toml",
  """[东门]
每分钟限流 = 40   # 人/分钟

[西门]
每分钟限流 = 40   # 人/分钟
""",
  "每分钟限流 = 40   # 人/分钟", "40", "30",
  "景区/应急通知.md 里写了东门的限流要求，请据此改 景区/闸机.toml。",
  section="[东门]",
  ticket=("景区/应急通知.md", "# 应急通知（2026-10-01）\n\n| 闸机 | 每分钟限流 |\n|---|---|\n| 东门 | 30 |\n\n西门暂不调整。\n"), tv="30",
  decoy="西门一行内容相同，通知说西门暂不调整。")

# ====================================================================== English
C("cfg-8622", "en", "ciTimeout", "Raise a CI job timeout in a pipeline YAML, keep the trailing comment",
  ".ci/pipeline.yml",
  """stages:
  build:
    timeout_minutes: 20   # was 15 before the monorepo split
    cache: true
  test:
    timeout_minutes: 30   # includes integration suite
    cache: true
""",
  "    timeout_minutes: 20   # was 15 before the monorepo split", "20", "25",
  "Bump the build stage timeout in .ci/pipeline.yml to 25 minutes. Leave the test stage and the comments alone. Reply DONE when finished.",
  section="  build:", done=True, decoy="The test stage has the same key; only the build stage changes.")

C("cfg-8623", "en", "mailrelay", "Lower max recipients in a mail relay INI per a change request",
  "relay/mail.ini",
  """[limits]
max_recipients = 100   ; per message
max_message_kb = 10240
rate_per_minute = 600

[tls]
required = yes
""",
  "max_recipients = 100   ; per message", "100", "50",
  "Apply the recipient limit from changes/CHG-4471.txt to relay/mail.ini.",
  ticket=("changes/CHG-4471.txt", "Change: max_recipients\nNew value: 50\nReason: spam wave on 2026-09-22\nApproved: J. Okafor\n"), tv="50")

C("cfg-8624", "en", "hpa", "Change the max replicas of one workload in a Helm values file, same key in another workload",
  "deploy/values.yaml",
  """api:
  replicaCount: 3
  autoscaling:
    maxReplicas: 10     # capped by node pool size
worker:
  replicaCount: 2
  autoscaling:
    maxReplicas: 10     # capped by node pool size
""",
  "    maxReplicas: 10     # capped by node pool size", "10", "14",
  "Let the worker autoscale up to 14 replicas in deploy/values.yaml. api stays as is. Reply DONE when done.",
  section="worker:", done=True, decoy="api has an identical maxReplicas line; only the worker block changes.")

C("cfg-8625", "en", "flagrollout", "Raise a feature flag rollout percentage in YAML, keeping the aligned comment",
  "flags/rollout.yaml",
  """new_checkout:
  enabled: true
  percent: 25       # ramp: 10 -> 25 -> 50
  owners: [payments]
search_v2:
  enabled: true
  percent: 80       # ramp done
  owners: [search]
""",
  "  percent: 25       # ramp: 10 -> 25 -> 50", "25", "50",
  "Move new_checkout to the next ramp step in flags/rollout.yaml (the comment tells you which one). Don't touch search_v2.",
  decoy="Both flags have a percent line; search_v2 must stay at 80.")

C("cfg-8626", "en", "backupkeep", "Change backup retention days in TOML with a comment, value from a runbook note",
  "ops/backup.toml",
  """[retention]
daily = 14     # days
weekly = 8     # weeks
monthly = 12   # months
""",
  "daily = 14     # days", "14", "21",
  "The new daily backup retention is in ops/runbook-note.md. Update ops/backup.toml accordingly and reply DONE.", done=True,
  ticket=("ops/runbook-note.md", "# Runbook note\n\nAfter the audit, keep daily backups for 21 days. Weekly and monthly are unchanged.\n"), tv="21")

C("cfg-8627", "en", "logrotate", "Change log rotation size in an INI file, trailing semicolon comment",
  "etc/logrotate.ini",
  """[app]
max_size_mb = 100    ; rotate when exceeded
keep_files = 7
compress = yes

[audit]
max_size_mb = 100    ; rotate when exceeded
keep_files = 30
compress = yes
""",
  "max_size_mb = 100    ; rotate when exceeded", "100", "250",
  "Audit logs grow faster; raise the audit section's max_size_mb to 250 in etc/logrotate.ini and leave the app section.",
  section="[audit]", decoy="[app] has an identical line.")

C("cfg-8628", "en", "cdnttl", "Change a CDN cache TTL for static assets in YAML, near-named key below",
  "cdn/cache.yaml",
  """rules:
  static:
    ttl_seconds: 3600       # images, css, js
    ttl_seconds_error: 30   # 4xx/5xx
  api:
    ttl_seconds: 0
""",
  "    ttl_seconds: 3600       # images, css, js", "3600", "7200",
  "Static assets can be cached for two hours. Update cdn/cache.yaml. Reply DONE.", done=True,
  decoy="ttl_seconds_error shares the key prefix; do not touch it.")

C("cfg-8629", "en", "dbpool", "Change the DB pool size in an env file, keep the comment",
  "services/orders/.env.prod",
  """DB_HOST=pg-orders.internal
DB_POOL_SIZE=20      # per instance; max_connections is 400
DB_POOL_TIMEOUT=5
LOG_LEVEL=info
""",
  "DB_POOL_SIZE=20      # per instance; max_connections is 400", "20", "30",
  "Set DB_POOL_SIZE to 30 in services/orders/.env.prod and leave the rest as is.")

C("cfg-8630", "en", "ratelimit", "Change the burst value of a rate limiter in TOML according to a ticket with several items",
  "gateway/limits.toml",
  """[login]
rate = 5
burst = 10     # allow short spikes

[search]
rate = 50
burst = 100    # allow short spikes
""",
  "burst = 10     # allow short spikes", "10", "20",
  "Do the login item from tickets/GW-318.txt in gateway/limits.toml. Reply DONE when it's in.", section="[login]", done=True,
  ticket=("tickets/GW-318.txt", "GW-318\n1. login.burst -> 20\n2. search.rate -> 80 (blocked, waiting on capacity review)\n"), tv="20",
  decoy="The ticket's other item is blocked and must not be applied.")

C("cfg-8631", "en", "tickrate", "Change a game server tick rate in INI, same-width value",
  "server/game.ini",
  """[world]
tick_rate = 64     ; Hz
max_players = 32
region = eu-west
""",
  "tick_rate = 64     ; Hz", "64", "32",
  "Drop tick_rate to 32 in server/game.ini for the soak test; keep everything else byte for byte.")

C("cfg-8632", "en", "otelsample", "Change telemetry sampling ratio in YAML, ticket gives the value",
  "otel/collector.yaml",
  """processors:
  probabilistic_sampler:
    sampling_percentage: 15   # prod default
  batch:
    timeout: 5s
    send_batch_size: 8192
""",
  "    sampling_percentage: 15   # prod default", "15", "5",
  "Set the sampler to the percentage in otel/ask.txt (otel/collector.yaml). Reply DONE.", done=True,
  ticket=("otel/ask.txt", "Hi - traces bill is too high. Please sample at 5 percent starting this week. Thanks, Dana\n"), tv="5")

# ====================================================================== 追加 8633..8649
C("cfg-8633", "zh", "beekeep", "Change the hive-scale reporting period in a beekeeping station config, keep aligned comments",
  "蜂场/称重.yaml",
  """蜂箱称重:
  上报周期分钟: 30    # 流蜜期可缩短
  重量突降告警kg: 2   # 疑似分蜂
  蜂箱数: 24
""",
  "  上报周期分钟: 30    # 流蜜期可缩短", "30", "10",
  "洋槐花期开始了，蜂箱称重的上报周期分钟改成 10，文件 蜂场/称重.yaml，别的行都别碰。改完回复 DONE。", done=True)

C("cfg-8634", "zh", "portcrane", "Change the wind-speed stop threshold of one crane in a port config; two cranes share the line text",
  "码头/岸桥.toml",
  """[岸桥1号]
停机风速 = 20   # m/s，十级风前
吊具型号 = "双箱"

[岸桥2号]
停机风速 = 20   # m/s，十级风前
吊具型号 = "单箱"
""",
  "停机风速 = 20   # m/s，十级风前", "20", "18",
  "2 号岸桥的停机风速调低到 18，改 码头/岸桥.toml，1 号不动。",
  section="[岸桥2号]", decoy="1 号岸桥有完全相同的一行。")

C("cfg-8635", "zh", "coffeeroast", "Change a roast drop temperature from an operator note in a coffee roastery YAML",
  "烘豆/曲线.yaml",
  """批次: 埃塞-水洗
下豆温度: 208      # ℃，浅烘
回温点秒: 70
发展时间占比: 0.18  # 目标 15%-20%
""",
  "下豆温度: 208      # ℃，浅烘", "208", "210",
  "烘豆师在 烘豆/备忘.txt 里写了这批的新下豆温度，照着改 烘豆/曲线.yaml。改完回复 DONE。", done=True,
  ticket=("烘豆/备忘.txt", "埃塞这批试烘后感觉偏生，下豆温度提到 210 ℃。\n回温点先不动。\n"), tv="210")

C("cfg-8636", "zh", "tutorscore", "Change the pass mark of a mock exam in an online tutoring INI with a semicolon note",
  "教务/测验.ini",
  """[模拟卷]
及格线 = 60     ; 满分 100
限时分钟 = 90
题数 = 40

[月考]
及格线 = 60     ; 满分 100
限时分钟 = 120
""",
  "及格线 = 60     ; 满分 100", "60", "65",
  "模拟卷的及格线提到 65，教务/测验.ini 里改，月考那边不变。改完回复 DONE。",
  section="[模拟卷]", done=True, decoy="[月考] 段有一模一样的及格线行。")

C("cfg-8637", "zh", "ferrytide", "Change the minimum water depth for sailing in a ferry schedule env file",
  "渡口/运行.env",
  """FERRY_ID=DK-02
MIN_DEPTH_CM=120     # 低于则停航
MAX_WIND_LEVEL=6
LOG_DIR=/var/log/ferry
""",
  "MIN_DEPTH_CM=120     # 低于则停航", "120", "140",
  "枯水期渡口最低通航水深抬高到 140 厘米，改 渡口/运行.env。")

C("cfg-8638", "zh", "vetfarm", "Change the feed ration of one pen from a farm ticket, indented YAML with decoy pen",
  "养殖/饲喂.yaml",
  """栏舍:
  A栏:
    日喂次数: 3
    每次投喂kg: 12.5   # 含补料
  B栏:
    日喂次数: 3
    每次投喂kg: 12.5   # 含补料
""",
  "    每次投喂kg: 12.5   # 含补料", "12.5", "11.0",
  "养殖/兽医意见.txt 说了哪个栏要减料，照办改 养殖/饲喂.yaml。改完回复 DONE。", section="  B栏:", done=True,
  ticket=("养殖/兽医意见.txt", "B栏近期消化不良，每次投喂量减到 11.0 kg，次数不变。A栏正常。\n"), tv="11.0",
  decoy="A 栏同值同注释，不能改。")

C("cfg-8639", "zh", "cranelock", "Change the lock-out duration of a smart locker bank, TOML table with similar key names",
  "快递柜/格口.toml",
  """[格口]
锁定分钟 = 15       # 连续输错密码后
锁定分钟上限 = 60   # 多次锁定累加封顶
超时未取小时 = 48
""",
  "锁定分钟 = 15       # 连续输错密码后", "15", "10",
  "智能柜输错密码后的锁定分钟改成 10，在 快递柜/格口.toml，其他键保持。",
  decoy="「锁定分钟上限」键名以「锁定分钟」开头，不能改错行。")

C("cfg-8640", "zh", "salonslot", "Change slot length of a hair salon booking config from a manager note, INI with quoted comment marker",
  "预约/时段.ini",
  """[剪发]
时段分钟 = 40    ; 含洗吹
提前预约天数 = 14

[烫染]
时段分钟 = 150   ; 含等待
提前预约天数 = 21
""",
  "时段分钟 = 40    ; 含洗吹", "40", "45",
  "店长在 预约/店长留言.txt 里说了剪发的时段要改，帮我落到 预约/时段.ini。改完回复 DONE。", section="[剪发]", done=True,
  ticket=("预约/店长留言.txt", "剪发总是超时，时段改成 45 分钟吧。烫染别动。——店长 汪俊豪\n"), tv="45")

C("cfg-8641", "zh", "schoolbell", "Change the length of a school period in a bell-schedule YAML, keep the comment",
  "校务/作息.yaml",
  """作息:
  课时分钟: 40      # 2025 秋季学期起
  课间分钟: 10
  大课间分钟: 25
""",
  "  课时分钟: 40      # 2025 秋季学期起", "40", "35",
  "校务/作息.yaml 的课时分钟改成 35，课间、大课间不变。改完回复 DONE。", done=True)

C("cfg-8642", "en", "kafkaretain", "Change a Kafka topic retention in a properties-style INI, trailing comment kept",
  "kafka/topics.ini",
  """[orders]
retention_hours = 72    ; replay window
partitions = 12

[clicks]
retention_hours = 72    ; replay window
partitions = 24
""",
  "retention_hours = 72    ; replay window", "72", "168",
  "Make the clicks topic keep data for a week (168 hours) in kafka/topics.ini; orders stays at 72.",
  section="[clicks]", decoy="[orders] has an identical retention line.")

C("cfg-8643", "en", "sshdcfg", "Change the idle timeout in a service TOML from a ticket with an inline note, then reply DONE",
  "bastion/session.toml",
  """[session]
idle_timeout_min = 15   # compliance: <= 15
max_sessions = 4
banner = "authorized use only"
""",
  "idle_timeout_min = 15   # compliance: <= 15", "15", "10",
  "Security asked for a shorter idle timeout, see bastion/SEC-209.txt. Please apply it to bastion/session.toml and reply DONE.", done=True,
  ticket=("bastion/SEC-209.txt", "SEC-209: idle_timeout_min must be 10 for all bastion hosts effective immediately.\nOwner: R. Valdez\n"), tv="10")

C("cfg-8644", "en", "retrycfg", "Change retry count of the upload client in YAML nested block, near-name key below",
  "client/upload.yaml",
  """upload:
  retries: 5            # exponential backoff
  retries_delay_ms: 200 # base delay
  chunk_mb: 8
""",
  "  retries: 5            # exponential backoff", "5", "3",
  "Reduce the upload client's retries to 3 in client/upload.yaml. Reply DONE.", done=True,
  decoy="retries_delay_ms starts with the same word; leave it.")

C("cfg-8645", "en", "envregion", "Change the cache size in an env file where the same number appears in another variable",
  "app/.env",
  """CACHE_MB=512      # per worker
WORKERS=4
UPLOAD_LIMIT_MB=512
REGION=ap-south
""",
  "CACHE_MB=512      # per worker", "512", "768",
  "Bump CACHE_MB to 768 in app/.env. UPLOAD_LIMIT_MB stays.", decoy="UPLOAD_LIMIT_MB also has 512.")

C("cfg-8646", "en", "alertthresh", "Change the CPU alert threshold of one host group per a ticket mentioning two groups",
  "monitoring/alerts.yaml",
  """groups:
  web:
    cpu_percent: 80     # page after 10m
    mem_percent: 85
  batch:
    cpu_percent: 80     # page after 10m
    mem_percent: 90
""",
  "    cpu_percent: 80     # page after 10m", "80", "90",
  "monitoring/ticket-77.txt has a request for the batch group's CPU alert. Apply it to monitoring/alerts.yaml. Reply DONE.",
  section="  batch:", done=True,
  ticket=("monitoring/ticket-77.txt", "Batch nodes sit at 85% CPU by design. Raise their cpu_percent alert to 90.\nWeb group: no change.\n"), tv="90",
  decoy="web has the same cpu_percent line; do not touch it.")

C("cfg-8647", "en", "quotedver", "Change a quoted version string in TOML, keep quotes and comment",
  "pkg/release.toml",
  """[release]
channel = "stable"
min_client = "2.4.1"   # first build with the new auth flow
notes_url = "https://example.test/notes"
""",
  'min_client = "2.4.1"   # first build with the new auth flow', "2.4.1", "2.5.0",
  "Raise min_client to 2.5.0 in pkg/release.toml; keep the quotes and the trailing comment.")

C("cfg-8648", "en", "cronconf", "Change a poll interval in an INI file indented under a section with blank-line separators",
  "ops/poller.conf.ini",
  """[sync]
poll_every_s = 45     ; lower = more load
chunk_rows = 200

[cleanup]
poll_every_s = 600    ; hourly is too slow
chunk_rows = 50
""",
  "poll_every_s = 45     ; lower = more load", "45", "30",
  "Set the sync job's poll_every_s to 30 in ops/poller.conf.ini and leave cleanup alone. Reply DONE when it's done.",
  section="[sync]", done=True)

C("cfg-8649", "zh", "ricefarm", "Change the irrigation start moisture from a technician note, YAML aligned comments with decoy",
  "农场/灌溉.yaml",
  """灌溉:
  启动土壤湿度: 35    # %，低于即灌
  停止土壤湿度: 60    # %
  单次最长分钟: 90
""",
  "  启动土壤湿度: 35    # %，低于即灌", "35", "40",
  "农场/技术员留言.txt 说灌溉要早点启动，照留言改 农场/灌溉.yaml。改完回复 DONE。", done=True,
  ticket=("农场/技术员留言.txt", "秧苗期启动土壤湿度提到 40%，停止湿度 65% 只是我的想法，先别改。\n"), tv="40",
  decoy="留言里提到的停止湿度 65% 只是设想，不能写入。")


# ====================================================================== emit
VERIFY = '''
import json

case = json.load(open("case.json"))
PATH, OLD, NEW, SECTION, TICKET = %r, %r, %r, %r, %r
if TICKET:
    assert case["files"][TICKET[0]] == TICKET[1], "ticket changed"
assert set(case["files"]) == {PATH} | ({TICKET[0]} if TICKET else set())
text = case["files"][PATH]
lines = text.splitlines(keepends=True)
start = 0
if SECTION is not None:
    hits = [i for i, l in enumerate(lines) if l.rstrip("\\n") == SECTION]
    assert len(hits) == 1, hits
    start = hits[0]
idx = [i for i, l in enumerate(lines) if i >= start and l.rstrip("\\n") == OLD]
assert idx, "target line missing"
if SECTION is None:
    assert len(idx) == 1, idx
lines[idx[0]] = NEW + "\\n"
print(json.dumps({"files": {PATH: "".join(lines)}}, ensure_ascii=False))
'''


def emit(c):
    lines = c["content"].splitlines(keepends=True)
    start = 0
    if c["section"] is not None:
        hits = [i for i, l in enumerate(lines) if l.rstrip("\n") == c["section"]]
        assert len(hits) == 1, (c["cid"], "section", hits)
        start = hits[0]
    idx = [i for i, l in enumerate(lines) if i >= start and l.rstrip("\n") == c["old"]]
    assert idx, (c["cid"], "old line not found")
    if c["section"] is None:
        assert len(idx) == 1, (c["cid"], "old line not unique")
    # the value must sit after the key separator, and the replacement must be literal
    sep = min(i for i in (c["old"].find(":"), c["old"].find("=")) if i >= 0)
    vpos = c["old"].find(c["ov"], sep)
    assert vpos > 0, (c["cid"], "value not after separator")
    new_line = c["old"][:vpos] + c["nv"] + c["old"][vpos + len(c["ov"]):]
    assert new_line != c["old"]
    out = list(lines)
    out[idx[0]] = new_line + "\n"
    expected = "".join(out)
    if c["ticket"]:
        assert c["tv"] in c["ticket"][1], c["cid"]
    # the new value must not be a bare literal that already exists on another target-file line by accident
    zh = c["lang"] == "zh"
    files = {c["path"]: c["content"]}
    if c["ticket"]:
        files[c["ticket"][0]] = c["ticket"][1]
    exp = {"max_output_chars": 400 if c["ticket"] else 300}
    if c["done"]:
        exp["output_contains"] = ["DONE"]
    if zh:
        ref = "已把 %s 里的 %s 改成 %s，注释和缩进没动。" % (c["path"], c["old"].split(":")[0].split("=")[0].strip(), c["nv"])
    else:
        ref = "Updated %s: the value is now %s, comments and alignment untouched." % (c["path"], c["nv"])
    if c["done"]:
        ref += "\nDONE"
    assert len(ref) <= exp["max_output_chars"]
    assert not c["done"] or "DONE" in ref
    reads = ("读 %s 取得新值 %s" % (c["ticket"][0], c["tv"])) if zh and c["ticket"] else ""
    if not zh and c["ticket"]:
        reads = "Read %s: new value %s" % (c["ticket"][0], c["tv"])
    sec = c["section"] if c["section"] else "(no section needed)"
    notes = f'''
## Traps
- {"TR-DECOY" if c["decoy"] else "TR-READONLY"}: {c["decoy"] or "只改目标值；整文件重写、丢行尾注释、动对齐或缩进，文件就不再逐字节相等。"} Target line: `{c["old"]}` ({sec}).

## Reference solution
1. {reads or "No ticket: the new value is in the prompt."}
2. Read {c["path"]}; locate the target line `{c["old"]}`.
3. replace_lines that single line with `{new_line}` (only {c["ov"]} -> {c["nv"]}).
4. Read {c["path"]} back and confirm only that line changed.
Final answer: {ref!r}. Criteria: file equals the expected content exactly{"; output contains DONE" if c["done"] else ""}.

## Why the answer is unique
Exactly one value changes; the rest of the line (comment, spacing, quotes) is kept literally, so the result file is fixed.
'''
    write_case(
        c["cid"], desc=c["desc"], task_type="edit_value",
        family="fam-cfg-b10e-%s-01" % c["slug"], level="L1", ref_calls=4 if c["ticket"] else 3,
        traps=["TR-DECOY" if c["decoy"] else "TR-READONLY"], decoys={("TR-DECOY" if c["decoy"] else "TR-READONLY"): None},
        axes=["OBS" if c["decoy"] else "CON"], files=files,
        case_expect={"files": {c["path"]: {"equals": expected}}},
        turns=[{"prompt": c["prompt"], "expect": exp}],
        verify=VERIFY % (c["path"], c["old"], new_line, c["section"], c["ticket"]), notes=notes)


for _c in CASES:
    emit(_c)
assert len(CASES) == 50 and sum(1 for c in CASES if c["lang"] == "zh") >= 15
assert len({c["slug"] for c in CASES}) == 50
