"""Sub 5: compound requests (look up + edit + report)."""
from common import mk


def oc(*v):
    return {"output_contains": list(v)}


def num(n, *extra):
    """A count with context, never the bare digit."""
    forms = ["%s 条" % n, "%s条" % n, "%s 个" % n, "%s个" % n, "%s 张" % n, "%s张" % n, "%s 课时" % n, "%s课时" % n,
             "共 %s" % n, "共%s" % n, "是 %s" % n, "是%s" % n, "为 %s" % n, "：%s" % n, ": %s" % n,
             "%s items" % n, "%s lines" % n, "%s SKU" % n, "%s are" % n, "are %s" % n, "is %s" % n, "total of %s" % n,
             "%s errors" % n, "%s out" % n]
    return {"output_contains_any": forms + list(extra)}


def c61():
    f = {"发布/VERSION": "3.14.2\n", "发布/README.md": "# 工具箱\n\n当前版本：待定\n\n安装：下载即用。\n"}

    def compute(files):
        return {"发布/README.md": files["发布/README.md"].replace("待定", files["发布/VERSION"].strip())}
    mk("hyb-31161", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("看一下 发布/VERSION 里的版本号，填进 发布/README.md 里“当前版本”那一行，然后告诉我填的是多少。", oc("3.14.2"))],
       gist="Fill README version from VERSION and report it.", ref="read both; replace; reply.", why="3.14.2.", ref_calls=4)


def c62():
    f = {"报价/价目.csv": "品名,单价\n网线,12\n路由器,189\n交换机,320\n", "报价/订单.txt": "客户: 华兴\n品名: 路由器\n数量: 6\n金额: \n"}

    def compute(files):
        return {"报价/订单.txt": "客户: 华兴\n品名: 路由器\n数量: 6\n金额: 1134\n"}
    mk("hyb-31162", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("订单文件 报价/订单.txt 的金额还空着，按价目表算好填上（金额冒号后面一个空格然后是数字），再回复我这单一共多少钱。", {"output_contains_any": ["1134 元","1134元","1134 块","1134块","1134 yuan","¥1134","￥1134","共 1134","是 1134","为 1134","：1134",": 1134","1134 RMB","1134 CNY"]})],
       gist="Compute order amount from price list, fill, report.", ref="read; write; reply.", why="6*189=1134.", ref_calls=4)


def c63():
    f = {"运维/app.log": "10:01 ERROR a\n10:02 INFO b\n10:05 ERROR c\n10:09 ERROR d\n10:10 WARN e\n", "运维/状态.md": "# 状态\n\n- 错误数：0\n- 负责人：小周\n"}

    def compute(files):
        n = sum(1 for l in files["运维/app.log"].split("\n") if " ERROR " in l)
        return {"运维/状态.md": files["运维/状态.md"].replace("错误数：0", "错误数：%d" % n)}
    mk("hyb-31163", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("数一下 运维/app.log 里 ERROR 有几条，把 运维/状态.md 里的“错误数”更新成这个数字，别的保持原样，最后也跟我说一声是几条。", num(3, "三条"))],
       gist="Count errors, update status doc, report.", ref="read; replace; reply.", why="3.", ref_calls=4)


def c64():
    f = {"团队/成员.csv": "name,city\nLu,Boston\nMai,Austin\nNia,Boston\n", "团队/city_notes.txt": "Boston: UTC-5\nAustin: UTC-6\n"}

    def compute(files):
        return {"团队/成员.csv": "name,city,offset\nLu,Boston,UTC-5\nMai,Austin,UTC-6\nNia,Boston,UTC-5\n"}
    mk("hyb-31164", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-MULTISRC",),
       turns=[("Add an offset column to 团队/成员.csv using the offsets in 团队/city_notes.txt, and then tell me which city has the most members.", oc("Boston"))],
       gist="Add column from lookup file and report the biggest city.", ref="read; write; reply.", why="Boston 2.", ref_calls=4)


def c65():
    f = {"账单/用电.csv": "月份,度数\n7月,310\n8月,420\n9月,380\n", "账单/备忘.txt": "电价: 0.6 元/度\n"}

    def compute(files):
        return {"账单/备忘.txt": "电价: 0.6 元/度\n8月最贵: 252 元\n"}
    mk("hyb-31165", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-NUMFMT",),
       turns=[("找出用电最多的月份，按备忘里的电价算出那个月电费，在 账单/备忘.txt 末尾补一行“8月最贵: 252 元”这种格式（月份和金额换成你算出来的），然后告诉我是哪个月、多少钱。", {"output_contains": ["8月"], "output_contains_any": ["252 元","252元","252 块","252块","252 yuan","¥252","￥252","共 252","是 252","为 252","：252",": 252","252 RMB","252 CNY"]})],
       gist="Find peak month, compute bill, append line, report.", ref="read two; append; reply.", why="420*.6=252.", ref_calls=4)


