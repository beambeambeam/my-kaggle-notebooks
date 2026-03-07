---
name: create-kaggle-competition-from-template
description: Create a new Kaggle competition workspace in this repo from `templates/kaggle.ipynb`. Use this whenever the user wants to start a new competition, create a fresh notebook folder, scaffold a new Kaggle draft, copy the repo template, or set up `overview.md`, `data.md`, and the first draft notebook under `notebooks/YYYY-MM-DD-competition-name/`. Trigger even if the user only says things like "start a new competition", "make a notebook folder for X", or "set up the Kaggle template for this comp".
---

# Create Kaggle Competition From Template

Use this skill to create a new competition folder in this repository using the standard project structure and `templates/kaggle.ipynb` as the starter notebook.

## Goal

Set up a fresh competition workspace with:

- `notebooks/YYYY-MM-DD-competition-name/`
- `overview.md`
- `data.md`
- first notebook draft copied from `templates/kaggle.ipynb`
- a readable 6-character competition code
- draft notebook naming that matches repo conventions

## Core Rules

- Always follow the repository structure described in `AGENTS.md`.
- Use `templates/kaggle.ipynb` as the default notebook starter unless the user asks for a different base.
- Use lowercase markdown names:
  - `overview.md`
  - `data.md`
- Prefer creating only the first draft notebook unless the user asks for more.
- Do not invent shared helper packages or `src/` structure.
- Keep the notebook self-contained.

## Required Output Structure

Create folders like:

- `notebooks/2026-03-08-titanic-passenger-survival/`
- `notebooks/2026-03-06-fraud-detection-cpe232-data-models/`

Inside the competition folder, usually create:

- `overview.md`
- `data.md`
- `<code>-01-short-description.ipynb`

## Naming Rules

### Competition folder

Use:

- `notebooks/YYYY-MM-DD-competition-name/`

Convert the competition name into a lowercase hyphenated folder name.

### Competition code

Choose a readable 6-character slug.

Good properties:

- exactly 6 characters
- easy to recognize
- tied to the competition name

Examples:

- Titanic -> `titnic`
- Fraud detection CPE232 -> `frd232`

### Notebook name

Use:

- `<code>-01-short-description.ipynb`

Examples:

- `titnic-01-eda-and-modeling.ipynb`
- `frd232-01-baseline-kaggle.ipynb`

The short description should be concise and reflect the first draft goal.

### Internal notebook slug

After copying the template notebook, update `NOTEBOOK_SLUG` inside the notebook so it exactly matches the new filename without `.ipynb`.

## Workflow

### 1. Gather or infer inputs

Determine:

- competition date
- competition name
- 6-character code
- first draft short description

If the user gave a clear competition name and date, use them directly.

### 2. Create the folder

Create:

- `notebooks/YYYY-MM-DD-competition-name/`

### 3. Add markdown files

Create:

- `overview.md`
- `data.md`

These can start as simple placeholders if the user did not provide details yet.

### 4. Copy the notebook template

Copy:

- `templates/kaggle.ipynb`

to:

- `notebooks/YYYY-MM-DD-competition-name/<code>-01-short-description.ipynb`

Then update inside the copied notebook:

- `COMPETITION`
- `ID_COL`
- `LABEL_COL`
- `NOTEBOOK_SLUG`

Only fill what is known. If target columns are not known yet, keep placeholders but still make the notebook filename and slug correct.

### 5. Verify and report

After creation:

- list the created files
- confirm the notebook filename
- confirm the chosen 6-character code
- mention any placeholders the user still needs to customize

## What To Put In The Markdown Files

### `overview.md`

Include a minimal but useful starting structure:

- competition name
- competition link if known
- problem statement
- objective
- high-level first-draft plan

### `data.md`

Include a minimal but useful starting structure:

- dataset summary
- important files
- target variable
- feature notes
- missing values or open questions

If details are not known, write short placeholders rather than hallucinating specifics.

## Safety Notes

- Do not overwrite an existing competition folder without checking first.
- Do not create extra notebooks unless the user asks.
- Do not add logs, CSVs, or generated outputs.
- Keep the first draft notebook template-focused and repo-consistent.

## Expected Output Style

When finished, report:

- the created competition folder path
- the created markdown files
- the created notebook path
- the chosen 6-character code
- any fields still needing manual customization inside the notebook

## Example

**User request:**
"Set up a new Kaggle competition folder for Titanic on 2026-03-08 and make the first notebook from the template."

**Expected behavior:**

- create `notebooks/2026-03-08-titanic-passenger-survival/`
- create `overview.md`
- create `data.md`
- copy `templates/kaggle.ipynb` to `titnic-01-eda-and-modeling.ipynb`
- update `NOTEBOOK_SLUG` to `titnic-01-eda-and-modeling`
- report the created structure back to the user
