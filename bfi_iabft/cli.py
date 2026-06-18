"""Command-line interface for bfi_iabft.

Usage:
    bfi-iabft demo
    bfi-iabft simulate
    bfi-iabft analyze --data ./data
"""

from __future__ import annotations
import argparse
import numpy as np

from .core import (BFIWeights, bfi, decision_tier, stability_distance,
                   lipschitz_constants)


def _demo() -> None:
    w = BFIWeights()
    Ls = lipschitz_constants(w)
    print("Behavioral Fairness Index — demo")
    print(f"  weights: alpha={w.alpha} beta={w.beta} gamma={w.gamma}")
    print(f"  Lipschitz constants: L1={Ls['L1']:.3f}  L2={Ls['L2']:.3f}  "
          f"Linf={Ls['Linf']:.3f}")
    print("  example sessions:")
    for (p, r, dh) in [(0.9, 0.9, 0.05), (0.7, 0.6, 0.30), (0.2, 0.1, 0.70)]:
        s = float(bfi(p, r, dh, w))
        print(f"    P={p} R={r} D_hat={dh} -> BFI={s:.3f} "
              f"tier={decision_tier(s)} rho={float(stability_distance(s)):.3f}")


def _simulate() -> None:
    try:
        from simulation.run_simulation import main as sim_main  # type: ignore
    except Exception:
        print("Run the bundled script directly:  python simulation/run_simulation.py")
        return
    sim_main()


def _analyze(data: str) -> None:
    try:
        import importlib.util
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "src",
                            "analyze_real_data.py")
        spec = importlib.util.spec_from_file_location("analyze_real_data", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        import sys
        sys.argv = ["analyze_real_data.py", "--data", data]
        mod.main()
    except Exception as e:
        print("Could not run analysis:", e)
        print("Run directly:  python src/analyze_real_data.py --data", data)


def main() -> None:
    ap = argparse.ArgumentParser(prog="bfi-iabft",
                                 description="Behavioral Fairness Index (IABFT)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("demo", help="print a short BFI demonstration")
    sub.add_parser("simulate", help="run the synthetic theorem-verification")
    pa = sub.add_parser("analyze", help="analyze a local Zenodo dataset")
    pa.add_argument("--data", default="./data")
    args = ap.parse_args()

    if args.cmd == "simulate":
        _simulate()
    elif args.cmd == "analyze":
        _analyze(args.data)
    else:
        _demo()


if __name__ == "__main__":
    main()
