from settings import *
import sqlite3

conn = sqlite3.connect(DB_NAME)
curs = conn.cursor()

while True:
    try:
        for i in curs.execute(input('> ')):
            print(i)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        conn.commit()
        conn.close()
        print('\nsaved.')
        quit()
