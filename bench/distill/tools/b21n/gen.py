"""Small filler-code generators so fixture files have realistic bulk. Names come from
per-case noun lists; all output is deterministic given (nouns, seed)."""
import random

from common import L


def R(seed):
    return random.Random("b21n-%s" % seed)


def py_mod(nouns, seed, header=None, n=4):
    r = R(seed)
    out = [header] if header else []
    out += ["import os", "import re", ""]
    for i in range(n):
        a, b = r.choice(nouns), r.choice(nouns)
        kind = r.randint(0, 3)
        if kind == 0:
            out += ["", "def clean_%s_%d(text):" % (a, i), "    text = text.strip().lower()", "    return re.sub(r\"\\s+\", \"-\", text)", ""]
        elif kind == 1:
            out += ["", "def pick_%s_%d(rows, key):" % (b, i), "    for row in rows:", "        if row.get(key):", "            return row", "    return None", ""]
        elif kind == 2:
            out += ["", "def %s_path_%d(root, name):" % (a, i), "    return os.path.join(root, \"%s\", name)" % b, ""]
        else:
            out += ["", "def count_%s_%d(items):" % (b, i), "    total = 0", "    for item in items:", "        total += len(item)", "    return total", ""]
    return L(*out)


def js_mod(nouns, seed, n=4, ts=False):
    r = R(seed)
    out = []
    for i in range(n):
        a, b = r.choice(nouns), r.choice(nouns)
        t = ": string" if ts else ""
        tn = ": number" if ts else ""
        k = r.randint(0, 2)
        if k == 0:
            out += ["export function slug%s%d(text%s)%s {" % (a.capitalize(), i, t, t), "  return text.trim().toLowerCase().replace(/\\s+/g, '-');", "}", ""]
        elif k == 1:
            out += ["export const %sLabel%d = (id%s)%s => `%s-${id}`;" % (b, i, tn, t, b), ""]
        else:
            out += ["export function sum%s%d(xs%s)%s {" % (a.capitalize(), i, ": number[]" if ts else "", tn),
                    "  return xs.reduce((acc, x) => acc + x, 0);", "}", ""]
    return L(*out)


def go_mod(pkg, nouns, seed, n=3):
    r = R(seed)
    out = ["package %s" % pkg, "", "import (", "\t\"fmt\"", "\t\"strings\"", ")", ""]
    for i in range(n):
        a = r.choice(nouns)
        k = r.randint(0, 1)
        if k == 0:
            out += ["func Format%s%d(id int) string {" % (a.capitalize(), i), "\treturn fmt.Sprintf(\"%s-%%04d\", id)" % a, "}", ""]
        else:
            out += ["func Normalize%s%d(s string) string {" % (a.capitalize(), i), "\treturn strings.ToLower(strings.TrimSpace(s))", "}", ""]
    return L(*out)


def sh_mod(nouns, seed, n=3):
    r = R(seed)
    out = ["#!/usr/bin/env bash", "set -euo pipefail", ""]
    for i in range(n):
        a = r.choice(nouns)
        out += ["log_%s_%d() {" % (a, i), "  echo \"[$(date +%%H:%%M)] %s step %d: $*\"" % (a, i), "}", ""]
    return L(*out)


def yaml_conf(nouns, seed, n=6):
    r = R(seed)
    out = []
    for i in range(n):
        a = r.choice(nouns)
        out += ["%s_%d:" % (a, i), "  enabled: %s" % r.choice(["true", "false"]), "  interval: %d" % r.randint(5, 90), ""]
    return L(*out)
