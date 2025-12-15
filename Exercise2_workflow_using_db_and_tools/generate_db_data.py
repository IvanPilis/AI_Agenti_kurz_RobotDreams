import os

import psycopg2
from datetime import date, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

# --- DB CONFIG ---
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="personal_finances",
    user="ivanp",
    password=os.environ['POSTGRES_DB_PASSWORD']
)

cur = conn.cursor()

# --- CREATE TABLE ---
cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    txn_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    category TEXT NOT NULL
);
""")
conn.commit()

cur.execute("""
DELETE FROM transactions;
""")
conn.commit()


# --- CATEGORIES ---
INCOME = "Income"
MORTGAGE = "Mortgage"
CAR = "Car Leasing"
INSURANCE = "Insurance"
GROCERIES = "Groceries"
ENTERTAINMENT = "Entertainment"
UTILITIES = "Utilities"
CHILDREN = "Children"
SAVINGS = "Savings"

categories = [
    (MORTGAGE, -1800),
    (CAR, -450),
    (INSURANCE, -300),
    (UTILITIES, -250),
    (GROCERIES, -700),
    (ENTERTAINMENT, -350),
    (CHILDREN, -600),
    (SAVINGS, -1000),
]

# --- GENERATE DATA (5 years monthly) ---
start_date = date.today().replace(year=date.today().year - 5, day=1)
rows = []

current = start_date
while current <= date.today():
    # Salary (bank employee, good income)
    rows.append((
        current,
        "Monthly salary",
        6500.00,
        INCOME
    ))

    # Expenses
    for cat, base_amount in categories:
        amount = base_amount + random.uniform(-50, 50)
        rows.append((
            current,
            f"{cat}",
            round(amount, 2),
            cat
        ))

    # Advance one month
    next_month = current.month + 1
    year = current.year + (next_month // 13)
    month = next_month if next_month <= 12 else 1
    current = current.replace(year=year, month=month)

# --- INSERT DATA ---
cur.executemany("""
INSERT INTO transactions (txn_date, description, amount, category)
VALUES (%s, %s, %s, %s)
""", rows)

conn.commit()
cur.close()
conn.close()

print(f"Inserted {len(rows)} transactions.")