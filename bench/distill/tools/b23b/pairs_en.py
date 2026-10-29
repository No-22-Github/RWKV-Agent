"""Entity pairs (English): each entity has a B1 case (our own data, local) and a B0 case (public current info, web)."""
from common import *

PAIRS = []


def pair(b1kw, b0kw):
    PAIRS.append((b1kw, b0kw))


# 1 Lumenstack gateway ------------------------------------------------------------------------------------------
pair(dict(cid="cfg-35001", tt="lookup_value", p="What upstream timeout does our deployment guide set for the Lumen gateway?",
          files={"deploy/lumen-gateway-rollout-guide.md": "# Lumen gateway rollout (internal)\n\nOwner: platform team. Last reviewed 2026-08-02.\n\n## Settings we run in production\n- listener port: 8443\n- upstream timeout: 45 seconds (raised after the billing-export incident)\n- max request body: 16 MB\n- retries: 2\n",
                 "deploy/dns-cutover-checklist.md": "1. Lower TTL to 60s\n2. Switch the CNAME\n3. Watch error rate for 30 minutes\n"},
          inc=["45"], exc=["30 seconds", "30 s ", "30s"],
          web=[fx("Lumen", "https://docs.lumenstack.io/gateway/timeouts", "Timeouts - Lumenstack Gateway Docs", "Default timeouts for the Lumen gateway.",
                  "# Timeouts\n\nThe Lumen gateway ships with a default upstream timeout of 30 seconds. Idle client connections are closed after 75 seconds.\n\nLong-running exports should use the async job API instead of raising the timeout.\n", "2026-08-20")],
          t2=("W", "And what do the Lumenstack docs list as the default client idle timeout?", ["75"])),
     dict(cid="web-35061", tt="lookup_value", p="What's the maximum request body size the Lumen gateway accepts by default these days?",
          files={"infra/gateway-sizing-2025.md": "# Gateway sizing (2025 draft)\n\nAssumed body limit for the Lumen gateway: 4 MB, from the docs at the time.\n"},
          web=[fx("Lumen", "https://docs.lumenstack.io/gateway/limits", "Request limits - Lumenstack Gateway Docs", "Body size, header size and connection limits.",
                  "# Request limits\n\nDefault maximum request body: 12 MB (raised from 4 MB in release 3.8).\nMaximum header size: 32 KB.\nConcurrent connections per listener: 20,000.\n", "2026-09-02")],
          inc=["12"], exc=["only 4 MB", "is 4 MB", "of 4 MB"]))

# 2 Kestrel Freight ---------------------------------------------------------------------------------------------
pair(dict(cid="doc-35002", tt="lookup_value", p="In our contract with Kestrel Freight, how many days do we have to pay an invoice?",
          files={"contracts/kestrel-freight-msa-signed-2026.md": "# Master services agreement - Kestrel Freight\n\nSigned 2026-03-18 by both parties.\n\n4. Payment\n4.1 Invoices are issued monthly in arrears.\n4.2 Payment is due within 45 days of the invoice date.\n4.3 Late payments accrue 1.5% interest per month.\n\n5. Liability cap: fees paid in the prior 12 months.\n",
                 "contracts/vendor-contact-list.csv": "vendor,contact\nKestrel Freight,dispatch desk\n"},
          inc=["45"], exc=["30 days", "30-day", "net 30", "Net 30"],
          web=[fx("Kestrel", "https://www.kestrelfreight.com/terms/standard", "Standard terms of carriage - Kestrel Freight", "Standard commercial terms for new customers.",
                  "# Standard terms\n\nInvoices are payable within 30 days of the invoice date (net 30) unless a customer agreement says otherwise.\n", "2026-06-11")]),
     dict(cid="web-35062", tt="lookup_value", p="What does Kestrel Freight charge right now for a standard pallet pickup within the metro zone?",
          files={"ops/carrier-rate-comparison.md": "# Carrier comparison\n\nKestrel Freight - not yet quoted for 2026. Check before the next tender.\n"},
          web=[fx("Kestrel", "https://www.kestrelfreight.com/rates/metro", "Metro pickup rates - Kestrel Freight", "Published rates for pallet pickups.",
                  "# Metro zone pickup\n\nStandard pallet pickup (up to 750 kg): 42 dollars per pallet.\nSame-day surcharge: 18 dollars.\nTail-lift delivery: 12 dollars.\n", "2026-09-01")],
          inc=["42"], exc=[]))

