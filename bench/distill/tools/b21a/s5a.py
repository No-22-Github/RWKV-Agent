"""b21a sub 5 (format-fragile edits, verify after), cases 31058-31066."""
from common import L, make, RW, RL, RB, RLW, RA

B = []


def reg(f):
    B.append(f)
    return f


def chk(cid, files, ops, turns, policy, desc, trap, steps, unique, task_type="edit_value", traps=("TR-DECOY", "TR-CLAIM")):
    make(cid, sub="verify", task_type=task_type, desc=desc, files=files, turns=turns, ops=ops, policy=policy, traps=traps, axes=("OBS", "VER"),
         notes_ref={"traps": [trap], "steps": steps + ["read back the edited region and compare with the request"], "unique": unique}, ref_calls=5)


@reg
def v1():
    f = {"manifest.json": L("{", '  "name": "tidepool",', '  "version": "1.2.0",', '  "tags": ["music", "audio"],', '  "author": "Mara Ito"', "}")}
    chk("cfg-31058", f, [[("sub", "manifest.json", '  "author": "Mara Ito"\n', '  "author": "Mara Ito",\n  "license": "MIT"\n')]],
        [("manifest.json 最后加一个键 license，值 MIT。要保证改完还是合法的 JSON（逗号别漏）。改完读一遍确认，然后告诉我最后三行是什么。", ["license", "MIT", "Mara Ito"], None)], None,
        "Appends a last key to a JSON object, needing a comma on the former last line", "TR-CLAIM: forgetting the comma after author leaves invalid JSON.", ["read_lines", "replace last-but-one line with comma, add license line"], "File ends with author comma + license.")


@reg
def v2():
    f = {"deploy/service.yaml": L("service:", "  name: notifier", "  env:", "    - name: MODE", "      value: prod", "    - name: REGION", "      value: eu-west", "  ports:", "    - 9000")}
    new = "    - name: REGION\n      value: eu-west\n    - name: RETRIES\n      value: \"3\"\n"
    chk("cfg-31059", f, [[("sub", "deploy/service.yaml", "    - name: REGION\n      value: eu-west\n", new)]],
        [("In deploy/service.yaml, add one more env entry RETRIES with the string value \"3\" after REGION, same indentation style as the others. Read the file back to make sure the YAML still lines up, then show me the env section.", ["RETRIES", "REGION"], None)], None,
        "Adds a yaml list item with exact indentation", "TR-CLAIM: indentation of the inserted lines must match siblings.", ["read_lines", "insert after line 7"], "RETRIES entry follows REGION.")


@reg
def v3():
    f = {"docs/limits.md": L("# 限额", "", "| 套餐 | 并发 | 日调用 |", "| --- | --- | --- |", "| 免费 | 2 | 1000 |", "| 标准 | 10 | 50000 |", "| 旗舰 | 50 | 1000000 |")}
    chk("doc-31060", f, [[("sub", "docs/limits.md", "| 旗舰 | 50 | 1000000 |\n", "| 旗舰 | 50 | 1000000 |\n| 定制 | 200 | 5000000 |\n")]],
        [("限额表里再加一行：定制套餐，并发 200，日调用 5000000，列数和表头一致。加完读回来核对列数，再告诉我这张表现在有几行数据。", ["定制", "4"], None)], None,
        "Adds a markdown table row with the right column count", "TR-CLAIM: row must have three cells and keep the separator row.", ["read_file", "append row after line 7"], "Row added; 4 data rows.",
        task_type="write_structured")


@reg
def v4():
    f = {"data/contacts.csv": L("name,company,note", 'Ana Ruiz,Lumen,"likes tea, no sugar"', "Bo Chen,Harbor,new lead", 'Cy Dunn,Lumen,"call after 5, ask for Eve"')}
    chk("tab-31061", f, [[("sub", "data/contacts.csv", "Bo Chen,Harbor,new lead\n", 'Bo Chen,Harbor,"signed, pending invoice"\n')]],
        [("data/contacts.csv: Bo Chen 的备注改成 signed, pending invoice（这里有逗号，csv 里要加引号，跟别的行一样）。其他行不动。改完读回来确认，回复这一行。", ["signed, pending invoice"], None)], None,
        "Edits a csv note that contains a comma, requiring quotes", "TR-CLAIM: unquoted comma breaks the column count.", ["read_file", "replace line 3", "read back"], "Line 3 becomes quoted.",
        task_type="write_summary")


@reg
def v5():
    f = {"config/features.toml": L("[flags]", "beta_ui = true", "new_search = false", "", "[regions]", 'enabled = ["cn", "us", "jp"]', "default = \"cn\"")}
    chk("cfg-31062", f, [[("sub", "config/features.toml", '["cn", "us", "jp"]', '["cn", "us", "jp", "sg"]')], [("sub", "config/features.toml", "new_search = false", "new_search = true")]],
        [("config/features.toml 的启用地区列表加上 sg（保持数组写法，别丢引号和逗号）。", ["sg"], None), ("再把 new_search 打开，改完读一遍文件确认两处都对，告诉我最终的这两行。", ["new_search = true", '"sg"'], None)], RL,
        "Two turns: extends a toml array then flips a flag", "TR-CLAIM: array syntax; second edit is on a line above the first.", ["read_lines", "edit array", "edit flag", "read back"], "Array has sg and flag true.")


