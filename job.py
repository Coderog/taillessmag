from settings import *
import sqlite3

conn = sqlite3.connect(DB_NAME)
curs = conn.cursor()

curs.execute('''UPDATE meta SET value = ? WHERE item = 'done';''', (len([i for i in curs.execute('SELECT id FROM pages')]),))
curs.execute('''UPDATE meta SET value = ? WHERE item = 'detailed';''', (len([i for i in curs.execute('SELECT id FROM pages WHERE done = 1')]),))

conn.commit()
conn.close()