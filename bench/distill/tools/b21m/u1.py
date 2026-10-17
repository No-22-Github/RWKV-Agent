"""33441-33447: undo (whole change, or undo and redo another way)."""
from p0 import undo, reg

W = ("list_files", "read_file", "write_file")
WB = ("list_files", "read_file", "write_file", "bash")


def eq(path, text):
    return {path: ("eq", text)}


@reg
def c33441():
    conf = "bind 127.0.0.1\nport 6379\nmaxmemory 256mb\nmaxmemory-policy allkeys-lru\n"
    undo("hyb-33441", files={"conf/redis.conf": conf}, p1="把 conf/redis.conf 里的 maxmemory 调到 1gb。", p2="刚才那个改动不合适，撤销吧。", rules={}, chk1=["1gb"], must=W,
         desc="Raises maxmemory, then the user asks to undo the change (file must be back to the original)", ref="第一轮改 maxmemory 为 1gb；用户接受后要求撤销，改回 256mb，其余不动。")


@reg
def c33442():
    a = "export function getUser(id) {\n  return db.find(id);\n}\n"
    b = "import { getUser } from './user.js';\nconst u = getUser(7);\nconsole.log(u);\n"
    undo("hyb-33442", files={"src/user.js": a, "src/main.js": b}, p1="Rename getUser to fetchUser in all the files under src.", p2="Actually, revert that rename. Put everything back.", rules={},
         chk1=["fetchUser"], must=WB, desc="Renames a function across two files, then asks to revert the rename completely",
         ref="Rename in both files; after accept, change fetchUser back to getUser in both so the tree equals the original.")


@reg
def c33443():
    mk = lambda n: "name: %s\ntimeout: 10\nretries: 2\n" % n
    files = {"svc/a.yaml": mk("a"), "svc/b.yaml": mk("b"), "svc/c.yaml": mk("c")}
    undo("hyb-33443", files=files, p1="把 svc 下三个 yaml 的 timeout 都改成 30。", p2="线上扛不住，全部改回去。", rules={}, chk1=["30"], must=W,
         desc="Raises timeout in three yaml files, then asks to restore all of them", ref="三个文件 timeout 10→30；用户接受后要求全部改回，终态等于原样。")


@reg
def c33444():
    cl = "# Changelog\n\n## 2.0\n- New editor\n\n## Deprecated\n- Legacy importer (removed in 3.0)\n- XML export\n\n## 1.9\n- Fixes\n"
    undo("hyb-33444", files={"CHANGELOG.md": cl}, p1="Remove the Deprecated section from CHANGELOG.md.", p2="Put that section back exactly as it was.", rules={},
         chk1=["Deprecated"], must=W, desc="Deletes a section from a changelog, then asks to bring it back unchanged",
         ref="Delete the section; after accept restore its heading and two bullets in the original position.")


@reg
def c33445():
    rd = "# 小工具\n\n一个命令行小工具。\n\n## 用法\n运行 tool --help\n"
    undo("hyb-33445", files={"README.md": rd}, p1="在 README.md 末尾加一段免责声明：本工具按现状提供。", p2="撤销吧，不用加免责声明了。", rules={}, chk1=["免责声明"], must=W,
         desc="Appends a disclaimer to the README, then asks to undo it", ref="末尾追加免责声明；用户接受后撤销，恢复原文。")


@reg
def c33446():
    t = "plan,price\nbasic,59\npro,129\n"
    undo("hyb-33446", files={"pricing.csv": t}, p1="把 pricing.csv 里 basic 的价格改成 69。", p2="撤销，改成 64 吧。", rules=eq("pricing.csv", t.replace("59", "64")), chk1=["69"], must=W,
         desc="Changes a price to 69, then asks to undo and use 64 instead", ref="先改 69；用户接受后要求撤销并改 64，终态 basic,64。")


@reg
def c33447():
    c = "host=api.local\nretries=3\ntimeout=20\n"
    undo("hyb-33447", files={"client.cfg": c}, p1="Set retries to 10 in client.cfg.", p2="Undo that, I'd rather have 5.", rules=eq("client.cfg", c.replace("retries=3", "retries=5")),
         chk1=["10"], must=W, desc="Raises retries to 10, then asks to undo and set 5 instead", ref="Set 10, then final retries=5 with the other lines untouched.")
