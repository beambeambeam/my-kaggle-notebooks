# AGENTS.md

This repository is a `uv`-managed workspace for Kaggle competition notebooks.

## Purpose

- Keep Kaggle work organized by competition and date.
- Prefer self-contained notebooks over shared Python packages.
- Use local tooling only for lightweight support tasks such as formatting, linting, and small utilities.

## Project Structure

- Competition work lives under `notebooks/`.
- Reusable starters live under `templates/`.
- Folder format:
  - `notebooks/YYYY-MM-DD-competition-name/`
- Each competition folder should usually contain:
  - `overview.md`
  - `data.md`
  - one or more draft notebooks
  - optional run logs created from notebook execution

Example:

```text
templates/
  kaggle.ipynb

notebooks/
  2026-03-08-titanic-passenger-survival/
    overview.md
    data.md
    titnic-01-eda-and-modeling.ipynb
    titnic-01-eda-and-modeling.log
    titnic-02-catboost-features.ipynb
```

## Notebook Philosophy

- Each notebook should be self-contained.
- Avoid `src/`, shared helper packages, and cross-competition utility modules unless there is a very strong reason.
- A notebook should contain everything needed for that specific draft:
  - package checks if needed
  - environment loading
  - Kaggle auth
  - data loading/downloading
  - feature engineering
  - modeling
  - diagnostics
  - submission generation
  - optional auto submission

## Notebook Naming Convention

- Notebook filename format:
  - `<code>-NN-short-description.ipynb`
- Log filename format:
  - `<code>-NN-short-description.log`
- `NN` is a two-digit draft number such as `01`, `02`, `03`.
- `code` is a 6-character readable identifier used to avoid confusion across competitions and multiple runs.

Example:

- `titnic-01-eda-and-modeling.ipynb`
- `titnic-02-catboost-features.ipynb`
- `titnic-03-catboost-tuned.ipynb`

## Code Prefix Rule

- Use a readable 6-character slug in front of every notebook draft name.
- The same 6-character slug should be used for all notebooks and logs within the same competition folder.
- Prefer readable slugs over random strings.
- Good slug properties:
  - 6 characters
  - easy to recognize
  - visually distinct
  - connected to the competition name when possible

Example:

- Titanic uses `titnic`

## Internal Notebook Slug

- Every notebook should define a `NOTEBOOK_SLUG` variable.
- `NOTEBOOK_SLUG` should match the notebook filename without `.ipynb`.
- Output artifacts should be named from `NOTEBOOK_SLUG`.

Examples:

- `submission_<NOTEBOOK_SLUG>.csv`
- `diagnostics_<NOTEBOOK_SLUG>.csv`
- `fold_scores_<NOTEBOOK_SLUG>.csv`
- `oof_predictions_<NOTEBOOK_SLUG>.csv`

Important:

- Use the exact notebook filename without `.ipynb`.
- Prefer hyphenated slugs that match the actual draft filename.

## Markdown Files Per Competition

Each competition folder should include these two markdown files:

- `overview.md`
  - competition summary
  - objective
  - high-level approach
  - useful notes
- `data.md`
  - dataset overview
  - feature descriptions
  - missing value notes
  - target definition
  - feature engineering hints

## Kaggle Notebook Workflow

Preferred notebook behavior:

- Load `.env` if present.
- Authenticate with `KaggleApi` if available.
- Support both local and Kaggle-hosted runs.
- Resolve data using this order:
  - existing mounted Kaggle input
  - existing local files
  - Kaggle API download if needed and available
- Write outputs either to `/kaggle/working` when available or the current working directory otherwise.
- Default to the Kaggle-first behavior unless there is a strong reason not to.
- Prefer logs as the main debugging artifact when a notebook run fails.

Useful runtime flags inside notebooks:

- `RUN_DOWNLOAD`
  - default preferred value: `True`
  - force Kaggle API download path
  - use `False` only when intentionally relying on existing mounted/local files
- `RUN_SUBMISSION`
  - default preferred value: `True`
  - auto submit generated CSV to Kaggle
  - `False`: only build the file
- `FORCE_DOWNLOAD`
  - default preferred value: `True`
  - redownload competition files even when an older local copy exists
  - `False`: reuse existing downloaded assets when possible

## Modeling Guidance

- Start with a simple baseline notebook first.
- Improve with a second notebook that focuses on stronger features and a better tabular model.
- For Titanic specifically:
  - baseline: logistic regression
  - stronger draft: CatBoost with richer feature engineering and cross-validation
  - later draft: tuned CatBoost with small parameter search and safer full-train refit
- Prefer cross-validation over a single holdout split when estimating leaderboard quality.
- Save diagnostics whenever possible.

## Notebook Debugging Lessons

- When a notebook fails, read the generated `.log` first before changing the notebook.
- Keep notebook defaults explicit and stable when that matches the workflow. In this repo, the preferred defaults are:
  - `RUN_DOWNLOAD = True`
  - `RUN_SUBMISSION = True`
  - `FORCE_DOWNLOAD = True`
- Be careful when building model constructors from parameter dictionaries.
  - Do not pass the same keyword twice, such as `iterations` inside both a base parameter dict and explicit keyword arguments.
- Be careful with pandas aggregation output shapes.
  - After `groupby(...).agg(...)`, verify the resulting columns before renaming them.
- Be careful with nested quotes inside notebook string literals.
  - Auto-submit message strings that use `strftime(...)` should be checked for quote mismatches.
- Prefer saving diagnostics before final submission logic when possible, so partial runs still produce useful debugging artifacts.

## Git Rules

- Notebook files should be tracked.
- Execution logs should not be tracked.
- Generated CSV outputs should not be tracked.
- Downloaded competition data should not be tracked.

Current ignore expectations include:

- `*.log`
- `*.csv`
- `data/`
- `.ipynb_checkpoints/`

Important:

- Do not ignore all `*.ipynb` files, because notebooks are core project assets.

## Current Titanic Reference

Reference folder:

- `notebooks/2026-03-08-titanic-passenger-survival`

Reference notebooks:

- `titnic-01-eda-and-modeling.ipynb`
  - simple baseline
  - end-to-end Kaggle flow
- `titnic-02-catboost-features.ipynb`
  - stronger feature engineering
  - CatBoost model
  - OOF validation and threshold tuning
- `titnic-03-catboost-tuned.ipynb`
  - small CatBoost parameter search
  - fixed full-train refit logic
  - OOF-based model selection and threshold tuning

## Tooling Notes

- `uv` is used as lightweight project tooling support.
- It is not the center of the notebook architecture.
- Keep the repo simple and notebook-first.
- `templates/kaggle.ipynb` is the default starter when creating a new Kaggle draft notebook.

## When Adding a New Competition

1. Create a folder using `YYYY-MM-DD-competition-name`.
2. Add `overview.md`.
3. Add `data.md`.
4. Choose a readable 6-character competition code.
5. Create `01` baseline notebook.
6. Create later drafts as needed using the same code prefix.
7. Keep logs and generated outputs ignored by git.

## UV

THIS IS UV PYTHON UV USING UV

## EDIT NOTEBOOK

NEVER EVER USING A SCRIPT PYTHON SCREIPT BASH SCRIPT OR ANY SCRIPT TO EDIT THE JUPYTER NOTEBOOK
YOU WILL NEVER GET WHAT YOU WANT
YOU WILL BROKE THE FORMAT
YOU WILL BROKE THE JSON
USE PROPER TOOLS DON'T WRITE SCRIPT TO DO IT
DO HARD WAY BECAUSE YOU NEVER MAKE IT PASS WHEN YOU USE SCRIPT
