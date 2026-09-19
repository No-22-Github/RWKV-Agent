import json
from pathlib import Path
import tempfile
import unittest
from replicate_summary import summarize


class ReplicaSummaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.runs = []
        for i, scores in enumerate([[True, True, False], [True, False, False], [True, False, False]]):
            p = Path(self.tmp.name)/str(i);p.mkdir();self.runs.append(p)
            self.put(p, 'run.json', {'run_id': str(i), 'model': {'id':'m'}, 'sampling':{}, 'harness':{'max_steps':10},
                                    'cases':[{'id':c,'turns':[{'expect':{}}]} for c in ['a','b','c']]})
            self.put(p, 'summary.json', {'run_id':str(i), 'cases':[{'id':c,'passed':passed,'turns':[{'result':{}}]} for c,passed in zip(['a','b','c'],scores)]})
            self.put(p, 'experiment.json', {'binary_sha256':'same','infrastructure_errors':[]})

    def put(self, p, name, value):
        (p/name).write_text(json.dumps(value))

    def test_casewise_all_any_and_mean(self):
        result = summarize(self.runs)
        self.assertEqual(result['pass_all_k']['passed'],1)
        self.assertEqual(result['pass_any_k']['passed'],2)
        self.assertAlmostEqual(result['pass_mean'],4/9)
        self.assertEqual(result['unstable_cases'],['b'])

    def test_incomplete_or_duplicate_replica_rejected(self):
        with self.assertRaises(ValueError):summarize(self.runs[:2])
        with self.assertRaises(ValueError):summarize([self.runs[0]]*3)

    def test_budget_or_frozen_case_change_rejected(self):
        for field in ['harness','cases']:
            with self.subTest(field=field):
                path=self.runs[2]/'run.json'; original=json.loads(path.read_text());changed=dict(original)
                changed[field] = {'max_steps':30} if field=='harness' else [{'id':c,'turns':[{'expect':{'output_equals':'new'}}]} for c in ['a','b','c']]
                self.put(self.runs[2],'run.json',changed)
                with self.assertRaises(ValueError):summarize(self.runs)
                self.put(self.runs[2],'run.json',original)

    def test_missing_case_not_silently_dropped(self):
        p=self.runs[2];s=json.loads((p/'summary.json').read_text());s['cases'].pop();self.put(p,'summary.json',s)
        with self.assertRaises(ValueError):summarize(self.runs)

    def test_infrastructure_failure_not_scored_as_failure(self):
        self.put(self.runs[2],'experiment.json',{'binary_sha256':'same','infrastructure_errors':['HTTP 503']})
        with self.assertRaises(ValueError):summarize(self.runs)


if __name__ == '__main__':unittest.main()
