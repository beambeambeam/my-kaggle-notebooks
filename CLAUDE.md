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

## UV

THIS IS UV PYTHON UV USING UV

## EDIT NOTEBOOK

NEVER EVER USING A SCRIPT PYTHON SCREIPT BASH SCRIPT OR ANY SCRIPT TO EDIT THE JUPYTER NOTEBOOK
YOU WILL NEVER GET WHAT YOU WANT
YOU WILL BROKE THE FORMAT
YOU WILL BROKE THE JSON
USE PROPER TOOLS DON'T WRITE SCRIPT TO DO IT
DO HARD WAY BECAUSE YOU NEVER MAKE IT PASS WHEN YOU USE SCRIPT
