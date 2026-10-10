def page(q, url_match, url, title, snippet, content, date, error=None):
    d = {"query_match": q, "url_match": url_match, "url": url, "title": title, "snippet": snippet, "published_at": date}
    if error:
        d["error"] = error
    else:
        d["content"] = content
    return d

def phr(items):
    return "\n## Five alternative phrasings of the task\n" + "".join("%d. %s\n" % (i + 1, x) for i, x in enumerate(items))

