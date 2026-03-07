# Titanic - Machine Learning from Disaster

## Competition Overview

**Kaggle Competition:** [Titanic - Machine Learning from Disaster](https://www.kaggle.com/c/titanic)

### Problem Statement
The sinking of the Titanic is one of the most infamous shipwrecks in history. On April 15, 1912, during her maiden voyage, the widely considered "unsinkable" RMS Titanic sank after colliding with an iceberg. Unfortunately, there weren't enough lifeboats for everyone on board, resulting in the death of 1,502 out of 2,224 passengers and crew.

### Objective
Build a predictive model that answers the question: **"What sorts of people were more likely to survive?"** using passenger data (age, gender, ticket class, fare, family relations, etc.).

This is a **binary classification** problem where we need to predict whether a passenger survived (1) or did not survive (0).

### Dataset
- **Training set:** 891 passengers with survival outcomes
- **Test set:** 418 passengers for prediction submission
- **Features:** Passenger demographics, ticket information, and embarkation details

### Approach
1. **Exploratory Data Analysis (EDA):** Understand survival patterns across demographics
2. **Feature Engineering:** Handle missing values, encode categorical features
3. **Modeling:** Train a simple Logistic Regression model for baseline testing
4. **Evaluation:** Calculate accuracy and other metrics
5. **Submission:** Generate predictions for test set

### Expected Outcome
A working Kaggle submission demonstrating the data science workflow from raw data to predictions.

---

**Folder:** `notebooks/2026-03-08-titanic-passenger-survival`

**Last Updated:** 2026-03-08
