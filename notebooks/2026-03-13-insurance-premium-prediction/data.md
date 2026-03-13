# Dataset Description

The dataset contains detailed records of insurance policyholders, capturing a wide array of personal, financial, and behavioral attributes. The goal is to build a robust regression model to accurately predict the `Premium Amount` billed to each customer.

## Files

- `train.csv`: the training set
- `test.csv`: the test set
- `sample_submission.csv`: a sample submission file in the correct format

## Columns

- `Age`: Age of the insured individual (numerical)
- `Gender`: Gender of the insured individual (categorical: `Male`, `Female`)
- `Annual Income`: Annual income of the insured individual (numerical, skewed)
- `Marital Status`: Marital status of the insured individual (categorical: `Single`, `Married`, `Divorced`)
- `Number of Dependents`: Number of dependents (numerical, with missing values)
- `Education Level`: Highest education level attained (categorical: `High School`, `Bachelor's`, `Master's`, `PhD`)
- `Occupation`: Occupation of the insured individual (categorical: `Employed`, `Self-Employed`, `Unemployed`)
- `Health Score`: A score representing the health status (numerical, skewed)
- `Location`: Type of location (categorical: `Urban`, `Suburban`, `Rural`)
- `Policy Type`: Type of insurance policy (categorical: `Basic`, `Comprehensive`, `Premium`)
- `Previous Claims`: Number of previous claims made (numerical, with outliers)
- `Vehicle Age`: Age of the vehicle insured (numerical)
- `Credit Score`: Credit score of the insured individual (numerical, with missing values)
- `Insurance Duration`: Duration of the insurance policy (numerical, in years)
- `Policy Start Date`: Start date of the insurance policy (text, improperly formatted)
- `Customer Feedback`: Short feedback comments from customers (text)
- `Smoking Status`: Smoking status of the insured individual (categorical: `Yes`, `No`)
- `Exercise Frequency`: Frequency of exercise (categorical: `Daily`, `Weekly`, `Monthly`, `Rarely`)
- `Property Type`: Type of property owned (categorical: `House`, `Apartment`, `Condo`)
- `Premium Amount`: Target variable representing the insurance premium amount (numerical, skewed)
