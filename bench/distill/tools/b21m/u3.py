"""33455-33460: undo with ordering, secrets, moves and merges."""
from p0 import undo, reg
from u1 import W, WB, eq


@reg
def c33455():
    o = "# 主机表\n10.0.0.1 gw\n\n# 数据库\n10.0.0.5 db1\n\n# 缓存\n10.0.0.9 cache1\n"
    undo("hyb-33455", files={"hosts.txt": o}, p1="把 hosts.txt 里的注释行和空行都删掉，只留主机记录。", p2="注释行还是要的，恢复它们（放回原位），空行不用恢复。",
         rules=eq("hosts.txt", "# 主机表\n10.0.0.1 gw\n# 数据库\n10.0.0.5 db1\n# 缓存\n10.0.0.9 cache1\n"), chk1=["10.0.0.5"], must=W,
         desc="Strips comments and blank lines from a hosts list, then asks to bring back only the comments in place", ref="先只留 3 条记录；之后恢复 3 条注释到原位，不恢复空行。")


@reg
def c33456():
    o = "[Docs](http://docs.example.org/guide)\n[Wiki](http://intranet.local/wiki)\n[Blog](http://blog.example.org)\n"
    f = "[Docs](https://docs.example.org/guide)\n[Wiki](http://intranet.local/wiki)\n[Blog](https://blog.example.org)\n"
    undo("hyb-33456", files={"links.md": o}, p1="Change every http:// link in links.md to https://.", p2="Revert the one that points at intranet.local, it has no TLS.", rules=eq("links.md", f),
         chk1=["https"], must=W, desc="Upgrades all links to https, then asks to revert the intranet one", ref="Upgrade all three, then restore the intranet.local link to http.")


@reg
def c33457():
    todo = "# 待办\n- [ ] 订机票\n- [x] 交房租\n- [ ] 买菜\n- [x] 寄快递\n- [ ] 复查报告\n"
    done = "# 已完成\n- [x] 报税\n"
    undo("hyb-33457", files={"todo.md": todo, "done.md": done}, p1="把 todo.md 里已完成的条目移到 done.md 的末尾。", p2="移得不对，全部放回去，两个文件都恢复成原样。", rules={},
         chk1=["交房租"], must=W, desc="Moves the finished items from todo.md to done.md, then asks to restore both files exactly", ref="先把 2 条已勾选项移走；之后放回原位，两个文件等于原样。")


@reg
def c33458():
    pj = '{\n  "name": "tidy",\n  "version": "1.4.2",\n  "author": "Lee Chen",\n  "license": "MIT"\n}\n'
    f = pj.replace("Lee Chen", "Sam Ortiz")
    undo("hyb-33458", files={"package.json": pj}, p1="Set the author in package.json to Sam Ortiz and bump the version to 2.0.0.", p2="Undo the version bump but keep the new author.", rules=eq("package.json", f),
         chk1=["2.0.0"], must=W, desc="Changes author and version, then asks to undo only the version bump", ref="作者与版本都改；用户要求版本恢复 1.4.2，作者保留 Sam Ortiz。")


@reg
def c33459():
    ini = "[db]\npassword=pg-8821-xq\n[cache]\npassword=rd-4410-zt\n[mq]\npassword=mq-7003-lw\n"
    f = "[db]\npassword=pg-8821-xq\n[cache]\npassword=CHANGEME\n[mq]\npassword=CHANGEME\n"
    undo("hyb-33459", files={"配置.ini": ini}, p1="把配置.ini 里三个 password 的值都换成占位符 CHANGEME，我要提交到公开仓库。", p2="db 的密码撤回来，还是原来的，另外两个继续用占位符。", rules=eq("配置.ini", f),
         chk1=["CHANGEME"], must=W, desc="Replaces three passwords with placeholders, then asks to restore only the db one", ref="三处换占位符；之后 db 恢复为原值 pg-8821-xq，其余保持 CHANGEME。")


@reg
def c33460():
    a = "# 会议 A\n- 预算批准\n- 下周评审\n"
    b = "# 会议 B\n- 招聘两名后端\n"
    undo("hyb-33460", files={"notes/a.md": a, "notes/b.md": b}, p1="把 notes/a.md 合并进 notes/b.md（接在末尾），然后删掉 a.md。", p2="合并错了。撤销：把 a.md 找回来，b.md 里合并进去的内容也去掉。", rules={},
         chk1=["a.md"], must=WB, desc="Merges one note into another and deletes it, then asks to undo the merge and bring a.md back", ref="追加 a.md 内容到 b.md 并删除 a.md；之后重建 a.md 并还原 b.md。")
