import sqlite3
import sys


db = sqlite3.connect(sys.argv[1])
tables = db.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()
for name, schema in tables:
    print(name, schema)
    print(db.execute(f'SELECT * FROM "{name}" LIMIT 20').fetchall())
