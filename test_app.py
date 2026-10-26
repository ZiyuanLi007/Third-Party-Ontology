import unittest, json, copy
from unittest.mock import patch
import app
class WorkbenchTests(unittest.TestCase):
 def setUp(self):
  self.docs=[{'id':r,'name':r+'.txt','role':r,'version':'v1','passages':[{'id':r+'-p1','locator':'p1','text':'Before signing, assess ICT critical function classification.'}]} for r in app.ROLES]
 def response(self):
  return {'summary':'Candidate assessment','layers':[{'role':r,'status':'supported','reason':'explicit text','citations':[{'passage_id':r+'-p1','quote':'Before signing'}]} for r in app.ROLES],'links':[{'from_role':'policy','to_role':'procedure','reason':'same task','citations':[{'passage_id':r+'-p1','quote':'Before signing'} for r in ['policy','procedure']]}]}
 def test_parse_exact(self):
  out=app.parse_file('x.txt',b'First paragraph\n\nSecond paragraph');self.assertEqual(len(out),2);self.assertEqual(out[1]['text'],'Second paragraph')
 def test_no_control_material(self):
  r=app.assess('classify',self.docs[:-1],'local');self.assertEqual(r['layers'][-1]['status'],'material_missing')
 def test_model_citations_valid(self):
  with patch('app.provider',return_value=self.response()):r=app.assess('classify',self.docs,'model')
  self.assertEqual(len(r['links']),1);self.assertEqual(r['layers'][0]['status'],'supported')
 def test_fabricated_citation_rejected(self):
  raw=self.response();raw['layers'][0]['citations'][0]['quote']='Invented fact'
  raw['links'][0]['citations'][0]['quote']='Invented fact'
  with patch('app.provider',return_value=raw):r=app.assess('classify',self.docs,'model')
  self.assertEqual(r['layers'][0]['status'],'uncertain');self.assertEqual(r['links'],[])
 def test_absent_material_overrides_model(self):
  with patch('app.provider',return_value=self.response()):r=app.assess('classify',self.docs[:-1],'model')
  self.assertEqual(r['layers'][-1]['status'],'material_missing')
 def test_extraction_hallucination(self):
  with patch('app.provider',return_value={'units':[{'passage_id':'policy-p1','quote':'Made up'}]}):
   with self.assertRaises(ValueError):app.process(self.docs[1],'model')
 def test_demo_modes(self):
  self.assertEqual([app.demo(c)['layers'][-1]['status'] for c in 'ABCD'],['supported','partial','material_missing','conflict'])
 def test_tpr_fixtures_differ_from_schema(self):
  nodes=json.loads((app.ROOT/'reference/data/nodes.json').read_text()); cases=json.loads((app.ROOT/'reference/data/cases.json').read_text()); mappings=json.loads((app.ROOT/'reference/data/mappings.json').read_text())
  ids={n['id'] for n in nodes}; self.assertIn('A-Control',ids); self.assertNotIn('C-Control',ids)
  for c in cases:
   self.assertTrue(set(c['node_ids'])<=ids)
   self.assertEqual(len([m for m in mappings if m['case']==c['id']]),len(c['node_ids'])-1)
 def test_ontology(self):
  x=app.ontology((app.ROOT/'reference/ontology/foundation.ttl').read_text());self.assertIn('https://example.org/tpr/foundation#Control',x['classes'])
class HttpTests(unittest.TestCase):
 def test_roundtrip_and_session_guard(self):
  import threading, urllib.request, urllib.error, tempfile
  from pathlib import Path
  server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
  worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
  base='http://127.0.0.1:'+str(server.server_port)
  old=copy.deepcopy(app.STATE)
  try:
   with tempfile.TemporaryDirectory() as tmp, patch('app.DATA',Path(tmp)):
    tpr=json.load(urllib.request.urlopen(base+'/api/tpr'));self.assertEqual(len(tpr['cases']),4);self.assertIn('A-Control',tpr['ttl'])
    state=json.load(urllib.request.urlopen(base+'/api/state'));self.assertNotIn('api_key',state['config'])
    def post(path,data,token=True):
     headers={'Content-Type':'application/json'}
     if token:headers['X-Workbench-Token']=state['token']
     return json.load(urllib.request.urlopen(urllib.request.Request(base+path,data=json.dumps(data).encode(),headers=headers)))
    with self.assertRaises(urllib.error.HTTPError):post('/api/demo',{'case':'A'},False)
    import base64
    d=post('/api/upload',{'name':'sample.txt','role':'policy','version':'v1','data':base64.b64encode(b'Before signing assess ICT criticality.').decode()})
    post('/api/process',{'id':d['id'],'mode':'local'})
    r=post('/api/assess',{'query':'ICT criticality','document_ids':[d['id']],'mode':'local'})
    self.assertEqual(r['layers'][3]['status'],'material_missing')
    self.assertEqual(r['layers'][1]['status'],'candidate_only')
    self.assertTrue((Path(tmp)/'state.json').exists())
    self.assertEqual(post('/api/demo',{'case':'D'})['layers'][-1]['status'],'conflict')
    with urllib.request.urlopen(base+'/') as response:self.assertIn(b'TRACE',response.read())
  finally:
   app.STATE.clear();app.STATE.update(old);server.shutdown();server.server_close()
if __name__=='__main__':unittest.main()
