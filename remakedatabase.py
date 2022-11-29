import sqlite3


conn = sqlite3.connect('Database.db')
c = conn.cursor()


# get all the tables
c.execute("SELECT name FROM sqlite_master WHERE type='table';")

# # for all the tables add new columns
for table in c.fetchall():
    c.execute("ALTER TABLE " + table[0] + " ADD COLUMN 'Project' TEXT")
    c.execute(
        "CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, Wealth STRING, Learning STRING, Project TEXT, Description STRING, Date STRING)".format(
            table[0]+"_new"))
    c.execute("INSERT INTO {} (id, Wealth, Learning, Project, Description, Date) SELECT id, Wealth, Learning, Project, Description, Date FROM {}".format(
        table[0]+"_new", table[0]))
    c.execute("DROP TABLE {}".format(table[0]))
    c.execute("ALTER TABLE {} RENAME TO {}".format(table[0]+"_new", table[0]))


# commit the changes
conn.commit()
