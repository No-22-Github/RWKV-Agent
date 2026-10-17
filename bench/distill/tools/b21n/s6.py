"""b21n sub 6: report_test_result 33560-33570 (logs are fixtures; nothing is run)."""
import random

from common import make, L, lineno, P_RO, P_READ, P_SEARCH, P_SRL, P_RWL, P_BASH
from gen import py_mod, js_mod, go_mod, sh_mod, yaml_conf

B = []


def reg(f):
    B.append(f)
    return f


def N(traps, steps, unique):
    return {"traps": traps, "steps": steps, "unique": unique}


def pytest_log(mod, names, fails, seed, secs):
    """names: list of (test, status); fails: {test: [trace lines]}"""
    out = ["============================= test session starts ==============================",
           "platform linux -- Python 3.12.4, pytest-8.2.0", "collected %d items" % len(names), ""]
    for t, s in names:
        out.append("%s::%s %s" % (mod, t, s))
    if fails:
        out += ["", "=================================== FAILURES ==================================="]
        for t, tr in fails.items():
            out += ["_" * 20 + " %s " % t + "_" * 20, ""] + tr + [""]
    nf = len(fails)
    ns = sum(1 for _, s in names if s == "SKIPPED")
    out.append("=== %d failed, %d passed, %d skipped in %.2fs ===" % (nf, len(names) - nf - ns, ns, secs))
    return L(*out)


@reg
def c60():
    names = [(t, "PASSED") for t in ["test_signup_ok", "test_signup_dup_email", "test_failed_login_locks_account", "test_logout_clears_token", "test_reset_mail_sent", "test_profile_edit", "test_avatar_size", "test_password_rules", "test_session_ttl", "test_oauth_state"]]
    names += [("test_email_case", "FAILED"), ("test_token_refresh", "FAILED"), ("test_admin_flag", "FAILED"), ("test_locale_default", "SKIPPED")]
    fails = {"test_email_case": ["    def test_email_case():", ">       assert normalize('A@B.COM') == 'a@b.com'", "E       AssertionError: assert 'A@b.com' == 'a@b.com'"],
             "test_token_refresh": ["    def test_token_refresh():", ">       refresh(tok)", "E       KeyError: 'expires_at'"],
             "test_admin_flag": ["    def test_admin_flag():", ">       assert user.is_admin is True", "E       AttributeError: 'User' object has no attribute 'is_admin'"]}
    f = {"reports/last_run.log": pytest_log("tests/test_auth.py", names, fails, 60, 1.84), "auth/service.py": py_mod(["user", "token"], 601, None, 3),
         "tests/test_auth.py": "# 14 tests, see reports/last_run.log\n", "README.md": "run: pytest tests\n"}
    make("code-33560", sub="report", task_type="report_test_result", desc="pytest log: three failures with different errors, a passing test with 'failed' in its name",
         files=f, turns=[{"p": "reports/last_run.log 是上次跑测试的输出。帮我看一下哪些用例失败了，各自是什么原因？",
                          "inc": ["test_email_case", "test_token_refresh", "test_admin_flag", "KeyError"]}],
         truth="import re\nans = [m for m in re.findall(r'::(\\w+) FAILED', files['reports/last_run.log'])]\nassert ans == ['test_email_case', 'test_token_refresh', 'test_admin_flag']\nans = ans[0]\n",
         readonly=True, decoy="test_failed_login_locks_account", policy=P_READ, ref_calls=2,
         notes=N("TR-DECOY: test_failed_login_locks_account passed; one SKIPPED.", "read log.", "3 failures; KeyError for refresh."))


