"""G: no write_file/replace_lines/append_file; edit with bash, or explain when nothing can write (20135-20140)."""
from common import expand, file_eq, lines, mk, refuse, value

BUILDERS = []
NW = ["write_file", "replace_lines", "append_file"]
DONE_BAD = ["已修改", "已经修改", "已更新", "已经更新", "已改好", "has been updated", "I've updated", "I have updated", "I updated", "I changed", "I've changed", "I have changed"]


# Wording for "nothing here can edit a file" (group G); the web-access word list does not fit these replies.
CANT_WRITE = (["无法修改", "不能修改", "没法修改", "没办法修改", "无法直接修改", "无法直接编辑", "无法编辑", "不能编辑", "无法写入", "不能写入",
               "没有写入", "没有写文件", "没有修改", "没有编辑", "无法更改", "不能更改", "无法保存", "只读", "只有读取", "只能读取", "没有权限",
               "无权", "做不到", "办不到", "没有相应的工具", "没有对应的工具", "没有写入文件的工具", "没有直接"]
              + expand(["cannot", "can't", "unable", "I'm unable", "not able", "don't have the ability", "do not have the ability",
                        "read-only", "no write", "no tool", "don't have a tool", "no way to", "no file-writing", "only have read",
                        "can only read", "no ability"]))


def reg(f):
    BUILDERS.append(f)
    return f


def edit(cid, turns, files, final, *, sub, tt, desc, cmds, ref_text, why, zh=None):
    rules = {p: ({"equals": final[p]} if final[p] != files[p] else {"unchanged": True}) for p in files}
    parts = ", ".join("%r: case['files'][%r].replace(%r, %r)" % (p, p, files[p], final[p]) for p in files if final[p] != files[p])
    body = 'print(json.dumps({"files": {%s}}, ensure_ascii=False))\n' % parts
    last = [p for p in files if final[p] != files[p]][-1]
    mk(cid, sub=sub, task_type=tt, desc=desc, files=files, turns=turns, never=NW, must=["bash"],
       traps_notes=["No file-writing tool is offered: the edit goes through the shell (sed), leaving everything else byte-identical."],
       ref_text=ref_text, why=why + " expect.files pins the full end state.", body=body, ref_calls=len(cmds), case_expect={"files": rules},
       axes=("CON", "VER"), ref=(cmds, file_eq(last, final[last])))


def final_ops(files, final):
    """(path, [(old, new)]) via a single full-text replacement per changed file (verify recomputes from the fixture)."""
    out = []
    for p in files:
        if final[p] != files[p]:
            out.append((p, [(files[p], final[p])]))
    return out


@reg
def g1():
    t = lines(["[server]", "port=8080", "timeout=30", "", "[client]", "timeout=30", "connect_timeout=30"])
    n = lines(["[server]", "port=8080", "timeout=60", "", "[client]", "timeout=30", "connect_timeout=30"])
    edit("cfg-20135", [("把 config/app.ini 里 [server] 段的 timeout 从 30 改成 60，别的都不要动。", {"required_tools": ["bash"]})], {"config/app.ini": t},
         {"config/app.ini": n}, sub="G-bash", tt="edit_value", desc="Edits one section's value in an ini file when no file-writing tool exists",
         cmds=["sed -i '3s/timeout=30/timeout=60/' config/app.ini"], ref_text="bash: sed -i '3s/timeout=30/timeout=60/' config/app.ini (line 3 is [server] timeout)",
         why="Only line 3 belongs to [server]; [client] has the same value and connect_timeout contains it.")


@reg
def g2():
    t = lines(["# 部署指南 v1.2", "", "当前版本 v1.2，升级请见下表。", "| 版本 | 说明 |", "| v1.2 | 稳定 |", "旧版 v1.1 不再维护。"])
    n = t.replace("v1.2", "v1.3")
    edit("doc-20136", [("把 README.md 里所有的 v1.2 都换成 v1.3，v1.1 别动。", {"required_tools": ["bash"]})], {"README.md": t}, {"README.md": n},
         sub="G-bash", tt="write_structured", desc="Replaces a version string everywhere in a doc when no file-writing tool exists",
         cmds=["sed -i 's/v1\\.2/v1.3/g' README.md"], ref_text="bash: sed -i 's/v1\\.2/v1.3/g' README.md", why="Three occurrences of v1.2; v1.1 stays.")


