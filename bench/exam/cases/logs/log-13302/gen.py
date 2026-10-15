#!/usr/bin/env python3
"""Generates log-13302 (en, root cause of one failed request in a big gateway log)."""
import random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "gen"))
from _lib import finish, build_log, offsets, check_size, PREFIX

CANARY = "EXAM-CANARY-5d28b0f4"
rng = random.Random(13302)
SVCS = ["gateway", "auth-svc", "payments-svc", "ledger-svc", "refund-svc", "notify-svc", "kyc-svc", "fx-svc"]
MSGS = ["GET /v1/accounts 200 %dms", "POST /v1/transfers 202 %dms", "session validated in %dms", "rate table loaded rows=%d",
        "ledger batch committed size=%d", "webhook delivered in %dms", "heartbeat ok %dms"]
N = 1400
T = "req-b81e04"
sp = {}
base = int(N * 0.72)
sp[base] = ("gateway", "INFO", T, "accepted POST /v1/refunds")
sp[base + 9] = ("refund-svc", "INFO", T, "refund requested amount=84.20 currency=EUR")
sp[base + 15] = ("payments-svc", "WARN", T, "slow downstream call 2210ms (budget 2000ms)")
sp[base + 22] = ("ledger-svc", "ERROR", T, "deadlock detected on table postings, transaction aborted")
sp[base + 23] = ("refund-svc", "ERROR", T, "ledger call failed, giving up after 1 attempt")
sp[base + 24] = ("gateway", "ERROR", T, "502 Bad Gateway returned to client")
# other 502s earlier and later with different culprits
for idx, (svc, other) in {int(N*0.30): ("fx-svc", "req-c40a19"), int(N*0.55): ("kyc-svc", "req-0d93ee"), int(N*0.88): ("notify-svc", "req-77a1f2")}.items():
    sp[idx] = (svc, "ERROR", other, "connection refused by dependency")
    sp[idx + 1] = ("gateway", "ERROR", other, "502 Bad Gateway returned to client")
text = build_log(rng, "# gateway.log format=v2 host=gw-edge-01 date=2026-09-15", N, 8 * 3600, SVCS, MSGS, sp)
size = check_size(text, 80_000, 200_000)
assert min(offsets(text, "req=" + T + " ")) >= PREFIX
prompt = ("A customer says their refund of 84.20 EUR failed this morning. Support gave me the request id req-b81e04 and I've dropped "
          "the gateway log here as gateway.log. Which backend service was actually the source of the failure? Just the service name is fine.")
expect = {"output_contains_any": ["ledger-svc"], "output_contains_any_token": True}
finish(HERE, "log-13302", CANARY, "logs", "root_cause", ["TR-LONG", "TR-DECOY"],
       {"TR-LONG": "gateway", "TR-DECOY": "payments-svc"}, "L2", {"gateway.log": text}, prompt, expect,
       "Find the true failing backend for one request in a 100KB+ gateway log where the gateway reports a generic 502.",
       '''log = case["files"]["gateway.log"]
assert log.startswith("# gateway.log format=v2")
culprits = []
for ln in log.splitlines():
    m = re.search(r"\\[([a-z-]+)\\] ERROR req=req-b81e04 ", ln)
    if m and m.group(1) not in ("gateway", "refund-svc"):
        culprits.append(m.group(1))
assert len(culprits) == 1
print(json.dumps({"expected_contains_any": culprits}))''',
       '''## Traps
- TR-LONG: log is %d bytes; all req-b81e04 lines are after byte %d (> 65536).
- TR-DECOY: the gateway logs "502 Bad Gateway" for the request (and for three other requests whose culprits are fx-svc, kyc-svc, notify-svc). A WARN from payments-svc (slow call) is also on the target request but is not the failure. Answering "gateway" or "payments-svc" is wrong.
## Reference solution
1. grep `req-b81e04` in gateway.log. 2. Read the ERROR lines: the first non-gateway ERROR is ledger-svc (deadlock). refund-svc only reports that its call failed.
## Why the answer is unique
The only ERROR on the request that originates a fault (not a relay) is ledger-svc "deadlock detected"; refund-svc and gateway log consequences.''' % (size, min(offsets(text, "req=" + T + " "))))
print("ok", size)