@reg
def c61():
    log = L("=== RUN   TestParse", "--- PASS: TestParse (0.00s)", "=== RUN   TestParseEmpty", "--- PASS: TestParseEmpty (0.00s)", "=== RUN   TestMerge", "    merge_test.go:41: got [a b], want [a b c]", "--- FAIL: TestMerge (0.00s)",
            "=== RUN   TestRetryTimeout", "    retry_test.go:77: context deadline exceeded after 200ms", "--- FAIL: TestRetryTimeout (0.20s)", "=== RUN   TestWindows", "--- SKIP: TestWindows (0.00s)",
            "=== RUN   TestFlush", "--- PASS: TestFlush (0.01s)", "FAIL", "FAIL\texample.com/merge\t0.231s", "FAIL")
    f = {"ci/go-test.log": log, "merge/merge.go": go_mod("merge", ["part", "set"], 611), "merge/merge_test.go": "package merge\n\n// see ci/go-test.log\n", "go.mod": "module example.com/merge\n\ngo 1.22\n"}
    make("code-33561", sub="report", task_type="report_test_result", desc="go test log with two FAIL, one SKIP",
         files=f, turns=[{"p": "ci/go-test.log has the output of the last go test run. Which tests failed and why? Don't count the skipped one.",
                          "inc": ["TestMerge", "TestRetryTimeout", "deadline exceeded"], "exc": []}],
         truth="import re\nans = re.findall(r'--- FAIL: (\\w+)', files['ci/go-test.log'])\nassert ans == ['TestMerge', 'TestRetryTimeout']\nans = ans[0]\n",
         readonly=True, decoy="TestWindows", policy=P_READ, ref_calls=2,
         notes=N("TR-DECOY: SKIP is not a failure.", "read log.", "TestMerge (got/want) and TestRetryTimeout (deadline)."))


@reg
def c62():
    log = L(" PASS  src/cart.test.js", " PASS  src/money.test.js", " FAIL  src/coupon.test.js", "  ● coupon › stacks two percent codes", "", "    expect(received).toBe(expected)", "    Expected: 18", "    Received: 20", "",
            "  ● coupon › rejects expired code", "", "    TypeError: Cannot read properties of undefined (reading 'getTime')", "",
            " PASS  src/tax.test.js", "", "Test Suites: 1 failed, 3 passed, 4 total", "Tests:       2 failed, 21 passed, 23 total", "Snapshots:   1 obsolete, 0 total")
    f = {"logs/jest.out": log, "src/coupon.js": js_mod(["code", "cart"], 621, 3), "src/coupon.test.js": "// jest tests, results in logs/jest.out\n", "package.json": "{\"scripts\": {\"test\": \"jest\"}}\n"}
    make("code-33562", sub="report", task_type="report_test_result", desc="jest output with two failing tests in one suite and an obsolete snapshot warning",
         files=f, turns=[{"p": "logs/jest.out 是 jest 的输出。哪个测试文件挂了？里面具体哪两个用例失败，各是什么问题？obsolete snapshot 那条只是警告，不算失败。",
                          "inc": ["coupon.test.js", "stacks two percent codes", "rejects expired code", "TypeError"]}],
         truth="ans = 'coupon.test.js'\nassert ' FAIL  src/coupon.test.js' in files['logs/jest.out']\n", readonly=True, decoy="obsolete", policy=P_READ, ref_calls=2,
         notes=N("TR-DECOY: snapshot warning.", "read output.", "coupon.test.js; two cases."))


@reg
def c63():
    log = L("TAP version 13", "1..9", "ok 1 - config loads", "ok 2 - empty config rejected", "not ok 3 - ports must be unique", "  ---", "  message: 'duplicate port 8080 in [web, api]'", "  ...",
            "ok 4 - env override", "ok 5 # SKIP needs docker", "ok 6 - tls off by default", "not ok 7 - path is absolute", "  ---", "  message: 'relative path ./data'", "  ...", "ok 8 - not ok is only a phrase here", "ok 9 - yaml anchors")
    f = {"test/out.tap": log, "src/config.sh": sh_mod(["port", "path"], 631, 3), "test/run.sh": "#!/usr/bin/env bash\nprove test/*.t\n"}
    make("code-33563", sub="report", task_type="report_test_result", desc="TAP output with two not ok lines and a tricky title",
         files=f, turns=[{"p": "test/out.tap 里哪几条用例没通过？原因分别是什么？SKIP 的不算。", "inc": ["ports must be unique", "path is absolute", "8080"]}],
         truth="ans = 'ports must be unique'\nassert 'not ok 3 - ports must be unique' in files['test/out.tap']\n", readonly=True, decoy="not ok is only a phrase here", policy=P_READ, ref_calls=2,
         notes=N("TR-DECOY: case 8's title contains 'not ok'.", "read tap.", "cases 3 and 7."))


