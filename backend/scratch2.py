import sqlite3
import json

conn = sqlite3.connect('./data/rag_grow.db')
c = conn.cursor()
c.execute("SELECT url, label FROM source_urls WHERE label LIKE '%hdfc%' OR label LIKE '%large%'")
rows = c.fetchall()
for r in rows:
    print(r)

c.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", c.fetchall())

try:
    c.execute("SELECT url, content FROM raw_documents WHERE url LIKE '%hdfc%' OR url LIKE '%large%'")
    docs = c.fetchall()
    for d in docs:
        print(d[0], d[1][:200].encode('ascii', 'ignore'))
except Exception as e:
    print("Error:", e)
