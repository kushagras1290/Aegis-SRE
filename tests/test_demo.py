import subprocess,sys
def test_demo_runs():
 p=subprocess.run([sys.executable,'scripts/demo.py'],capture_output=True,text=True,check=True); assert 'root_cause=postgres' in p.stdout and 'mutations=1' in p.stdout