@reg
def c64():
    run1 = pytest_log("tests/test_cache.py", [("test_set_get", "PASSED"), ("test_ttl_expire", "FAILED"), ("test_evict_lru", "FAILED"), ("test_clear", "PASSED"), ("test_keys_sorted", "FAILED"), ("test_size", "PASSED")],
                      {"test_ttl_expire": ["E       assert None is not None"], "test_evict_lru": ["E       KeyError: 'b'"], "test_keys_sorted": ["E       assert ['b', 'a'] == ['a', 'b']"]}, 641, 0.9)
    run2 = pytest_log("tests/test_cache.py", [("test_set_get", "PASSED"), ("test_ttl_expire", "PASSED"), ("test_evict_lru", "PASSED"), ("test_clear", "PASSED"), ("test_keys_sorted", "FAILED"), ("test_size", "PASSED")],
                      {"test_keys_sorted": ["E       assert ['b', 'a'] == ['a', 'b']"]}, 642, 0.8)
    f = {"build/test.log": "## run 1 (09:12)\n" + run1 + "\n## run 2 after the cache fix (09:40)\n" + run2, "cache/store.py": py_mod(["key", "slot"], 643, None, 3), "tests/test_cache.py": "# see build/test.log\n"}
    make("code-33564", sub="report", task_type="report_test_result", desc="Two runs in one log: only the latest failures count",
         files=f, turns=[{"p": "build/test.log 里有两次运行（修之前和修之后）。以最后一次为准，现在还有哪些用例是失败的？原因是什么？",
                          "inc": ["test_keys_sorted"], "any": ["assert ['b', 'a'] == ['a', 'b']", "顺序", "排序", "order", "sorted", "['b', 'a']"]}],
         truth="log = files['build/test.log'].split('## run 2')[1]\nimport re\nans = re.findall(r'::(\\w+) FAILED', log)\nassert ans == ['test_keys_sorted']\nans = ans[0]\n",
         readonly=True, decoy="test_ttl_expire", trap="TR-SUPERSEDE", extra_traps=("TR-DECOY",), policy=P_READ, ref_calls=2,
         notes=N("TR-SUPERSEDE: run 1 had three failures.", "read log, use run 2.", "only test_keys_sorted."))


@reg
def c65():
    names = [(t, "PASSED") for t in ["test_slug_basic", "test_slug_unicode", "test_slug_empty", "test_url_join"]] + [("test_url_trailing", "FAILED"), ("test_query_sort", "PASSED")]
    f = {"out/pytest.txt": pytest_log("tests/test_url.py", names, {"test_url_trailing": ["    def test_url_trailing():", ">       assert join('/a/', 'b') == '/a/b'", "E       AssertionError: assert '/a//b' == '/a/b'"]}, 65, 0.3),
         "web/url.py": "import re\n\n\ndef slug(s):\n    return re.sub(r'\\W+', '-', s).strip('-')\n\n\ndef join(base, part):\n    return base + '/' + part\n\n\ndef sort_query(q):\n    return '&'.join(sorted(q.split('&')))\n",
         "tests/test_url.py": "# see out/pytest.txt\n"}
    ln = lineno(f, "web/url.py", "return base + '/' + part")
    make("code-33565", sub="report", task_type="report_test_result", desc="Report the failing test, then find the source line responsible",
         files=f, turns=[{"p": "out/pytest.txt 里有失败的用例吗？是哪个，报什么错？", "inc": ["test_url_trailing", "//"]},
                         {"p": "那是 web/url.py 里哪一行导致的？只告诉我行号和那行代码，先不要改。", "inc": [str(ln)]}],
         truth="ans = 'test_url_trailing'\nassert 'test_url_trailing FAILED' in files['out/pytest.txt']\n", readonly=True, decoy="slug", policy=P_RO, ref_calls=4,
         notes=N("TR-DECOY: other helpers in url.py.", "read log; locate join.", "test_url_trailing; join line %d." % ln))


