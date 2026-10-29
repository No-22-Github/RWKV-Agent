"""35101-35116 (C1) and 35151-35156 (C0): config edits."""
from common import c1, c0

BUILDERS = []


def reg(f):
    BUILDERS.append(f)
    return f


@reg
def cfg_35101():
    files = {"config/staging.yaml": "service: checkout\ntimeout: 20\nretries: 2\n", "config/production.yaml": "service: checkout\ntimeout: 20\nretries: 4\n"}
    c1("cfg-35101", tt="edit_value", files=files, p1="Set the request timeout to 45 seconds.", stem="staging",
       desc="Asks for a 45 second timeout while staging and production configs both hold one", ref="list_files config, read both; ask whether staging, production or both.")


@reg
def cfg_35102():
    files = {"services/order-svc.toml": "name = \"order\"\npool_size = 20\n", "services/billing-svc.toml": "name = \"billing\"\npool_size = 20\n",
             "services/gateway.toml": "name = \"gateway\"\nlisten = \":8080\"\n"}
    c1("cfg-35102", tt="edit_value", files=files, p1="把数据库连接池大小调成 50。", stem="order-svc",
       desc="Asks to set the pool size to 50 with two services defining pool_size", ref="读三个服务配置，order 和 billing 都有 pool_size，追问改哪个。")


@reg
def cfg_35103():
    files = {"config/mailer.ini": "[smtp]\nhost = smtp-eu1.corpmail.net\nport = 587\nsender = noreply@harborline.io\n"}
    c1("cfg-35103", tt="edit_value", files=files, p1="Point the mail service at the new SMTP host.", stem="smtp-eu1",
       desc="Asks to switch the SMTP host without giving the new host", ref="read mailer.ini, see the current host, ask for the new hostname.")


@reg
def cfg_35104():
    files = {"team/owners.yaml": "payments: Lena Fischer\nsearch: Omar Haddad\nnotifications: Priya Raman\n"}
    c1("cfg-35104", tt="edit_value", files=files, p1="把负责人换成新来的同事。", stem="owners",
       desc="Asks to replace an owner with a new colleague without naming who or which team", ref="读 owners.yaml，三个团队，新同事姓名未知，追问哪个团队、换成谁。")


@reg
def cfg_35105():
    files = {"app/web.env": "LOG_LEVEL=info\nPORT=3000\n", "app/worker.env": "LOG_LEVEL=info\nQUEUE=default\n", "app/cron.env": "LOG_LEVEL=warn\nTZ=UTC\n"}
    c1("cfg-35105", tt="edit_value", files=files, p1="Turn on debug logging.", stem="worker",
       desc="Asks to turn on debug logging with three env files each holding a log level", ref="read the three env files; ask which service(s).")


@reg
def cfg_35106():
    files = {"nginx/site-a.conf": "server {\n  server_name a.lumenbridge.cn;\n  client_max_body_size 5m;\n}\n",
             "nginx/site-b.conf": "server {\n  server_name b.lumenbridge.cn;\n  client_max_body_size 5m;\n}\n",
             "nginx/admin.conf": "server {\n  server_name admin.lumenbridge.cn;\n  client_max_body_size 1m;\n}\n"}
    c1("cfg-35106", tt="edit_value", files=files, p1="把最大上传大小改成 20MB。", stem="site-a",
       desc="Asks for a 20MB upload limit with three nginx server blocks defining one", ref="读三份 nginx 配置，都有上限，追问改哪个站点。")


@reg
def cfg_35107():
    files = {"config/client.json": "{\n  \"base_url\": \"https://api.northwind-data.io/v2\",\n  \"timeout_ms\": 8000\n}\n",
             "config/mobile.json": "{\n  \"base_url\": \"https://api.northwind-data.io/v2\",\n  \"timeout_ms\": 12000\n}\n"}
    c1("cfg-35107", tt="edit_value", files=files, p1="Switch the API base URL over to v3.", stem="mobile",
       desc="Asks to move the API base URL to v3 while web client and mobile configs both hold it", ref="read both json files; ask which client config(s).")


@reg
def cfg_35108():
    files = {"backup/nightly.yaml": "job: nightly\nretention_days: 7\n", "backup/weekly.yaml": "job: weekly\nretention_days: 28\n",
             "backup/archive.yaml": "job: archive\nkeep_days: 365\n"}
    c1("cfg-35108", tt="edit_value", files=files, p1="把备份保留天数改成 14 天。", stem="nightly",
       desc="Asks for a 14 day backup retention while nightly and weekly jobs each have one", ref="读三份备份配置，追问是 nightly、weekly 还是 archive。")


