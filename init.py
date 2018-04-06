from settings import *
import sqlite3

conn = sqlite3.connect(DB_NAME)
curs = conn.cursor()

curs.execute('CREATE TABLE pages (id INT UNIQUE, url TEXT UNIQUE, done INT, title TEXT, content TEXT, linksto TEXT)')
# curs.execute('INSERT INTO pages VALUES (0, ?, 0, \'\')', (START_URL,))

conn.commit()
conn.close()
