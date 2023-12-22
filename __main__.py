import sys
import datetime
import calendar
import csv
import time
import os
import sqlite3
import schedule
import matplotlib.pyplot as plt
from sets import bot
from asking import ask


# date = 2018-01-01 00:00:00.000000
datenow = "2018-01-01"


############################## database ########################################

class Database:
    def __init__(self, chat_id):
        self.conn = sqlite3.connect('Database.db')
        self.c = self.conn.cursor()
        self.chat_id = "U"+str(chat_id)
        # create table if not exists named after chat_id
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, Wealth STRING, Learning STRING, Project STRING, Description STRING,Income STRING, Date STRING)".format(self.chat_id))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def insert(self, wealth, income, learning, Project, description, date):
        self.c.execute(
            "INSERT INTO {} (Wealth,  Learning, Project, Description,Income, Date) VALUES (?, ?, ?, ?, ?, ?)".format(
                self.chat_id), (wealth,  learning, Project, description, income, date))

        self.conn.commit()

    def update(self, wealth, learning, Project,   description, income,  date, id):
        self.c.execute(
            "UPDATE {} SET Wealth = ?, Learning = ?, Project = ?, Description = ?,Income = ?, Date = ? WHERE id = ?".format(
                self.chat_id), (wealth,  learning, Project, description, income, date, id))
        self.conn.commit()

    def singleUpdate(self, id, **kwargs):
        for key, value in kwargs.items():
            self.c.execute(
                "UPDATE {} SET {} = ? WHERE id = ?".format(
                    self.chat_id, key), (value, id))
            self.conn.commit()

    def delete(self, id):
        self.c.execute("DELETE FROM {} WHERE id = ?".format(
            self.chat_id), (id,))
        self.conn.commit()

    def select(self, id):
        self.c.execute("SELECT * FROM {} WHERE id = ?".format(
            self.chat_id), (id,))
        return self.c.fetchall()

    def selectAll(self):
        self.c.execute("SELECT * FROM {}".format(self.chat_id))
        return self.c.fetchall()

    def tableNames():
        conn = sqlite3.connect('Database.db')
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        conn.close()
        return tables

    def __str__(self):
        return "Database({})".format(self.chat_id)

############################## end database ####################################


# Create a function to handle the "/start" and "/help" commands
@bot.message_handler(commands=['start', 'help'])
def replydate(message):
    bot.reply_to(
        message, "Hello, I am a bot that will help you calculate your wealth.\n"
        "i will ask you in the first day of the month.\n")
    bot.send_message(message.chat.id, "send /help to see this massage again.\n"
                     "send /date to see how many days left.\n"
                     "send /run to start.\n"
                     "send /file to get your data.\n"
                     "send /stop to stop.\n"
                     "send /add to add data.\n"
                     "send /delete to delete data.\n"
                     "send /update to update data.\n"
                     "send /status to see the run status.\n"
                     "send /graph to see the graph of your wealth.\n")


# Create a function to handle the "/date" command
@bot.message_handler(commands=['date'])
def replydate(message):
    today = datetime.date.today()
    lastday = datetime.date(today.year, today.month,
                            calendar.monthrange(today.year, today.month)[1])
    bot.reply_to(message, "There are {} days left.".format(
        (lastday - today).days))


# Create a function to handle the "/run" command
@bot.message_handler(commands=['run'])
def replydate(message):
    global isrun
    try:
        if isrun:
            bot.reply_to(message, "The bot is already running.")
        else:
            raise Exception
    except:
        isrun = True
        # chat_id = message.chat.id
        # db = Database(chat_id)

        bot.reply_to(message, "Hello, I am a bot that will help you calculate your wealth.\n"
                     "i will ask you in the first day of the month.\n")
        schedule.every().day.at("00:00").do(run, message)

        while isrun:
            schedule.run_pending()
            time.sleep(30)


def run(message):
    global datenow
    print("run")

    today = datetime.date.today()
    lastday = datetime.date(today.year, today.month,
                            calendar.monthrange(today.year, today.month)[1])
    if (lastday - today).days == 0:
        bot.send_message(message.chat.id, "are you ready to add your data?")
        datenow = str(today)
        takeData(message)
    else:
        pass


# Create a function to handle the "/stop" command
@bot.message_handler(commands=['stop'])
def replydate(message):
    global isrun
    try:
        if isrun:
            isrun = False
            schedule.clear()
            bot.reply_to(message, "The bot is stopped.")
        else:
            bot.reply_to(message, "The bot is already stopped.")
    except:
        bot.reply_to(message, "The bot didn't run yet.")


