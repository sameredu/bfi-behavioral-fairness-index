"""Reproduce every number, table and figure of the paper (v3).
Usage from the repository root:  IABFT_DATA=./data python src/run_all.py
Outputs go to ./results/."""
import os, sys, subprocess
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
res = os.path.join(root, 'results'); os.makedirs(res, exist_ok=True)
env = dict(os.environ, PYTHONPATH=here,
           IABFT_DATA=os.path.abspath(os.environ.get('IABFT_DATA', os.path.join(root, 'data'))))
steps = [os.path.join(here, 'load.py'), os.path.join(here, 'analyze.py'), os.path.join(here, 'ablation.py'), os.path.join(here, 'robustness.py'),
         os.path.join(root, 'figures', 'make_figures_2_3_4.py'), os.path.join(root, 'figures', 'make_figure1_pipeline.py'),
         os.path.join(root, 'tests', 'test_bfi.py')]
for s in steps:
    print('==>', os.path.relpath(s, root)); subprocess.run([sys.executable, s], cwd=res, env=env, check=True)
