"""Harness behavior checks, not a second implementation of the physics."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('runner',ROOT/'run.py')
runner=importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)

class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.case={'case_id':'contract-test','observables':{'x':{'expected':2.,'unit':'J','atol':1e-8,'rtol':1e-8}}}
        self.payload={'schema_version':1,'case_id':'contract-test','implementation':'test',
                      'observations':{'x':2.},'checks':{'conservation':True}}
    def test_valid_contract(self):
        self.assertEqual(runner.validate(self.payload,self.case,'test'),[])
    def test_wrong_number_rejected(self):
        self.payload['observations']['x']=3.
        self.assertTrue(runner.validate(self.payload,self.case,'test'))
    def test_nonfinite_and_boolean_rejected(self):
        for value in (float('nan'),float('inf'),True,None):
            self.payload['observations']['x']=value
            self.assertTrue(runner.validate(self.payload,self.case,'test'))
    def test_identity_and_case_must_match(self):
        self.payload['case_id']='another-model'
        self.assertTrue(runner.validate(self.payload,self.case,'test'))
        self.payload['case_id']='contract-test'
        self.assertTrue(runner.validate(self.payload,self.case,'somebody-else'))
    def test_missing_and_false_physics_checks_rejected(self):
        for checks in ({},{'balance':False},{'balance':1}):
            self.payload['checks']=checks
            self.assertTrue(runner.validate(self.payload,self.case,'test'))
    def test_non_object_output_rejected(self):
        self.assertTrue(runner.validate([],self.case,'test'))

class ExecutionTests(unittest.TestCase):
    def test_missing_is_not_passed(self):
        entry={'case':'valves','implementation':'claude','entrypoint':'implementations/claude/valves.py',
               'status':'missing','provenance':'Unavailable original.'}
        result=runner.run_entry(entry,runner.environment())
        self.assertEqual(result['status'],'missing')
    def test_cache_and_invalidation_and_bad_output(self):
        # This is a tiny protocol fixture, explicitly not a physics implementation.
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'cases').mkdir()
            script=root/'probe.py'
            fixture={'case_id':'protocol-only','observables':{'x':{'expected':2.,'unit':'test','atol':0.,'rtol':0.}}}
            (root/'cases/probe.json').write_text(json.dumps(fixture))
            script.write_text("import json\nprint(json.dumps({'schema_version':1,'case_id':'protocol-only','implementation':'test','observations':{'x':2.},'checks':{'probe':True}}))\n")
            entry={'case':'probe','implementation':'test','entrypoint':'probe.py','status':'available','provenance':'Protocol test only.'}
            with patch.object(runner,'ROOT',root):
                a=runner.run_entry(entry,runner.environment())
                b=runner.run_entry(entry,runner.environment())
                self.assertEqual((a['status'],a['cached']),('passed',False))
                self.assertEqual((b['status'],b['cached']),('passed',True))
                script.write_text(script.read_text()+'\n# changed implementation\n')
                c=runner.run_entry(entry,runner.environment())
                self.assertEqual((c['status'],c['cached']),('passed',False))
                fixture['observables']['x']['expected']=3.
                (root/'cases/probe.json').write_text(json.dumps(fixture))
                d=runner.run_entry(entry,runner.environment())
                self.assertEqual(d['status'],'failed')
                script.write_text("print('not JSON')\n")
                e=runner.run_entry(entry,runner.environment())
                self.assertEqual(e['status'],'failed')
    def test_different_models_are_not_compared(self):
        records=[{'case':'valves','status':'passed','implementation':'one'},
                 {'case':'sweater_equal','status':'passed','implementation':'two'}]
        result=runner.compare(records)
        self.assertTrue(all(r['status']=='incomplete' for r in result))

if __name__=='__main__': unittest.main()
