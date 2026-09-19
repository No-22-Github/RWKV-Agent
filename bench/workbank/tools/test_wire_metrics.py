import unittest

from wire_metrics import split_think, call_object, analyze, infrastructure_failure
import json
from pathlib import Path
import tempfile


class WireMetricsTest(unittest.TestCase):
    def test_stream_failure_is_not_a_model_failure(self):
        self.assertTrue(infrastructure_failure("runner error: rwkv_lightning continuation error: read stream: unexpected EOF"))
        self.assertTrue(infrastructure_failure("runner error: HTTP 522"))
        self.assertFalse(infrastructure_failure("runner error: agent protocol error: tool call JSON decode failed: unexpected EOF"))
        self.assertFalse(infrastructure_failure("output contains timeout"))
    def test_prefilled_and_short_think(self):
        self.assertEqual(split_think(">已找到</think>950", "User: x\n\nAssistant: <think"), ("prefilled", "已找到", "950"))
        self.assertEqual(split_think("<think>好</think>950"), ("self", "好", "950"))
        self.assertEqual(split_think("<think></think>950"), ("empty", "", "950"))

    def test_call_shape_is_not_tag_mention(self):
        self.assertIsNone(call_object("<tool_call> or answer directly"))
        self.assertIsNone(call_object('<tool_call>{"name":"x","arguments":{}}</tool_call> trailing'))
        self.assertEqual(call_object('```json\n{"name":"x","arguments":{}}\n```')["name"], "x")

    def test_fast_prefill_closes_with_generated_bracket(self):
        call='<tool_call>{"name":"read_file","arguments":{}}'
        self.assertEqual(split_think('>'+call,'Assistant: <think></think'),('empty','',call))
        self.assertEqual(split_think('>950','Assistant: <think></think'),('empty','','950'))
        self.assertEqual(split_think(call,'Assistant: <think></think>'),('empty','',call))
        self.assertEqual(split_think('950','Assistant: <think></think'),('unclosed','950',''))

    def test_forced_without_answer_and_other_failures(self):
        with tempfile.TemporaryDirectory() as path:
            case = {"id":"nt-1", "passed":False, "turns":[{"passed":False,"failures":["tools = [calculator], want []", 'output "9000 MiB" is not a plain number'], "result":{"output":"9000 MiB", "forced_answer_reason":"duplicate_tool_call", "steps":[{"number":1,"stage":"decision","action_type":"tool","tool":"calculator","tool_executed":True,"model_output":""}]}}]}
            Path(path, "summary.json").write_text(json.dumps({"cases":[case]}))
            bank = {"nt-1":{"turns":[{"expect":{"expected_number":9000,"tools":[]}}]}}
            m = analyze(path, bank)["metrics"]
            self.assertEqual(m["forced_triggered"], 1)
            self.assertEqual(m["forced_without_answer"], 1)
            self.assertEqual(m["answer_match_with_other_failures"], 1)
            self.assertEqual(m["passed"], 0)


if __name__ == "__main__":
    unittest.main()
