"""b21a sub 1 (point edits), cases 31001-31010."""
from common import L, make, RW, RL, RB, RLW, RA

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c1():
    f = {"conf/nginx.conf": L("worker_processes 2;", "", "http {", "  server {", "    server_name www.lantern.example;", "    listen 8080;",
        "    client_max_body_size 10m;", "    location / { proxy_pass http://web_pool; }", "  }", "", "  server {", "    server_name api.lantern.example;",
        "    listen 8080;", "    client_max_body_size 10m;", "    location / { proxy_pass http://api_pool; }", "  }", "", "  server {",
        "    server_name admin.lantern.example;", "    listen 8081;", "    client_max_body_size 10m;", "  }", "}")}
    old = "    server_name api.lantern.example;\n    listen 8080;\n    client_max_body_size 10m;\n"
    make("cfg-31001", sub="point", task_type="edit_value", desc="Raises one server block's upload limit in a nginx config with three identical limits",
         files=f, turns=[("conf/nginx.conf 里 api.lantern.example 那个 server 的上传大小限制太小了，改成 50m，别的站点不要动。改完告诉我改的是第几行。", ["50m", "client_max_body_size"], None)],
         ops=[[("sub", "conf/nginx.conf", old, old.replace("10m", "50m"))]], policy=RL,
         notes_ref={"traps": ["TR-DECOY: three server blocks carry the identical client_max_body_size 10m line; only the api block changes."],
                    "steps": ["read_lines conf/nginx.conf to get numbered lines", "replace_lines on line 14 with the 50m line", "read back lines 12-15"],
                    "unique": "Only the api.lantern.example block's limit becomes 50m; expect.files equals pins the whole file."})


@reg
def c2():
    f = {"docker-compose.yml": L("services:", "  web:", "    image: registry.local/shop-web:1.4.2", "    ports:", '      - "8080:80"', "    environment:", "      LOG_LEVEL: info",
        "      CACHE_TTL: 60", "  worker:", "    image: registry.local/shop-worker:1.4.2", "    environment:", "      LOG_LEVEL: info", "      CACHE_TTL: 60",
        "  scheduler:", "    image: registry.local/shop-sched:1.4.2", "    environment:", "      LOG_LEVEL: info", "      CACHE_TTL: 60")}
    old = "  worker:\n    image: registry.local/shop-worker:1.4.2\n    environment:\n      LOG_LEVEL: info\n"
    make("cfg-31002", sub="point", task_type="edit_value", desc="Switches one compose service to debug logging while two others share the same line",
         files=f, turns=[("In docker-compose.yml, switch only the worker service to LOG_LEVEL debug. The web and scheduler services stay at info. Tell me which line you changed.", ["debug", "worker"], None)],
         ops=[[("sub", "docker-compose.yml", old, old.replace("info", "debug"))]], policy=None,
         notes_ref={"traps": ["TR-DECOY: LOG_LEVEL: info appears under three services."], "steps": ["read_file docker-compose.yml", "replace_lines on line 12", "read back"],
                    "unique": "Only the worker's LOG_LEVEL line changes to debug."})


@reg
def c3():
    f = {"settings.ini": L("[database]", "host = db01.internal", "port = 5432", "timeout = 30", "", "[cache]", "host = cache01.internal", "port = 6379", "timeout = 30", "",
        "[queue]", "host = mq01.internal", "port = 5672", "timeout = 30", "", "[mail]", "host = smtp.internal", "port = 25", "timeout = 30")}
    old = "[cache]\nhost = cache01.internal\nport = 6379\ntimeout = 30\n"
    make("cfg-31003", sub="point", task_type="edit_value", desc="Changes the timeout of one ini section where four sections share the same key",
         files=f, turns=[("settings.ini 里缓存（cache）段的超时时间改成 5，其他段的 timeout 都保持原样。改完把这一段贴给我看看。", ["timeout = 5", "[cache]"], None),
                         ("队列（queue）段的 timeout 也改成 15，同样只改那一段。改完两段的 timeout 都告诉我。", ["15", "5"], None)],
         ops=[[("sub", "settings.ini", old, old.replace("timeout = 30", "timeout = 5"))], [("sub", "settings.ini", "[queue]\nhost = mq01.internal\nport = 5672\ntimeout = 30\n", "[queue]\nhost = mq01.internal\nport = 5672\ntimeout = 15\n")]], policy=RW,
         notes_ref={"traps": ["TR-DECOY: timeout = 30 appears in four sections."], "steps": ["read_file settings.ini", "replace line 9", "read back the section"],
                    "unique": "Only [cache] timeout becomes 5."})


