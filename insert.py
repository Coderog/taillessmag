import sqlite3
from settings import *

conn = sqlite3.connect(DB_NAME)
curs = conn.cursor()

try:
    while True:
        url = input('Url? ')
        curs.execute('INSERT INTO pages VALUES ((SELECT MAX(id) FROM pages) + 1, ?, 0, \'\', \'\', \'\')', (url,))
except sqlite3.Error:
    quit()
except KeyboardInterrupt:
    conn.commit()
    conn.close()
