# Dataset Description

The dataset contains detailed records of financial transactions.
These include sender and recipient balances, transaction types, and flagged illegal attempts.

Your task is to use these features to predict **`is_fraud`**, which shows whether a transaction was made by a fraudulent agent.

---

# Files

- **train.csv** — training dataset
- **test.csv** — test dataset
- **sample_submission.csv** — example submission file with the correct format

---

# Columns

- **time_ind**
  Simulation time unit.
  `step = 1` equals **1 hour**.
  Total **744 steps = 30 days**.

- **transac_type**
  Type of transaction.
  Possible values: `CASH-IN`, `CASH-OUT`, `DEBIT`, `PAYMENT`, `TRANSFER`.

- **amount**
  Transaction amount (local currency).

- **src_acc**
  Customer who initiates the transaction.

- **src_bal**
  Sender balance before the transaction.

- **src_new_bal**
  Sender balance after the transaction.

- **dst_acc**
  Transaction recipient.

- **dst_bal**
  Recipient balance before the transaction.
  Missing for merchants.

- **dst_new_bal**
  Recipient balance after the transaction.
  Missing for merchants.

- **is_fraud**
  Indicates transactions made by fraudulent agents.
  This is the **target variable**.

- **is_flagged_fraud**
  Transactions flagged as illegal attempts.
  Example: transferring more than **200,000** in one transaction.