@reg
def c4():
    f = {"config/app.yaml": L("app:", "  name: ledger", "  mode: production", "database:", "  pool_size: 10", "  replica:", "    pool_size: 10", "    lag_alert_seconds: 30",
        "cache:", "  pool_size: 10", "  ttl_seconds: 300", "limits:", "  rate_per_minute: 120", "  burst: 20")}
    old = "  replica:\n    pool_size: 10\n"
    make("cfg-31004", sub="point", task_type="edit_value", desc="Edits a nested replica pool size among three same-valued pool_size keys",
         files=f, turns=[("config/app.yaml 里数据库只读副本（replica）的连接池大小改成 25。主库和缓存的 pool_size 不要变。完成后说明改了哪一行，行号是多少。", ["25"], None)],
         ops=[[("sub", "config/app.yaml", old, old.replace("10", "25"))]], policy=None,
         notes_ref={"traps": ["TR-DECOY: pool_size: 10 appears under database, database.replica and cache."], "steps": ["read_lines config/app.yaml", "replace_lines 7", "read back"],
                    "unique": "Only the replica pool_size is 25."})


@reg
def c5():
    f = {"README.md": L("# Hearth CLI", "", "## 安装", "", "```", "pip install hearth==2.3.1", "```", "", "## 升级", "", "旧版本用户请执行：", "", "```", "pip install hearth==2.3.1 --upgrade", "```", "",
        "## 兼容性", "", "当前稳定版 2.3.1，支持 Python 3.9 及以上。", "", "## 历史版本", "", "- 2.2.0：新增导出命令", "- 2.3.1：修复编码问题")}
    old1 = "```\npip install hearth==2.3.1\n```\n"
    make("doc-31005", sub="point", task_type="write_structured", desc="Updates the version in the install section of a README only, history stays",
         files=f, turns=[("README 里“安装”那一节的命令版本号从 2.3.1 更新到 2.4.0。升级一节、兼容性说明和历史版本列表保持原样，我之后再单独处理。改完告诉我改了哪一行。", ["2.4.0"], None),
                         ("好，现在升级一节里那条带 --upgrade 的命令也改成 2.4.0。兼容性和历史版本还是不动。改完告诉我 README 里现在还剩几处 2.3.1。", ["2", "2.4.0"], None)],
         ops=[[("sub", "README.md", old1, old1.replace("2.3.1", "2.4.0"))], [("sub", "README.md", "pip install hearth==2.3.1 --upgrade", "pip install hearth==2.4.0 --upgrade")]], policy=RLW,
         notes_ref={"traps": ["TR-DECOY: 2.3.1 appears four times; only the install command line changes."], "steps": ["read_lines README.md", "replace_lines 6", "read back"],
                    "unique": "Only line 6 becomes pip install hearth==2.4.0."})


@reg
def c6():
    f = {"src/settings.py": L("# runtime settings", "DEBUG = False", "ALLOWED_HOSTS = ['localhost']", "", "DATABASES = {", "    'default': {", "        'NAME': 'orders',", "        'TIMEOUT': 20,", "    },",
        "    'reports': {", "        'NAME': 'reports',", "        'TIMEOUT': 20,", "    },", "}", "", "HTTP_RETRY = {", "    'TIMEOUT': 20,", "    'MAX_TRIES': 3,", "}")}
    old = "        'NAME': 'reports',\n        'TIMEOUT': 20,\n"
    make("code-31006", sub="point", task_type="fix_edge_case", desc="Changes the reports database timeout in a settings module with three TIMEOUT: 20 entries",
         files=f, turns=[("The reports database in src/settings.py keeps timing out on big exports. Raise its TIMEOUT to 120, and leave the orders database and HTTP_RETRY as they are. Which lines did you change?", ["120"], None)],
         ops=[[("sub", "src/settings.py", old, old.replace("20", "120"))]], policy=RL,
         notes_ref={"traps": ["TR-DECOY: 'TIMEOUT': 20 appears three times."], "steps": ["read_lines src/settings.py", "replace_lines 12", "read back"],
                    "unique": "Only line 12 changes to 'TIMEOUT': 120,."})


@reg
def c7():
    f = {".env.production": L("# production env", "APP_ENV=production", "APP_PORT=3000", "DB_HOST=pg-prod-1", "DB_PORT=5432", "REDIS_HOST=redis-prod-1", "REDIS_PORT=6379",
        "MAIL_HOST=mail-prod-1", "MAIL_PORT=587", "SENTRY_SAMPLE_RATE=0.1", "TRACE_SAMPLE_RATE=0.1", "LOG_SAMPLE_RATE=0.1")}
    make("cfg-31007", sub="point", task_type="edit_value", desc="Changes one sample rate in an env file with three 0.1 rates",
         files=f, turns=[("线上 .env.production 里，链路追踪的采样率（TRACE_SAMPLE_RATE）调到 0.5。错误上报和日志的采样率不动。改完你再看一下确认没改错行，然后告诉我。", ["TRACE_SAMPLE_RATE=0.5"], None),
                         ("错误上报的采样率（SENTRY_SAMPLE_RATE）也调到 0.2，日志的不动。完成后告诉我三个采样率现在各是多少。", ["0.2", "0.5", "0.1"], None)],
         ops=[[("sub", ".env.production", "TRACE_SAMPLE_RATE=0.1\n", "TRACE_SAMPLE_RATE=0.5\n")], [("sub", ".env.production", "SENTRY_SAMPLE_RATE=0.1\n", "SENTRY_SAMPLE_RATE=0.2\n")]], policy=None,
         notes_ref={"traps": ["TR-DECOY: three *_SAMPLE_RATE=0.1 lines."], "steps": ["read_file", "replace line 11", "read back"], "unique": "Only TRACE_SAMPLE_RATE=0.5."})


