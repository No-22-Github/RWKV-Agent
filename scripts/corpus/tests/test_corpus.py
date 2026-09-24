import argparse
import json
import tempfile
import unittest
from pathlib import Path

from scripts.corpus import __main__ as cli
from scripts.corpus import bank, decontam, paths, render, runs, script, similarity, wire


def step(action, **fields):
    return {"stage": "decision", "action_type": action, **fields}


def tool(name, arguments):
    return step("tool", tool=name, tool_arguments=arguments, tool_executed=True)


def final(text):
    return step("final", model_output=text)


def case_run(*steps, output=None, passed=True, retries=0, case_id="c"):
    answer = output if output is not None else steps[-1].get("model_output", "")
    return runs.CaseRun(case_id, passed, [{"steps": list(steps), "output": answer}], retries)


class WireTest(unittest.TestCase):
    def test_tool_call_is_compact_name_first_and_keeps_unicode(self):
        self.assertEqual(wire.tool_call("read_file", {"path": "说明.md"}),
                         '<tool_call>{"name":"read_file","arguments":{"path":"说明.md"}}</tool_call>')


class ScriptTest(unittest.TestCase):
    def test_path_ids_round_trip(self):
        self.assertEqual(script.base_case_id(script.path_id("cfg-0012", 2)), "cfg-0012")
        self.assertEqual(script.base_case_id("cfg-0012"), "cfg-0012")


class PathsTest(unittest.TestCase):
    def test_normalize_drops_defaults_and_empty_optionals_only(self):
        self.assertEqual(paths.normalize_arguments("list_files", {"path": "", "max_depth": 3, "max_results": 20}),
                         {"max_results": 20})
        # A float equal to an int default is not the default the harness applies.
        self.assertEqual(paths.normalize_arguments("list_files", {"max_depth": 3.0}), {"max_depth": 3.0})
        self.assertEqual(paths.normalize_arguments("read_lines", {"path": "a", "start_line": "", "end_line": 0}),
                         {"path": "a", "end_line": 0})

    def test_extract_keeps_actions_in_order(self):
        path = paths.extract(case_run(tool("list_files", {"path": ""}), final("42")))
        self.assertEqual([action.tool for action in path], ["list_files", None])
        self.assertEqual(path[0].text, wire.tool_call("list_files", {}))
        self.assertEqual(path[1].text, "42")

    def test_extract_rejects_unclean_runs(self):
        cases = {
            "protocol retry": case_run(final("x"), retries=1),
            "tool error or rejection": case_run({**tool("read_file", {"path": "a"}), "tool_error": "missing"}, final("x")),
            "answer repaired by the harness": case_run(final("x"), output="y"),
            "answer stage (forced closeout)": case_run({**final("x"), "stage": "answer"}),
            "final before the last step": case_run(final("x"), tool("read_file", {"path": "a"}), output="x"),
        }
        for reason, run in cases.items():
            with self.subTest(reason), self.assertRaisesRegex(paths.Unclean, reason.split(" (")[0]):
                paths.extract(run)

    def test_select_prefers_shortest_then_new_tool_sequences(self):
        read = paths.Action(wire.tool_call("read_file", {"path": "a"}), "read_file")
        search = paths.Action(wire.tool_call("search_text", {"query": "a"}), "search_text")
        read_b = paths.Action(wire.tool_call("read_file", {"path": "b"}), "read_file")
        answer = paths.Action("42")
        stat = paths.CaseStats(candidates=[
            ((search, read, answer), 0),
            ((read, answer), 1),
            ((read, answer), 2),        # exact duplicate
            ((read_b, answer), 3),      # same tool sequence as the kept (read, answer)
            ((read, read_b, answer), 4),    # new shape but over the cap
        ])
        kept = paths.select(stat, max_per_case=2)
        self.assertEqual(kept, [(read, answer), (search, read, answer)])
        self.assertEqual(dict(stat.drops), {"duplicate path": 1, "same tool sequence": 1, "over per-case cap": 1})


