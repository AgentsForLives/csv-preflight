import csv,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from csv_check import audit
class AuditTests(unittest.TestCase):
    def test_duplicates(self):
        self.assertEqual(audit('id,name\n0001,Ana\n0001,Ana\n',key='id')['issues'],[{'row':3,'type':'exact_duplicate','first_row':2}])
    def test_conflicting_key(self):
        self.assertEqual(audit('id,name\n0001,Ana\n0001,Bob\n',key='id')['issues'][0],{'type':'conflicting_key','key':'0001','rows':[2,3]})
    def test_empty_values(self):
        self.assertEqual({x['type'] for x in audit('id,name\n, \n',['name'],'id')['issues']},{'required_empty','key_empty'})
    def test_width(self):
        self.assertEqual(audit('a,b\n1,2,3\n')['issues'][0]['type'],'column_count')
    def test_multiline_bom(self):
        self.assertEqual(audit('\ufeffid,name\r\n0001,"Ana,\nA"\r\n',key='id')['issues'],[])
    def test_headers(self):
        for s in ['', 'a,a\n',',b\n',' ,b\n']:
            with self.subTest(s=s),self.assertRaises(ValueError):audit(s)
    def test_absent_columns(self):
        with self.assertRaises(ValueError):audit('a\n1\n',['b'])
        with self.assertRaises(ValueError):audit('a\n1\n',key='b')
    def test_malformed_quotes(self):
        with self.assertRaises(csv.Error):audit('a,b\n1,"unterminated\n')
    def test_cli_no_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'in.csv';out=Path(d)/'out.json';src.write_text('id,name\n0001,Ana\n')
            original=src.read_bytes();script=str(Path(__file__).with_name('csv_check.py').resolve())
            cmd=[sys.executable,script,str(src),'--key','id','--output',str(out)]
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertEqual(json.loads(out.read_text())['modifications'],0)
            prior=out.read_bytes();self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            self.assertEqual(out.read_bytes(),prior)
            self.assertNotEqual(subprocess.run([sys.executable,script,str(src),'--output',str(src)],capture_output=True).returncode,0)
            self.assertEqual(src.read_bytes(),original)
if __name__=='__main__':unittest.main()