@reg
def c8():
    f = {"pricing.md": L("# 价格表（2026 年）", "", "| 套餐 | 月付 | 年付 | 席位上限 |", "| --- | --- | --- | --- |", "| 基础版 | 49 | 490 | 5 |", "| 团队版 | 149 | 1490 | 25 |",
        "| 企业版 | 399 | 3990 | 200 |", "", "## 说明", "", "- 年付相当于月付 10 个月", "- 团队版席位上限 25，超出每席位 8 元/月", "- 企业版席位上限 200，超出请联系销售")}
    old = "| 团队版 | 149 | 1490 | 25 |\n"
    make("doc-31008", sub="point", task_type="write_structured", desc="Updates one row of a markdown price table, keeping column count and notes",
         files=f, turns=[("价格表里团队版月付涨到 169，年付按 10 个月算对应改掉，席位上限不变。说明里没提价格，不用动。改完告诉我这一行现在是什么。", ["169", "1690"], None),
                         ("企业版也涨：月付 429，年付同样按 10 个月算。表格列数别弄乱。改完把两行都告诉我。", ["429", "4290"], None)],
         ops=[[("sub", "pricing.md", old, "| 团队版 | 169 | 1690 | 25 |\n")], [("sub", "pricing.md", "| 企业版 | 399 | 3990 | 200 |\n", "| 企业版 | 429 | 4290 | 200 |\n")]], policy=RW,
         notes_ref={"traps": ["TR-DECOY: 25 appears in table and notes; the annual price must be recomputed 169*10=1690."], "steps": ["read_file", "replace row 6", "read back row"],
                    "unique": "Row becomes | 团队版 | 169 | 1690 | 25 |."})


@reg
def c9():
    f = {"deploy/cron.txt": L("# m h dom mon dow command", "0 2 * * * /opt/jobs/backup.sh --target nas", "30 2 * * * /opt/jobs/backup.sh --target s3", "0 3 * * 0 /opt/jobs/vacuum.sh",
        "15 4 * * * /opt/jobs/report.sh --daily", "15 4 * * 1 /opt/jobs/report.sh --weekly", "0 5 1 * * /opt/jobs/archive.sh")}
    make("fs-31009", sub="point", task_type="bulk_edit", desc="Moves one cron job time where two backup lines are near-identical",
         files=f, turns=[("deploy/cron.txt: the backup to s3 should run at 03:45 instead of 02:30. The nas backup must stay at 02:00. Tell me the final line for the s3 job.", ["45 3 * * *", "s3"], None)],
         ops=[[("sub", "deploy/cron.txt", "30 2 * * * /opt/jobs/backup.sh --target s3\n", "45 3 * * * /opt/jobs/backup.sh --target s3\n")]], policy=RB,
         notes_ref={"traps": ["TR-DECOY: two backup.sh lines differ only in time/target."], "steps": ["bash sed on the s3 line", "grep backup deploy/cron.txt"], "unique": "Only line 3 changes."})


@reg
def c10():
    f = {"package.json": L("{", '  "name": "lamp-ui",', '  "version": "0.8.3",', '  "scripts": {', '    "build": "vite build",', '    "test": "vitest run"', "  },", '  "dependencies": {',
        '    "react": "^18.2.0",', '    "react-dom": "^18.2.0"', "  },", '  "devDependencies": {', '    "vite": "^5.0.0",', '    "vitest": "^1.2.0"', "  }", "}")}
    make("cfg-31010", sub="point", task_type="edit_value", desc="Bumps one dependency range in package.json with look-alike react entries",
         files=f, turns=[("package.json 里把 vite 的版本范围改成 ^5.4.0，别的依赖和项目版本都不要变，注意别破坏 JSON 格式。改完告诉我改了哪一行。", ["^5.4.0"], None)],
         ops=[[("sub", "package.json", '"vite": "^5.0.0"', '"vite": "^5.4.0"')]], policy=None,
         notes_ref={"traps": ["TR-DECOY: ^5.0.0 style ranges and vitest next to vite."], "steps": ["read_file", "replace line 13", "read back"], "unique": "Only the vite range changes."})
