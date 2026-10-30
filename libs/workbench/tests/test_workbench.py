import ast
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import server
import adk_patterns
import llm_patterns
from fastapi.testclient import TestClient


class WorkbenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(server.app)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None,None,None)

    def run_method(self, method, data, session=None):
        response=self.client.post('/api/run',json={'method':method,'data':data,'session':session})
        self.assertEqual(response.status_code,200,response.text)
        self.assertTrue(response.json()['ok'],response.text)
        return response.json()

    def test_catalog_covers_all_exports_and_source(self):
        payload=self.client.get('/api/catalog').json()
        expected={f'{module.__name__}.{s}' for module in (adk_patterns,llm_patterns) for s in module.__all__}
        self.assertEqual({m['id'] for m in payload['methods']},expected)
        for method in payload['methods']:
            response=self.client.get('/api/method/'+method['id'])
            self.assertEqual(response.status_code,200)
            self.assertTrue(response.json()['implementation'])
            self.assertTrue(response.json()['demo_code'])
            ast.parse(response.json()['demo_code'])
            self.assertTrue(response.json()['setup'])

    def test_stateless_offline_methods(self):
        for method in server.CATALOG.values():
            if method['external'] or method['example'] or method['demo'] in {'vision','crewai_wrapper'}:
                continue
            with self.subTest(method=method['id']):
                self.run_method(method['id'],method['default'])

    @unittest.skipUnless(importlib.util.find_spec('crewai'), 'optional CrewAI dependency missing')
    def test_crewai_tool_runs_locally(self):
        result=self.run_method('adk_patterns.crewai_tool',{'text':'hello agent'})
        self.assertEqual(result['result'],'HELLO AGENT')

    def test_every_offline_graph(self):
        for method in server.CATALOG.values():
            if not method['example']:
                continue
            with self.subTest(method=method['id']):
                result=self.run_method(method['id'],method['default'])
                self.assertTrue(result['events'])
                self.client.delete('/api/session/'+result['session'])

    def test_counter_continuity_and_reset(self):
        first=self.run_method('adk_patterns.LocalSession','go')
        second=self.run_method('adk_patterns.LocalSession','go',first['session'])
        self.assertEqual(second['state']['attempts'],2)
        self.client.delete('/api/session/'+first['session'])
        self.assertEqual(self.client.post('/api/run',json={'method':'adk_patterns.LocalSession','data':'go','session':first['session']}).status_code,404)

    def test_review_rewrite_approve_and_stale_response(self):
        result=self.run_method('adk_patterns.reviewed_pipeline','AI')
        token=result['session']
        self.assertIsNotNone(result['pending'])
        blocked=self.client.post('/api/run',json={'method':'adk_patterns.reviewed_pipeline','data':'new','session':token})
        self.assertEqual(blocked.status_code,409)
        response=self.client.post(f'/api/session/{token}/review',json={'decision':{'decision':'revise','notes':'更简洁'}})
        self.assertEqual(response.status_code,200,response.text)
        self.assertIn('更简洁',response.json()['pending']['message'])
        response=self.client.post(f'/api/session/{token}/review',json={'decision':{'decision':'approve'}})
        self.assertEqual(response.json()['result']['status'],'approved')
        self.assertIsNone(response.json()['pending'])
        self.assertEqual(self.client.post(f'/api/session/{token}/review',json={'decision':{'decision':'approve'}}).status_code,404)
        self.client.delete('/api/session/'+token)

    def test_image_upload_and_bad_image(self):
        png='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='
        result=self.run_method('llm_patterns.vision_messages',{'image_base64':png,'question':'describe'})
        self.assertTrue(result['result']['messages'][0]['content'][1]['image_url']['url'].startswith('data:image/png'))
        response=self.client.post('/api/run',json={'method':'llm_patterns.image_data_url','data':{'image_base64':'bad'}})
        self.assertEqual(response.status_code,422)

    def test_validation_and_unknown_methods(self):
        response=self.client.post('/api/run',json={'method':'llm_patterns.sum_amounts','data':{'amounts':[0.1]}})
        self.assertEqual(response.status_code,422)
        self.assertIn('TypeError',response.json()['error'])
        self.assertEqual(self.client.post('/api/run',json={'method':'os.system','data':'ls'}).status_code,404)

    def test_external_requests_require_opt_in(self):
        for method in server.CATALOG.values():
            if method['external']:
                response=self.client.post('/api/run',json={'method':method['id'],'data':method['default']})
                self.assertEqual(response.status_code,400)

    def test_source_search_and_notebook_outputs_excluded(self):
        response=self.client.get('/api/sources',params={'q':'newsletter'})
        self.assertGreater(response.json()['total'],0)
        response=self.client.get('/api/sources',params={'q':'RequestInput','group':'ai-agents-week-03'})
        self.assertGreater(response.json()['total'],0)
        notebook=next(k for k in server.RECORDS if k.endswith('google_adk_basics.ipynb'))
        content=self.client.get('/api/source',params={'path':notebook}).json()
        self.assertTrue(content['notebook'])
        self.assertIn('# Cell ',content['content'])
        self.assertNotIn('"execution_count":',content['content'])

    def test_source_traversal_and_private_files_rejected(self):
        for path in ['../../.env','course/../.env','.git/config','course/ai-agents-week-02/google_adk_basics/.env']:
            self.assertEqual(self.client.get('/api/source',params={'path':path}).status_code,404)
        self.assertTrue(all('.venv' not in k and '.env' not in k for k in server.RECORDS))

    def test_cross_origin_rejected_and_headers(self):
        response=self.client.post('/api/run',headers={'Origin':'https://other.example'},json={})
        self.assertEqual(response.status_code,403)
        response=self.client.get('/')
        self.assertEqual(response.status_code,200)
        self.assertIn("script-src 'self'",response.headers['content-security-policy'])
        self.assertEqual(self.client.get('/static/app.js').status_code,200)

if __name__=='__main__':
    unittest.main()
