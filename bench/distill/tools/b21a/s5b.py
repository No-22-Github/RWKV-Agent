"""b21a sub 5 (format-fragile edits, verify after), cases 31067-31075."""
from common import L, make, RW, RL, RB, RLW, RA
from s5a import chk

B = []


def reg(f):
    B.append(f)
    return f


@reg
def w1():
    f = {"data/menu.json": L("[", '  {"id": 1, "name": "豆浆", "price": 3},', '  {"id": 2, "name": "油条", "price": 2},', '  {"id": 3, "name": "粢饭", "price": 5}', "]")}
    chk("cfg-31067", f, [[("sub", "data/menu.json", '  {"id": 3, "name": "粢饭", "price": 5}\n', '  {"id": 3, "name": "粢饭", "price": 5},\n  {"id": 4, "name": "茶叶蛋", "price": 2}\n')], [("sub", "data/menu.json", '"name": "豆浆", "price": 3', '"name": "豆浆", "price": 4')]],
        [("data/menu.json 的菜单最后加一项：id 4，茶叶蛋，价格 2。保持 JSON 数组合法。", ["茶叶蛋"], None), ("豆浆涨价到 4。改完把整个文件读一遍，确认 JSON 合法、没有改到别的价格，然后告诉我最终每项的价格。", ["4", "茶叶蛋", "粢饭"], None)], None,
        "Appends a JSON array element then reprices an earlier one", "TR-CLAIM: comma after the former last element; price 2 occurs for two items.", ["read_lines", "edit line 4 + insert", "edit line 2", "read back"], "Final array has 4 items, 豆浆 4.")


@reg
def w2():
    f = {"docs/faq.yaml": L("faq:", "  - q: 如何重置密码？", "    a: |", "      在登录页点击“忘记密码”，", "      按邮件提示操作。", "  - q: 如何导出数据？", "    a: 设置里点击导出。")}
    chk("doc-31068", f, [[("sub", "docs/faq.yaml", "      按邮件提示操作。\n", "      按邮件提示操作。\n      链接 30 分钟内有效。\n")], [("sub", "docs/faq.yaml", "    a: 设置里点击导出。\n", "    a: 设置里点击导出，支持 CSV 和 JSON。\n")]],
        [("FAQ 里“如何重置密码”的回答再加一行“链接 30 分钟内有效。”，缩进和上面两行一致。", ["30 分钟"], None), ("“如何导出数据”的回答改成“设置里点击导出，支持 CSV 和 JSON。”。改完读回文件，确认缩进没乱，把两条回答都告诉我。", ["CSV 和 JSON", "30 分钟"], None)], RL,
        "Extends a yaml block scalar then edits a later plain scalar", "TR-CLAIM: block scalar lines need the same 6-space indent.", ["read_lines", "insert after 5", "replace line 8", "read back"], "Block scalar has 3 lines.", task_type="write_structured")


@reg
def w3():
    f = {"tools/clean.sh": L("#!/bin/sh", "set -e", "TARGET=/var/cache/app", "for f in $TARGET/*.tmp; do", "  rm -f \"$f\"", "done", "echo cleaned")}
    chk("code-31069", f, [[("sub", "tools/clean.sh", "echo cleaned\n", 'echo "cleaned $TARGET"\n')], [("sub", "tools/clean.sh", "*.tmp", "*.cache")]],
        [("Update tools/clean.sh so the last line prints the target dir too: echo \"cleaned $TARGET\" (double quotes, variable kept literal in the file).", ["cleaned $TARGET"], None),
         ("Also make the loop remove *.cache files instead of *.tmp. Re-read the script afterwards to check the loop is intact, and show me the final script.", ["*.cache", "done"], None)], RB,
        "Edits a shell script twice keeping quoting and loop syntax", "TR-CLAIM: $ must survive; only the glob changes in turn 2.", ["read_file", "edit last line", "edit glob", "cat script"], "Final script as expected.", task_type="fix_edge_case")


@reg
def w4():
    f = {"net/wg.ini": L("[Interface]", "Address = 10.8.0.2/24", "DNS = 1.1.1.1", "", "[Peer]", "Endpoint = vpn.orchid.example:51820", "AllowedIPs = 10.8.0.0/24", "PersistentKeepalive = 25")}
    chk("cfg-31070", f, [[("sub", "net/wg.ini", "AllowedIPs = 10.8.0.0/24\n", "AllowedIPs = 10.8.0.0/24, 192.168.50.0/24\n")], [("sub", "net/wg.ini", "DNS = 1.1.1.1\n", "DNS = 10.8.0.1\n")]],
        [("net/wg.ini 的 AllowedIPs 追加一个网段 192.168.50.0/24，用逗号加空格接在后面。", ["192.168.50.0/24"], None), ("再把 DNS 换成 10.8.0.1。然后读回文件确认两处都对，告诉我这两行现在的样子。", ["10.8.0.1", "192.168.50.0/24"], None)], None,
        "Extends a comma list value then replaces the DNS line", "TR-CLAIM: list separator format and exact single-line replacement.", ["read_lines", "edit line 7", "edit line 3", "read back"], "AllowedIPs two ranges, DNS 10.8.0.1.")