@reg
def c66():
    log = L("[10:01:12] suite=ingest total=8", "[10:01:12] PASS parse_header", "[10:01:12] PASS parse_rows", "[10:01:13] FAIL parse_quotes expected 3 cols got 2", "[10:01:13] PASS dedupe",
            "[10:01:14] FAIL load_batch timeout after 5000ms", "[10:01:19] RETRY load_batch (1/1)", "[10:01:20] PASS load_batch", "[10:01:20] PASS flush", "[10:01:21] PASS audit_trail", "[10:01:21] done failed=1 retried=1 passed=7")
    f = {"ci/ingest.log": log, "ingest/parse.py": py_mod(["row", "col"], 661, None, 3), "ingest/load.py": py_mod(["batch", "chunk"], 662, None, 2)}
    make("code-33566", sub="report", task_type="report_test_result", desc="A retried test passes on retry, only one genuine failure remains",
         files=f, turns=[{"p": "Read ci/ingest.log: after the retries, which test is still failing and what was the problem? load_batch eventually passed.",
                          "inc": ["parse_quotes", "3 cols"]},
                         {"p": "And what happened with load_batch the first time?", "inc": ["timeout"], "any": ["5000", "5 s", "5s", "5 sec"]}],
         truth="ans = 'parse_quotes'\nassert 'FAIL parse_quotes' in files['ci/ingest.log']\n", readonly=True, decoy="load_batch", trap="TR-SUPERSEDE", extra_traps=("TR-DECOY",), policy=P_RO, ref_calls=3,
         notes=N("TR-SUPERSEDE: load_batch failed then passed on retry.", "read log.", "parse_quotes; load_batch timed out first."))


@reg
def c67():
    log = L("<testsuite name=\"geo\" tests=\"6\" failures=\"2\" errors=\"1\" skipped=\"0\">", "  <testcase name=\"distance_zero\"/>", "  <testcase name=\"distance_antipode\"/>",
            "  <testcase name=\"bearing_north\"><failure message=\"expected 0.0 but was 360.0\"/></testcase>", "  <testcase name=\"bbox_wrap\"><failure message=\"lon 181 not normalised\"/></testcase>",
            "  <testcase name=\"parse_dms\"><error message=\"NumberFormatException: 12°x\"/></testcase>", "  <testcase name=\"round_trip\"/>", "</testsuite>")
    f = {"target/geo-report.xml": log, "src/geo.ts": js_mod(["lat", "lon"], 671, 3, ts=True), "README.md": "reports go to target/\n"}
    make("code-33567", sub="report", task_type="report_test_result", desc="JUnit-style XML with failures and one error",
         files=f, turns=[{"p": "target/geo-report.xml 是测试报告。失败（failure）和出错（error）的用例各有哪些？原因是什么？", "inc": ["bearing_north", "bbox_wrap", "parse_dms", "360.0"]}],
         truth="ans = 'bearing_north'\nassert 'bearing_north' in files['target/geo-report.xml']\n", readonly=True, decoy="distance_zero", policy=P_RO, ref_calls=2,
         notes=N("TR-DECOY: passing testcases listed as empty elements.", "read xml.", "2 failures + 1 error."))


