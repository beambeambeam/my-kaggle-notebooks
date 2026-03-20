# Dataset Description

This dataset contains real-world style loan application records for a binary approval prediction task.

Each row represents one applicant and includes demographic, financial, credit, and asset-related features that can be used to predict **`Loan_status`**.

---

## Files

- **train.csv** - training dataset with features and `Loan_status`
- **test.csv** - test dataset with features only
- **sample_submission.csv** - example submission format

---

## Target

- **`Loan_status`**
  `1` means approved and `0` means rejected.

---

## Feature Notes

- **`id`** - unique applicant identifier used for submission
- **`No_of_dependents`** - number of dependents
- **`Education`** - graduate or not graduate
- **`Self_employed`** - whether the applicant is self-employed
- **`Income_annum`** - annual income
- **`Loan_amount`** - requested loan amount
- **`Loan_term`** - repayment term in years
- **`Cibil_score`** - creditworthiness score
- **`Residential_assets_value`** - residential asset value
- **`Commercial_assets_value`** - commercial asset value
- **`Luxury_assets_value`** - luxury asset value
- **`Bank_asset_value`** - bank balance or liquid assets

---

## Open Questions

- Check for missing values across categorical and numeric columns.
- Inspect whether income, loan, and asset features need scaling or log transforms.
- Compare class balance before choosing thresholding or validation strategy.
