# Publishing this repository on GitHub (public, citable, reusable)

This release is **non-anonymized** and intended for public, reusable, citable
distribution. Author names, affiliations, ORCID, and the Zenodo dataset DOI are
included throughout.

> Repository name used in `CITATION.cff`, `pyproject.toml`, and the paper:
> `iabft-behavioral-fairness-index`
> Owner used in the URLs: `sameredu` — change both if you use a different account/name.

---

## Step 1 — create the repository on GitHub

1. Go to https://github.com/new
2. **Repository name:** `iabft-behavioral-fairness-index`
3. **Description:**
   *Behavioral Fairness Index (BFI) — Infrastructure-Aware Behavioral Fairness Theory: installable Python package, simulation, and figures.*
4. **Visibility:** Public
5. Do **not** add a README/license/.gitignore (this folder already has them).
6. Click **Create repository**.

## Step 2 — push the code (command line)

From inside this folder:

```bash
git init
git add .
git commit -m "Initial public release: bfi-iabft v1.0.0 (BFI / IABFT)"
git branch -M main
git remote add origin https://github.com/sameredu/iabft-behavioral-fairness-index.git
git push -u origin main
```

If prompted for a password, paste a **Personal Access Token** instead
(GitHub -> Settings -> Developer settings -> Personal access tokens -> Fine-grained,
with `Contents: Read and write` on this repo).

### Or with the GitHub CLI

```bash
gh repo create sameredu/iabft-behavioral-fairness-index \
  --public --source=. --remote=origin --push \
  --description "Behavioral Fairness Index (BFI) — IABFT"
```

## Step 3 — make it discoverable

On the repo page -> gear next to **About**:

- **Topics:** learning-analytics, algorithmic-fairness, educational-data-mining,
  fair-assessment, moodle, python
- Tick **Releases** and **Packages** visibility.

## Step 4 — cut a release and mint a software DOI (Zenodo)

1. Link GitHub to Zenodo: https://zenodo.org/account/settings/github/ -> toggle this repo ON.
2. On GitHub: **Releases -> Draft a new release**.
   - Tag: `v1.0.0`  -  Title: `bfi-iabft v1.0.0`
   - Description: short summary + link to the dataset DOI.
   - **Publish release.**
3. Zenodo automatically archives the release and mints a software DOI.
4. Add the new DOI badge to `README.md` and cite it next to the dataset DOI.

## Step 5 (optional) — publish to PyPI so anyone can `pip install bfi-iabft`

```bash
pip install build twine
python -m build                 # builds dist/*.whl and dist/*.tar.gz
python -m twine upload dist/*    # needs a PyPI account + API token
```

After this, the install line in the README and paper works as-is:

```bash
pip install bfi-iabft
```

---

## Reusability checklist (already satisfied in this repo)

- [x] MIT license (`LICENSE`)
- [x] Installable package with clean API (`pyproject.toml`, `bfi_iabft/`)
- [x] Command-line interface (`bfi-iabft demo | simulate | analyze`)
- [x] 12 passing unit tests (`tests/`)
- [x] Reproducible simulation of Theorems T1-T5 (`simulation/`)
- [x] Figure-regeneration scripts (`figures/`)
- [x] Machine-readable citation (`CITATION.cff`)
- [x] Pinned dependencies (`requirements.txt`, optional extras)
- [x] Dataset referenced via DOI, not bundled (`docs/DATA_AND_CODE_AVAILABILITY.md`)
- [x] No student data or secrets committed (`.gitignore` excludes `data/`, `*.xlsx`)
