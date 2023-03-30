import sys
import telebot
import datetime
import calendar
import csv
import time
import os
import sqlite3
import schedule
import matplotlib.pyplot as plt


api = os.environ['apif']
bot = telebot.TeleBot(api)
global add
add = False


############################## database ########################################

class Database:
    def __init__(self, chat_id):
        self.conn = sqlite3.connect('Database.db')
        self.c = self.conn.cursor()
        self.chat_id = "U"+str(chat_id)
        # create table if not exists named after chat_id
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, Wealth STRING, Income STRING, Learning STRING, Project STRING, Description STRING, Date STRING)".format(self.chat_id))
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def insert(self, wealth, income, learning, Project, description, date):
        self.c.execute(
            "INSERT INTO {} (Wealth, Income, Learning, Project, Description, Date) VALUES (?, ?, ?, ?, ?, ?)".format(
                self.chat_id), (wealth, income, learning, Project, description, date))

        self.conn.commit()

    def update(self, wealth, income, learning, Project, description, date, id):
        self.c.execute(
            "UPDATE {} SET Wealth = ?,Income = ?, Learning = ?, Project = ?, Description = ?, Date = ? WHERE id = ?".format(
                self.chat_id), (wealth, income, learning, Project, description, date, id))
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
        chat_id = message.chat.id
        db = Database(chat_id)

        bot.reply_to(message, "Hello, I am a bot that will help you calculate your wealth.\n"
                     "i will ask you in the first day of the month.\n")
        schedule.every().day.at("00:00").do(run, message)

        while isrun:
            schedule.run_pending()
            time.sleep(30)


def run(message):
    print("run")

    today = datetime.date.today()
    lastday = datetime.date(today.year, today.month,
                            calendar.monthrange(today.year, today.month)[1])
    if (lastday - today).days == 0:
        global add
        add = False
        bot.send_message(message.chat.id, "are you ready to add your data?")
        getwealth(message)
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
        writer.writerow(['id', 'Wealth', 'Learning',
                        'Project', 'Description', 'Income', 'Date'])
        writer.writerows(data)
    f.close()
    bot.send_document(chat_id, open('data{}.csv'.format(chat_id), 'rb'))
    os.remove('data{}.csv'.format(chat_id))


# Create a function to handle the "/add" command
@bot.message_handler(commands=['add'])
def replydate(message):
    bot.reply_to(message, "ok i will add your data.")
    bot.send_message(message.chat.id, "or send (exit) to exit.")

    global add
    add = True

    getwealth(message)


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
        bot.send_message(message.chat.id, "or send (exit) to exit.")

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
        bot.send_message(message.chat.id, "or send (exit) to exit.")
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


def getwealth(message):
    chat_id = message.chat.id
    if message.text == "exit":
        bot.reply_to(message, "ok, i will not add your data.")
        global add
        add = False
    else:
        bot.send_message(chat_id, "Please enter your wealth:")
        bot.register_next_step_handler(message, getincome)


def getincome(message):
    chat_id = message.chat.id
    wealth = message.text
    if wealth.isdigit():
        bot.send_message(chat_id, "Please enter your income:")
        bot.register_next_step_handler(message, getlearning, wealth)
    else:
        bot.send_message(chat_id, "Please enter your wealth as number:")
        bot.send_message(chat_id, "example: 10000000000")
        bot.register_next_step_handler(message, getincome)


def getlearning(message, wealth):
    chat_id = message.chat.id
    income = message.text
    bot.send_message(chat_id, "Please enter your learning:")
    bot.register_next_step_handler(message, getdescription, wealth, income)


def getproject(message, wealth, income):
    chat_id = message.chat.id
    learning = message.text
    bot.send_message(chat_id, "Please enter your project:")
    bot.register_next_step_handler(
        message, getdescription, wealth, income, learning)


def getdescription(message, wealth, income, learning):
    chat_id = message.chat.id
    project = message.text
    bot.send_message(chat_id, "Please enter your description:")
    bot.register_next_step_handler(
        message, gatdate, wealth, income, learning, project)


def gatdate(message, wealth, income, learning, project):
    chat_id = message.chat.id
    description = message.text
    global add

    if add == True:
        bot.send_message(chat_id, "Please enter your date:\n"
                         "(format: year-month-day)\n"
                         "(example: 2018-01-01)")

        bot.register_next_step_handler(
            message, getdate2, wealth, income, learning, project, description)
    else:
        date = datetime.date.today().strftime("%Y-%m-%d")
        sure(message, wealth, income, learning, project, description, date)


