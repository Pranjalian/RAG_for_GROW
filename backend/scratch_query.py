import sqlite3
conn = sqlite3.connect('data/rag_grow.db')
cursor = conn.cursor()

tables = ['news_tracking', 'nfo_tracking']
for table in tables:
    print(f"\n--- Searching in {table} ---")
    cursor.execute(f"SELECT * FROM {table}")
    cols = [col[0] for col in cursor.description]
    for row in cursor.fetchall():
        row_str = " ".join(str(val).lower() for val in row)
        if 'franklin' in row_str or 'multi cap' in row_str:
            print(dict(zip(cols, row)))
