"""G1 configs: cfg-35517..35523."""
import random

import fill
from common import make, T

B = []


def reg(f):
    B.append(f)
    return f


def R(k):
    return random.Random("b23g-cfg-" + k)


@reg
def c01():
    r = R("01")
    bl = fill.yaml_blocks(r, 90)
    header = ["# per-service overrides, generated from the mesh inventory", "# edit the inventory, not this file, for new services"]
    ps = [(45, ["", "ledger-staging:", "  replicas: 2", "  pool_size: 20", "  timeout_s: 12"]),
          (330, ["", "ledger-prod:", "  replicas: 6", "  pool_size: 96", "  timeout_s: 30"])]
    lines = fill.compose(bl, ps, header=header, n=520)
    make("cfg-35517", sub="G1", task_type="lookup_value", desc="YAML overrides, prod entry deep in the file, staging on the first screen",
         path="deploy/service-mesh-overrides.yaml", lines=lines,
         turns=[T("In deploy/service-mesh-overrides.yaml, what pool_size does the ledger-prod entry set?", "96", "  pool_size: 96", "  pool_size: 20",
                  excl=["pool_size: 20"])],
         notes=("The first screen has ledger-staging with pool_size 20.", "read_file -> search_text 'ledger-prod' -> read the block -> 96.",
                "Only one ledger-prod key."))


@reg
def c02():
    r = R("02")
    bl = fill.ini_blocks(r, 90, avoid=("cache",))
    header = ["; vault sync settings", "; values are seconds unless noted"]
    ps = [(60, ["", "[cache]", "sync_interval = 45"]), (340, ["", "[replication]", "region_pair = eu-west:eu-north", "sync_interval = 300"])]
    lines = fill.compose(bl, ps, header=header, n=520)
    make("cfg-35518", sub="G1", task_type="lookup_value", desc="INI sections, sync interval of [replication] deep in the file",
         path="conf/vault-sync.ini", lines=lines,
         turns=[T("In the [replication] section of conf/vault-sync.ini, what is sync_interval?", "300", "sync_interval = 300", "sync_interval = 45",
                  excl=["sync_interval = 45"])],
         notes=("The first screen has [cache] with sync_interval = 45.", "read_file -> search_text '[replication]' -> read the section -> 300.",
                "Only [replication] has region_pair."))


@reg
def c03():
    r = R("03")
    bl = fill.toml_blocks(r, 90)
    header = ["# scheduler limits", "# one table per pool"]
    ps = [(50, ["", "[pools.interactive]", "max_concurrent_jobs = 16", "queue_timeout_s = 20"]),
          (350, ["", "[pools.batch]", "max_concurrent_jobs = 48", "queue_timeout_s = 600"])]
    lines = fill.compose(bl, ps, header=header, n=540)
    make("cfg-35519", sub="G1", task_type="lookup_value", desc="TOML pools, batch pool limit deep in the file",
         path="config/scheduler-limits.toml", lines=lines,
         turns=[T("In config/scheduler-limits.toml, what is max_concurrent_jobs for the [pools.batch] table?", "48", "max_concurrent_jobs = 48",
                  "max_concurrent_jobs = 16", excl=["max_concurrent_jobs = 16"])],
         notes=("The first screen has [pools.interactive] with 16.", "read_file -> search_text 'pools.batch' -> 48.", "queue_timeout_s = 600 is unique to the batch pool."))


@reg
def c04():
    r = R("04")
    bl = fill.props_blocks(r, 90, avoid=("invoice",))
    header = ["# payments client tuning", "# one block per downstream"]
    ps = [(55, ["", "# payout client", "payout.client.read.timeout.ms=3000"]),
          (360, ["", "# refund client", "refund.client.read.timeout.ms=8500"])]
    lines = fill.compose(bl, ps, header=header, n=560)
    make("cfg-35520", sub="G1", task_type="lookup_value", desc="Properties file, refund client timeout deep in the file",
         path="conf/payments-client.properties", lines=lines,
         turns=[T("What read timeout in milliseconds does conf/payments-client.properties set for the refund client?", 8500,
                  "refund.client.read.timeout.ms", "payout.client.read.timeout.ms", excl=["3000", "3,000"])],
         notes=("The first screen has the payout client at 3000.", "read_file -> search_text 'refund' -> 8500.", "One refund timeout key."))


@reg
def c05():
    r = R("05")
    bl = fill.yaml_blocks(r, 90)
    header = ["# 生产告警规则", "# 修改前请先在评审群里确认"]
    ps = [(50, ["", "memory_critical:", "  threshold: 90", "  for_minutes: 5"]),
          (340, ["", "cpu_critical:", "  threshold: 85", "  for_minutes: 15"])]
    lines = fill.compose(bl, ps, header=header, n=520)
    make("cfg-35521", sub="G1", task_type="lookup_value", desc="告警规则 YAML，cpu_critical 在后部",
         path="配置/告警规则-生产.yaml", lines=lines,
         turns=[T("配置/告警规则-生产.yaml 里，cpu_critical 规则要持续多少分钟才会触发？", "15", "for_minutes: 15", "for_minutes: 5",
                  excl=["for_minutes: 5"])],
         notes=("第一屏有 memory_critical（5 分钟）。", "read_file -> search_text 'cpu_critical' -> 15。", "cpu_critical 只有一处。"))


@reg
def c06():
    r = R("06")
    bl = fill.ini_blocks(r, 90, avoid=("cache",))
    header = ["; 网关路由配置", "; 单位：秒"]
    ps = [(60, ["", "[prod]", "upstream_timeout = 60"]), (350, ["", "[gray]", "upstream_timeout = 27"])]
    lines = fill.compose(bl, ps, header=header, n=520)
    make("cfg-35522", sub="G1", task_type="lookup_value", desc="网关路由 INI，灰度段在后部",
         path="配置/网关路由.ini", lines=lines,
         turns=[T("配置/网关路由.ini 里，[gray] 灰度段的 upstream_timeout 是多少秒？", "27", "upstream_timeout = 27", "upstream_timeout = 60", excl=["upstream_timeout = 60"])],
         notes=("第一屏是 [prod] 段（60 秒）。", "read_file -> search_text '[gray]' -> 27。", "[gray] 只有一段。"))


@reg
def c07():
    r = R("07")
    bl = fill.props_blocks(r, 90)
    header = ["# 短信通道配置", "# 每个通道一个块"]
    ps = [(55, ["", "# 验证码通道", "channel.verify.daily_limit=200000"]), (360, ["", "# 营销通道", "channel.marketing.daily_limit=50000"])]
    lines = fill.compose(bl, ps, header=header, n=560)
    make("cfg-35523", sub="G1", task_type="lookup_value", desc="短信通道 properties，营销通道上限在后部",
         path="配置/短信通道.properties", lines=lines,
         turns=[T("配置/短信通道.properties 里，营销短信通道每天最多发多少条？", ("any", ["50000", "50,000", "5万", "5 万"]),
                  "channel.marketing.daily_limit", "channel.verify.daily_limit", excl=["200000", "200,000", "20万"])],
         notes=("第一屏是验证码通道的上限（200000）。", "read_file -> search_text '营销' -> 50000。", "营销通道只有一个 key。"))