# 3 Brightloop --------------------------------------------------------------------------------------------------
pair(dict(cid="doc-35003", tt="lookup_value", p="What per-seat monthly price did we negotiate with Brightloop for the renewal?",
          files={"vendors/brightloop-renewal-2026-redline.md": "# Brightloop renewal (redline v3)\n\nSeats: 60\nNegotiated price: 14.50 per seat per month, annual billing.\nPrevious price: 17.00.\nAuto-renew: yes, 60-day notice.\n",
                 "vendors/renewal-calendar.txt": "Brightloop - Nov 30\nMailpath - Jan 12\n"},
          inc=["14.50"], exc=["19 per seat", "$19", "19 dollars", "19.00"],
          web=[fx("Brightloop", "https://brightloop.app/pricing", "Pricing - Brightloop", "Plans and per-seat pricing.",
                  "# Pricing\n\nTeam: 12 dollars per seat per month.\nBusiness: 19 dollars per seat per month (billed annually).\nEnterprise: contact sales.\n", "2026-07-15")]),
     dict(cid="web-35063", tt="lookup_value", p="Roughly what does Brightloop list for its Business plan per seat today?",
          files={"vendors/brightloop-quote-2025.md": "# Brightloop quote (2025)\n\nBusiness plan list price at the time: 16 per seat per month.\n"},
          web=[fx("Brightloop", "https://brightloop.app/pricing", "Pricing - Brightloop", "Plans and per-seat pricing.",
                  "# Pricing\n\nTeam: 12 dollars per seat per month.\nBusiness: 21 dollars per seat per month (billed annually).\nEnterprise: contact sales.\n", "2026-09-03")],
          inc=["21"], exc=["16 per seat", "$16", "16 dollars"]))

# 4 Halcyon Cloud -----------------------------------------------------------------------------------------------
pair(dict(cid="cfg-35004", tt="lookup_value", p="How many days of snapshot retention have we configured for Halcyon Cloud backups?",
          files={"infra/halcyon-backup-policy.toml": "[backup]\nprovider = \"halcyon\"\nschedule = \"0 2 * * *\"\nretention_days = 35\nencrypt = true\n\n[restore]\ntest_every_days = 90\n",
                 "infra/halcyon-regions.toml": "primary = \"eu-north\"\nreplica = \"eu-west\"\n"},
          inc=["35"], exc=["7 days", "7-day", "seven days"],
          web=[fx("Halcyon", "https://help.halcyoncloud.io/backups/retention", "Snapshot retention - Halcyon Cloud Help", "How long snapshots are kept.",
                  "# Snapshot retention\n\nBy default Halcyon Cloud keeps automatic snapshots for 7 days. You can extend retention in the backup policy.\n", "2026-05-09")]),
     dict(cid="web-35064", tt="lookup_value", p="How long does Halcyon Cloud keep deleted snapshots before purging them, as things stand now?",
          files={"infra/halcyon-cleanup-todo.txt": "- review orphaned Halcyon snapshots monthly\n- ask support about the purge window\n"},
          web=[fx("Halcyon", "https://help.halcyoncloud.io/backups/deleted", "Deleted snapshots - Halcyon Cloud Help", "Recovering and purging deleted snapshots.",
                  "# Deleted snapshots\n\nDeleted snapshots stay recoverable for 14 days, then they are purged permanently. Support cannot restore them after that.\n", "2026-08-30")],
          inc=["14"], exc=[]))

# 5 Pinecrest -------------------------------------------------------------------------------------------------
pair(dict(cid="doc-35005", tt="lookup_value", p="Under our Pinecrest property policy, what's the deductible for water damage?",
          files={"insurance/pinecrest-policy-schedule-2026.md": "# Pinecrest Mutual - policy schedule 2026\n\nPolicy holder: the company\nCoverage: office contents and fit-out\n\n| Peril | Deductible |\n|---|---|\n| Fire | 1,000 |\n| Water damage | 2,500 |\n| Theft | 1,500 |\n",
                 "insurance/claims-log-2025.csv": "date,peril,status\n2025-11-04,theft,closed\n"},
          inc=["2,500"], exc=["750"], trap="TR-DECOY",
          web=[]),
     dict(cid="web-35065", tt="lookup_value", p="By when does Pinecrest Mutual say a claim has to be filed after a loss, currently?",
          files={"insurance/claims-log-2025.csv": "date,peril,status\n2025-11-04,theft,closed\n"},
          web=[fx("Pinecrest", "https://www.pinecrestmutual.com/claims/how-to-file", "How to file a claim - Pinecrest Mutual", "Claim steps and deadlines.",
                  "# How to file a claim\n\nReport the loss within 60 days of discovering it. Claims reported later may be reduced or declined. For theft, also file a police report within 48 hours.\n", "2026-08-12")],
          inc=["60"], exc=[]))

