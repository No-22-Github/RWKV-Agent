"""b23d D1 part c: 3-turn chains, ids 35225-35235."""
from common import mk, T, L

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c25():
    e, w = "inventory/warehouse-east.csv", "inventory/warehouse-west.csv"
    files = {e: L("sku,qty", "K-204,120", "K-310,75"), w: L("sku,qty", "K-204,55", "K-117,200")}
    mk("hyb-35225", sub="D1", tt="comp", trap="TR-MULTISRC", desc="Read stock in two warehouses, then transfer units between the files and report the unchanged total", files=files,
       turns=[T("How many units of SKU K-204 does the east warehouse hold?", inc=["120"]),
              T("And the west warehouse?", inc=["55"]),
              T("Move 40 units of K-204 from east to west by updating the two stock files. Give me the new counts and the combined total.", inc=["80", "95", "175"])],
       edits=[(e, "K-204,120", "K-204,80"), (w, "K-204,55", "K-204,95")], vals=["175"], must=["read_file", "replace_lines", "write_file", "calculator"], rc=6,
       dep="combined 120+55=175 from turns 1-2")


@reg
def c26():
    f = "配置/邮件模板-欢迎.txt"
    files = {f: L("标题：欢迎加入星河社区", "署名：星河运营组")}
    mk("hyb-35226", sub="D1", tt="undo", trap="TR-CLAIM", desc="Change a subject line, revert it, change the signature instead", files=files,
       turns=[T("欢迎邮件模板的标题是什么？文件在 配置 目录。", inc=["欢迎加入星河社区"]),
              T("标题改成“欢迎来到星河社区”。", inc=["欢迎来到星河社区"]),
              T("等等，标题其实要保持原样，撤回；改成把署名换成“星河社区团队”。告诉我现在两项分别是什么，以及标题原来是什么。", inc=["星河社区团队", "欢迎加入星河社区"])],
       edits=[(f, "署名：星河运营组", "署名：星河社区团队")], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c27():
    a, b = "src/ingest_worker.go", "src/export_job.go"
    files = {a: L("package main", "// TODO: handle partial batches", "func ingest() {}", "// TODO: add backpressure"), b: L("package main", "// TODO: paginate large exports", "func export() {}")}
    mk("hyb-35227", sub="D1", tt="comp", trap="TR-MULTISRC", desc="Count TODO comments in a folder, delete one, list what remains and the original count", files=files,
       turns=[T("How many TODO comments are there in src/?", inc=["3"]),
              T("Remove the one in export_job.go and tell me which one it was.", inc=["paginate"]),
              T("Which TODOs remain and in which files? And how many were there originally?", inc=["handle partial batches", "add backpressure", "ingest_worker.go", "3"])],
       edits=[(b, "// TODO: paginate large exports\n", "")], must=["search_text", "read_file", "replace_lines", "write_file"], rc=5, dep="original count 3")


@reg
def c28():
    f = "文档/报销单-10月.txt"
    files = {f: L("交通：320", "住宿：1450", "餐饮：610")}
    mk("hyb-35228", sub="D1", tt="comp", trap="TR-CLAIM", desc="Cap one expense, trim another, compare final total to the original", files=files,
       turns=[T("报销单-10月 里住宿是多少？", inc=["1450"]),
              T("住宿超标了，限额 1200，改成限额数，告诉我改后总额。", any=["2130", "2,130"]),
              T("再把餐饮砍到 500。告诉我最终总额，比最初少了多少。", inc=["2020", "360"])],
       edits=[(f, "住宿：1450", "住宿：1200"), (f, "餐饮：610", "餐饮：500")], vals=["2020", "360"], must=["read_file", "replace_lines", "write_file", "calculator"], rc=5,
       dep="original total 2380 from the fixture; difference 360")


@reg
def c29():
    n, out = "notes/standup-1007.txt", "notes/imani-actions.txt"
    files = {n: L("- rotate API keys (owner: Imani)", "- fix flaky test suite (owner: Wei)", "- update runbook (owner: Imani)")}
    mk("hyb-35229", sub="D1", tt="write", trap="TR-CLAIM", desc="Filter one owner's actions into a new file, remove one, recall the count before", files=files,
       turns=[T("Who owns the 'rotate API keys' action in notes/standup-1007.txt?", inc=["Imani"]),
              T("Create notes/imani-actions.txt listing only Imani's actions, one per line, exactly as written in the standup notes."),
              T("Imani finished the runbook. Remove that line from her file, then tell me who owns the flaky test item and how many items Imani had before.", inc=["Wei", "2"])],
       adds=[(out, "- rotate API keys (owner: Imani)\n")], exact=[out], must=["read_file", "write_file", "replace_lines", "search_text"], rc=5, dep="Imani had 2 items before")


@reg
def c30():
    f = "配置/小程序-功能开关.json"
    files = {f: '{\n  "beta_banner": true,\n  "dark_mode": false,\n  "lang_detect": true\n}\n'}
    mk("hyb-35230", sub="D1", tt="multi", trap="TR-CLAIM", desc="Flip a switch, user accepts, read back, flip another and recap originals", files=files,
       turns=[T("把 配置/小程序-功能开关.json 里的 dark_mode 打开。"),
              T("我接受了这次修改。再看一眼文件，三个开关现在各是什么状态？", inc=["beta_banner", "dark_mode", "lang_detect"], review="accept"),
              T("beta_banner 关掉，其他不动。然后告诉我今天动过哪两个开关、各自原来是什么状态。", inc=["beta_banner", "dark_mode"])],
       edits=[(f, '"dark_mode": false', '"dark_mode": true'), (f, '"beta_banner": true', '"beta_banner": false')], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c31():
    f = "deps/pins-ml-service.txt"
    files = {f: L("numpy==1.26.4", "pandas==2.1.0", "torch==2.2.1")}
    mk("hyb-35231", sub="D1", tt="undo", trap="TR-CLAIM", desc="Upgrade two pins, roll one back, then show a before/after table of all three", files=files,
       turns=[T("What version of pandas is pinned in deps/pins-ml-service.txt?", inc=["2.1.0"]),
              T("Upgrade pandas to 2.2.3 and torch to 2.3.0. Tell me the two new pins.", inc=["2.2.3", "2.3.0"]),
              T("Hold on, torch 2.3.0 breaks our CUDA image. Roll torch back, keep the pandas upgrade, and give me a before/after table for all three packages.", inc=["1.26.4", "2.1.0", "2.2.3", "2.2.1"])],
       edits=[(f, "pandas==2.1.0", "pandas==2.2.3")], vals=["2.3.0"], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c32():
    a, b = "文档/合同-甲.txt", "文档/合同-乙.txt"
    files = {a: L("合同编号：J-2210", "付款期限：30 天"), b: L("合同编号：Y-2214", "付款期限：45 天")}
    mk("hyb-35232", sub="D1", tt="comp", trap="TR-MULTISRC", desc="Compare payment terms of two contracts, align the longer one, recall both originals", files=files,
       turns=[T("合同-甲 的付款期限是多少天？", inc=["30"]),
              T("合同-乙呢？", inc=["45"]),
              T("把付款期限更长的那份改成和另一份一样，然后告诉我两份各自的原始期限。", inc=["30", "45"])],
       edits=[(b, "付款期限：45 天", "付款期限：30 天")], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c33():
    f = "conf/mailer.ini"
    files = {f: L("smtp_host = mail.brightpath.io", "smtp_port = 587", "smtp_tls = on")}
    mk("hyb-35233", sub="D1", tt="undo", trap="TR-CLAIM", desc="Two staged edits rejected, then only one redone; recall the dropped intention", files=files,
       turns=[T("Change smtp_port in conf/mailer.ini to 2525 and set smtp_tls to off."),
              T("I rejected those edits. Which smtp_port and smtp_tls values are in the file now?", inc=["587", "on"], review="reject"),
              T("OK, just change smtp_port to 2525 and leave TLS alone. Then tell me what TLS is set to, and what I first wanted it to be.", inc=["on", "off", "2525"])],
       edits=[(f, "smtp_port = 587", "smtp_port = 2525")], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c34():
    log, out = "日志/网关-1015.log", "日志/网关-1015-统计.txt"
    files = {log: L("09:00 INFO 启动", "09:03 ERROR 上游超时", "09:10 INFO 心跳", "09:12 WARN 连接池 80%", "09:20 ERROR 证书即将过期", "09:31 INFO 心跳", "09:45 WARN 磁盘 85%", "10:02 ERROR 上游超时", "10:15 INFO 心跳")}
    mk("hyb-35234", sub="D1", tt="write", trap="TR-CLAIM", desc="Count log levels, write counts to a file, update after a manual extra error and report the increase", files=files,
       turns=[T("日志/网关-1015.log 里 ERROR 和 WARN 各有几条？", inc=["3", "2"]),
              T("把统计结果写到 日志/网关-1015-统计.txt，两行，格式“ERROR: 数量”“WARN: 数量”。"),
              T("我手工又补了一条 ERROR 没写进日志，把统计文件更新一下。然后告诉我现在 ERROR 是几条，比日志里原来的多了几条。", inc=["4", "1"])],
       adds=[(out, L("ERROR: 4", "WARN: 2"))], exact=[out], must=["read_file", "write_file", "replace_lines", "search_text"], rc=5, dep="original ERROR count 3 from turn 1")


@reg
def c35():
    o, r, c = "docs/api-reference/orders.md", "docs/api-reference/refunds.md", "docs/api-reference/customers.md"
    files = {o: L("# Orders API", "POST /v1/orders creates an order.", "GET /v1/orders/{id} fetches one order."),
             r: L("# Refunds API", "Refunds hang off an order: POST /v1/orders/{id}/refunds"),
             c: L("# Customers API", "GET /v1/customers/{id} fetches one customer.")}
    mk("hyb-35235", sub="D1", tt="comp", trap="TR-MULTISRC", desc="Find files mentioning an endpoint, rewrite the mentions, verify nothing is left", files=files,
       turns=[T("Which files in docs/api-reference mention the /v1/orders endpoint?", inc=["orders.md", "refunds.md"]),
              T("We're moving to /v2/orders. Update every mention in those files and tell me how many lines you changed.", any=["3", "three"]),
              T("Check that nothing in docs still points at /v1/orders, and remind me which two files you touched.", inc=["orders.md", "refunds.md"])],
       edits=[(o, "POST /v1/orders creates", "POST /v2/orders creates"), (o, "GET /v1/orders/{id} fetches", "GET /v2/orders/{id} fetches"), (r, "POST /v1/orders/{id}/refunds", "POST /v2/orders/{id}/refunds")],
       must=["search_text", "read_file", "replace_lines", "write_file"], rc=8)
