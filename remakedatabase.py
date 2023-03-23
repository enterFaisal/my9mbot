import sqlite3


conn = sqlite3.connect('Database.db')
c = conn.cursor()

# id INTEGER PRIMARY KEY, Wealth TEXT, Learning TEXT,Project TEXT, Description TEXT, Date TEXT
# add income to U1015728318 table to before last column

c.execute("ALTER TABLE U1015728318 ADD COLUMN Income TEXT")
# make the date last column
c.execute("ALTER TABLE U1015728318 ADD COLUMN Date_new TEXT")
# copy the old date column to the new date column
c.execute("UPDATE U1015728318 SET Date_new = Date")
c.execute("ALTER TABLE U1015728318 DROP COLUMN Date")
c.execute("ALTER TABLE U1015728318 RENAME COLUMN Date_new TO Date")

# make Income = 990
c.execute("UPDATE U1015728318 SET Income = 990")


conn.commit()
conn.close()

print("Database updated")


# # commit the changes
# conn.commit()
