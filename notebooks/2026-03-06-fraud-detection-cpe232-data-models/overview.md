# Overview

## Competition Overview

Fraudulent transactions pose a major risk in financial systems. They affect both financial institutions and individuals.
In this competition, you will build a machine learning model that detects fraudulent activity using transaction-level data.

Participants will work with a simulated dataset that contains detailed financial transaction records.
These include sender and recipient balances, transaction types, and flagged illegal attempts.

The goal is to predict whether a transaction is fraudulent (`is_fraud`) using the provided features.

This competition is part of the **CPE232 Data Models** course in the **Computer Engineering program at KMUTT**.
The main purpose is to help students improve practical skills in:

- data cleaning
- data preprocessing
- hyperparameter tuning

These skills are important for building strong machine learning models.

---

## Timeline

- **Start:** a day ago
- **Close:** 6 days to go

---

# Description

## Learning Outcomes

By joining this competition, students will improve their skills in:

- **Data Cleaning**
  Handling missing values, dealing with outliers, and preparing data for model training.

- **Data Preprocessing**
  Encoding categorical variables, feature scaling, and transforming data for better model performance.

- **Hyperparameter Tuning**
  Adjusting model parameters to improve accuracy and generalization.

---

# Evaluation

Submissions are evaluated using **F1 Macro**.

This metric balances **precision** and **recall** across both classes.
It helps ensure fair evaluation even when the dataset is imbalanced.

---

# Submission Format

Participants must submit a **CSV file** with the following columns:

| id      | is_fraud |
|---------|----------|
| 5408227 | 1        |
| 5408228 | 0        |
| 5408229 | 0        |