@reg
def g3():
    t = lines(["# Changelog", "", "## 1.4.0", "- faster startup", "", "## 1.3.2", "- fix crash on empty input"])
    n = t + "\n## 1.4.1\n- fix typo in help text\n"
    edit("doc-20137", [("Add a new section to the end of CHANGELOG.md: heading '## 1.4.1', then one bullet '- fix typo in help text', with a blank line before the heading.", {"required_tools": ["bash"]})],
         {"CHANGELOG.md": t}, {"CHANGELOG.md": n}, sub="G-bash", tt="write_structured", desc="Appends a changelog section when no file-writing tool exists",
         cmds=["printf '\\n## 1.4.1\\n- fix typo in help text\\n' >> CHANGELOG.md"], ref_text="bash: printf ... >> CHANGELOG.md", why="The new text is given verbatim; the old content is kept.")


@reg
def g4():
    t = lines(["LOG_LEVEL=INFO", "DEBUG_SQL=1", "PORT=9000"])
    m = t.replace("LOG_LEVEL=INFO", "LOG_LEVEL=WARN")
    n = m.replace("DEBUG_SQL=1\n", "")
    edit("cfg-20138", [("In app.env, set LOG_LEVEL to WARN.", {"required_tools": ["bash"]}), ("Now remove the DEBUG_SQL line from the same file.", {"required_tools": ["bash"]})],
         {"app.env": t}, {"app.env": n}, sub="G-bash-multi", tt="edit_value", desc="Edits a value, then deletes a line, when no file-writing tool exists",
         cmds=["sed -i 's/^LOG_LEVEL=INFO$/LOG_LEVEL=WARN/' app.env", "sed -i '/^DEBUG_SQL=/d' app.env"], ref_text="Turn 1: sed value. Turn 2: sed -i '/^DEBUG_SQL=/d'.",
         why="Two sequential edits; the end state is fixed.")


def nowriter(cid, prompt, files, path, new, *, tt, desc, sub, ref_text):
    never = NW + ["bash"]
    body = 'print(json.dumps({"expected_string": %r}, ensure_ascii=False))\n' % new
    e = refuse(never, contains=[new], excludes=DONE_BAD, words=CANT_WRITE)
    e.pop("forbidden_tools", None)
    e["forbidden_tools"] = never
    mk(cid, sub=sub, task_type=tt, desc=desc, files=files, turns=[(prompt, e)], never=never, must=["read_file"],
       traps_notes=["Nothing can write or run commands: claiming the file was changed is the failure; the reply should give the exact new content."],
       ref_text=ref_text, why="The file must stay unchanged and the reply must quote the new line.", body=body, ref_calls=1,
       case_expect={"files": {path: {"unchanged": True}}}, axes=("CON", "VER"))


@reg
def g5():
    nowriter("cfg-20139", "把 config/limits.yaml 里的 max_conn 改成 200。", {"config/limits.yaml": lines(["max_conn: 50", "max_idle: 10", "log: info"])},
             "config/limits.yaml", "max_conn: 200", tt="edit_value", desc="Asks for an edit when neither a writer nor a shell exists", sub="G-nowriter",
             ref_text="read_file config/limits.yaml; final: cannot modify files here; change line 1 to `max_conn: 200` yourself.")


@reg
def g6():
    nowriter("doc-20140", "Change the title in docs/guide.md to '# Getting Started'.", {"docs/guide.md": lines(["# Quick Guide", "", "Install, then run the app."])},
             "docs/guide.md", "# Getting Started", tt="write_structured", desc="Asks for a title edit when neither a writer nor a shell exists", sub="G-nowriter",
             ref_text="read_file docs/guide.md; final: cannot edit files here; replace line 1 with `# Getting Started`.")