@reg
def cfg_35109():
    files = {"config/regions.yaml": "default_region: eu-west-2\nenabled:\n  - eu-west-2\n  - us-east-1\n"}
    c1("cfg-35109", tt="edit_value", files=files, p1="Change the default region to the new one we're launching in.", stem="eu-west-2",
       desc="Asks to change the default region to an unnamed new one", ref="read regions.yaml; the new region is not in the workspace, ask for its name.")


@reg
def cfg_35110():
    files = {"config/edge-cache.yaml": "layer: edge\nttl: 300\n", "config/api-cache.yaml": "layer: api\nttl: 120\n"}
    c1("cfg-35110", tt="edit_value", files=files, p1="Increase the cache TTL to 600.", p2="The API one.", stem="api-cache",
       rules={"config/api-cache.yaml": ("sub", "ttl: 120", "ttl: 600")}, req2=None,
       desc="Asks for TTL 600 while edge and API caches both define a TTL; the answer picks the API cache", ref="ask which cache; after the answer change only api-cache.yaml.")


@reg
def cfg_35111():
    files = {"monitoring/cpu-alert.yaml": "metric: cpu\nthreshold: 80\n", "monitoring/mem-alert.yaml": "metric: memory\nthreshold: 85\n",
             "monitoring/disk-alert.yaml": "metric: disk\nthreshold: 75\n"}
    c1("cfg-35111", tt="edit_value", files=files, p1="把告警阈值调到 90%。", p2="CPU 的改，内存和磁盘别动。", stem="cpu-alert",
       rules={"monitoring/cpu-alert.yaml": ("sub", "threshold: 80", "threshold: 90")},
       desc="Asks to set an alert threshold to 90 with three alert files; the answer picks CPU", ref="追问哪个告警；答复后只改 cpu-alert.yaml。")


@reg
def cfg_35112():
    files = {"cron/jobs.yaml": "jobs:\n  - name: billing-export\n    owner: dmitri.v\n    schedule: \"0 2 * * *\"\n  - name: log-rotate\n    owner: sana.k\n    schedule: \"0 4 * * 0\"\n"}
    c1("cfg-35112", tt="edit_value", files=files, p1="Update the owner of the billing job to the new hire.", p2="Her handle is tamsin.o, same format as the others.", stem="dmitri.v",
       rules={"cron/jobs.yaml": ("sub", "owner: dmitri.v", "owner: tamsin.o")},
       desc="Asks to hand the billing job to an unnamed new hire; turn 2 gives the handle", ref="read jobs.yaml; ask for the new hire's handle; then edit one line.")


@reg
def cfg_35113():
    files = {"config/primary.env": "DB_HOST=10.20.4.11\nDB_PORT=5432\n", "config/replica.env": "DB_HOST=10.20.4.12\nDB_PORT=5432\n"}
    c1("cfg-35113", tt="edit_value", files=files, p1="把数据库主机换成新地址。", p2="主库的，新地址 10.20.9.30，从库先不动。", stem="replica",
       rules={"config/primary.env": ("sub", "DB_HOST=10.20.4.11", "DB_HOST=10.20.9.30")},
       desc="Asks to swap the database host without the new address or which of primary and replica", ref="追问新地址与主/从；答复后只改 primary.env。")


@reg
def cfg_35114():
    files = {"limits/public-api.yaml": "name: public\nrpm: 300\n", "limits/partner-api.yaml": "name: partner\nrpm: 600\n"}
    c1("cfg-35114", tt="edit_value", files=files, p1="Lower the rate limit to 100 requests per minute.", p2="Public API only.", stem="partner",
       rules={"limits/public-api.yaml": ("sub", "rpm: 300", "rpm: 100")},
       desc="Asks to lower a rate limit while public and partner API each have one", ref="ask which API; then change public-api.yaml only.")


@reg
def cfg_35115():
    files = {"auth/web-session.yaml": "kind: web\nttl_minutes: 30\n", "auth/admin-session.yaml": "kind: admin\nttl_minutes: 15\n",
             "auth/api-token.yaml": "kind: api\nttl_minutes: 1440\n"}
    c1("cfg-35115", tt="edit_value", files=files, p1="把会话过期时间改成 2 小时。", p2="只改 web 的，注意单位是分钟。", stem="admin-session",
       rules={"auth/web-session.yaml": ("sub", "ttl_minutes: 30", "ttl_minutes: 120")},
       desc="Asks for a 2 hour session expiry with web, admin and API session files", ref="追问改哪一类会话；答复后 web-session 改成 120。")


