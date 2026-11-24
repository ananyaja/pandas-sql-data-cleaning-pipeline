# Data Quality & Cleaning Log

## 1. Input Summary
- **Source File:** `01_raw/messy_transactions.csv`
- **Initial Shape:** 500 rows × 7 columns
- **Target Output:** `03_cleaned/cleaned_transactions.csv` (UTF-8 CSV)

## 2. Anomalies Detected & Handled
- **Duplicate `transaction_id` Rows Removed:** 25 (case- and whitespace-normalized before deduplication)
- **Invalid / Unparseable Dates:** 15 rows flagged
- **Missing, Non-Numeric, or Non-Positive Amounts:** 32 rows flagged
- **Missing or Malformed Emails:** 50 rows flagged
- **Total Quarantined Rows (`03_cleaned/quarantined_rows.csv`):** 91

## 3. Output Verification
- **Clean Rows Written:** 384 rows × 7 columns
- **Reproducibility:** Run `python 02_scripts/clean_transactions.py` from the project root.
