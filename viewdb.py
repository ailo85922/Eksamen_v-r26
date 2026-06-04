import sqlite3

conn = sqlite3.connect("game.db")
c = conn.cursor()

c.execute("SELECT * FROM scores")
print(c.fetchall())

conn.close()