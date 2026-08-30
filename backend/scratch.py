import sqlite3
conn = sqlite3.connect('./data/rag_grow.db')
c = conn.cursor()
c.execute("SELECT content FROM raw_documents WHERE url LIKE '%hdfc-large%'")
row = c.fetchone()
print(row[0] if row else 'Not found')