# Create a function to handle the "/file" command
@bot.message_handler(commands=['file', 'data'])
def file(message):
    chat_id = message.chat.id
    db = Database(chat_id)
    data = db.selectAll()
    with open('data{}.csv'.format(chat_id), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'Wealth',  'Learning',
                        'Project', 'Description', 'Income',  'Date'])
        writer.writerows(data)
    f.close()
    bot.send_document(chat_id, open('data{}.csv'.format(chat_id), 'rb'))
    os.remove('data{}.csv'.format(chat_id))


# Create a function to handle the "/add" command
@bot.message_handler(commands=['add'])
def replydate(message):
    bot.reply_to(message, "ok i will add your data.")
    bot.send_message(message.chat.id, "or send (/cancel) to /cancel.")

    takeData(message, addDate=True)


# Create a function to handle the "/delete" command
@bot.message_handler(commands=['delete'])
def replydate(message):
    chat_id = message.chat.id
    db = Database(chat_id)
    data = db.selectAll()
    if data:
        file(message)
        bot.reply_to(
            message, "please send the id of the data you want to delete from (1 to {})".format(len(data)))
        bot.send_message(message.chat.id, "or send (/cancel) to /cancel.")

        bot.register_next_step_handler(message, delete)
    else:
        bot.reply_to(message, "there is no data to delete.")


# Create a function to handle the "/update" command
@bot.message_handler(commands=['update'])
def replydate(message):
    chat_id = message.chat.id
    db = Database(chat_id)
    data = db.selectAll()
    if data:
        file(message)
        bot.reply_to(
            message, "please send the id of the data you want to update from (1 to {}).".format(len(data)))
        bot.send_message(message.chat.id, "or send (/cancel) to /cancel.")
        bot.register_next_step_handler(message, askupdate)
    else:
        bot.reply_to(message, "there is no data to update.")


# Create a function to handle the "/status" command
@bot.message_handler(commands=['status'])
def replydate(message):
    global isrun
    try:
        if isrun:
            bot.reply_to(message, "The bot is running.")
        else:
            bot.reply_to(message, "The bot is stopped.")
    except:
        bot.reply_to(message, "The bot didn't run yet.")


# Create a function to handle the "/graph" command
@bot.message_handler(commands=['graph'])
def replydate(message):
    # make graph from wealth
    chat_id = message.chat.id
    db = Database(chat_id)
    data = db.selectAll()
    try:
        if data:
            wealth = []
            date = []
            for i in data:
                wealth.append(int(i[1]))
                date.append(i[6][:-3])
            plt.plot(date, wealth)
            plt.xlabel('Date')
            plt.xticks(rotation=0, fontsize=6)
            plt.ylabel('Wealth')
            plt.title('Wealth Graph')
            plt.savefig("graph{}.png".format(chat_id))
            bot.send_photo(chat_id, open('graph{}.png'.format(chat_id), 'rb'))
            os.remove('graph{}.png'.format(chat_id))
            plt.clf()
        else:
            bot.reply_to(message, "there is no data to make graph.")
    except:
        error = sys.exc_info()[0]
        bot.reply_to(
            message, "there is a problem to make graph.\n{}".format(error))


####################################### take data ########################################


def takeData(message, addDate=False):
    chat_id = message.chat.id
    if message.text == "/cancel":
        bot.reply_to(message, "ok, i will not add your data.")
        return
    wealth = "a"
    while not wealth.isdigit():
        wealth = ask(
            message, "Please enter your wealth as number or /cancel to cancel.")
        if wealth == "/cancel":
            bot.reply_to(message, "ok, i will not add your data.")
            return
    income = "a"
    while not income.isdigit():
        income = ask(
            message, "Please enter your income as number or /cancel to cancel.")
        if income == "/cancel":
            bot.reply_to(message, "ok, i will not add your data.")
            return
    learning = ask(message, "Please enter your learning or /cancel to cancel.")
    if learning == "/cancel":
        bot.reply_to(message, "ok, i will not add your data.")
        return
    project = ask(message, "Please enter your project or /cancel to cancel.")
    if project == "/cancel":
        bot.reply_to(message, "ok, i will not add your data.")
        return
    description = ask(
        message, "Please enter your description or /cancel to cancel.")
    if description == "/cancel":
        bot.reply_to(message, "ok, i will not add your data.")
        return
    if addDate:
        date = ask(
            message, f"Please enter your date or /cancel to cancel.\n/this for this date {datenow}")
        if date == "/cancel":
            bot.reply_to(message, "ok, i will not add your data.")
            return
    else:
        date = datenow

    sure = ask(message, "Are you sure you want to save this data? (/yes or /no)")
    if sure.lower() in ["yes", "y", "/yes", "/y"]:
        db = Database(chat_id)
        db.insert(wealth, income, learning, project, description, date)
        bot.reply_to(message, "Data saved.")
    else:
        bot.reply_to(message, "ok, i will not add your data.")
        return


