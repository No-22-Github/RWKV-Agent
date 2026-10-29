"""G1 code: code-35524..35530."""
import random

import fill
from common import make, T

B = []


def reg(f):
    B.append(f)
    return f


def R(k):
    return random.Random("b23g-code-" + k)


@reg
def k01():
    r = R("01")
    bl = fill.py_blocks(r, 70)
    header = ['"""Retry and timeout policy for ledger clients."""', "", "import random", "import time", "", "CONNECT_TIMEOUT_S = 10"]
    ps = [(300, ["", "", "READ_TIMEOUT_S = 75"])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("code-35524", sub="G1", task_type="lookup_value", desc="Python module, read timeout constant deep in the file",
         path="src/ledger/retry_policy.py", lines=lines,
         turns=[T("What is READ_TIMEOUT_S set to in src/ledger/retry_policy.py?", "75", "READ_TIMEOUT_S = 75", "CONNECT_TIMEOUT_S = 10",
                  excl=["CONNECT_TIMEOUT_S = 10"])],
         notes=("The module opens with CONNECT_TIMEOUT_S = 10, a sibling constant.", "read_file -> search_text 'READ_TIMEOUT_S' -> 75.", "One definition."))


@reg
def k02():
    r = R("02")
    bl = fill.py_blocks(r, 70, avoid=("manifest",))
    header = ['"""Manifest checks used by the ingest pipeline."""', "", "", "class SchemaViolation(Exception):", "    pass", "", "",
              "def validate_schema(doc):", '    """Make sure the required top-level keys exist."""', '    if "version" not in doc:',
              "        raise SchemaViolation(\"missing version\")", "    return True"]
    ps = [(320, ["", "", "class ChecksumMismatchError(Exception):", "    pass", "", "", "def validate_manifest(doc, digest):",
                 '    """Verify the digest recorded in the manifest."""', '    if doc.get("sha256") != digest:',
                 '        raise ChecksumMismatchError(doc.get("name"))', "    return True"])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("code-35525", sub="G1", task_type="lookup_value", desc="Python validators, checksum exception defined deep in the file",
         path="src/ingest/manifest_check.py", lines=lines,
         turns=[T("Which exception does validate_manifest raise in src/ingest/manifest_check.py when the checksum doesn't match?",
                  "ChecksumMismatchError", "raise ChecksumMismatchError(", "raise SchemaViolation(", excl=["SchemaViolation"])],
         notes=("The first screen has validate_schema raising SchemaViolation.", "read_file -> search_text 'validate_manifest' -> ChecksumMismatchError.",
                "validate_manifest is defined once."))


@reg
def k03():
    r = R("03")
    bl = fill.go_blocks(r, 70, avoid=("Inflight",))
    header = ["package queue", "", "import (", '\t"strings"', '\t"sync"', ")", "", "const defaultBatchSize = 32"]
    ps = [(310, ["", "// defaultMaxInflight bounds unacknowledged jobs per dispatcher.", "const defaultMaxInflight = 128"])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("code-35526", sub="G1", task_type="lookup_value", desc="Go dispatcher, max-inflight default deep in the file",
         path="internal/queue/dispatcher.go", lines=lines,
         turns=[T("What is the default max inflight value in internal/queue/dispatcher.go?", "128", "const defaultMaxInflight = 128",
                  "const defaultBatchSize = 32", excl=["defaultBatchSize = 32"])],
         notes=("The first screen has defaultBatchSize = 32, a nearby default.", "read_file -> search_text 'Inflight' -> 128.", "One defaultMaxInflight."))


@reg
def k04():
    r = R("04")
    bl = fill.go_blocks(r, 70, avoid=("purge", "janitor"))
    header = ["package auth", "", "import (", '\t"strings"', '\t"sync"', '\t"time"', ")", "", "const staleAfter = 30 * time.Minute", "",
              "func (c *tokenCache) evictOldest() {", "\tc.mu.Lock()", "\tdefer c.mu.Unlock()", "\tdelete(c.items, c.oldest)", "}"]
    ps = [(300, ["", "// purgeExpired drops entries whose ttl has passed.", "func (c *tokenCache) purgeExpired() {", "\tc.mu.Lock()",
                 "\tdefer c.mu.Unlock()", "\tfor k, it := range c.items {", "\t\tif it.expired() {", "\t\t\tdelete(c.items, k)", "\t\t}", "\t}", "}"]),
          (420, ["", "const janitorInterval = 90 * time.Second"])]
    lines = fill.compose(bl, ps, header=header, n=520)
    make("code-35527", sub="G1", task_type="lookup_value", desc="Go token cache, purge method and janitor interval deep in the file",
         path="pkg/auth/token_cache.go", lines=lines,
         turns=[T("Which method of tokenCache in pkg/auth/token_cache.go removes the expired entries?", "purgeExpired", "func (c *tokenCache) purgeExpired()",
                  "func (c *tokenCache) evictOldest()", excl=["evictOldest"]),
                T("And how often does the janitor run?", "90", "janitorInterval = 90 * time.Second", "staleAfter = 30 * time.Minute", excl=["30 min"])],
         notes=("The first screen has evictOldest and a 30-minute staleness constant.", "read_file -> search_text 'purge' -> purgeExpired; search_text 'janitor' -> 90s.",
                "Both definitions are unique."))


@reg
def k05():
    r = R("05")
    bl = fill.js_blocks(r, 70)
    header = ["// checkout flow helpers", "'use strict';", "", 'const GIFTCARD_FLAG = "ff_giftcard_redeem";']
    ps = [(300, ["", 'const EXPRESS_FLAG = "ff_express_checkout_v3";'])]
    lines = fill.compose(bl, ps, header=header, n=480)
    make("code-35528", sub="G1", task_type="lookup_value", desc="JS module, express checkout flag defined deep in the file",
         path="src/web/checkout-flow.js", lines=lines,
         turns=[T("What is the name of the feature flag that gates express checkout in src/web/checkout-flow.js?", "ff_express_checkout_v3",
                  'EXPRESS_FLAG = "ff_express_checkout_v3"', 'GIFTCARD_FLAG = "ff_giftcard_redeem"', excl=["ff_giftcard_redeem"])],
         notes=("The first screen declares the gift-card flag.", "read_file -> search_text 'FLAG' or 'express' -> ff_express_checkout_v3.", "One EXPRESS_FLAG."))


@reg
def k06():
    r = R("06")
    bl = fill.py_blocks(r, 70)
    header = ['"""风控规则引擎：按金额与设备特征给交易打分。"""', "", "import math", "", "LOW_RISK_AMOUNT = 500  # 低风险金额上限（元）"]
    ps = [(310, ["", "", "HIGH_RISK_AMOUNT = 20000  # 高风险金额阈值（元）"])]
    lines = fill.compose(bl, ps, header=header, n=500)
    make("code-35529", sub="G1", task_type="lookup_value", desc="风控规则引擎，高风险金额阈值在后部",
         path="src/风控/规则引擎.py", lines=lines,
         turns=[T("src/风控/规则引擎.py 里，单笔交易的 HIGH_RISK_AMOUNT 阈值是多少元？", ("any", ["20000", "20,000", "2万", "2 万"]),
                  "HIGH_RISK_AMOUNT = 20000", "LOW_RISK_AMOUNT = 500", excl=["LOW_RISK_AMOUNT = 500"])],
         notes=("文件开头定义了 LOW_RISK_AMOUNT = 500。", "read_file -> search_text 'HIGH_RISK' -> 20000。", "HIGH_RISK_AMOUNT 只定义一次。"))


@reg
def k07():
    r = R("07")
    bl = fill.js_blocks(r, 70)
    header = ["// 订单状态机", "'use strict';", "", "const AUTO_CANCEL_MINUTES = 30; // 未支付自动取消（分钟）"]
    ps = [(300, ["", "const AUTO_CONFIRM_HOURS = 168; // 发货后自动确认收货（小时）"])]
    lines = fill.compose(bl, ps, header=header, n=480)
    make("code-35530", sub="G1", task_type="lookup_value", desc="订单状态机，自动确认收货时长在后部",
         path="src/订单/状态机.js", lines=lines,
         turns=[T("src/订单/状态机.js 里，发货后多少小时会自动确认收货？", "168", "AUTO_CONFIRM_HOURS = 168", "AUTO_CANCEL_MINUTES = 30",
                  excl=["AUTO_CANCEL_MINUTES = 30"])],
         notes=("开头有未支付自动取消的 30 分钟常量。", "read_file -> search_text 'AUTO_CONFIRM' -> 168。", "常量只定义一次。"))