def c66():
    f = {"协议/合同.md": "# 合同\n\n甲方：北辰科技\n乙方：南岸咨询\n金额：人民币 50,000 元\n期限：12 个月\n", "协议/摘要.txt": "合同摘要\n"}

    def compute(files):
        return {"协议/摘要.txt": "合同摘要\n甲方：北辰科技\n乙方：南岸咨询\n金额：50000\n期限：12\n"}
    mk("hyb-31166", sub="compound", scen_type=("hybrid", "tool_then_write"), files=f, compute=compute, traps=("TR-NUMFMT",),
       turns=[("从 协议/合同.md 里摘出甲方、乙方、金额、期限，追加到 协议/摘要.txt 里（保留原来的第一行），每项一行，写成“金额：50000”这样，金额只写数字不带逗号和单位，期限只写数字。写完告诉我乙方是谁。", oc("南岸咨询"))],
       gist="Append contract facts to summary, report party B.", ref="read; append; reply.", why="explicit.", ref_calls=3)


def c67():
    f = {"值日/本周.txt": "周一 阿宝\n周二 小米\n周三 阿宝\n周四 大壮\n周五 小米\n", "值日/通知.txt": "本周值日：\n"}

    def compute(files):
        return {"值日/通知.txt": "本周值日：\n阿宝: 周一、周三\n小米: 周二、周五\n大壮: 周四\n"}
    mk("hyb-31167", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-DUPROW",),
       turns=[("把 值日/本周.txt 按人归并，接在 值日/通知.txt 的第一行后面，格式“阿宝: 周一、周三”，人的顺序按第一次出现的顺序。弄完告诉我谁值日最多。", oc("阿宝", "小米"))],
       gist="Group duty roster by person, append to notice, report.", ref="read; append; reply.", why="two tie.", ref_calls=3)


def c68():
    f = {"库存/stock.csv": "sku,qty\nA1,3\nB2,0\nC3,12\nD4,0\n", "库存/缺货.txt": ""}

    def compute(files):
        return {"库存/缺货.txt": "B2\nD4\n"}
    mk("hyb-31168", sub="compound", scen_type=("hybrid", "tool_then_write"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("Put the SKUs that are out of stock (qty 0) from 库存/stock.csv into 库存/缺货.txt, one per line in file order, and tell me how many there are.", num(2, "two", "Two"))],
       gist="Write out-of-stock list into empty file and count.", ref="read; write; reply.", why="B2 D4.", ref_calls=3)


def c69():
    f = {"课程/大纲.md": "# 大纲\n\n第一章 基础 (2 课时)\n第二章 进阶 (3 课时)\n第三章 实战 (5 课时)\n", "课程/进度.csv": "章,课时,完成\n"}

    def compute(files):
        return {"课程/进度.csv": "章,课时,完成\n第一章,2,否\n第二章,3,否\n第三章,5,否\n"}
    mk("hyb-31169", sub="compound", scen_type=("hybrid", "tool_then_write"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("根据 课程/大纲.md 往 课程/进度.csv 里补三行（表头已有，保留），列是章、课时、完成，课时写数字，完成都填“否”。然后告诉我总课时。", num(10, "总课时 10", "总计 10"))],
       gist="Fill progress sheet from outline and report total hours.", ref="read; append; reply.", why="10.", ref_calls=3)


def c70():
    f = {"客服/工单.csv": "id,级别,状态\n11,高,open\n12,低,closed\n13,高,open\n14,中,open\n15,高,closed\n", "客服/日报.md": "# 日报\n\n待处理高优先级：\n"}

    def compute(files):
        return {"客服/日报.md": "# 日报\n\n待处理高优先级：11、13\n"}
    mk("hyb-31170", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把还开着（open）的高级别工单 id 填到 客服/日报.md 的“待处理高优先级：”后面，用顿号隔开、按 id 升序，然后回复我有几张。", num(2, "两张", "两条"))],
       gist="Fill open high tickets into report and report count.", ref="read; replace; reply.", why="11,13.", ref_calls=4)


