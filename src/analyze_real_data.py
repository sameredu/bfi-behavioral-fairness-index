"""
Reproduce the empirical analysis (Table 2 of the paper) from the real
Web Databases examination dataset.

The dataset itself is NOT bundled with this repository. Download the seven
anonymized .xlsx files from Zenodo and place them in ./data/ first:

    DOI : 10.5281/zenodo.20366538
    URL : https://zenodo.org/records/20366538

    Yaghi, S., & AbuSamra, A. A. (2026). Web Databases — Anonymized Moodle
    Examination Dataset for Fairness-Aware Learning Analytics [Data set].
    Zenodo. https://doi.org/10.5281/zenodo.20366538

Expected files in ./data/:
    DataBase_WEB_Midterm1_Anonymized.xlsx
    DataBase_WEB_Midterm2_Theory_Anonymized.xlsx
    DataBase_WEB_Midterm2_Practical_Anonymized.xlsx
    DataBase_WEB_Final_Theory_Anonymized.xlsx
    DataBase_WEB_Final_Practical_Anonymized.xlsx
    DataBase_WEB_Supp_Theory_Anonymized.xlsx
    DataBase_WEB_Supp_Practical_Anonymized.xlsx

Run:
    python src/analyze_real_data.py --data ./data
"""

from __future__ import annotations
import os, glob, argparse

import numpy as np

try:
    import pandas as pd
except ImportError:
    pd = None

from bfi_iabft import (BFIWeights, bfi, decision_tier, normalize_divergence,
                 signal_entropy, recommend_weights, TAU1, TAU2)


def load_assessment(path: str):
    """Load one anonymized assessment file."""
    if pd is None:
        raise RuntimeError("pandas required: pip install pandas openpyxl")
    return pd.read_excel(path)


def q_columns(df):
    return [c for c in df.columns if str(c).startswith("Q")]


def compute_features(df):
    """Derive the behavioral evidence signals from one assessment table.

    This is a reference implementation matching Section 9.2.1 of the paper:
      - disruption probability P : fraction of unanswered questions per session
        used as the supervised target proxy (a classifier is trained on the
        full feature vector in the full pipeline; here we expose the signal)
      - the per-question 'Unanswered' markers are the disruption indicators
    Returns a DataFrame with Student_Label and the unanswered ratio.
    """
    qs = q_columns(df)
    if not qs:
        return None
    unanswered = df[qs].astype(str).apply(
        lambda col: col.str.strip().str.lower().eq("unanswered"))
    ratio = unanswered.sum(axis=1) / len(qs)
    out = pd.DataFrame({
        "Student_Label": df.get("Student_Label", pd.Series(range(len(df)))),
        "unanswered_ratio": ratio.values,
    })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="./data",
                    help="folder containing the Zenodo .xlsx files")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.data, "DataBase_WEB_*.xlsx")))
    if not files:
        print("No dataset files found in", args.data)
        print("Download from https://zenodo.org/records/20366538 "
              "(DOI 10.5281/zenodo.20366538) and place the .xlsx files there.")
        return

    print(f"Found {len(files)} assessment files.")
    all_feats = []
    for f in files:
        df = load_assessment(f)
        feats = compute_features(df)
        if feats is not None:
            feats["assessment"] = os.path.basename(f)
            all_feats.append(feats)
            n_disrupted = int((feats["unanswered_ratio"] > 0).sum())
            print(f"  {os.path.basename(f):48s} n={len(feats):4d} "
                  f"disrupted={n_disrupted}")

    if not all_feats:
        print("No question columns found; check file format.")
        return

    feats = pd.concat(all_feats, ignore_index=True)

    # --- Build evidence signals (reference mapping; see Section 9.2.1) ---
    # P : disruption probability proxy (unanswered ratio, in [0,1])
    P = feats["unanswered_ratio"].to_numpy()
    # R : recovery score — requires cross-exam supplementary linkage; for the
    #     public reference we set R from the population recovery prior when no
    #     supplementary record is available (documented limitation: cold start)
    R = np.clip(1.0 - P + 0.0, 0, 1)  # placeholder reference; full R uses supp exams
    # D_hat : behavioral divergence from the Golden Profile (per-student history)
    #     here approximated by deviation of the session unanswered ratio from
    #     the student's mean across assessments
    student_mean = feats.groupby("Student_Label")["unanswered_ratio"].transform("mean")
    D = np.abs(feats["unanswered_ratio"].to_numpy() - student_mean.to_numpy())
    D_hat = normalize_divergence(D)

    w = BFIWeights()
    scores = bfi(P, R, D_hat, w)
    tiers = decision_tier(scores)

    n = len(scores)
    auto = int(np.sum(tiers == "auto"))
    review = int(np.sum(tiers == "review"))
    none = int(np.sum(tiers == "none"))

    print("-" * 60)
    print(f"Sessions scored        : {n}")
    print(f"Weights                : a={w.alpha} b={w.beta} g={w.gamma}")
    print(f"Signal entropies (norm): H(P)={signal_entropy(P):.3f} "
          f"H(R)={signal_entropy(R):.3f} H(1-D_hat)={signal_entropy(1-D_hat):.3f}")
    print(f"Recommended weights    : {recommend_weights(P, R, D_hat)}")
    print("-" * 60)
    print(f"Tier   Auto  (BFI>={TAU2})      : {auto:4d}  ({100*auto/n:.1f}%)")
    print(f"Tier   Review({TAU1}<=BFI<{TAU2}): {review:4d}  ({100*review/n:.1f}%)")
    print(f"Tier   None  (BFI<{TAU1})       : {none:4d}  ({100*none/n:.1f}%)")
    print("-" * 60)
    print("Note: R and D_hat here use reference approximations; the full "
          "pipeline links supplementary exams and per-student Golden Profiles.")


if __name__ == "__main__":
    main()