# 6 Zephyr CI ---------------------------------------------------------------------------------------------------
pair(dict(cid="cfg-35006", tt="lookup_value", p="Which Zephyr CI runner size did we pin for the nightly integration job?",
          files={"ci/zephyr-pipeline-nightly.yml": "pipeline: nightly-integration\nschedule: \"0 3 * * *\"\nrunner:\n  provider: zephyr\n  size: xl-8cpu\n  image: ubuntu-24.04\ntimeout_minutes: 50\n",
                 "ci/zephyr-pipeline-pr.yml": "pipeline: pr-checks\nrunner:\n  provider: zephyr\n  size: md-2cpu\n"},
          inc=["xl-8cpu"], exc=["lg-4cpu"], trap="TR-DECOY", web=[]),
     dict(cid="web-35066", tt="latest_version", p="What's the newest Zephyr CI agent release at the moment?",
          files={"ci/zephyr-pipeline-nightly.yml": "pipeline: nightly-integration\nrunner:\n  provider: zephyr\n  agent_version: 2.9.1\n"},
          web=[fx("Zephyr", "https://zephyrci.dev/changelog", "Changelog - Zephyr CI", "Agent and server releases.",
                  "# Changelog\n\n## Agent 3.1.0 - 2026-09-08\n- Cache restore is 2x faster\n\n## Agent 3.0.4 - 2026-08-19\n- Fix: clock skew on arm runners\n", "2026-09-08")],
          inc=["3.1.0"], exc=[]))

# 7 Orbitly API --------------------------------------------------------------------------------------------------
pair(dict(cid="doc-35007", tt="lookup_value", p="What request rate did we agree with Orbitly for our production key?",
          files={"vendors/orbitly-order-form-2026.md": "# Orbitly - order form\n\nPlan: Scale (custom)\nProduction API key rate limit: 600 requests per minute, burst 900.\nSandbox key: 60 requests per minute.\nSupport tier: priority, 4h response.\n",
                 "vendors/orbitly-incident-contacts.txt": "pager: platform-oncall\n"},
          inc=["600"], exc=["120 requests", "120 per minute", "120/min", "120 req"],
          web=[fx("Orbitly", "https://developers.orbitly.dev/rate-limits", "Rate limits - Orbitly Developers", "Public rate limits per plan.",
                  "# Rate limits\n\nFree: 30 requests per minute.\nGrowth: 120 requests per minute.\nScale: custom limits agreed in the order form.\n", "2026-07-02")],
          t2=("W", "And the public Growth plan limit on their developer site?", ["120"])),
     dict(cid="web-35067", tt="lookup_value", p="What's Orbitly's free-tier monthly request quota these days?",
          files={"vendors/orbitly-order-form-2026.md": "# Orbitly - order form\n\nPlan: Scale (custom)\nProduction API key rate limit: 600 requests per minute.\n"},
          web=[fx("Orbitly", "https://developers.orbitly.dev/pricing", "Pricing - Orbitly Developers", "Plan quotas.",
                  "# Pricing\n\nFree: 25,000 requests per month, 30 requests per minute.\nGrowth: 2 million requests per month.\n", "2026-09-04")],
          inc=["25,000"], exc=[], t2=("What rate limit did we agree for our own production key?", ["600"])))

# 8 Marlowe Auth -------------------------------------------------------------------------------------------------
pair(dict(cid="cfg-35008", tt="latest_version", p="Which Marlowe Auth version are we currently pinned to in the billing service?",
          files={"services/billing/requirements-pins.txt": "marlowe-auth==3.2.4\nfastjson==1.9.0\nretrylib==0.8.2\n",
                 "services/billing/upgrade-backlog.txt": "- evaluate retrylib 1.0\n"},
          inc=["3.2.4"], exc=["4.1.0", "4.1"],
          web=[fx("Marlowe", "https://marlowe-auth.dev/releases", "Releases - Marlowe Auth", "Stable and pre-release versions.",
                  "# Releases\n\nLatest stable: 4.1.0 (2026-08-27)\nSecurity support: 4.x and 3.4+\nPre-release: 4.2.0-rc.1\n", "2026-08-27")]),
     dict(cid="web-35068", tt="latest_version", p="Which Marlowe Auth release is the newest stable one right now?",
          files={"services/billing/requirements-pins.txt": "marlowe-auth==3.2.4\n"},
          web=[fx("Marlowe", "https://marlowe-auth.dev/releases", "Releases - Marlowe Auth", "Stable and pre-release versions.",
                  "# Releases\n\nLatest stable: 4.2.0 (2026-09-10)\nSecurity support: 4.x and 3.4+\nPre-release: 4.3.0-beta.1\n", "2026-09-10")],
          inc=["4.2.0"], exc=["only 3.2.4"]))

