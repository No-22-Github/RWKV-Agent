"""b12t zero-call negatives (v1.41), ids 9481-9500: 7 weather concept questions (M10e), 7 shell knowledge
questions and 6 how-to-write-a-command questions with an invented path and 'do not run it' (M9e).
Tools (bash, get_weather, file tools) are offered; the right action is to answer directly. No fixture files."""
import json

from common import write_case

REFS = {}
BUILDERS = []
SPEC = {}


def phrasings(*items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, t) for i, t in enumerate(items))


def zero(cid, *, kind, topic, desc, prompt, contains, answer, alts, task_type="concept", decoy=None):
    verify = '''
import json
case = json.load(open("case.json"))
assert case["files"] == {}
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % json.dumps(contains, ensure_ascii=False)
    sub = "M10e" if kind == "weather" else "M9e"
    what = "weather concept" if kind == "weather" else "knowledge/how-to"
    notes = f"""## Traps
- TR-NOTOOLNEED: a {what} question that needs no tool; get_weather / bash / file tools are offered but any call (including listing a directory first) is wrong.

## Reference solution
No tool call. Final answer: {answer}

## Why the answer is unique
Nothing on disk or in a forecast is asked for. The reply must contain one of {contains}.
""" + phrasings(*alts)
    SPEC[cid] = dict(kind="zero_call", sub=sub)
    if decoy is None:
        decoy = "run it to see" if prompt.isascii() else "运行一下看看"

    def build():
        return write_case(
            cid, desc=desc, task_type=task_type, family=f"fam-nt-b12t-{topic}-01", level="L1", ref_calls=0,
            traps=["TR-NOTOOLNEED"], decoys={"TR-NOTOOLNEED": decoy}, axes=["DEC"], files={}, verify=verify, notes=notes,
            turns=[{"prompt": prompt, "expect": {"tools": [], "require_active_no_call": True, "output_contains_any": contains, "max_output_chars": 600}}])
    build.__name__ = cid.replace("-", "_")
    BUILDERS.append(build)


WD = "查一下今天的天气"

# ---------------------------------------------------------------- weather concepts (5 zh, 2 en)
zero("nt-9481", kind="weather", topic="relhumidity", desc="Weather concept question (relative humidity of 100 percent) with tools offered; answered without a call",
     prompt="天气预报里说相对湿度 100%，是不是就意味着正在下雨？相对湿度到底指什么？", contains=["饱和", "水汽", "最大"], decoy=WD,
     answer="相对湿度是空气中实际水汽含量与同温度下饱和水汽量之比，100% 表示饱和，不一定下雨。",
     alts=["相对湿度 100% 是不是一定在下雨？这个数字怎么理解？", "湿度 100% 说明什么？和下雨有必然联系吗？", "天气里的相对湿度是个什么概念，100% 代表下雨吗？", "为什么湿度很高有时也不下雨？相对湿度的定义是什么？", "解释一下相对湿度，100% 就是在下雨吗？"])
zero("nt-9482", kind="weather", topic="thunderlag", desc="Weather concept question (why lightning is seen before thunder is heard) with tools offered; answered without a call",
     prompt="打雷的时候总是先看到闪电，过几秒才听到雷声，这是为什么？能不能用这个间隔估算闪电离我多远？", contains=["光速", "声速", "光的速度", "声音的速度", "传播速度", "传播得快", "传播得慢", "三秒", "3 秒", "3秒"], decoy=WD,
     answer="光速远快于声速，所以先见闪后闻雷；间隔秒数乘约 340 米，或每 3 秒约 1 公里。",
     alts=["为什么雷声总比闪电晚到？间隔几秒大概能算出多远？", "看到闪电后数几秒才听见雷，怎么估计雷电的距离？", "闪电和雷声不是同时发生的吗？为什么我先看到后听到？", "能靠闪电和雷声的时间差判断雷离我多远吗？原理是什么？", "解释一下为什么先闪后雷，以及怎么粗略估算距离。"])
zero("nt-9483", kind="weather", topic="radiativecooling", desc="Weather concept question (why clear calm nights get colder) with tools offered; answered without a call",
     prompt="为什么晴朗无风的夜晚比有云的夜晚冷得多？云层到底起什么作用？", contains=["辐射", "散热", "热量", "保温", "吸收", "反射", "温室"], decoy=WD,
     answer="晴夜地面向太空辐射散热，无云遮挡热量散失快；云吸收并回射长波辐射，起保温作用。",
     alts=["夜里没云的时候为什么降温特别厉害？", "有云的晚上为什么不那么冷？云层是怎么保温的？", "晴天夜晚降温快的原因是什么？", "云对夜间气温有什么影响？为什么晴夜更冷？", "解释一下夜间辐射降温，和云量有什么关系。"])
zero("nt-9484", kind="weather", topic="lowpressure", desc="Weather concept question (why low pressure brings clouds and rain) with tools offered; answered without a call",
     prompt="常听说低气压控制的地方容易阴雨，高气压控制的地方多晴天，这背后的原理是什么？", contains=["上升", "下沉", "冷却", "凝结", "辐合", "辐散"], decoy=WD,
     answer="低压区空气辐合上升，水汽冷却凝结成云致雨；高压区空气下沉增温，云难以形成，天气晴好。",
     alts=["为什么低压天气多云多雨，高压天气晴朗？", "气压高低为什么会影响天晴还是天阴？", "低气压为什么容易下雨？高气压又为什么晴？", "能讲讲低压和高压天气不同的物理原因吗？", "天气图上的低压中心为什么常伴随云雨？"])
zero("nt-9485", kind="weather", topic="inversion", desc="English weather concept question (temperature inversion) with tools offered; answered without a call",
     prompt="In meteorology, what is a temperature inversion, and why does it tend to trap smog near the ground?", contains=["warmer", "cooler", "colder", "increases with", "stable", "trap", "lid"], decoy="check the weather for me",
     answer="Normally air cools with height; in an inversion a warm layer sits above cooler surface air, so the air is stable and pollutants cannot rise.",
     alts=["What does a temperature inversion mean and why does smog get stuck under it?", "Explain an atmospheric inversion layer and why pollution lingers beneath it.", "Why do inversions cause smog to stay near the ground?", "Briefly, what's a temperature inversion in weather terms?", "How does a warm layer above cold air trap pollution? What's that called?"])
zero("nt-9486", kind="weather", topic="winddirection", desc="Weather concept question (meaning of a named wind direction) with tools offered; answered without a call",
     prompt="天气预报说「西北风 3 到 4 级」，这个西北风是风吹向西北，还是从西北方向吹来？风级又是怎么划分的？", contains=["吹来", "来自", "来的方向", "从西北", "风速", "蒲福"], decoy=WD,
     answer="风向指风吹来的方向，西北风是从西北吹向东南；风级按风速划分（蒲福风级），3 到 4 级是微风到和风。",
     alts=["西北风到底是往哪边吹的？风力 3 到 4 级是什么程度？", "预报里的风向是指风来的方向还是去的方向？风级怎么分？", "东南风是从东南吹来还是吹向东南？蒲福风级是什么？", "怎么理解天气预报中的风向和风力等级？", "解释一下风向的命名规则，以及风级大概对应多大的风。"])
zero("nt-9487", kind="weather", topic="jetstream", desc="English weather concept question (jet stream) with tools offered; answered without a call",
     prompt="What is the jet stream, and why does it matter for the weather we experience at the surface?", contains=["high altitude", "upper", "strong wind", "fast", "narrow", "storm", "westerl", "ribbon", "river"], decoy="check the weather for me",
     answer="Narrow fast bands of strong wind high in the atmosphere, steering storm systems and separating warm from cold air.",
     alts=["Can you explain what the jet stream is and how it affects weather?", "Briefly describe the jet stream and its role in steering storms.", "What's the jet stream in simple terms, and why do forecasters watch it?", "How does the jet stream influence surface weather patterns?", "Tell me what a jet stream is and why it matters."])

# ---------------------------------------------------------------- shell knowledge (4 zh, 3 en)
zero("nt-9488", kind="shell", topic="chmod755", desc="Asks what chmod 755 means with bash offered; answered without a call",
     prompt="chmod 755 里的 755 是什么意思？每一位数字分别代表谁的权限？", contains=["所有者", "属主", "拥有者", "rwx", "读", "可执行", "执行"], 
     answer="三位数字依次是所有者、所属组、其他人；7 = 读写执行，5 = 读加执行。",
     alts=["解释一下 chmod 755，三个数字各代表什么？", "755 权限是怎么算出来的？", "chmod 的数字权限 755 对应哪些读写执行？", "文件权限 rwxr-xr-x 和 755 是什么关系？", "chmod 755 给了谁什么权限？"])
zero("nt-9489", kind="shell", topic="redirectappend", desc="Asks the difference between > and >> in a shell with bash offered; answered without a call",
     prompt="In a shell, what's the difference between `>` and `>>` when redirecting output to a file? Which one could wipe out my existing data?", contains=["append", "overwrite", "truncat", "replace"],
     answer="> truncates/overwrites the file, >> appends to the end; > can destroy existing data.",
     alts=["What is the difference between > and >> redirection in bash?", "If I write `cmd > out` versus `cmd >> out`, what happens to existing content?", "Which redirect overwrites and which appends?", "Explain shell output redirection with > and >>.", "Is `>>` safer than `>` for a file I want to keep?"])
zero("nt-9490", kind="shell", topic="killsignals", desc="Asks the difference between kill -9 and kill -15 with bash offered; answered without a call",
     prompt="kill -9 和 kill -15 有什么区别？平时应该先用哪个？", contains=["SIGKILL", "SIGTERM", "强制", "优雅", "清理", "无法捕获", "不能被捕获"],
     answer="-15 发送 SIGTERM，进程可捕获并清理后退出；-9 发送 SIGKILL，内核强制终止，无法捕获，应作为最后手段。",
     alts=["杀进程时 kill 和 kill -9 区别在哪？", "SIGTERM 和 SIGKILL 有什么不同，该先用哪个？", "为什么不建议一上来就 kill -9？", "kill -15 杀不掉的时候再用 -9，原因是什么？", "解释一下 kill 的 15 号和 9 号信号。"])
zero("nt-9491", kind="shell", topic="psgrepself", desc="Asks why ps aux piped to grep shows the grep line itself with bash offered; answered without a call",
     prompt="When I run `ps aux | grep nginx`, the output also contains the grep command itself. Why does that happen, and what's a clean way to avoid it?", contains=["pgrep", "[n]ginx", "grep -v", "itself", "its own", "own process"],
     answer="grep is a process whose command line contains 'nginx', so ps lists it; use pgrep, or grep '[n]ginx', or pipe through grep -v grep.",
     alts=["Why does grep show up in its own ps aux | grep results?", "How do I stop `ps aux | grep name` from listing the grep process?", "Why do I see a grep line when filtering ps output?", "Is there a cleaner alternative to ps aux | grep for finding a process?", "What's the trick with `grep '[n]ginx'` in ps pipelines?"])
zero("nt-9492", kind="shell", topic="andvssemicolon", desc="Asks the difference between && and ; between shell commands with bash offered; answered without a call",
     prompt="命令之间用 && 连接和用分号 ; 连接，有什么区别？什么时候该用哪个？", contains=["成功", "退出码", "前一个", "失败", "返回值", "状态"],
     answer="&& 只有前一条命令成功（退出码 0）才执行后一条；; 不论成败都继续执行。",
     alts=["shell 里 a && b 和 a ; b 有什么不同？", "&& 什么时候不会执行后面的命令？", "分号和双与号连接命令的区别是什么？", "为什么脚本里常用 && 把几条命令串起来？", "解释命令连接符 && 与 ; 的差异。"])
zero("nt-9493", kind="shell", topic="symlinkhard", desc="Asks the difference between hard and symbolic links with bash offered; answered without a call",
     prompt="What's the difference between a hard link and a symbolic link in Linux? What happens to each if the original file is deleted?", contains=["inode", "pointer", "dangling", "broken", "path", "shortcut"],
     answer="A hard link is another name for the same inode so the data survives deleting the original name; a symlink stores a path and dangles/breaks if the target is removed.",
     alts=["Explain ln versus ln -s: hard links vs symlinks.", "If I delete the original file, which kind of link still works?", "Hard link or soft link: how do they differ internally?", "What is an inode and how does it relate to hard links?", "Why can't hard links point to directories or across filesystems while symlinks can?"])
zero("nt-9494", kind="shell", topic="stderrredirect", desc="Asks what 2>&1 means in a shell command with bash offered; answered without a call",
     prompt="命令末尾常见的 `> out.txt 2>&1` 是什么意思？为什么 2>&1 要写在重定向后面？", contains=["标准错误", "stderr", "标准输出", "stdout", "文件描述符"],
     answer="2>&1 把标准错误（文件描述符 2）重定向到标准输出（1）当前指向的位置；先 > 文件再 2>&1，两者才都进文件。",
     alts=["2>&1 到底是什么意思？", "为什么日志重定向要写成 > file 2>&1？", "标准错误和标准输出怎么合并到一个文件？", "解释 shell 里的 2>&1，顺序为什么重要？", "把 stderr 也写进文件的写法是什么，原理是什么？"])

# ---------------------------------------------------------------- how-to-command with invented path (4 zh, 2 en)
zero("nt-9495", kind="howto", topic="copywithtimes", desc="Asks for a command copying a directory preserving timestamps without running it while bash is offered", task_type="snippet_in_reply",
     prompt="我想把 /data/reports 整个目录复制一份到 /data/reports_bak，并且保留文件的修改时间和权限。请写出命令，先别运行，我确认后自己执行。",
     contains=["cp -a", "cp -p", "cp -rp", "cp -pr", "cp -r", "rsync", "-a"],
     answer="`cp -a /data/reports /data/reports_bak`（或 rsync -a）。",
     alts=["给我一条命令：复制 /data/reports 到 /data/reports_bak，时间戳和权限都要保留。不要执行。", "怎么把 /data/reports 完整备份成 /data/reports_bak 且保留属性？只写命令。", "写命令即可，不要跑：目录 /data/reports 拷贝为 /data/reports_bak，保持原文件时间和权限。", "用 cp 复制整个 /data/reports 到 /data/reports_bak 并保留属性，命令怎么写？别运行。", "我要给 /data/reports 做个带时间戳的副本 /data/reports_bak，请给命令，不执行。"])
zero("nt-9496", kind="howto", topic="chmodsh", desc="Asks for a command making every shell script in a tree executable without running it while bash is offered", task_type="snippet_in_reply",
     prompt="我有个目录 /srv/demo-site，想给它下面所有 .sh 脚本加上可执行权限。请写一条命令，只写出来，先不要运行。",
     contains=["chmod"],
     answer="`find /srv/demo-site -name '*.sh' -exec chmod +x {} +`。",
     alts=["怎么批量给 /srv/demo-site 里的 .sh 文件加执行权限？只给命令，不要执行。", "写条命令：/srv/demo-site 下所有 shell 脚本 chmod +x，先别跑。", "递归地让 /srv/demo-site 里的 .sh 都可执行，命令是什么？我自己运行。", "给我 find 加 chmod 的组合命令，目标是 /srv/demo-site 的 .sh 文件，不要运行。", "我想让 /srv/demo-site 下的脚本全部可执行，请写出命令但不要执行。"])
zero("nt-9497", kind="howto", topic="splitbig", desc="Asks for a command splitting a large file into fixed-size pieces without running it while bash is offered", task_type="snippet_in_reply",
     prompt="I have a huge file at /tmp/bigdump.sql and need to cut it into 100 MB pieces named part_aa, part_ab, and so on. What command does that? Please just write it, don't run anything.",
     contains=["split"],
     answer="`split -b 100M /tmp/bigdump.sql part_`; cat part_* rejoins them.",
     alts=["Give me a command to break /tmp/bigdump.sql into 100 MB chunks with the prefix part_. Don't execute it.", "How do I split /tmp/bigdump.sql into 100M pieces? Command only.", "Write the split invocation for 100 MB parts of /tmp/bigdump.sql, prefix part_; I'll run it later.", "I need /tmp/bigdump.sql chopped into 100 MB files called part_aa, part_ab... Show the command but don't run it.", "Command (not executed) to cut a big SQL dump into 100-megabyte segments?"])
zero("nt-9498", kind="howto", topic="renameext", desc="Asks for a loop renaming file extensions without running it while bash is offered", task_type="snippet_in_reply",
     prompt="/home/demo/pics 里的图片后缀都是 .jpeg，我想统一改成 .jpg。请写一段 shell 命令来做这件事，不要运行，我检查后再执行。",
     contains=["mv", "rename"],
     answer="`for f in /home/demo/pics/*.jpeg; do mv \"$f\" \"${f%.jpeg}.jpg\"; done`。",
     alts=["怎么批量把 /home/demo/pics 下的 .jpeg 改名为 .jpg？写出命令，别执行。", "写一个循环，把 /home/demo/pics 里 .jpeg 文件的后缀换成 .jpg，先不要跑。", "给我批量改扩展名的 shell 命令：/home/demo/pics 的 jpeg 变 jpg，只写不运行。", "用 for 循环加 mv 或 rename 把 /home/demo/pics 的 .jpeg 统一成 .jpg，请给命令但别执行。", "我想统一图片后缀 .jpeg 到 .jpg，目录是 /home/demo/pics，请写命令，不要运行。"])
zero("nt-9499", kind="howto", topic="tailfollow", desc="Asks for a command showing the last lines of a log and following new ones without running it while bash is offered", task_type="snippet_in_reply",
     prompt="I want to see the last 50 lines of /srv/demo/events.out and keep watching as new lines arrive. What command should I use? Don't run it, I'll type it in my own terminal.",
     contains=["tail"],
     answer="`tail -n 50 -f /srv/demo/events.out` (or -F to survive rotation).",
     alts=["Write the command to follow /srv/demo/events.out starting from its last 50 lines. Don't execute.", "How can I watch /srv/demo/events.out live, showing the last 50 lines first? Just the command.", "Give me a command to stream new entries of /srv/demo/events.out after printing 50 lines. No running it.", "Which command tails /srv/demo/events.out with 50 lines of context and keeps following? I'll run it myself.", "Command only, please: last 50 lines then follow for /srv/demo/events.out."])
zero("nt-9500", kind="howto", topic="curldownload", desc="Asks for a download command with redirects and retries without running it while bash is offered", task_type="snippet_in_reply",
     prompt="我想用命令行把 https://example.com/files/pkg.tgz 下载保存成 /tmp/pkg.tgz，要能跟随跳转，失败时自动重试 3 次。请写出命令，不要运行，我自己执行。",
     contains=["curl", "wget"],
     answer="`curl -L --retry 3 -o /tmp/pkg.tgz https://example.com/files/pkg.tgz`（或 wget -t 3 -O）。",
     alts=["用 curl 或 wget 下载 https://example.com/files/pkg.tgz 到 /tmp/pkg.tgz，要跟随重定向并重试 3 次，写命令别运行。", "给我一条下载命令：保存为 /tmp/pkg.tgz，跟随跳转，最多重试 3 次，先不要执行。", "怎么命令行下载 https://example.com/files/pkg.tgz 并自动重试？只写出来。", "写一条带重试和跳转跟随的下载命令，文件存成 /tmp/pkg.tgz，不用跑。", "请给出 curl -L 加重试参数下载 https://example.com/files/pkg.tgz 的命令，输出到 /tmp/pkg.tgz，不要运行。"])
