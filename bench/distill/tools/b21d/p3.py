"""31371-31430: questions that read like general or web questions but are answered only by workspace files (plus web controls)."""
from common import mk_notes, write

BUILDERS = []


def reg(f):
    BUILDERS.append(f)
    return f


VER = '''
import re
m = re.search(%r, case["files"][%r])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]
%s
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
'''


def fx(query, url, title, content, date="2026-08-20"):
    return {"query_match": query, "url": url, "url_match": url.split("://")[1], "title": title,
            "snippet": content.split("\n")[0][:160], "content": content, "published_at": date}


def local(cid, *, tt, files, q, path, pat, variant, decoy, desc, ref, trap="TR-DECOY", web=None, webval=None, sub="local"):
    """Answer exists only in files. variant A: read_file required, web_search forbidden. B: only the value is judged."""
    import re
    ans = re.search(pat, files[path]).group(1)
    assert len(ans) >= 2
    e = {"output_contains": [ans]}
    if ans.isascii():
        e["output_contains_token"] = True
    if variant == "A":
        e["required_tools"] = ["read_file"]
        e["forbidden_tools"] = ["web_search"]
        policy = {"must_offer": ["list_files", "read_file", "web_search"], "never_offer": ["bash"]}
    else:
        policy = {"must_offer": (["search_text", "read_file", "web_search"] if int(cid.split("-")[1]) % 4 == 0 else ["list_files", "read_file", "web_search"])}
    if webval:
        e["output_excludes"] = [webval]
    extra = "assert %r not in ans\n" % webval if webval else ""
    body = VER % (pat, path, extra)
    notes = mk_notes("- Trap (%s): the question sounds like general knowledge or a web question, web_search is offered, and a near-miss value sits in the workspace%s." % (trap, " and the fixture search returns a different public figure" if webval else ""),
                     ref, "The asked value exists only in %s (and is the one the reply must contain); web results, if any, carry a different figure." % path)
    write(cid, sub=sub, task_type=tt, desc=desc, files=files, turns=[{"prompt": q, "expect": e}], notes=notes, body=body, ref_calls=3,
          policy=policy, traps=[trap], decoys={trap: decoy}, axes=("DEC", "VER") if trap == "TR-SUPERSEDE" else ("DEC", "OBS"),
          web=web, kind="local")


def ext(cid, *, files, q, web, ans, localval, desc, ref, trap=None, sub="ext", decoy=None):
    """Control: the answer is external and time-sensitive, web_fixture has it, the workspace holds an older value."""
    assert len(ans) >= 2
    e = {"required_tools": ["web_search"], "output_contains": [ans]}
    if ans.isascii():
        e["output_contains_token"] = True
    if localval:
        e["output_excludes"] = [localval]
    pol = {"must_offer": (["web_search", "web_fetch", "list_files"] if int(cid.split("-")[1]) % 2 == 0 else ["web_search", "list_files"])}
    body = '''
page = " ".join(w["content"] for w in case["web_fixture"])
assert %r in page
assert %r in case["turns"][0]["expect"]["output_contains"]
print(json.dumps({"expected_string": %r}, ensure_ascii=False))
''' % (ans, ans, ans)
    notes = mk_notes("- Control: the answer is a current external fact; a stale local note must not be quoted.%s" % (" TR-DECOY: older value in workspace." if trap else ""),
                     ref, "web_fixture holds the only current value; the workspace note is dated earlier and its value must not be reported.")
    write(cid, sub=sub, task_type="lookup_value", desc=desc, files=files, turns=[{"prompt": q, "expect": e}], notes=notes, body=body, ref_calls=3,
          policy=pol, traps=[trap] if trap else [], decoys={trap: decoy or localval} if trap else None, axes=("VER",) if not trap else ("VER", "OBS"),
          web=web, kind="ext")
