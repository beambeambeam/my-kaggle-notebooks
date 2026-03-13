# Overview

Accurate premium pricing is the cornerstone of a sustainable insurance ecosystem, ensuring that policyholders are charged fairly based on their unique risk profiles. In this competition, your challenge is to build a machine learning model that can precisely estimate Insurance Premium Amounts based on a diverse array of customer attributes.

Participants will work with a comprehensive dataset containing detailed records of policyholders, encompassing demographic data, financial history, and lifestyle indicators—such as health scores, smoking status, and previous claims history. The goal is to predict the continuous value of the Premium Amount using these features, helping to bridge the gap between individual risk and financial coverage.

This competition is part of the CPE232 Data Models course in the Computer Engineering program at KMUTT. The primary goal is to help students enhance their practical skills in data cleaning, preprocessing, and hyperparameter tuning, which are essential for building high-performing machine learning models.

## Evaluation

Submissions will be evaluated using Mean Absolute Error (MAE). This metric measures the average magnitude of prediction errors without considering direction, using the average absolute difference between predicted insurance premiums and actual values.

Formula:

```text
MAE = (1 / n) * sum(|y_i - y_hat_i|)
```

Lower MAE is better.

## Submission File

Participants should submit a CSV file with the following columns:

| id | Premium Amount |
| --- | --- |
| 520001 | 1 |
| 520002 | 0 |
| 520003 | 0 |