def c71():
    f = {"整理/文件清单.txt": "合同_2026.pdf\n照片_01.jpg\n报告_Q3.docx\n照片_02.jpg\n预算.xlsx\n", "整理/分类.md": ""}

    def compute(files):
        return {"整理/分类.md": "## 图片\n- 照片_01.jpg\n- 照片_02.jpg\n\n## 文档\n- 合同_2026.pdf\n- 报告_Q3.docx\n- 预算.xlsx\n"}
    mk("hyb-31171", sub="compound", scen_type=("hybrid", "tool_then_write"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("把 整理/文件清单.txt 分成图片和文档两类写进 整理/分类.md：先“## 图片”，再“## 文档”，每个文件一行“- 文件名”，类内保持原顺序，两类之间空一行，文件末尾留换行。图片就是 jpg，其他都算文档。", None),
              ("再告诉我图片有几张。", num(2, "两张"))],
       gist="Classify files into two sections and then report image count.", ref="read; write; reply.", why="2.", ref_calls=3)


def c72():
    f = {"预算/项目.csv": "项目,预算,已用\n官网,50000,32000\n小程序,80000,81000\n数据中台,120000,60000\n", "预算/预警.txt": ""}

    def compute(files):
        return {"预算/预警.txt": "小程序 超支 1000\n"}
    mk("hyb-31172", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-SIGN",),
       turns=[("看 预算/项目.csv，已用超过预算的项目写进 预算/预警.txt，一行一个，格式“项目 超支 金额”，金额是超出的部分。写完回复我超支的是哪个项目。", oc("小程序"))],
       gist="Write overspend warnings and name the project.", ref="read; write; reply.", why="1000.", ref_calls=3)


def c73():
    f = {"设备/版本.txt": "agent 2.1.0\nproxy 1.9.4\ncollector 3.0.1\n", "设备/升级单.md": "# 升级单\n\n"}

    def compute(files):
        return {"设备/升级单.md": "# 升级单\n\n- agent: 2.1.0 -> 2.2.0\n- proxy: 1.9.4 -> 2.0.0\n- collector: 3.0.1\n"}
    mk("hyb-31173", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("读 设备/版本.txt，把升级单 设备/升级单.md 补全：每个组件一行，agent 要升到 2.2.0，proxy 要升到 2.0.0，collector 不升级。要升级的写成“- agent: 2.1.0 -> 2.2.0”，不升级的只写“- collector: 3.0.1”。", None),
              ("加上之后告诉我哪个组件不需要升级。", oc("collector"))],
       gist="Upgrade sheet then report non-upgraded component.", ref="read; append; reply.", why="collector.", ref_calls=3)


def c74():
    f = {"小记/想法.txt": "做个读书笔记工具\n周末去爬山\n给爸妈买体检卡\n", "小记/索引.md": "# 索引\n\n"}

    def compute(files):
        return {"小记/索引.md": "# 索引\n\n1. 做个读书笔记工具\n2. 给爸妈买体检卡\n\n共 2 条\n"}
    mk("hyb-31174", sub="compound", scen_type=("hybrid", "tool_then_write"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("把 小记/想法.txt 每条加上序号（“1. 内容”）写到 小记/索引.md 里（原来的标题保留），然后空一行加“共 N 条”，N 是条数。", None),
              ("第二条（周末去爬山）我已经完成了，把它从索引里拿掉，剩下的重新编号，共几条也更新。", None)],
       gist="Index ideas then remove one and renumber.", ref="write; rewrite.", why="final 2 items (周末去爬山 removed)", ref_calls=4)


def c75():
    f = {"出差/行程.csv": "日期,城市,酒店\n09-20,北京,望京店\n09-21,北京,望京店\n09-22,成都,春熙店\n", "出差/报销说明.txt": "每晚住宿上限 500 元。\n"}

    def compute(files):
        return {"出差/住宿.csv": "城市,酒店,晚数\n北京,望京店,2\n成都,春熙店,1\n"}
    mk("hyb-31175", sub="compound", scen_type=("hybrid", "compound_request"), files=f, compute=compute, traps=("TR-MULTISRC",),
       turns=[("按 出差/行程.csv 统计每家酒店住了几晚，写到 出差/住宿.csv（列：城市,酒店,晚数，按首次出现顺序），再按报销说明告诉我这趟住宿最多能报多少钱。", {"output_contains_any": ["1500 元","1500元","1500 块","1500块","1500 yuan","¥1500","￥1500","共 1500","是 1500","为 1500","：1500",": 1500","1500 RMB","1500 CNY"]})],
       gist="Nights per hotel to csv and max reimbursement.", ref="read two; write; reply.", why="3*500=1500.", ref_calls=4)


BUILDERS = [c61, c62, c63, c64, c65, c66, c67, c68, c69, c70, c71, c72, c73, c74, c75]