class BankTest(unittest.TestCase):
    RECORD = {
        "id": "r1", "scenario": "cfg", "initial_files": {"a.txt": "7"},
        "expected": {"turn_expectation": {"output_contains": ["7"]}},
        "messages": [
            {"role": "user", "text": "What is in a.txt?"},
            {"role": "assistant", "kind": "tool_call", "name": "read_file", "arguments": {"path": "a.txt"},
             "supervised": True},
            {"role": "tool", "payload": "{}"},
            {"role": "assistant", "kind": "final", "text": "7", "supervised": True},
        ],
    }

    def test_record_becomes_case_and_script(self):
        case = bank.record_to_case(self.RECORD)
        self.assertEqual(case["turns"], [{"prompt": "What is in a.txt?", "expect": {"output_contains": ["7"]}}])
        entry = bank.record_to_script(self.RECORD)
        self.assertEqual([o["text"] for o in entry["outputs"]],
                         [wire.tool_call("read_file", {"path": "a.txt"}), "7"])

    def test_bank_round_trip_and_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as root:
            bank.write(Path(root), [{"id": "b"}, {"id": "a"}])
            self.assertEqual([case["id"] for case in bank.load(Path(root))], ["a", "b"])
        with self.assertRaises(ValueError):
            bank.by_id([{"id": "a"}, {"id": "a"}])

    def test_script_paths_resolve_to_their_bank_case(self):
        cases = {"c": {"id": "c", "files": {}}}
        resolved = render.cases_for_script(cases, [{"case_id": "c--p1"}, {"case_id": "c--p2"}])
        self.assertEqual([case["id"] for case in resolved], ["c--p1", "c--p2"])
        with self.assertRaises(ValueError):
            render.cases_for_script(cases, [{"case_id": "d--p1"}])


class SimilarityTest(unittest.TestCase):
    def test_boilerplate_is_ignored(self):
        template = "Reply with only the final answer and nothing else please."
        test = [similarity.features({"turns": [{"prompt": f"task {i} {template}"}]}) for i in range(10)]
        common = similarity.boilerplate(test, 0.05)
        self.assertTrue(common["prompt"])
        candidate = similarity.strip(similarity.features({"turns": [{"prompt": "other " + template}]}), common)
        self.assertEqual(similarity.scores(candidate, similarity.strip(test[0], common))["prompt"], 0.0)

    def test_fixture_reuse_counts_by_containment(self):
        fixture = {"deploy.yaml": "a: 1\nb: 2\nc: 3\nd: 4\n"}
        test = similarity.features({"files": fixture})
        bigger = similarity.features({"files": {**fixture, "extra.txt": "x\ny\nz\nw\n"}})
        self.assertEqual(similarity.scores(bigger, test)["files"], 0.5)
        self.assertEqual(similarity.containment(test["files"], bigger["files"]), 1.0)

    def test_nearest_flags_a_renamed_copy(self):
        original = {"id": "t1", "files": {"svc/notify-hub.yaml": "retries: 3\ntimeout: 30\nregion: eu\n"},
                    "turns": [{"prompt": "How many retries does notify-hub allow before paging CHG-2193?"}]}
        unrelated = {"id": "t2", "files": {"b.csv": "x,y\n1,2\n"}, "turns": [{"prompt": "Sum column y."}]}
        test = [(case["id"], similarity.features(case)) for case in (original, unrelated)]
        common = similarity.boilerplate([features for _, features in test], 0.99)
        row = decontam.nearest({**original, "id": "cand"}, test, common, {"prompt": 0.35, "files": 0.3, "names": 0.3})
        self.assertEqual(row["flagged"], ["prompt", "files", "names"])
        self.assertEqual(row["nearest"]["files"], "t1")


class CliTest(unittest.TestCase):
    def parse(self, *argv):
        parser = argparse.ArgumentParser()
        commands = parser.add_subparsers(dest="command", required=True)
        for name, module in cli.COMMANDS.items():
            module.add_arguments(commands.add_parser(name))
        return parser.parse_args(argv)

    def test_render_passes_flags_after_double_dash_to_agent_eval(self):
        args = self.parse("render", "--records", "r.jsonl", "--out", "o", "--", "--profile", "g1j")
        self.assertEqual(args.extra, ["--profile", "g1j"])

    def test_paths_accepts_repeated_runs(self):
        args = self.parse("paths", "--run", "a", "--run", "b", "--out", "s.jsonl")
        self.assertEqual(args.run, [Path("a"), Path("b")])


if __name__ == "__main__":
    unittest.main()
