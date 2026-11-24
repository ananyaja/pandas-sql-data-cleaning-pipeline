# Data Dictionary — `cleaned_transactions.csv`

## 1. Dataset Overview
- **File Path:** `03_cleaned/cleaned_transactions.csv`
- **Encoding & Format:** UTF-8 CSV, comma-delimited, header row included
- **Grain / Primary Key:** One unique transaction per row, keyed on `transaction_id`
- **Upstream Source:** `01_raw/messy_transactions.csv`
- **Transformation Script:** `02_scripts/clean_transactions.py`

---

## 2. Schema & Field Definitions

| Column Name | Data Type | Nullable | Format / Allowed Values | Transformation & Business Rules |
| :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | `STRING` (PK) | No | `TXN-XXXX` (Uppercase) | Trimmed whitespace, converted to uppercase, and deduplicated (`keep="first"`). |
| `customer_name` | `STRING` | No | Title Case (`First Last`) | Trimmed leading/trailing whitespace; collapsed internal multiple spaces into a single space. |
| `email_address` | `STRING` | No | Lowercase RFC-style (`user@domain.tld`) | Trimmed whitespace and lowercased. Rows with missing or invalid TLD format are quarantined. |
| `order_date` | `DATE` (`STRING`) | No | ISO 8601 (`YYYY-MM-DD`) | Standardized from 5 mixed input formats (`%Y-%m-%d`, `%d/%m/%Y`, `%m-%d-%Y`, `%d %b %Y`, `%Y/%m/%d`). Unparseable dates are quarantined. |
| `amount` | `DECIMAL(10,2)` | No | Positive float (`0.00`, > `0.00`) | Stripped currency symbols/labels (`$`, `INR`, commas) and rounded to 2 decimal places. Missing, non-numeric (`NULL`, `TBD`), or `<= 0` amounts are quarantined. |
| `payment_status` | `STRING` (Enum) | No | `Completed`, `Pending`, `Failed`, `Refunded`, `Unknown` | Case- and whitespace-normalized against lookup map; blank or unrecognized values (`N/A`) mapped to `Unknown`. |
| `region_city` | `STRING` (Enum) | No | `Mumbai`, `Bengaluru`, `Delhi`, `Cuttack`, `Kolkata`, `Unknown` | Standardized city aliases (`Bangalore` → `Bengaluru`, `New Delhi` → `Delhi`); blank values mapped to `Unknown`. |

---

## 3. Quarantine & Exception Handling (`quarantined_rows.csv`)
Records failing strict integrity checks are excluded from `cleaned_transactions.csv` and preserved untouched (with normalized headers) in `03_cleaned/quarantined_rows.csv` for client review:
1. **Invalid Dates:** Missing dates, non-date strings (`invalid_date`), or impossible calendar dates (e.g., `2026-02-30`).
2. **Invalid Amounts:** Blank values, placeholders (`NULL`, `TBD`), or zero/negative transaction amounts (`<= 0.00`).
3. **Invalid Contact Info:** Blank email addresses or strings failing basic `local@domain.tld` syntax validation.

---

## 4. Reproducibility & Verification
- **Command:** `python 02_scripts/clean_transactions.py`
- **Audit Trail:** Full row-count reconciliations and anomaly counts are recorded in `04_docs/CLEANING_LOG.md`.
