# Customer Transactions Data Cleaning & Audit Pipeline

A reproducible Python (Pandas) data-cleaning and documentation workflow that transforms raw, inconsistent transaction exports into a standardized dataset alongside a quarantine file and full audit trail.

## Project Structure

```text
├── 01_raw/
│   └── messy_transactions.csv       # Untouched input dataset (500 rows)
├── 02_scripts/
│   ├── generate_messy_data.py       # Synthetic messy dataset generator
│   └── clean_transactions.py        # Reproducible cleaning & validation script
├── 03_cleaned/
│   ├── cleaned_transactions.csv     # Standardized, deduplicated output
│   └── quarantined_rows.csv         # Anomalous records isolated for review
└── 04_docs/
    ├── CLEANING_LOG.md              # Automated row-count reconciliation & summary
    └── DATA_DICTIONARY.md           # Schema, data types, and business rulesg and documentation workflow that transforms raw, inconsistent transaction exports into a standardized dataset alongside a quarantine file and full audit trail.