def getdate2(message, wealth, income, learning, project, description):
    date = message.text
    sure(message, wealth, income, learning, project, description, date)


def sure(message, wealth, income, learning, project, description, date):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Do you want to save this data? (y/n)")
    bot.register_next_step_handler(
        message, save, wealth, income, learning, project, description, date)


def save(message, wealth, income, learning, project, description, date):
    chat_id = message.chat.id
    global add
    if message.text == "y" or message.text == "Y" or message.text == "yes" or message.text == "Yes":
        db = Database(chat_id)
        db.insert(wealth, income, learning, project, description, date)
        bot.send_message(chat_id, "Data saved.")
    elif message.text == "n" or message.text == "N" or message.text == "no" or message.text == "No":
        bot.send_message(chat_id, "Do you want to enter data again? (y/n)")
        bot.register_next_step_handler(message, again)
    else:
        bot.send_message(chat_id, "Please enter y/n")
        bot.register_next_step_handler(
            message, save, wealth, income, learning, project, description, date)


def again(message):
    chat_id = message.chat.id
    if message.text == "y" or message.text == "Y" or message.text == "yes" or message.text == "Yes":
        getwealth(message)
    elif message.text == "n" or message.text == "N" or message.text == "no" or message.text == "No":
        bot.send_message(chat_id, "Ok, Bye.")
    else:
        bot.send_message(chat_id, "Please enter y/n")
        bot.register_next_step_handler(message, again)


def askupdate(message):
    chat_id = message.chat.id
    if message.text == "exit" or message.text == "Exit":
        bot.send_message(chat_id, "Ok, Bye.")
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

                bot.send_message(
                    chat_id, "do you want to update the all column or only one box?")
                bot.send_message(
                    chat_id, "please enter (all) or the name of the box.")
                bot.send_message(
                    chat_id, "example: wealth, income, learning, project, description, date")
                bot.send_message(
                    chat_id, "if you want to exit, please enter (exit).")
                bot.register_next_step_handler(message, ask2update, id)
            else:
                bot.send_message(chat_id, "id not found.")
                bot.send_message(
                    chat_id, "Please enter the id of the data you want to update or (exit) to cancel.")
                bot.register_next_step_handler(message, askupdate)

        except:
            bot.send_message(chat_id, "id not found.")
            bot.send_message(
                chat_id, "Please enter the id of the data you want to update or (exit) to cancel.")
            bot.register_next_step_handler(message, askupdate)


def ask2update(message, id):
    chat_id = message.chat.id
    updatebox = message.text
    if message.text == "exit" or message.text == "Exit":
        bot.send_message(chat_id, "Ok, Bye.")
    else:
        if message.text == "all" or message.text == "All":
            bot.send_message(
                chat_id, "please enter the new data in the following order:")
            bot.send_message(
                chat_id, "Wealth#Income#Learning#Project#Description#Date")
            bot.send_message(
                chat_id, "example: 1000#1000#text#text#text#2018-01-01")
            bot.register_next_step_handler(message, update, id, updatebox)
        elif message.text == "wealth" or message.text == "Wealth":
            bot.send_message(chat_id, "Please enter your wealth:")
            bot.register_next_step_handler(message, update, id, updatebox)
        elif message.text == "income" or message.text == "Income":
            bot.send_message(chat_id, "Please enter your income:")
            bot.register_next_step_handler(message, update, id, updatebox)
        elif message.text == "learning" or message.text == "Learning":
            bot.send_message(chat_id, "Please enter your learning:")
            bot.register_next_step_handler(message, update, id, updatebox)
        elif message.text == "project" or message.text == "Project":
            bot.send_message(chat_id, "Please enter your project:")
            bot.register_next_step_handler(message, update, id, updatebox)
        elif message.text == "description" or message.text == "Description":
            bot.send_message(chat_id, "Please enter your description:")
            bot.register_next_step_handler(message, update, id, updatebox)
        elif message.text == "date" or message.text == "Date":
            bot.send_message(chat_id, "Please enter your date:")
            bot.register_next_step_handler(message, update, id, updatebox)
        else:
            bot.send_message(
                chat_id, "Please enter the name of the box you want to update or (all) to update all column or (exit) to cancel.")
            bot.register_next_step_handler(message, ask2update, id)