@reg
def cfg_35116():
    files = {"flags/rollout.yaml": "new_checkout:\n  rollout_percent: 10\nsearch_v2:\n  rollout_percent: 50\n"}
    c1("cfg-35116", tt="edit_value", files=files, p1="Set the feature flag rollout to the percentage we agreed on.", p2="Sorry, 35 percent, for new_checkout.", stem="new_checkout",
       rules={"flags/rollout.yaml": ("sub", "new_checkout:\n  rollout_percent: 10", "new_checkout:\n  rollout_percent: 35")},
       desc="Asks to set a flag rollout to an agreed but unstated percentage", ref="ask which flag and what percentage; then edit one value.")


# ---- C0 ----
@reg
def cfg_35151():
    files = {"config/staging.yaml": "service: payments\ntimeout: 15\n", "config/production.yaml": "service: payments\ntimeout: 15\n"}
    c0("cfg-35151", tt="edit_value", files=files, prompts=["Set the timeout in the staging config to 40 seconds."], decoy=True,
       rules={"config/staging.yaml": ("sub", "timeout: 15", "timeout: 40")},
       desc="Names staging explicitly, production must stay", ref="read staging.yaml, replace the value.")


@reg
def cfg_35152():
    files = {"services/search-svc.toml": "name = \"search\"\npool_size = 20\n", "services/gateway.toml": "name = \"gateway\"\nlisten = \":8080\"\n"}
    c0("cfg-35152", tt="edit_value", files=files, prompts=["把数据库连接池大小调成 50。"],
       rules={"services/search-svc.toml": ("sub", "pool_size = 20", "pool_size = 50")},
       desc="Only one service defines a pool size", ref="只有 search-svc 有 pool_size，直接改。")


@reg
def cfg_35153():
    files = {"config/mailer.ini": "[smtp]\nhost = smtp-eu1.corpmail.net\nport = 587\n"}
    c0("cfg-35153", tt="edit_value", files=files, prompts=["Switch the SMTP host to smtp-eu2.corpmail.net."],
       rules={"config/mailer.ini": ("sub", "smtp-eu1.corpmail.net", "smtp-eu2.corpmail.net")},
       desc="Gives the new SMTP host explicitly", ref="edit the single host line.")


@reg
def cfg_35154():
    files = {"app/web.env": "LOG_LEVEL=info\nPORT=3000\n", "app/worker.env": "LOG_LEVEL=info\nQUEUE=default\n", "app/cron.env": "LOG_LEVEL=warn\nTZ=UTC\n"}
    c0("cfg-35154", tt="edit_value", files=files, prompts=["把 worker 的日志级别改成 debug，其他服务不动。"], decoy=True,
       rules={"app/worker.env": ("sub", "LOG_LEVEL=info", "LOG_LEVEL=debug")},
       desc="Names the worker explicitly among three env files", ref="只改 worker.env。")


@reg
def cfg_35155():
    files = {"cron/jobs.yaml": "jobs:\n  - name: billing-export\n    owner: dmitri.v\n    schedule: \"0 2 * * *\"\n  - name: log-rotate\n    owner: sana.k\n    schedule: \"0 4 * * 0\"\n"}
    c0("cfg-35155", tt="edit_value", files=files,
       prompts=["Change the owner of the billing-export job to ines.duarte.", "Also move its schedule to 03:30 every day."], decoy=True,
       rules={"cron/jobs.yaml": ("sub", "owner: dmitri.v\n    schedule: \"0 2 * * *\"", "owner: ines.duarte\n    schedule: \"30 3 * * *\"")},
       desc="Two explicit edits to one job over two turns", ref="turn 1 edit owner line; turn 2 edit the cron line of the same job.")


@reg
def cfg_35156():
    files = {"services/auth.toml": "timeout = 10\n", "services/orders.toml": "timeout = 10\n", "services/search.toml": "timeout = 10\n"}
    c0("cfg-35156", tt="edit_value", files=files, prompts=["把所有服务的 timeout 都改成 30。"],
       rules={"services/auth.toml": ("sub", "timeout = 10", "timeout = 30"), "services/orders.toml": ("sub", "timeout = 10", "timeout = 30"),
              "services/search.toml": ("sub", "timeout = 10", "timeout = 30")},
       desc="Explicitly asks for every service to change", ref="三个文件都改成 30。")
