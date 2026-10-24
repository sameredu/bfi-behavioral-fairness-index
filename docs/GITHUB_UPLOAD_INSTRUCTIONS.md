# How to publish this repository on GitHub

> The repository name used in the paper and CITATION.cff is
> `iabft-behavioral-fairness-index`. Change it everywhere if you prefer another name.

## Option A — via the GitHub web interface (no command line)

1. Go to https://github.com/new
2. Repository name: `iabft-behavioral-fairness-index`
3. Description: *Infrastructure-Aware Behavioral Fairness Theory — Behavioral Fairness Index (BFI): reference implementation, simulation, and figures.*
4. Choose **Public** (or **Private** during double-blind review).
5. Do **not** initialize with a README (this folder already has one).
6. Create the repository, then on the next page click **uploading an existing file**
   and drag in the contents of this folder.

## Option B — via the command line (git)

From inside this folder:

```bash
git init
git add .
git commit -m "Initial release: BFI reference implementation, simulation, and figures"
git branch -M main

# create the empty repo first on github.com, then:
git remote add origin https://github.com/sameredu/iabft-behavioral-fairness-index.git
git push -u origin main
```

If you use a personal access token instead of a password:

```bash
# when prompted for password, paste your token (Settings -> Developer settings -> Tokens)
git push -u origin main
```

## Option C — GitHub CLI

```bash
gh repo create sameredu/iabft-behavioral-fairness-index --public --source=. --remote=origin --push
```

## After pushing

1. Add topics: `learning-analytics`, `fairness`, `educational-data-mining`, `moodle`.
2. (Optional) Link Zenodo to the repo and cut a release `v1.0.0` to mint a software DOI.
3. Confirm the README "Data availability" Zenodo link resolves:
   https://doi.org/10.5281/zenodo.20366538

## Double-blind reminder

While the paper is under double-blind review, keep the repo **private** and share an
anonymized link with the editor, or mirror it on https://anonymous.4open.science .
De-anonymize (make public, restore names/ORCID) only after acceptance.