@reg
def v6():
    f = {"src/routes.py": L("ROUTES = {", "    '/': 'home',", "    '/about': 'about',", "    '/pricing': 'pricing'", "}", "", "DEFAULT = 'home'")}
    chk("code-31063", f, [[("sub", "src/routes.py", "    '/pricing': 'pricing'\n}", "    '/pricing': 'pricing',\n    '/blog': 'blog'\n}")]],
        [("Add a '/blog' route that maps to 'blog' in src/routes.py. It's a python dict, so mind the comma. Re-read it after the edit and confirm it would still parse, then show me the dict.", ["/blog", "pricing"], None)], None,
        "Adds a dict entry needing a comma on the previous line", "TR-CLAIM: previous entry has no trailing comma.", ["read_lines", "replace lines 4-4 with comma + new entry", "read back"], "Dict ends with pricing, then blog.", task_type="fix_edge_case")


@reg
def v7():
    f = {"charts/queue.yaml": L("queue:", "  name: mail", "  retry:", "    max: 3", "    backoff: 10", "  consumers: 2", "", "dead_letter:", "  enabled: true", "  retry:", "    max: 3", "    backoff: 10")}
    chk("cfg-31064", f, [[("sub", "charts/queue.yaml", "  retry:\n    max: 3\n    backoff: 10\n  consumers: 2\n", "  retry:\n    max: 5\n    backoff: 10\n    jitter: true\n  consumers: 2\n")],
                          [("sub", "charts/queue.yaml", "dead_letter:\n  enabled: true\n", "dead_letter:\n  enabled: false\n")]],
        [("队列 queue 的重试次数 max 改成 5，并在 backoff 下面加一行 jitter: true（缩进跟 backoff 一样）。dead_letter 那段先别碰。", ["jitter"], None),
         ("现在把 dead_letter 的 enabled 关掉。注意前面加了一行，行号变了，别改错位置。改完读回来核对，把整个文件的最终样子告诉我。", ["enabled: false", "jitter: true", "max: 5"], None)], RL,
        "Inserts a line then edits a later line whose number shifted", "TR-DECOY: line numbers drift by one after the first turn; retry blocks are duplicated.", ["read_lines", "replace 4-5", "re-read", "replace dead_letter enabled"], "queue retry 5+jitter, dead_letter disabled.")


@reg
def v8():
    f = {"table/prices.md": L("| 商品 | 单价 | 库存 |", "| --- | --- | --- |", "| 茶叶 | 38 | 120 |", "| 咖啡豆 | 66 | 80 |", "| 糖 | 9 | 300 |")}
    new = L("| 商品 | 单价 | 库存 | 备注 |", "| --- | --- | --- | --- |", "| 茶叶 | 38 | 120 | 新品 |", "| 咖啡豆 | 66 | 80 |  |", "| 糖 | 9 | 300 |  |")
    chk("doc-31065", f, [[("sub", "table/prices.md", f["table/prices.md"], new)]],
        [("table/prices.md 的表格最后加一列“备注”，茶叶那行写“新品”，其他行留空。每一行包括分隔行的列数都要一致，空单元格也要有竖线。改完读回来核对。", ["备注", "新品"], None)], RW,
        "Adds a table column to every row including the separator", "TR-CLAIM: every row needs 4 cells; empty cell format '|  |'.", ["read_file", "rewrite table", "read back"], "Equals exact table.", task_type="write_structured")


@reg
def v9():
    f = {"srv/upstream.conf": L("upstream api {", "    server 10.0.0.11:8000;", "    server 10.0.0.12:8000;", "}", "", "upstream web {", "    server 10.0.0.21:3000;", "    server 10.0.0.22:3000;", "}")}
    chk("cfg-31066", f, [[("sub", "srv/upstream.conf", "    server 10.0.0.12:8000;\n", "    server 10.0.0.12:8000;\n    server 10.0.0.13:8000 backup;\n")], [("sub", "srv/upstream.conf", "    server 10.0.0.22:3000;\n", "    server 10.0.0.22:3000 weight=2;\n")]],
        [("srv/upstream.conf 的 api 组里再加一台备用机：10.0.0.13:8000，后面写 backup，行尾要有分号，位置在现有两台后面。", ["10.0.0.13"], None),
         ("web 组里 10.0.0.22 的权重设成 2（写在地址后面、分号前面）。改完把整个文件读一遍，确认花括号和分号都没问题，告诉我最后的内容。", ["weight=2", "backup"], None)], None,
        "Inserts an upstream server then edits a later one in the second turn", "TR-DECOY: second edit sits below the inserted line.", ["read_lines", "insert after 3", "replace line 9"], "Two edits as expected.")
