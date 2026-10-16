"""31331-31340: config edits with a missing environment, service or value."""
from p2 import clarify, reg

W = ("list_files", "read_file", "write_file")


@reg
def c31331():
    files = {"config/dev.yaml": "service: web\ntimeout: 10\nretries: 2\n", "config/prod.yaml": "service: web\ntimeout: 10\nretries: 5\n"}
    clarify("cfg-31331", scen="cfg", task_type="edit_value", files=files, p1="把超时时间调大一点。", stems=["dev", "prod"], must=W,
            desc="Asks to raise a timeout without saying which environment or what value", ref="list_files config，看到 dev 和 prod 都有 timeout: 10，追问改哪个环境、改成多少。")


@reg
def c31332():
    files = {"config/gateway.yaml": "name: gateway\nport: 8080\nupstream: auth\n", "config/auth.yaml": "name: auth\nport: 8081\n", "README.md": "# 服务配置\n"}
    clarify("cfg-31332", scen="cfg", task_type="edit_value", files=files, p1="把端口改成 8443。", p2="网关的端口改，auth 不用动。", stems=["gateway", "auth"], must=W,
            rules={"config/gateway.yaml": ("sub", "port: 8080", "port: 8443")},
            desc="Asks to change a port to 8443 when two services each define a port", ref="两个服务都有 port，追问是哪一个；用户答网关后只改 gateway.yaml。")


@reg
def c31333():
    files = {"services/api.yaml": "log_level: info\nname: api\n", "services/worker.yaml": "log_level: info\nname: worker\n", "services/scheduler.yaml": "log_level: info\nname: scheduler\n"}
    clarify("cfg-31333", scen="cfg", task_type="edit_value", files=files, p1="Bump the log level to debug.", p2="Just the worker, please.", stems=["worker", "scheduler"], must=W,
            rules={"services/worker.yaml": ("sub", "log_level: info", "log_level: debug")},
            desc="Asks to set log level to debug with three services all at info", ref="三个服务都是 info，追问改哪一个或全部；用户答 worker，只改 worker.yaml。")


@reg
def c31334():
    files = {"config/prod.yaml": "db_host: db-old.internal\ndb_port: 5432\n", "config/staging.yaml": "db_host: db-stg.internal\ndb_port: 5432\n"}
    clarify("cfg-31334", scen="cfg", task_type="edit_value", files=files, p1="把数据库地址换成新的。", p2="新地址是 db-new.internal，只改 prod，staging 先不动。", stems=["prod", "staging"], must=W,
            rules={"config/prod.yaml": ("sub", "db_host: db-old.internal", "db_host: db-new.internal")},
            desc="Asks to switch the database host without giving the new address or the environment", ref="缺新地址与环境，两项都追问；补充后只改 prod.yaml 的 db_host。")


@reg
def c31335():
    files = {"clients/client-a.yaml": "name: A\nretry: 3\n", "clients/client-b.yaml": "name: B\nretry: 3\n"}
    clarify("cfg-31335", scen="cfg", task_type="edit_value", files=files, p1="Increase the retry count.", stems=["client-a", "client-b"], must=W,
            desc="Asks to increase retry count with two clients and no target value", ref="两个 client 都有 retry: 3，追问哪个客户端、增加到多少。")


@reg
def c31336():
    files = {"config/pool-dev.yaml": "max_connections: 20\n", "config/pool-prod.yaml": "max_connections: 100\n", "config/pool-test.yaml": "max_connections: 5\n"}
    clarify("cfg-31336", scen="cfg", task_type="edit_value", files=files, p1="把最大连接数改成 200。", stems=["pool-prod", "pool-dev"], must=W,
            desc="Asks to set max connections to 200 with dev, prod and test pool configs", ref="三份 pool 配置，追问改哪个（全部还是某个环境）。")


@reg
def c31337():
    files = {"config/web.yaml": "cache:\n  enabled: true\n  ttl: 300\n", "config/worker.yaml": "cache:\n  enabled: true\n  ttl: 60\n"}
    clarify("cfg-31337", scen="cfg", task_type="edit_value", files=files, p1="把缓存关掉。", p2="web 的缓存关，worker 的保留。", stems=["web", "worker"], must=W,
            rules={"config/web.yaml": ("sub", "enabled: true", "enabled: false")},
            desc="Asks to turn the cache off when both web and worker configs enable one", ref="两处都启用缓存，追问关哪一个；答复后只改 web.yaml。")


@reg
def c31338():
    files = {"deploy/staging.toml": "[http]\nread_timeout = 15\nwrite_timeout = 15\n", "deploy/prod.toml": "[http]\nread_timeout = 15\nwrite_timeout = 15\n"}
    clarify("cfg-31338", scen="cfg", task_type="edit_value", files=files, p1="Set the timeout to 30 seconds.", p2="Prod only, and just the read timeout.", stems=["staging", "prod"], must=W,
            rules={"deploy/prod.toml": ("sub", "read_timeout = 15", "read_timeout = 30")},
            desc="Asks to set timeout to 30 when two environments and two timeout keys exist", ref="环境与超时类型都不明；追问；补充后只改 prod.toml 的 read_timeout。")


@reg
def c31339():
    files = {"app/VERSION": "2.4.1\n", "docs/version.txt": "文档版本 2.4.0\n", "package.json": "{\"name\": \"demo\", \"version\": \"2.4.1\"}\n"}
    clarify("cfg-31339", scen="cfg", task_type="edit_value", files=files, p1="把版本号升一下。", stems=["VERSION", "package.json"], must=W,
            desc="Asks to bump the version with three places holding versions and no target", ref="三处版本号并不一致，追问升到多少、改哪几处。")


@reg
def c31340():
    files = {"config/mail.yaml": "admin_email: old-admin@example.com\nsmtp: mail.internal\n", "config/alerts.yaml": "admin_email: old-admin@example.com\nlevel: warn\n"}
    clarify("cfg-31340", scen="cfg", task_type="edit_value", files=files, p1="Change the admin email.", p2="Alerts only, use ops@example.com.", stems=["mail.yaml", "alerts.yaml"], must=W,
            rules={"config/alerts.yaml": ("sub", "admin_email: old-admin@example.com", "admin_email: ops@example.com")},
            desc="Asks to change the admin email without the new address, with two files holding it", ref="缺新邮箱，且两个文件都有；追问；补充后只改 alerts.yaml。")
