"""Sub 4: undo and redo (turn 1 edits, turn 2 asks to restore the original and apply something else)."""
from common import mk


def c51():
    f = {"配置/app.conf": "port = 8080\nhost = 0.0.0.0\nworkers = 4\nlog = info\n"}

    def compute(files):
        return {"配置/app.conf": "port = 8080\nhost = 0.0.0.0\nworkers = 8\nlog = info\n"}
    mk("cfg-31151", sub="undo", scen_type=("config", "edit_value"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把 配置/app.conf 里的端口改成 9090。", None),
              ("哎我看错了，要改的是 workers，不是端口。端口恢复成原来的，workers 改成 8。", None)],
       gist="Wrong key edited then restore and edit the right one.", ref="edit; restore+edit.", why="port back to 8080.", ref_calls=4)


def c52():
    f = {"文档/说明.md": "# 安装说明\n\n1. 下载安装包\n2. 双击运行\n3. 重启电脑\n"}

    def compute(files):
        return {"文档/说明.md": "# 安装说明\n\n1. 下载安装包\n2. 双击运行\n3. 点击完成\n"}
    mk("doc-31152", sub="undo", scen_type=("docs", "draft_document"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把说明里的最后一步删掉，文件是 文档/说明.md。", None),
              ("删得不对，不要删。恢复原样，但第 3 步的内容改成“点击完成”。", None)],
       gist="Step deleted then restore and reword.", ref="edit; edit.", why="3 steps.", ref_calls=4)


def c53():
    f = {"数据/价格.csv": "商品,单价\n苹果,5\n梨,4\n橙子,6\n"}

    def compute(files):
        return {"数据/价格.csv": "商品,单价\n苹果,5\n梨,4\n橙子,7\n"}
    mk("tab-31153", sub="undo", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("数据/价格.csv 里所有单价都涨 10%，直接改文件。", None),
              ("老板说只有橙子涨价，而且是涨到 7 块。其他的恢复成涨价前的价格。", None)],
       gist="Blanket price change then restore all but one.", ref="edit; edit.", why="only orange 7.", ref_calls=4)


def c54():
    f = {"notes/todo.txt": "buy milk\ncall bank\nsend invoice\nbook dentist\n"}

    def compute(files):
        return {"notes/todo.txt": "buy milk\ncall bank\nsend invoice\nbook dentist\nrenew passport\n"}
    mk("doc-31154", sub="undo", scen_type=("docs", "draft_document"), files=f, compute=compute,
       turns=[("Clear everything in notes/todo.txt, I want to start fresh.", None),
              ("Wait, undo that, I need all the old items back exactly as they were. And add 'renew passport' at the end.", None)],
       gist="File cleared then restored with an extra item.", ref="write empty; restore from history.", why="restored.", ref_calls=4)


def c55():
    f = {"环境/dev.env": "API_URL=http://localhost:3000\nDEBUG=true\nTOKEN=dev-123\n"}

    def compute(files):
        return {"环境/dev.env": "API_URL=http://localhost:4000\nDEBUG=true\nTOKEN=dev-123\n"}
    mk("cfg-31155", sub="undo", scen_type=("config", "edit_value"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把 环境/dev.env 里的 DEBUG 关掉。", None),
              ("不用关了，DEBUG 改回去；我真正要改的是 API_URL，端口换成 4000，别的不变。", None)],
       gist="Debug flag turned off then restored, port changed.", ref="edit; edit.", why="debug true.", ref_calls=4)


def c56():
    f = {"项目/计划.md": "# 计划\n\n- 9月：需求\n- 10月：开发\n- 11月：测试\n- 12月：上线\n"}

    def compute(files):
        return {"项目/计划.md": "# 计划\n\n- 9月：需求\n- 10月：开发\n- 11月：测试\n- 12月：上线\n- 1月：回顾\n"}
    mk("hyb-31156", sub="undo", scen_type=("hybrid", "undo_change"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把 项目/计划.md 的上线时间提前到 11 月，测试和上线合并成一行。", None),
              ("这样太赶了，撤销，恢复原来的四行。然后在最后加一行“- 1月：回顾”。", None)],
       gist="Merged plan lines then undo and append.", ref="edit; restore+append.", why="five lines.", ref_calls=4)


def c57():
    f = {"表/人员.csv": "姓名,部门\n甲,研发\n乙,市场\n丙,研发\n丁,财务\n"}

    def compute(files):
        return {"表/人员.csv": "姓名,部门\n甲,研发\n乙,市场\n丙,研发\n丁,行政\n"}
    mk("hyb-31157", sub="undo", scen_type=("hybrid", "undo_change"), files=f, compute=compute, traps=("TR-DUPROW",),
       turns=[("表/人员.csv 里把研发部的人都删掉。", None),
              ("Oops, I did not mean that. Put them back where they were, and instead change 丁's department to 行政.", None)],
       gist="Rows removed then restored and another row changed.", ref="edit; restore+edit.", why="four rows.", ref_calls=4)


def c58():
    f = {"设置/rules.txt": "max_retry=3\ntimeout=30\nverbose=no\nmode=safe\n"}

    def compute(files):
        return {"设置/rules.txt": "max_retry=5\ntimeout=30\nverbose=no\nmode=safe\n"}
    mk("hyb-31158", sub="undo", scen_type=("hybrid", "undo_change"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("In 设置/rules.txt set mode to fast and timeout to 10.", None),
              ("That was too aggressive. Revert both to what they were. I just need max_retry to be 5.", None)],
       gist="Two values changed then both reverted, third changed.", ref="edit; restore+edit.", why="orig mode safe timeout 30.", ref_calls=4)


def c59():
    f = {"稿/开场白.txt": "各位同事大家好，今天我们回顾本季度的销售情况。\n先看整体，再看分区。\n"}

    def compute(files):
        return {"稿/开场白.txt": "各位同事大家好，今天我们回顾本季度的销售情况。\n先看整体，再看分区，最后聊聊下季度的目标。\n"}
    mk("hyb-31159", sub="undo", scen_type=("hybrid", "undo_change"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把 稿/开场白.txt 改得正式一点，直接改文件。", None),
              ("改得我不喜欢，原文还给我（就是你改之前的样子）。然后只在第二句末尾加上“，最后聊聊下季度的目标”，句号保留在最后。", None)],
       gist="Rewrite rejected, original restored, small addition.", ref="edit; restore+edit.", why="exact restoration.", ref_calls=4)


def c60():
    f = {"日历/周计划.csv": "星期,事项\n周一,例会\n周二,评审\n周三,出差\n周四,出差\n周五,复盘\n"}

    def compute(files):
        return {"日历/周计划.csv": "星期,事项\n周一,例会\n周二,评审\n周三,出差\n周四,出差\n周五,团建\n"}
    mk("hyb-31160", sub="undo", scen_type=("hybrid", "undo_change"), files=f, compute=compute, traps=("TR-DUPROW",),
       turns=[("把 日历/周计划.csv 里连着两天的出差合成一天，只保留周三。", None),
              ("不行，周四也得留着出差，恢复。周五的复盘改成团建就行。", None)],
       gist="Merged trip days then restored, Friday changed.", ref="edit; restore+edit.", why="five rows.", ref_calls=4)


BUILDERS = [c51, c52, c53, c54, c55, c56, c57, c58, c59, c60]
