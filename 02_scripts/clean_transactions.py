import re
from pathlib import Path
import pandas as pd

INPUT_CSV = Path("01_raw/messy_transactions.csv")
OUTPUT_DIR = Path("03_cleaned")
DOCS_DIR = Path("04_docs")

CLEAN_CSV = OUTPUT_DIR / "cleaned_transactions.csv"
QUARANTINE_CSV = OUTPUT_DIR / "quarantined_rows.csv"
LOG_MD = DOCS_DIR / "CLEANING_LOG.md"

CITY_MAP = {
    "mumbai": "Mumbai",
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "new delhi": "Delhi",
    "delhi": "Delhi",
    "cuttack": "Cuttack",
    "kolkata": "Kolkata",
}

STATUS_MAP = {
    "completed": "Completed",
    "pending": "Pending",
    "failed": "Failed",
    "refunded": "Refunded",
}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def standardize_headers(df: pd.DataFrame) -> pd.DataFrame:
    cleaned_cols = []
    for col in df.columns:
        s = col.strip().lower()
        s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
        cleaned_cols.append(s)
    df = df.copy()
    df.columns = cleaned_cols
    return df


def parse_amount(series: pd.Series) -> pd.Series:
    def _clean_one(val):
        if pd.isna(val):
            return None
        s = str(val).strip()
        if s == "" or s.upper() in {"NULL", "TBD", "NAN", "N/A"}:
            return None
        # Strip currency symbols/codes and commas while preserving sign and decimals
        s = re.sub(r"(?i)\b(inr|usd|rs)\b", "", s)
        s = re.sub(r"[^0-9.\-]", "", s)
        if s in {"", "-", "."}:
            return None
        try:
            return round(float(s), 2)
        except ValueError:
            return None

    return series.apply(_clean_one)


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    # Try explicit common formats first to avoid day/month ambiguity where clear,
    # then fall back to flexible parsing for remaining strings.
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d %b %Y", "%Y/%m/%d"]
    parsed = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")

    for idx, raw in series.items():
        if pd.isna(raw):
            continue
        s = str(raw).strip()
        if not s or s.lower() in {"invalid_date", "nan", "nat"}:
            continue

        matched = None
        for fmt in formats:
            try:
                matched = pd.to_datetime(s, format=fmt, errors="raise")
                break
            except ValueError:
                continue

        if matched is None:
            matched = pd.to_datetime(s, errors="coerce")

        if pd.notna(matched):
            parsed.at[idx] = matched.normalize()

    return parsed


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Read everything as string first so nothing gets silently coerced before inspection
    raw_df = pd.read_csv(INPUT_CSV, dtype=str, keep_default_na=False)
    initial_rows, initial_cols = raw_df.shape

    df = standardize_headers(raw_df)

    # Normalize IDs and text fields
    df["transaction_id"] = df["transaction_id"].str.strip().str.upper()
    df["customer_name"] = (
        df["customer_name"]
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )
    df["email_address"] = df["email_address"].str.strip().str.lower()

    status_clean = df["payment_status"].str.strip().str.lower()
    df["payment_status"] = status_clean.map(STATUS_MAP).fillna("Unknown")

    city_clean = df["region_city"].str.strip().str.lower()
    df["region_city"] = city_clean.map(CITY_MAP).fillna("Unknown")

    df["order_date_parsed"] = parse_mixed_dates(df["order_date"])
    df["amount_parsed"] = parse_amount(df["amount"])

    # Deduplicate by transaction_id (keep first occurrence after trimming/uppercasing)
    dup_mask = df.duplicated(subset=["transaction_id"], keep="first")
    duplicates_removed = int(dup_mask.sum())
    df = df.loc[~dup_mask].copy()

    # Flag anomalies for quarantine vs. clean output
    invalid_date_mask = df["order_date_parsed"].isna()
    missing_or_neg_amount_mask = df["amount_parsed"].isna() | (df["amount_parsed"] <= 0)
    invalid_email_mask = ~df["email_address"].apply(lambda e: bool(EMAIL_RE.match(e)))

    quarantine_mask = invalid_date_mask | missing_or_neg_amount_mask | invalid_email_mask
    quarantined_df = df.loc[quarantine_mask].copy()
    clean_df = df.loc[~quarantine_mask].copy()

    # Format final output columns cleanly
    clean_out = pd.DataFrame({
        "transaction_id": clean_df["transaction_id"],
        "customer_name": clean_df["customer_name"],
        "email_address": clean_df["email_address"],
        "order_date": clean_df["order_date_parsed"].dt.strftime("%Y-%m-%d"),
        "amount": clean_df["amount_parsed"].map(lambda x: f"{x:.2f}"),
        "payment_status": clean_df["payment_status"],
        "region_city": clean_df["region_city"],
    })

    clean_out.to_csv(CLEAN_CSV, index=False, encoding="utf-8")
    quarantined_df.to_csv(QUARANTINE_CSV, index=False, encoding="utf-8")

    log_content = f"""# Data Quality & Cleaning Log

## 1. Input Summary
- **Source File:** `{INPUT_CSV}`
- **Initial Shape:** {initial_rows} rows × {initial_cols} columns
- **Target Output:** `{CLEAN_CSV}` (UTF-8 CSV)

## 2. Anomalies Detected & Handled
- **Duplicate `transaction_id` Rows Removed:** {duplicates_removed} (case- and whitespace-normalized before deduplication)
- **Invalid / Unparseable Dates:** {int(invalid_date_mask.sum())} rows flagged
- **Missing, Non-Numeric, or Non-Positive Amounts:** {int(missing_or_neg_amount_mask.sum())} rows flagged
- **Missing or Malformed Emails:** {int(invalid_email_mask.sum())} rows flagged
- **Total Quarantined Rows (`03_cleaned/quarantined_rows.csv`):** {len(quarantined_df)}

## 3. Output Verification
- **Clean Rows Written:** {len(clean_out)} rows × {clean_out.shape[1]} columns
- **Reproducibility:** Run `python 02_scripts/clean_transactions.py` from the project root.
"""
    LOG_MD.write_text(log_content, encoding="utf-8")

    print(f"Initial rows: {initial_rows}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Quarantined rows: {len(quarantined_df)}")
    print(f"Clean rows saved: {len(clean_out)} -> {CLEAN_CSV}")
    print(f"Audit log saved -> {LOG_MD}")


if __name__ == "__main__":
    main()