def update(message, id, updatebox):
    chat_id = message.chat.id
    db = Database(chat_id)
    if message.text == "exit" or message.text == "Exit":
        bot.send_message(chat_id, "Ok, Bye.")
    else:
        if updatebox == "all" or updatebox == "All":
            try:
                wealth, income, learning, project, description, date = message.text.split(
                    "#")
                db.update(wealth, income, learning, project,
                          description, date, id)
                bot.send_message(chat_id, "Data updated.")
            except:
                bot.send_message(
                    chat_id, "Please enter the new data in the following order:")
                bot.send_message(
                    chat_id, "Wealth#Income#Learning#Project#Description#Date")
                bot.send_message(
                    chat_id, "example: 1000#1000#text#text#text#2018-01-01")
                bot.send_message(
                    chat_id, "if you want to exit, please enter (exit).")
                bot.register_next_step_handler(message, update, id, updatebox)
        else:
            data = db.select(id)
            data = list(data[0])
            if updatebox == "wealth" or updatebox == "Wealth":
                try:
                    wealth = message.text
                    db.update(wealth, data[2], data[3],
                              data[4], data[5], date[6], id)
                    bot.send_message(chat_id, "Data updated.")
                except:
                    bot.send_message(
                        chat_id, "Please enter your wealth or (exit) to cancel.")
                    bot.register_next_step_handler(
                        message, update, id, updatebox)
            elif updatebox == "income" or updatebox == "Income":
                try:
                    income = message.text
                    db.update(data[1], income, data[3],
                              data[4], data[5], data[6], id)
                    bot.send_message(chat_id, "Data updated.")
                except:
                    bot.send_message(
                        chat_id, "Please enter your income or (exit) to cancel.")
                    bot.register_next_step_handler(
                        message, update, id, updatebox)
            elif updatebox == "learning" or updatebox == "Learning":
                try:
                    learning = message.text
                    db.update(data[1], data[2], learning,
                              data[4], data[5], data[6], id)
                    bot.send_message(chat_id, "Data updated.")
                except:
                    bot.send_message(
                        chat_id, "Please enter your learning or (exit) to cancel.")
                    bot.register_next_step_handler(
                        message, update, id, updatebox)
            elif updatebox == "project" or updatebox == "Project":
                try:
                    project = message.text
                    db.update(data[1], data[2], data[3], project,
                              data[5], data[6], id)
                    bot.send_message(chat_id, "Data updated.")
                except:
                    bot.send_message(
                        chat_id, "Please enter your project or (exit) to cancel.")
                    bot.register_next_step_handler(
                        message, update, id, updatebox)
            elif updatebox == "description" or updatebox == "Description":
                try:
                    description = message.text
                    db.update(data[1], data[2], data[3], data[4],
                              description,  data[6], id)
                    bot.send_message(chat_id, "Data updated.")
                except:
                    bot.send_message(
                        chat_id, "Please enter your description or (exit) to cancel.")
                    bot.register_next_step_handler(
                        message, update, id, updatebox)
            elif updatebox == "date" or updatebox == "Date":
                try:
                    date = message.text
                    db.update(data[1], data[2], data[3], data[4], data[5],
                              date, id)
                    bot.send_message(chat_id, "Data updated.")
                except:
                    bot.send_message(
                        chat_id, "Please enter your date or (exit) to cancel.")
                    bot.register_next_step_handler(
                        message, update, id, updatebox)
            else:
                bot.send_message(
                    chat_id, "Please enter the name of the box you want to update or (exit) to cancel.")
                bot.register_next_step_handler(message, ask2update, id)


def delete(message):
    chat_id = message.chat.id
    if message.text == "exit" or message.text == "Exit":
        bot.send_message(chat_id, "Ok, Bye.")
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
                bot.send_message(
                    chat_id, "Are you sure you want to delete this data? (yes/no)")
                bot.register_next_step_handler(message, delete2, id)
            else:
                bot.send_message(
                    chat_id, "Please enter a valid id or (exit) to cancel.")
                bot.register_next_step_handler(message, delete)
        except:
            bot.send_message(
                chat_id, "Please enter a number or send exit to exit.")
            bot.register_next_step_handler(message, delete)


def delete2(message, id):
    chat_id = message.chat.id
    if message.text == "exit" or message.text == "Exit":
        bot.send_message(chat_id, "Ok, Bye.")
    else:
        if message.text == "yes" or message.text == "Yes" or message.text == "Y" or message.text == "y":
            db = Database(chat_id)
            db.delete(id)
            bot.send_message(chat_id, "Data deleted.")
        elif message.text == "no" or message.text == "No":
            bot.send_message(chat_id, "Ok, Bye.")
        else:
            bot.send_message(
                chat_id, "Please enter yes or no or (exit) to cancel.")
            bot.register_next_step_handler(message, delete2, id)


######################################## end take data ########################################


if __name__ == '__main__':
    print("Bot started")

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
