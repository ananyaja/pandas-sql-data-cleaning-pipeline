import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_PATH = Path("01_raw/messy_transactions.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Deliberately inconsistent headers (mixed case, leading/trailing spaces, symbols)
HEADERS = [
    " Transaction ID ",
    "Customer_Name",
    "Email Address",
    "Order Date",
    "Amount ($)",
    "Payment_Status",
    "Region/City",
]

FIRST_NAMES = ["Aarav", "Priya", "Rohan", "Ananya", "Vikram", "Sneha", "Kabir", "Meera", "Arjun", "Diya"]
LAST_NAMES = ["Sharma", "Patel", "Nair", "Das", "Verma", "Reddy", "Gupta", "Joshi", "Rao", "Singh"]
DOMAINS = ["gmail.com", "yahoo.co.in", "outlook.com", "company.org"]
STATUSES = ["Completed", "COMPLETED", "completed ", "Pending", "PENDING", "Failed", "Refunded", "N/A", ""]
CITIES = ["Mumbai", "mumbai", " MUMBAI ", "Bengaluru", "Bangalore", "Delhi", "New Delhi", "Cuttack", "Kolkata", ""]

DATE_FORMATS = [
    "%Y-%m-%d",       # 2026-04-15 (ISO standard)
    "%d/%m/%Y",       # 15/04/2026
    "%m-%d-%Y",       # 04-15-2026
    "%d %b %Y",       # 15 Apr 2026
    "%Y/%m/%d",       # 2026/04/15
]

def random_messy_date():
    base = datetime(2026, 1, 1) + timedelta(days=random.randint(0, 300))
    if random.random() < 0.04:
        return random.choice(["2026-02-30", "invalid_date", ""])  # Malformed / missing dates
    return base.strftime(random.choice(DATE_FORMATS))

def random_messy_amount():
    val = round(random.uniform(15.0, 2500.0), 2)
    style = random.random()
    if style < 0.04:
        return random.choice(["", "NULL", "TBD"])      # Missing / non-numeric
    elif style < 0.08:
        return f"-{val}"                               # Negative amount anomaly
    elif style < 0.25:
        return f"${val:,.2f}"                          # Currency symbol + comma
    elif style < 0.40:
        return f" {val} INR "                          # Trailing currency text + spaces
    return str(val)

def make_row(txn_num):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    full_name = f"{first} {last}"
    if random.random() < 0.20:
        full_name = f"  {full_name.upper()} " if random.random() < 0.5 else full_name.lower()

    email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{random.choice(DOMAINS)}"
    if random.random() < 0.07:
        email = ""                                     # Missing email
    elif random.random() < 0.05:
        email = f"{first.lower()}@{last.lower()}"      # Invalid email format (missing TLD)

    txn_id = f"TXN-{1000 + txn_num}"
    if random.random() < 0.15:
        txn_id = f" txn-{1000 + txn_num} "             # Lowercase + whitespace

    return [
        txn_id,
        full_name,
        email,
        random_messy_date(),
        random_messy_amount(),
        random.choice(STATUSES),
        random.choice(CITIES),
    ]

def main():
    rows = [make_row(i) for i in range(1, 476)]

    # Inject 25 exact and near-duplicate rows to hit 500 total rows
    for _ in range(25):
        dup = list(random.choice(rows))
        if random.random() < 0.5:
            dup[0] = dup[0].strip().lower()            # Near-duplicate ID casing/spacing
        rows.append(dup)

    random.shuffle(rows)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(rows)

    print(f"Generated {len(rows)} messy rows at: {OUTPUT_PATH.resolve()}")

if __name__ == "__main__":
    main()
