"""Reproduce every empirical number, table and figure in the revised manuscript.

Usage (from the repository root):
    IABFT_DATA=./data python src/run_all.py
Place the seven anonymized .xlsx files from Zenodo (doi:10.5281/zenodo.20366538) in ./data first.
Outputs are written to ./results/.
"""
import os, sys, subprocess
here=os.path.dirname(os.path.abspath(__file__)); root=os.path.dirname(here)
os.makedirs(os.path.join(root,'results'),exist_ok=True)
env=dict(os.environ, IABFT_DATA=os.path.abspath(os.environ.get('IABFT_DATA',os.path.join(root,'data'))),
         PYTHONPATH=here)
for s in ['load.py','analyze.py','validity.py','validity2.py',os.path.join('..','figures','make_figures_3_4_results.py')]:
    print('==>',s); subprocess.run([sys.executable,os.path.join(here,s)],cwd=os.path.join(root,'results'),env=env,check=True)