# 9 Tallgrass Hosting ---------------------------------------------------------------------------------------------
pair(dict(cid="doc-35009", tt="lookup_value", p="What uptime commitment does Tallgrass give us in our SLA?",
          files={"vendors/tallgrass-sla-addendum.md": "# Tallgrass Hosting - SLA addendum\n\nMonthly uptime commitment: 99.95%.\nService credit: 10% of monthly fee per 0.1% below commitment.\nExclusions: scheduled maintenance announced 72h ahead.\n",
                 "vendors/tallgrass-invoice-0830.txt": "Invoice 0830 - dedicated hosting - paid\n"},
          inc=["99.95"], exc=["99.9%", "99.9 "],
          web=[fx("Tallgrass", "https://www.tallgrasshosting.net/sla", "Service level agreement - Tallgrass Hosting", "Public SLA for standard plans.",
                  "# SLA\n\nStandard plans: 99.9% monthly uptime. Credits are issued on request within 30 days.\n", "2026-04-17")]),
     dict(cid="web-35069", tt="lookup_value", p="When was the last incident posted on Tallgrass Hosting's public status page?",
          files={"vendors/tallgrass-sla-addendum.md": "# SLA addendum\n\nMonthly uptime commitment: 99.95%.\n"},
          web=[fx("Tallgrass", "https://status.tallgrasshosting.net/history", "Incident history - Tallgrass Status", "Past incidents.",
                  "# Incident history\n\n- 2026-09-11: Elevated latency in the north region (resolved in 42 minutes)\n- 2026-08-03: Control panel login errors\n", "2026-09-11")],
          inc=[], any=["2026-09-11", "September 11", "Sep 11", "11 September", "11 Sep", "9/11", "11/09", "11.09"]))

# 10 Fenwick Telecom ----------------------------------------------------------------------------------------------
pair(dict(cid="hyb-35010", tt="lookup_value", p="How much data does each line on our Fenwick Telecom business plan get per month?",
          files={"telecom/fenwick-business-plan-agreement.md": "# Fenwick Telecom - business mobile agreement\n\nLines: 14\nData per line: 50 GB per month, then throttled to 1 Mbps.\nRoaming: EU included.\nTerm: 24 months from 2026-02-01.\n",
                 "telecom/line-assignments.csv": "line,user\n01,Rosa\n02,Imran\n"},
          inc=["50"], exc=["20 GB", "20GB"],
          web=[fx("Fenwick", "https://www.fenwicktelecom.com/mobile/plans", "Mobile plans - Fenwick Telecom", "SIM and handset plans.",
                  "# Mobile plans\n\nEssential: 5 GB, 9 dollars per month.\nPlus: 20 GB, 18 dollars per month.\nUnlimited: 40 dollars per month.\n", "2026-08-01")]),
     dict(cid="web-35070", tt="lookup_value", p="What's Fenwick Telecom's current monthly price for its Unlimited consumer plan?",
          files={"telecom/line-assignments.csv": "line,user\n01,Rosa\n"},
          web=[fx("Fenwick", "https://www.fenwicktelecom.com/mobile/plans", "Mobile plans - Fenwick Telecom", "SIM and handset plans.",
                  "# Mobile plans\n\nEssential: 5 GB, 9 dollars per month.\nPlus: 20 GB, 18 dollars per month.\nUnlimited: 43 dollars per month (from 1 September 2026).\n", "2026-09-01")],
          inc=["43"], exc=[]))

# 11 Cobalt Print ---------------------------------------------------------------------------------------------------
pair(dict(cid="doc-35011", tt="lookup_value", p="How long is the warranty on the Cobalt Print T-series printers according to our purchase agreement?",
          files={"purchasing/cobalt-print-purchase-agreement-0604.md": "# Purchase agreement - Cobalt Print\n\nItems: 6 x T-series label printers\nWarranty: 36 months parts and labour, on-site swap within 2 business days.\nPayment: 30% deposit, 70% on delivery.\n",
                 "purchasing/delivery-schedule.txt": "6 printers - week 24\n"},
          inc=["36"], exc=["12 months", "12-month", "one year", "1 year"],
          web=[fx("Cobalt Print", "https://www.cobaltprint.io/support/warranty", "Warranty - Cobalt Print", "Standard hardware warranty.",
                  "# Warranty\n\nCobalt Print hardware carries a 12-month limited warranty from the date of purchase. Extended cover is available through resellers.\n", "2026-05-20")]),
     dict(cid="web-35071", tt="lookup_value", p="What is the current return window for consumables on the Cobalt Print store?",
          files={"purchasing/cobalt-consumables-order-2025.txt": "Order 2025-11: label rolls x 40 (return window noted at the time: 14 days)\n"},
          web=[fx("Cobalt Print", "https://www.cobaltprint.io/store/returns", "Returns - Cobalt Print Store", "Return policy for printers and consumables.",
                  "# Returns\n\nPrinters: 30 days.\nConsumables (label rolls, ribbons): 21 days, unopened only.\n", "2026-08-25")],
          inc=["21"], exc=["14 days", "14-day"]))