@reg
def c68():
    names = [(t, "PASSED") for t in ["test_job_failed_event", "test_failed_to_dict", "test_retry_after_failed", "test_queue_len", "test_pop_empty", "test_priority", "test_cancel", "test_requeue", "test_stats", "test_close", "test_resume", "test_drain"]]
    names += [("test_gpu_backend", "SKIPPED")]
    log = pytest_log("tests/test_jobs.py", names, {}, 68, 2.5).replace("=== 0 failed", "=== 0 failed")
    f = {"logs/jobs.log": log + "warning: DeprecationWarning: use asyncio.run in tests/test_jobs.py:14\n", "jobs/queue.py": py_mod(["job", "slot"], 681, None, 3), "tests/test_jobs.py": "# 13 tests\n"}
    make("code-33568", sub="report", task_type="report_test_result", desc="Everything passes; names contain 'failed' and a warning is present",
         files=f, turns=[{"p": "Did anything fail in logs/jobs.log? Several test names contain the word failed, so read the actual results. Tell me how many passed.",
                          "inc": ["12"], "any": ["no failure", "nothing failed", "none failed", "no test failed", "0 failed", "all passed", "all tests passed", "did not fail", "No tests failed", "no failures", "without failures", "all 12", "没有失败", "全部通过"]}],
         truth="ans = '12'\nassert files['logs/jobs.log'].count(' PASSED') == 12 and ' FAILED' not in files['logs/jobs.log']\n", readonly=True, decoy="1", policy=P_RO, ref_calls=2,
         notes=N("TR-DECOY: 'failed' in passing names, DeprecationWarning, SKIPPED.", "read log.", "0 failed, 12 passed, 1 skipped."))


@reg
def c69():
    names = [("t_%02d" % i, "PASSED") for i in range(1, 15)] + [("t_15", "FAILED"), ("t_16", "FAILED"), ("t_17", "SKIPPED"), ("t_18", "SKIPPED"), ("t_19", "PASSED")]
    fails = {"t_15": ["E       ZeroDivisionError: division by zero"], "t_16": ["E       assert 41 == 42"]}
    f = {"ci/summary.log": pytest_log("tests/test_calc.py", names, fails, 69, 3.1), "calc/core.py": py_mod(["term", "unit"], 691, None, 3)}
    make("code-33569", sub="report", task_type="report_test_result", desc="Count passed failed skipped from a pytest log",
         files=f, turns=[{"p": "ci/summary.log 这次一共通过了几个、失败了几个、跳过了几个？失败的是哪几个？", "inc": ["15", "2", "t_15", "t_16"]}],
         truth="ans = '15'\nlog = files['ci/summary.log']\nassert '2 failed, 15 passed, 2 skipped' in log\n", readonly=True, decoy="17", policy=P_RO, ref_calls=2,
         notes=N("TR-DECOY: total is 19; passed excludes skipped.", "read the summary line.", "15 passed, 2 failed, 2 skipped."))


@reg
def c70():
    log = L("running 7 tests", "test store::put_get ... ok", "test store::overwrite ... ok", "test store::delete_missing ... FAILED", "test store::scan_range ... ok", "test index::build ... ok", "test index::rebuild_empty ... FAILED", "test index::stats ... ignored", "",
            "failures:", "", "---- store::delete_missing stdout ----", "thread 'store::delete_missing' panicked at 'called `Option::unwrap()` on a `None` value', src/store.rs:88:34", "",
            "---- index::rebuild_empty stdout ----", "thread 'index::rebuild_empty' panicked at 'index out of bounds: the len is 0 but the index is 0', src/index.rs:41:15", "",
            "test result: FAILED. 4 passed; 2 failed; 1 ignored; 0 measured")
    f = {"target/cargo-test.txt": log, "src/store.rs": "\n".join(["// store"] + ["const K%d: u32 = %d;" % (i, i * 7) for i in range(1, 87)] + ["let v = map.get(k).unwrap();"]) + "\n", "src/index.rs": "// index\n", "Cargo.toml": "[package]\nname = \"kv\"\n"}
    make("code-33570", sub="report", task_type="report_test_result", desc="cargo test output: two panics at given locations",
         files=f, turns=[{"p": "Which tests failed in target/cargo-test.txt, and where did each panic happen (file and line)? The test that was not run doesn't count.",
                          "inc": ["store::delete_missing", "index::rebuild_empty", "src/store.rs:88", "src/index.rs:41"]},
                         {"p": "How many tests passed in total?", "inc": ["4"]}],
         truth="ans = 'store::delete_missing'\nassert 'delete_missing ... FAILED' in files['target/cargo-test.txt']\n", readonly=True, decoy="src/store.rs:87", policy=P_RO, ref_calls=3,
         notes=N("TR-DECOY: ignored test.", "read the panic lines.", "two failures; 4 passed."))
