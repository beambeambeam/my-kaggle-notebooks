---
name: organize-kaggle-dump
description: Organize files dropped into this repo's `dump/` folder into the Kaggle notebook project structure. Use this whenever the user asks to sort, move, rename, or normalize dumped notebook files, old competition folders, loose markdown files, notebook logs, or messy draft names into `notebooks/YYYY-MM-DD-competition-name/`. This skill should trigger even if the user just says things like "organize dump", "sort these old notebooks", "rename these drafts", or "move this old Kaggle work into the repo structure".
---

# Organize Kaggle Dump

Use this skill when the user has dropped old Kaggle project files into `dump/` and wants them reorganized into the repository's standard structure.

## Goal

Turn loose or messy Kaggle competition files into the repo convention:

- `notebooks/YYYY-MM-DD-competition-name/`
- lowercase `overview.md`
- lowercase `data.md`
- notebook names like `<code>-NN-short-description.ipynb`
- log names like `<code>-NN-short-description.log`

Do this without rewriting notebook contents unless the user explicitly asks for content changes.

## Core Rules

- Inspect `dump/` first before moving anything.
- Infer whether the dumped files belong to one competition or multiple competitions.
- Read lightweight metadata first:
  - markdown overview/data files
  - notebook titles
  - obvious competition names in filenames
- Do not modify notebook cells or markdown body text unless the user asks.
- Prefer renaming and moving files only.
- Keep `dump/` itself intact so the user can reuse it later.
- Leave `dump/.gitignore` and `dump/.keep` alone.

## Repo Conventions To Apply

### Folder naming

Create folders like:

- `notebooks/2026-03-08-titanic-passenger-survival/`
- `notebooks/2026-03-06-fraud-detection-cpe232-data-models/`

If the user gives a date, use it directly. If the dump clearly represents a single competition and the user gave a date such as `2026-03-06`, apply that date to the competition folder.

### Markdown naming

Normalize to:

- `overview.md`
- `data.md`

Typical conversions:

- `Overview.md` -> `overview.md`
- `data-description.md` -> `data.md`

### Notebook naming

Normalize to:

- `<code>-NN-short-description.ipynb`

Examples:

- `titnic-01-eda-and-modeling.ipynb`
- `frd232-03-xgboost-kaggle.ipynb`
- `frd232-05-xgboost-blend.ipynb`

### Log naming

Normalize to the notebook stem plus `.log`:

- `titnic-01-eda-and-modeling.log`
- `frd232-04-xgboost-final.log`

## Choosing the 6-character code

Choose a readable 6-character code per competition.

Good properties:

- exactly 6 characters
- easy to recognize
- tied to the competition name when possible

Examples:

- Titanic -> `titnic`
- Fraud detection CPE232 -> `frd232`

Prefer readable compact abbreviations over random strings.

## Workflow

### 1. Inspect the dump

List the contents of `dump/` and identify:

- markdown files
- notebooks
- logs
- whether files appear to belong to one or more competitions

Read lightweight clues before renaming:

- `overview.md`
- `data*.md`
- notebook first markdown title or obvious notebook naming

### 2. Infer the competition folder

Determine:

- competition name
- date to use
- 6-character code

If the user already told you the date, use that. If multiple competitions are mixed together, split them into separate competition folders.

### 3. Move without rewriting content

Create the target folder under `notebooks/` and move files there.

Do not open notebooks and rewrite internals unless the user asks. This skill is primarily for filesystem organization.

### 4. Rename files to standard form

Apply these transformations where reasonable:

- overview markdown -> `overview.md`
- data markdown -> `data.md`
- draft notebook names -> `<code>-NN-short-description.ipynb`
- matching logs -> `<code>-NN-short-description.log`

Use short, clear descriptions based on the existing draft names.

Examples:

- `draft-01-manual-ml.ipynb` -> `frd232-01-manual-ml.ipynb`
- `draft-03-xgboost-kaggle.ipynb` -> `frd232-03-xgboost-kaggle.ipynb`
- `draft-04-xgboost-kaggle.log` -> `frd232-04-xgboost-final.log`

### 5. Verify and report

After moving everything:

- list the final folder contents
- confirm `dump/` still exists
- tell the user exactly what was created and renamed

## Important Safety Notes

- Do not delete user files unless the user clearly wants them removed.
- Do not change notebook code just to make names more consistent.
- Do not overwrite existing competition folders blindly; inspect first.
- If there is ambiguity about whether dumped files belong to multiple competitions, inspect more before moving.

## Expected Output Style

When done, report:

- the created competition folder path
- the new filenames
- whether `dump/` is now empty or still contains leftovers

## Example

**User request:**
"I dropped a bunch of old fraud notebooks into dump. Organize them like the repo structure and rename only, don't touch notebook contents."

**Expected behavior:**

- inspect `dump/`
- infer this is one fraud competition
- create `notebooks/2026-03-06-fraud-detection-cpe232-data-models/`
- rename files with code `frd232`
- move notebooks, logs, `overview.md`, and `data.md`
- leave `dump/` reusable afterward
