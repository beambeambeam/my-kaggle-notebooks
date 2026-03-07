# Titanic Dataset Description

## Overview
This dataset contains information about passengers aboard the RMS Titanic. The training set includes the actual survival outcomes, while the test set is used for submission predictions.

## Data Files
- **train.csv** - 891 rows, 12 columns (includes target variable)
- **test.csv** - 418 rows, 11 columns (no target variable)

## Features

### PassengerId
- **Type:** Integer
- **Description:** Unique identifier for each passenger
- **Missing Values:** None
- **Range:** 1 - 891 (train), 892 - 1309 (test)

### Pclass (Passenger Class)
- **Type:** Categorical (1, 2, 3)
- **Description:** Ticket class - a proxy for socio-economic status
  - 1 = Upper class
  - 2 = Middle class
  - 3 = Lower class
- **Missing Values:** None
- **Note:** Likely correlated with survival

### Sex
- **Type:** Categorical (male, female)
- **Description:** Gender of the passenger
- **Missing Values:** None
- **Note:** Women had higher survival rates ("women and children first" policy)

### Age
- **Type:** Continuous (numeric)
- **Description:** Age in years
- **Missing Values:** ~19.9% missing
- **Range:** 0.42 - 80
- **Handling:** Can be filled with median/mean or created as a categorical feature (child vs adult)

### SibSp
- **Type:** Integer
- **Description:** Number of siblings/spouses aboard
- **Missing Values:** None
- **Range:** 0 - 8
- **Note:** Can indicate if traveling with family

### Parch
- **Type:** Integer
- **Description:** Number of parents/children aboard
- **Missing Values:** None
- **Range:** 0 - 6
- **Note:** Can indicate if traveling with family

### Ticket
- **Type:** String
- **Description:** Ticket number
- **Missing Values:** None
- **Note:** Can be complex; may need special encoding

### Fare
- **Type:** Continuous (numeric)
- **Description:** Passenger fare paid
- **Missing Values:** 1 missing in test set
- **Range:** 0 - 512.33
- **Note:** Proxy for class/wealth; can be filled with median

### Cabin
- **Type:** String
- **Description:** Cabin number where passenger stayed
- **Missing Values:** ~77% missing
- **Note:** Highly sparse; may extract deck information if available

### Embarked
- **Type:** Categorical (S, C, Q)
- **Description:** Port of embarkation
  - S = Southampton
  - C = Cherbourg
  - Q = Queenstown
- **Missing Values:** 2 missing in train set
- **Handling:** Fill with mode (S)

### Survived (Target Variable - Train Only)
- **Type:** Binary (0, 1)
- **Description:** Survival outcome
  - 0 = Did not survive
  - 1 = Survived
- **Distribution:** ~38% survived, ~62% did not survive (class imbalance)

## Data Quality Summary

| Feature | Type | Missing | Distinct |
|---------|------|---------|----------|
| PassengerId | Integer | 0 | 891 |
| Pclass | Categorical | 0 | 3 |
| Sex | Categorical | 0 | 2 |
| Age | Numeric | 177 (19.9%) | ~88 |
| SibSp | Integer | 0 | 7 |
| Parch | Integer | 0 | 7 |
| Ticket | String | 0 | 681 |
| Fare | Numeric | 0 | 248 |
| Cabin | String | 687 (77.1%) | 147 |
| Embarked | Categorical | 2 (0.2%) | 3 |
| Survived | Binary | 0 | 2 |

## Key Insights for Feature Engineering

1. **Age** - Important predictor but has missing values; consider imputation or binning
2. **Sex** - Strong predictor; women survived at higher rates
3. **Pclass** - Clear survival difference by ticket class
4. **Family Features** - SibSp + Parch can be combined into family size
5. **Fare** - Correlated with Pclass; can be binned into ranges
6. **Cabin** - Highly sparse; extract deck letter if useful, otherwise drop
7. **Embarked** - May have correlations with other features

---

**Folder:** `notebooks/2026-03-08-titanic-passenger-survival`

**Last Updated:** 2026-03-08