@reg
def w5():
    f = {"plan/checklist.md": L("# 上线检查清单", "", "- [x] 数据库备份", "- [x] 灰度配置", "- [ ] 通知客服", "- [ ] 关闭旧入口", "- [ ] 更新状态页")}
    chk("doc-31071", f, [[("sub", "plan/checklist.md", "- [ ] 通知客服\n", "- [x] 通知客服\n")], [("sub", "plan/checklist.md", "- [ ] 更新状态页\n", "- [x] 更新状态页\n- [ ] 复盘会议\n")]],
        [("清单里“通知客服”做完了，帮我打上勾，别的不动。", ["通知客服"], None), ("“更新状态页”也做完了，打勾；然后在清单最后加一项未完成的“复盘会议”。改完读回来告诉我还剩几项没完成。", ["复盘会议", "2"], None)], None,
        "Ticks checklist boxes and appends a new open item", "TR-DECOY: bracket syntax must be exactly [x] and [ ].", ["read_file", "toggle line 5", "toggle line 7 and add line", "read back"], "Two unchecked: 关闭旧入口, 复盘会议.", task_type="write_structured")


@reg
def w6():
    f = {"data/stock.csv": L("sku,name,qty,loc", "A-100,螺丝 M3,500,仓1", "A-101,螺丝 M4,350,仓1", "B-200,垫片,1200,仓2", "B-201,螺母 M3,0,仓2")}
    chk("tab-31072", f, [[("sub", "data/stock.csv", "B-201,螺母 M3,0,仓2\n", "B-201,螺母 M3,800,仓2\n")], [("sub", "data/stock.csv", "A-101,螺丝 M4,350,仓1\n", "A-101,螺丝 M4,350,仓3\n")]],
        [("螺母 M3（B-201）到货了，库存改成 800。csv 其他行不动。", ["800"], None), ("螺丝 M4 搬到仓3了，改它的仓位那一列，数量不变。改完把文件读回来检查列没错位，把这两行贴给我。", ["仓3", "800", "A-101"], None)], None,
        "Edits qty then location columns of different csv rows", "TR-DECOY: columns shift easily; qty vs loc.", ["read_file", "replace line 5", "replace line 3", "read back"], "Two rows changed.", task_type="write_summary")


@reg
def w7():
    f = {"index.html": L("<ul class=\"nav\">", "  <li><a href=\"/\">首页</a></li>", "  <li><a href=\"/docs\">文档</a></li>", "  <li><a href=\"/blog\">博客</a></li>", "</ul>")}
    chk("doc-31073", f, [[("sub", "index.html", "  <li><a href=\"/docs\">文档</a></li>\n", "  <li><a href=\"/docs\">文档</a></li>\n  <li><a href=\"/pricing\">定价</a></li>\n")], [("sub", "index.html", "<a href=\"/blog\">博客</a>", "<a href=\"/news\">动态</a>")]],
        [("index.html 导航里在“文档”后面插入“定价”，链接 /pricing，写法和别的项一致。", ["定价"], None), ("再把“博客”改成“动态”，链接改成 /news。改完读回来检查标签都闭合了，告诉我导航现在的四项。", ["动态", "定价", "/news"], None)], RW,
        "Inserts an html list item then rewrites another's text and href", "TR-CLAIM: tags must stay closed.", ["read_lines", "insert after 3", "replace line 5", "read back"], "Nav has four items.", task_type="write_structured")


@reg
def w8():
    f = {"src/discount.py": L("def discount(total, vip):", "    rate = 0.1 if vip else 0.0", "    if total > 1000:", "        rate += 0.05", "    return round(total * (1 - rate), 2)")}
    chk("code-31074", f, [[("sub", "src/discount.py", "total > 1000:", "total >= 1000:")], [("sub", "src/discount.py", "rate = 0.1 if vip", "rate = 0.15 if vip")]],
        [("In src/discount.py the threshold check should be >= 1000, not > 1000 (an order of exactly 1000 gets the extra 5%). Fix just that.", [">= 1000"], None),
         ("Then raise the VIP rate from 0.1 to 0.15. Read the function back afterwards to make sure the indentation is still right and tell me what the final function looks like.", ["0.15", ">= 1000"], None)], None,
        "Fixes a comparison then a rate in python, keeping indentation", "TR-CLAIM: indentation in python; two separate lines.", ["read_lines", "replace line 3", "replace line 2", "read back"], "Both changes applied.", task_type="fix_edge_case")


@reg
def w9():
    f = {"settings/rules.json": L("{", '  "rules": [', '    {"name": "spam", "action": "drop"},', '    {"name": "bulk", "action": "delay"},', '    {"name": "phish", "action": "drop"}', "  ]", "}")}
    chk("cfg-31075", f, [[("sub", "settings/rules.json", '    {"name": "bulk", "action": "delay"},\n    {"name": "phish", "action": "drop"}\n', '    {"name": "bulk", "action": "delay"}\n')], [("sub", "settings/rules.json", '"name": "bulk", "action": "delay"', '"name": "bulk", "action": "drop"')]],
        [("settings/rules.json 把最后一条 phish 规则删掉。删掉后前一条后面不能留逗号，JSON 要保持合法。", ["phish"], None), ("再把 bulk 的 action 从 delay 改成 drop。完事后读回来检查 JSON 合法，告诉我现在剩几条规则、各自的动作。", ["spam", "bulk", "drop"], None)], RL,
        "Deletes the last JSON array element (dropping the trailing comma) then edits another", "TR-CLAIM: leftover comma makes invalid JSON.", ["read_lines", "replace lines 4-5", "replace line 4", "read back"], "Two rules, both drop.")
