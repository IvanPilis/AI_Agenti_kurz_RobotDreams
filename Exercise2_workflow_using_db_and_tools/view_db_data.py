import os

import psycopg2
from datetime import date, timedelta
import random
from dotenv import load_dotenv
from psycopg2 import sql

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

# Query to retrieve all data from transactions table
query = sql.SQL("SELECT * FROM transactions")
cur.execute(query)

# Fetch all rows
rows = cur.fetchall()

# Query to retrieve all data from transactions table
query2 = sql.SQL("SELECT sum(amount) FROM transactions where category='Mortgage' and EXTRACT(YEAR FROM txn_date) = EXTRACT(YEAR FROM CURRENT_DATE);")
cur.execute(query2)
rows2 = cur.fetchall()

print(rows2)
print(len(rows2))


print(rows)
print(len(rows))