def askupdate(message):
    chat_id = message.chat.id
    if message.text == "/cancel":
        bot.send_message(chat_id, "Ok, Bye.")
        return
    else:
        try:
            id = int(message.text)
            db = Database(chat_id)
            data = db.select(id)
            if data:
                id, wealth, income, learning, project, description, date = data[0]

                bot.send_message(chat_id, f"id: {id}\n"
                                 f"Wealth: {wealth}\n"
                                 f"Income: {income}\n"
                                 f"Learning: {learning}\n"
                                 f"Project: {project}\n"
                                 f"Description: {description}\n"
                                 f"Date: {date}\n")

                updatebox = ask(message,  """do you want to update the all column or only one box?\nplease enter (/all) or the name of the box.\n
                    example: /wealth, /income, /learning, /project, /description, /date\nif you want to /cancel, please enter (/cancel).""")

            else:
                bot.send_message(chat_id, "id not found.")
                bot.send_message(
                    chat_id, "Please enter the id of the data you want to update or (/cancel) to cancel.")
                bot.register_next_step_handler(message, askupdate)

        except:
            bot.send_message(chat_id, "id not found.")
            bot.send_message(
                chat_id, "Please enter the id of the data you want to update or (/cancel) to cancel.")
            bot.register_next_step_handler(message, askupdate)

    if updatebox == "/cancel" or updatebox == "/cancel":
        bot.send_message(chat_id, "Ok, Bye.")
    else:
        if updatebox == "/all":
            bot.send_message(
                chat_id, """please enter the new data in the following order:\n
                \nWealth#Income#Learning#Project#Description#Date\n
                example: 1000#1000#text#text#text#2018-01-01""")
            bot.register_next_step_handler(message, update, id, updatebox)
        elif updatebox[:1] == "/":
            bot.send_message(chat_id, f"Please enter the new {updatebox[1:]}:")
            bot.register_next_step_handler(message, update, id, updatebox)
        else:
            bot.send_message(
                chat_id, "wrong input,")
            askupdate(message)
            return


def update(message, id, updatebox):
    chat_id = message.chat.id
    db = Database(chat_id)
    if message.text == "/cancel":
        bot.send_message(chat_id, "Ok, Bye.")
        return

    if updatebox == "/all":
        try:
            wealth, income, learning, project, description, date = message.text.split(
                "#")
            db.update(wealth,  learning, project,
                      description, income, date, id)
            bot.send_message(chat_id, "Data updated.")
        except:
            bot.send_message(
                chat_id, "Please enter the new data in the following order:\n\nWealth#Income#Learning#Project#Description#Date\nExample: 1000#1000#text#text#text#2018-01-01.\nTo cancel, enter (/cancel).")
            bot.register_next_step_handler(message, update, id, updatebox)
    else:
        data = db.select(id)
        data = list(data[0])
        if updatebox[0] == "/":
            updatebox = updatebox[1:]
        try:
            db.singleUpdate(id, **{updatebox: message.text})
            bot.send_message(chat_id, "Data updated.")
        except Exception as e:
            bot.send_message(
                chat_id, f"error: {e}\n\n______\n/cancel to cancel.\nPlease enter the new {updatebox}:")
            bot.register_next_step_handler(message, update, id, updatebox)


def delete(message):
    chat_id = message.chat.id
    if message.text == "/cancel":
        bot.send_message(chat_id, "Ok, Bye.")
        return
    try:
        id = int(message.text)
        db = Database(chat_id)
        data = db.select(id)
        if data:
            id, wealth, income, learning, project, description, date = data[0]
            bot.send_message(chat_id, f"id: {id}\n"
                             f"Wealth: {wealth}\n"
                             f"Income: {income}\n"
                             f"Learning: {learning}\n"
                             f"Project: {project}\n"
                             f"Description: {description}\n"
                             f"Date: {date}\n")

            sure = ask(
                message, "Are you sure you want to delete this data? (/yes or /no)")

            if sure in ["yes", "y", "/yes", "/y"]:
                db = Database(chat_id)
                db.delete(id)
                bot.send_message(chat_id, "Data deleted.")
            else:
                bot.send_message(chat_id, "Ok, Bye.")
            return

        else:
            bot.send_message(
                chat_id, "Please enter a valid id or (/cancel) to cancel.")
            bot.register_next_step_handler(message, delete)
    except:
        bot.send_message(
            chat_id, "Please enter a number or send /cancel to /cancel.")
        bot.register_next_step_handler(message, delete)


######################################## end take data ########################################

if __name__ == '__main__':
    print("Bot started")

    # get the pid of the process and save it in file
    pid = os.getpid()
    open("pid.txt", "w").write(str(pid))

    try:
        tables = Database.tableNames()
    except:
        tables = []

    # send message to all users
    for table in tables:
        try:
            bot.send_message(table[0][1:], "Bot restarted.")
        except:
            pass

    bot.infinity_polling()
