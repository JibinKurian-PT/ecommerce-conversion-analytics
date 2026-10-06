import pandas as pd
import mysql.connector
from getpass import getpass
from pathlib import Path

# ============================================================
# 1. FILE PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

file_path = PROJECT_DIR / "data" / "raw" / "category_tree.csv"

# ============================================================
# 2. LOAD CSV
# ============================================================

print("Loading category_tree.csv...")

df = pd.read_csv(file_path)

print(f"Category rows found: {len(df)}")
print(f"Columns: {list(df.columns)}")


# ============================================================
# 3. CONNECT TO MYSQL
# ============================================================

print("\nConnecting to MySQL...")

password = getpass("Enter your MySQL root password: ")

connection = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=password,
    database="retail_analytics"
)

cursor = connection.cursor()

print("MySQL connection successful.")


# ============================================================
# 4. CLEAR EXISTING CATEGORY DATA
# ============================================================

print("\nClearing existing category data...")

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
cursor.execute("DELETE FROM fact_events")
cursor.execute("DELETE FROM dim_category")

connection.commit()

print("Existing category data cleared.")


# ============================================================
# 5. PREPARE DATA
# ============================================================

insert_query = """
INSERT INTO dim_category
(categoryid, parentid)
VALUES (%s, %s)
"""

data = []

for row in df.itertuples(index=False):

    categoryid = int(row.categoryid)

    if pd.isna(row.parentid):
        parentid = None
    else:
        parentid = int(row.parentid)

    data.append((categoryid, parentid))


# ============================================================
# 6. INSERT DATA
# ============================================================

print("\nInserting categories into MySQL...")

cursor.executemany(insert_query, data)

cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

connection.commit()

print(f"Inserted rows: {cursor.rowcount}")


# ============================================================
# 7. VERIFY ROW COUNT
# ============================================================

cursor.execute("""
SELECT COUNT(*)
FROM dim_category
""")

count = cursor.fetchone()[0]

print(f"\nRows currently in dim_category: {count}")


# ============================================================
# 8. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL connection closed.")

print("\n========================================")
print("CATEGORY IMPORT COMPLETED")
print("========================================")
