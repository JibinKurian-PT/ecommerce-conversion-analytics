import pandas as pd
import mysql.connector
from getpass import getpass
import time
from pathlib import Path

# ============================================================
# 1. FILE PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

file_path = PROJECT_DIR / "data" / "processed" / "final_time_aware_events.csv"

CHUNK_SIZE = 10000


# ============================================================
# 2. CONNECT TO MYSQL
# ============================================================

print("=" * 60)
print("CONNECTING TO MYSQL")
print("=" * 60)

password = getpass("Enter your MySQL root password: ")

connection = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=password,
    database="retail_analytics"
)

cursor = connection.cursor()

print("MySQL connection successful.\n")


# ============================================================
# 3. CLEAR EXISTING DATA
# ============================================================

print("Clearing existing fact_events data...")

cursor.execute("DELETE FROM fact_events")
connection.commit()

print("fact_events is empty.\n")


# ============================================================
# 4. INSERT QUERY
# ============================================================

insert_query = """
INSERT INTO fact_events (
    event_row_id,
    event_timestamp,
    visitorid,
    event,
    itemid,
    transactionid,
    categoryid,
    available,
    category_property_timestamp,
    availability_property_timestamp
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""


# ============================================================
# 5. HELPER FUNCTION
# ============================================================

def clean_integer(value):

    if pd.isna(value):
        return None

    return int(value)


# ============================================================
# 6. IMPORT CSV IN CHUNKS
# ============================================================

print("=" * 60)
print("STARTING EVENT IMPORT")
print("=" * 60)

start_time = time.time()

total_inserted = 0


for chunk_number, df in enumerate(
    pd.read_csv(
        file_path,
        chunksize=CHUNK_SIZE
    ),
    start=1
):

    data = []

    # --------------------------------------------------------
    # Use COLUMN NAMES instead of positions
    # --------------------------------------------------------

    for row in df.itertuples(index=False):

        event_row_id = int(row.event_row_id)

        event_timestamp = int(row.timestamp)

        visitorid = int(row.visitorid)

        event = row.event

        itemid = int(row.itemid)

        transactionid = clean_integer(row.transactionid)

        categoryid = clean_integer(row.categoryid)

        category_property_timestamp = clean_integer(
            row.category_property_timestamp
        )

        available = clean_integer(
            row.available
        )

        availability_property_timestamp = clean_integer(
            row.availability_property_timestamp
        )

        data.append(
            (
                event_row_id,
                event_timestamp,
                visitorid,
                event,
                itemid,
                transactionid,
                categoryid,
                available,
                category_property_timestamp,
                availability_property_timestamp
            )
        )


    # --------------------------------------------------------
    # INSERT CURRENT CHUNK
    # --------------------------------------------------------

    cursor.executemany(
        insert_query,
        data
    )

    connection.commit()

    total_inserted += len(data)

    elapsed = time.time() - start_time

    print(
        f"Chunk {chunk_number:4d} | "
        f"Inserted: {total_inserted:,} rows | "
        f"Time: {elapsed / 60:.2f} min"
    )


# ============================================================
# 7. VERIFY TOTAL ROW COUNT
# ============================================================

print("\n" + "=" * 60)
print("IMPORT COMPLETED")
print("=" * 60)

cursor.execute("""
SELECT COUNT(*)
FROM fact_events
""")

mysql_count = cursor.fetchone()[0]

print(f"Rows inserted by Python : {total_inserted:,}")
print(f"Rows currently in MySQL : {mysql_count:,}")


# ============================================================
# 8. EVENT DISTRIBUTION
# ============================================================

print("\nEvent distribution in MySQL:")

cursor.execute("""
SELECT
    event,
    COUNT(*) AS event_count
FROM fact_events
GROUP BY event
ORDER BY event_count DESC
""")

for event, count in cursor.fetchall():

    print(
        f"{event:12s} : {count:,}"
    )


# ============================================================
# 9. AVAILABLE DISTRIBUTION
# ============================================================

print("\nAvailable distribution in MySQL:")

cursor.execute("""
SELECT
    available,
    COUNT(*) AS row_count
FROM fact_events
GROUP BY available
ORDER BY available
""")

for available, count in cursor.fetchall():

    print(
        f"{str(available):12s} : {count:,}"
    )


# ============================================================
# 10. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\nMySQL connection closed.")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
