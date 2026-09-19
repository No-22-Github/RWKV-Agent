import unittest

from scorer_ablation import rescore


class ScorerSensitivityTests(unittest.TestCase):
    def numeric(self, output, failures=(), **extra):
        case = {'id':'sample', 'turns':[{'result':{'output':output}, 'failures':list(failures)}], **extra}
        frozen = {'turns':[{'expect':{'expected_number':42,'tolerance':0}}]}
        return rescore(case, frozen, relax=True)

    def test_numeric_sentence_and_not_substring(self):
        self.assertTrue(self.numeric('Total: 42.', ['output "Total: 42." is not a plain number'])['passed'])
        self.assertFalse(self.numeric('142', ['numeric output = 142, want 42 within 0'])['passed'])

    def test_preserves_execution_and_protocol_failures(self):
        for failure in ['runner error: failed', 'answer contract repaired: [protocol_tag]', 'required tool "read_file" was not called']:
            self.assertFalse(self.numeric('42', [failure])['passed'])
        self.assertFalse(self.numeric('42', error='script failed')['passed'])
        self.assertFalse(self.numeric('42', failures=['expect.files missing'])['passed'])

    def test_numeric_any_is_explicitly_optimistic(self):
        result = self.numeric('42 is wrong; answer is 43', ['output "..." is not a plain number'])
        self.assertTrue(result['passed'])
        self.assertEqual(result['turns'][0]['numbers'], [42,43])

    def test_calls_and_forbidden_are_separate_axis(self):
        case = {'id':'sample','turns':[{'result':{'output':'Value MANGO'},'failures':[
            'output = "Value MANGO", want "MANGO" after trimming outer whitespace',
            'missing required call to read_file with argument fields map[path:answer.txt]',
            'forbidden tool "list_files" was called']}]}
        spec = {'turns':[{'expect':{'output_equals':'MANGO'}}]}
        self.assertFalse(rescore(case,spec,relax=True)['passed'])
        self.assertTrue(rescore(case,spec,relax=True,drop_calls=True)['passed'])

    def test_casefold_is_a_separate_diagnostic(self):
        case = {'id':'sample','turns':[{'result':{'output':'west is larger'},'failures':[
            'output = "west is larger", want "WEST" after trimming outer whitespace']}]}
        spec = {'turns':[{'expect':{'output_equals':'WEST'}}]}
        self.assertFalse(rescore(case,spec,relax=True)['passed'])
        self.assertTrue(rescore(case,spec,relax=True,ignore_case=True)['passed'])


if __name__ == '__main__':
    unittest.main()
