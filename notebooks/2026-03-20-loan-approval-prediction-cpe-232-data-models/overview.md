# Overview

## Competition Overview

Efficient and accurate loan approval is crucial for financial institutions because they need to balance default risk with the goal of lending to qualified applicants.

In this competition, the task is to build a machine learning model that predicts **`Loan_status`** from applicant demographics, financial information, credit score, and asset values.

This competition is part of the **CPE 232 Data Models** course in the **Computer Engineering program at KMUTT**.
The core learning goals are:

- data cleaning
- data preprocessing
- hyperparameter tuning

---

## Timeline

- **Start:** 2 days ago
- **Close:** 7 days to go

---

## Objective

Train a binary classification model that predicts whether a loan application is:

- `1` for approved
- `0` for rejected

The first notebook draft will focus on:

- loading and validating the dataset
- quick EDA on applicant, credit, and asset features
- a clean preprocessing baseline
- one strong submission-ready classification model

---

## Evaluation

Submissions are evaluated using **F1 Score**.

This makes precision and recall both important, which is useful when approval and rejection errors have different practical costs.

---

## Submission Format

Submit a CSV file with exactly two columns:

| id | Loan_status |
|----|-------------|
| 1  | 1           |
| 2  | 0           |

