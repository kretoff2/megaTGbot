import telebot
from telebot import types
import sqlite3 as sql
import datetime
from datetime import *
import random
import requests
import os
import json
import array
import config

bot = telebot.TeleBot(config.bot)

conn = sql.connect('db.sql')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, first_name varchar(50), last_name varchar(50), chatID int, bagsTimeOut float, schoolID int, autorizationStep int, teacher bit, experience int, level int, coins int, diamonds int, tickets int, class var(6))')
cur.execute('CREATE TABLE IF NOT EXISTS schools(id int auto_increment primary key, schoolID int, contry varchar(20), obl varchar(50), sity varchar(50), school varchar(50), rating int)')
cur.execute('CREATE TABLE IF NOT EXISTS bags (id int auto_increment primary key, date varchar(50), user varchar(100), bag varchar(5000), bagId int)')
cur.execute('CREATE TABLE IF NOT EXISTS admins (id int auto_increment primary key, name varchar(50), chatID int)')
cur.execute('CREATE TABLE IF NOT EXISTS news (id int auto_increment primary key, date varchar(50), news varchar(5000), NewsId int)')
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Беларусь"))
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Россия"))

conn.commit()
cur.close()
conn.close()
data = {
    "usersData":{

    },
    "education":{

    }
}
lessonsData = {}
if not os.path.exists('./data.json'):
    with open('data.json', 'w') as f:
        json.dump(data, f)
with open('data.json', 'r') as f:
    data = json.load(f)
with open('lessons.json', 'r') as f:
    lessonsData = json.load(f)
def my_markup():
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton("Личный кабинет 🪪")
    btn2 = types.KeyboardButton("Настройки ⚙️")
    markup.row(btn1, btn2)
    btn = types.KeyboardButton("Обучение 📖")
    markup.add(btn)
    btn = types.KeyboardButton("Школа 🏫")
    markup.add(btn)
    return markup
@bot.message_handler(commands=['allMessage'])
def main(message):
  if (message.chat.id != config.ADMIN_ID):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  markup = types.ReplyKeyboardMarkup(row_width=1)
  btn = types.KeyboardButton("Отмена")
  markup.add(btn)
  bot.send_message(message.chat.id,'Введите сообщение которое отправится всем пользователям бота, для отмены напишите "отмена"', reply_markup=markup)
  bot.register_next_step_handler(message, allMesage)

def allMesage(message):
  if message.text.strip().lower() == "отмена":
    bot.send_message(message.chat.id, "отмена прошла успешно")
    return
  conn = sql.connect('db.sql')
  cur = conn.cursor()

  cur.execute('SELECT * FROM users')
  users = cur.fetchall()

  cur.close()
  conn.close()

  for el in users:
    bot.send_message(el[3], f'Рассылка:\n{message.text}', reply_markup=my_markup())
@bot.message_handler(commands=['start'])
def main(message):
    i = False
    for users in data["usersData"]:
        if users == message.chat.id:
            i = True
    if i == False:
        data["usersData"][str(message.chat.id)] = {}
        data["usersData"][str(message.chat.id)]["invited"] = {}
        data["usersData"][str(message.chat.id)]["invitedCol"] = 0
        data["usersData"][str(message.chat.id)]["inviter"] = None
        data["education"][str(message.chat.id)] = {}
        save_data()
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users')
    users = cur.fetchall()
    cur.close()
    conn.close()
    ok = True
    ccc = True
    for el in users:
        if el[3] == message.chat.id:
            ok = False
            if el[6] != 0:
                ccc = False
    if ccc == True:
        if ok == True:
            conn = sql.connect('db.sql')
            cur = conn.cursor()
            cur.execute('INSERT INTO users (first_name, last_name, chatID, bagsTimeOut, autorizationStep, experience, level, coins, diamonds, tickets) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (message.from_user.first_name, message.from_user.last_name, message.chat.id, 0, 0, 0, 0, 0, 0, 0))
            conn.commit()
            cur.close()
            conn.close()
            start_command = message.text
            refer_id = str(start_command[7:])
            if refer_id != "" and refer_id != str(message.chat.id):
                data["usersData"][str(message.chat.id)]["inviter"] = int(refer_id)
                data["usersData"][str(refer_id)]["invitedCol"]+=1
                data["usersData"][str(message.chat.id)]["invited"][str(data["usersData"][str(refer_id)]["invitedCol"])] = message.chat.id
                save_data()
                bot.send_message(refer_id, f"По вашей ссылке зарегестрировался пользователь @{message.from_user.username}")
        markup = types.InlineKeyboardMarkup()
        btnBel = types.InlineKeyboardButton("Беларусь", callback_data="first_register_step:Беларусь")
        btnRus = types.InlineKeyboardButton("Россия", callback_data="first_register_step:Россия")
        btn1488 = types.InlineKeyboardButton('1488', url='https://www.youtube.com/watch?v=dQw4w9WgXcQ')
        markup.row(btnBel)
        markup.row(btnRus)
        markup.row(btn1488)
        bot.send_message(message.chat.id,"Выбери страну", reply_markup=markup)
    if ccc==False and ok == False:
        Go_start(message)
def go_education(message):
    i = False
    for users in data["education"]:
        if users == message.chat.id:
            i = True
    if i == False or data['education'][str(message.chat.id)] == {}:
        data['education'][str(message.chat.id)]['completed_lesson'] = 0
        data['education'][str(message.chat.id)]['completed_tests'] = 0
        data['education'][str(message.chat.id)]['completed_courses'] = 0
        data['education'][str(message.chat.id)]['GPA'] = 0
        data['education'][str(message.chat.id)]['problems_solved'] = 0
        data['education'][str(message.chat.id)]['decided_correctly'] = 0
        save_data()
    markup = types.InlineKeyboardMarkup()
    text = f"Привет {message.from_user.first_name}, давай начнем обучение.\n\nТы прошел(а):\n{data['education'][str(message.chat.id)]['completed_lesson']} уроков" \
           f"\n{data['education'][str(message.chat.id)]['completed_courses']} учебных курсов\n{data['education'][str(message.chat.id)]['completed_tests']} тестов\n" \
           f"\nСредний балл: {data['education'][str(message.chat.id)]['GPA']}\n\nРешено задач: {data['education'][str(message.chat.id)]['problems_solved']}" \
           f"\nРешено правильно: {data['education'][str(message.chat.id)]['decided_correctly']}"
    bot.send_message(message.chat.id, text, reply_markup=markup)
def Go_start(message):
    bot.send_message(message.chat.id, "Привет, я твой телеграм бот помощник. Что ты хочешь узнать?", reply_markup=my_markup())
def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f)
def my_room(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chatID = "%s"'%(message.chat.id))
    info = cur.fetchone()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Школа", callback_data=f"school_info:{info[5]}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пригласить друга", callback_data="invite_frend")
    markup.add(btn)
    if (info[13] == None):
        btn = types.InlineKeyboardButton("Выбрать класс", callback_data=f"class_vibor")
    else:
        btn = types.InlineKeyboardButton("Изменить класс", callback_data="class_vibor")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Изменить имя", callback_data=f"new_name:{message.chat.id}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Изменить фамилию", callback_data=f"new_last_name:{message.chat.id}")
    markup.add(btn)
    data["usersData"]["tempMessage"] = message
    infoText = f"ID: {info[3]}\n\nИмя: {info[1]}\nФамилия: {info[2]}\n\nКласс: {info[13]}\n\nОпыт: {info[8]}\nУровень: {info[9]}\nМонеты: {info[10]}\nАлмазы: {info[11]}\nБилеты: {info[12]}\n\nПриглашено друзей: {data['usersData'][str(message.chat.id)]['invitedCol']}"
    bot.send_message(message.chat.id, infoText, reply_markup=markup)

@bot.message_handler(commands=['op'])
def main(message):
  if (message.chat.id != config.ADMIN_ID):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  bot.send_message(message.chat.id, 'Введите имя администратора')
  bot.register_next_step_handler(message, addAdmin)

@bot.message_handler(commands=['deop'])
def main(message):
  if (message.chat.id != config.ADMIN_ID):
    bot.send_message(message.chat.id, "Вам не доступна эта команда")
    return
  bot.send_message(message.chat.id, 'Введите имя администратора')
  bot.register_next_step_handler(message, delAdmin)

def delAdmin(message):
  conn = sql.connect('db.sql')
  cur = conn.cursor()
  cur.execute('SELECT * FROM admins')
  cur.execute('DELETE FROM admins WHERE name = "%s"' % (message.text.strip()))
  conn.commit()
  cur.close()
  conn.close()

def addAdmin(message):
  if (message.text.strip().lower() == 'отмена'):
    bot.send_message(message.chat.id, 'Отменено')
    return
  conn = sql.connect('db.sql')
  cur = conn.cursor()

  cur.execute('SELECT * FROM users')
  users = cur.fetchall()

  chatID = None

  for el in users:
    if(message.text.strip() == el[1]):
      chatID = el[3]
  if chatID == None:
    bot.send_message(message.chat.id, "Такого пользователя не существует")
    cur.close()
    conn.close()
    return

  cur.execute('INSERT INTO admins (name, chatID) VALUES ("%s", "%s")' % (message.text.strip(), chatID))
  conn.commit()
  bot.send_message(message.chat.id, 'Администратор успешно добавлен')
  cur.close()
  conn.close()

def school_info(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT schoolID FROM users WHERE chatID = ?', (message.chat.id,))
    temp = cur.fetchone()
    schoolID = temp[0]
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    temp = cur.fetchone()
    my_class = temp[0]
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Расписание на сегодня", callback_data=f"rasp:{schoolID}:{my_class}:0")
    btn2 = types.InlineKeyboardButton("Расписание на завтра", callback_data=f"rasp:{schoolID}:{my_class}:1")
    markup.add(btn1, btn2)
    btn = types.InlineKeyboardButton("Расписание на неделю", callback_data=f"rasp:{schoolID}:{my_class}:2")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Новости", callback_data=f"news:{schoolID}:{my_class}")
    markup.add(btn)
    btn1 = types.InlineKeyboardButton("Дз", callback_data=f"homeTask:{schoolID}:{my_class}:0")
    btn2 = types.InlineKeyboardButton("ГДЗ", callback_data="GDZ")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Что ты хочешь узнать?", reply_markup=markup)
def rasp(message, schoolID, scholl_class, id):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="school_infoo")
    markup.add(btn)
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    v = 0
    if id == "0":
        v = datetime.today().weekday()
    elif id == "1":
        v = datetime.today().weekday()+1
        if v == 7:
            v = 0
    if id == "2":
        i = 0
        info = "Расписание:\n"
        t = ["Понедельник","Вторник","Среда","Четверг","Пятница","Суббота","Воскресение"]
        for i in range(0, 7):
            cur.execute("SELECT * FROM rasp WHERE class = ? AND day = ?", (scholl_class, i))
            rasp = cur.fetchone()
            if rasp != None:
                info += "\n"+t[i]+":\n"
                j = 0
                for j in range(0, 10):
                    if rasp[j + 3] != None:
                        info += str(j + 1) + ". " + rasp[j + 3] + "\n"
                    j += 1
            i += 1
        cur.close()
        conn.close()
        btn = types.InlineKeyboardButton("Изменить расписание", callback_data=f"add_rasp_list:{schoolID}:{scholl_class}")
        markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info,reply_markup=markup)
        return
    cur.execute("SELECT * FROM rasp WHERE class = ? AND day = ?", (scholl_class, v))
    rasp = cur.fetchone()
    cur.close()
    conn.close()
    if rasp == None:
        btn = types.InlineKeyboardButton("Добавить расписание", callback_data=f"add_rasp_list:{schoolID}:{scholl_class}")
        markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Расписание не задано", reply_markup=markup)
    else:
        btn = types.InlineKeyboardButton("Изменить расписание", callback_data=f"add_rasp_list:{schoolID}:{scholl_class}:{v}:1")
        markup.add(btn)
        info = "Расписание:\n"
        i = 0
        for i in range(0,10):
            if rasp[i+3] != None:
                info+=str(i+1) + ". " + rasp[i+3] + "\n"
            i+=1
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def add_rasp_list(message, schoolID, school_class):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"rasp:{schoolID}:{school_class}:2")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Понедельник", callback_data=f"add_dz:{schoolID}:{school_class}:0:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Вторник", callback_data=f"add_dz:{schoolID}:{school_class}:1:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Среда", callback_data=f"add_dz:{schoolID}:{school_class}:2:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Четверг", callback_data=f"add_dz:{schoolID}:{school_class}:3:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пятница", callback_data=f"add_dz:{schoolID}:{school_class}:4:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Суббота", callback_data=f"add_dz:{schoolID}:{school_class}:5:1")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Воскресение", callback_data=f"add_dz:{schoolID}:{school_class}:6:1")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="На какой день недели вы хотите ввести рассписание", reply_markup=markup)
def add_dz(message, schoolID, school_class, day = None, number = None, subject = None):
    subjects = {"Русский язык", "Белорусский язык", "Иностранный язык", "Математика", "Алгебра", "Геометрия",
                "Русская литература", "Белорусская литература", "Человек и мир", "Всемирная истроия",
                "История Беларуси", "История России", "Искусство", "Биология", "География", "Информатика", "Физика",
                "Химия", "Обществоведение", "Допризывная подготовка", "Медицинская подготовка", "Черчение",
                "Астрономия"}
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Закончить", callback_data=f"rasp:{schoolID}:{school_class}:2")
    markup.add(btn)
    if subject == None:
        for el in subjects:
            btn = types.InlineKeyboardButton(el, callback_data=f"add_dz:{schoolID}:{school_class}:{day}:{number}:{el}")
            markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Выбери {number} урок", reply_markup=markup)
        return
    conn = sql.connect(f"./sqls/{schoolID}.sql")
    cur = conn.cursor()
    cur.execute('SELECT * FROM rasp WHERE class = ? AND day = ?', (school_class, day))
    temp = cur.fetchone()
    if temp == None:
        cur.execute('INSERT INTO rasp (class, day, lesson1) VALUES (?, ?, ?)', (school_class, day, subject))
    else:
        cur.execute(f'UPDATE rasp SET lesson{number} = ? WHERE class = ? AND day = ?', (subject, school_class, day))
    conn.commit()
    cur.close()
    conn.close()
    if number == 10:
        rasp(message, schoolID, school_class, 2)
        return
    for el in subjects:
        btn = types.InlineKeyboardButton(el, callback_data=f"add_dz:{schoolID}:{school_class}:{day}:{int(number)+1}:{el}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Выбери {int(number)+1} урок", reply_markup=markup)
def see_news(message, schoolID, school_class):
    pass
def see_dz(message, schoolID, school_class, id):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM dz WHERE class = ?',(school_class,))
    dzs = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data='school_infoo')
    markup.add(btn)
    temp_array = []
    for el in dzs:
        for elem in temp_array:
            if el[1] != elem:
                temp_array.append(el[1])
    for el in temp_array:
        btn = types.InlineKeyboardButton(el, callback_data=f'see_dz_step_1:{schoolID}:{school_class}:{el}')
        markup.add(btn)
    btn = types.InlineKeyboardButton("Добавить дз", callback_data=f"add_homeTask:{schoolID}:{school_class}")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Удалить дз", callback_data=f"rem_homeTask:{schoolID}:{school_class}")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери день",reply_markup=markup)
def see_dz_step_1(message, schoolID, school_class, date):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM dz WHERE class = ? AND date = ?',(school_class, date))
    dzs = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f'homeTask:{schoolID}:{school_class}:0')
    markup.add(btn)
    info = f"Дз на {date}\n\n"
    for el in dzs:
        info += f"{el[2]}: {el[3]}\n"
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text = info, reply_markup=markup)
def add_homeTask(message, schoolID, school_class):
    pass
def rem_homeTask(message, schoolID, school_class):
    pass
def create_new_scholl_db(schoolID):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS rasp (id int auto_increment primary key, class varchar(6), day int, lesson1 varchar(25), lesson2 varchar(25), lesson3 varchar(25), lesson4 varchar(25), lesson5 varchar(25), lesson6 varchar(25), lesson7 varchar(25), lesson8 varchar(25), lesson9 varchar(25), lesson10 varchar(25))')
    cur.execute('CREATE TABLE IF NOT EXISTS news (id int auto_increment primary key, date varchar(50), news varchar(5000), NewsId int, class varchar(6))')
    cur.execute('CREATE TABLE IF NOT EXISTS dz (id int auto_increment primary key, date varchar(50), predmet varchar(25), dz varchar(1000), dzId int, class varchar(25))')
    conn.commit()
    cur.close()
    conn.close()
@bot.message_handler()
def main(message):
    if message.text == "Личный кабинет 🪪":
        my_room(message)
    elif message.text == "Настройки ⚙️":
        bot.send_message(message.chat.id, "Раздел находится в разработке")
    elif message.text == "Обучение 📖":
        go_education(message)
    elif message.text == "Школа 🏫":
        school_info(message)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global data
    callRazd = call.data.split(':')
    if callRazd[0] == "first_register_step":
        data["usersData"][str(call.message.chat.id)]["contry"] = callRazd[1]
        send_vibor_obl(call)
    elif callRazd[0] == "second_register_step":
        data["usersData"][str(call.message.chat.id)]["obl"] = callRazd[1]
        send_vibor_sity(call.message)
    elif callRazd[0] == "second_register_step_else":
        data["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        data["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_obl)
    elif callRazd[0] == "serd_register_step":
        data["usersData"][str(call.message.chat.id)]["sity"] = callRazd[1]
        send_vibor_school(call.message)
    elif callRazd[0] == "serd_register_step_else":
        data["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        data["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_sity)
    elif callRazd[0] == "fourth_register_step":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute(f"SELECT schoolID FROM schools WHERE school = ?",(callRazd[1],))
        school = cur.fetchone()
        cur.execute('UPDATE users SET schoolID = ? WHERE chatID = ?', (school[0], call.message.chat.id))
        cur.execute('UPDATE users SET autorizationStep = ? WHERE chatID = ?', (1, call.message.chat.id))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, "Вы успешно зарегистрированы")
        Go_start(call.message)
    elif callRazd[0] == "fourth_register_step_else":
        data["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        data["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_school)
    elif callRazd[0] == "school_info":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM schools WHERE schoolID = ?", (int(callRazd[1]),))
        info = cur.fetchone()
        if info == None:
            return
        cur.close()
        conn.close()
        infoText = f'ID: {info[1]}\n\nСтрана: {info[2]}\nОбласть: {info[3]}\nГород/деревня: {info[4]}\nШкола: {info[5]}\nРэйтинг: {info[6]}'
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Назад", callback_data="back_to_my_room")
        markup.add(btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=infoText, reply_markup=markup)
    elif callRazd[0] == "back_to_my_room":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE chatID = "%s"' % (call.message.chat.id))
        info = cur.fetchone()
        cur.close()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Школа", callback_data=f"school_info:{info[5]}")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Пригласить друга", callback_data="invite_frend")
        markup.add(btn)
        infoText = f"ID: {info[3]}\n\nИмя: {info[1]}\nФамилия: {info[2]}\n\nКласс: {info[13]}\n\nОпыт: {info[8]}\nУровень: {info[9]}\nМонеты: {info[10]}\nАлмазы: {info[11]}\nБилеты: {info[12]}\n\nПриглашено друзей: {data['usersData'][str(call.message.chat.id)]['invitedCol']}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=infoText, reply_markup=markup)
    elif callRazd[0] == "class_vibor":
        markup = types.InlineKeyboardMarkup()
        i = 0
        for i in range(0,11):
            i+=1
            btn = types.InlineKeyboardButton(str(i), callback_data=f"set_class:{i}")
            markup.add(btn)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери класс",reply_markup=markup)
    elif callRazd[0] == "set_class":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute('UPDATE users SET class = ? WHERE chatID = ?', (callRazd[1], call.message.chat.id))
        conn.commit()
        cur.close()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('"А"', callback_data="set_class_letter:А")
        btn2 = types.InlineKeyboardButton('"Б"', callback_data="set_class_letter:Б")
        btn3 = types.InlineKeyboardButton('"В"', callback_data="set_class_letter:В")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"Г"', callback_data="set_class_letter:Г")
        btn2 = types.InlineKeyboardButton('"Д"', callback_data="set_class_letter:Д")
        btn3 = types.InlineKeyboardButton('"Е"', callback_data="set_class_letter:Е")
        markup.add(btn1, btn2, btn3)
        btn1 = types.InlineKeyboardButton('"Ж"', callback_data="set_class_letter:Ж")
        btn2 = types.InlineKeyboardButton('"З"', callback_data="set_class_letter:З")
        btn3 = types.InlineKeyboardButton('"И"', callback_data="set_class_letter:И")
        markup.add(btn1, btn2, btn3)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбери класс", reply_markup=markup)
    elif callRazd[0] == "set_class_letter":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute('SELECT class FROM users WHERE chatID = ?', (call.message.chat.id,))
        temp = cur.fetchone()
        cur.execute('UPDATE users SET class = ? WHERE chatID = ?', (f'{temp[0]}"{callRazd[1]}"', call.message.chat.id))
        conn.commit()
        cur.execute('SELECT * FROM users WHERE chatID = "%s"' % (call.message.chat.id))
        info = cur.fetchone()
        cur.close()
        conn.close()
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Школа", callback_data=f"school_info:{info[5]}")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Пригласить друга", callback_data="invite_frend")
        markup.add(btn)
        infoText = f"ID: {info[3]}\n\nИмя: {info[1]}\nФамилия: {info[2]}\n\nКласс: {info[13]}\n\nОпыт: {info[8]}\nУровень: {info[9]}\nМонеты: {info[10]}\nАлмазы: {info[11]}\nБилеты: {info[12]}\n\nПриглашено друзей: {data['usersData'][str(call.message.chat.id)]['invitedCol']}"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=infoText, reply_markup=markup)
    elif callRazd[0] == "invite_frend":
        bot.send_message(call.message.chat.id, f"Если ваш друг перейдет по вашей реферальной ссылке, то вы получите 10 алмазов\n\nВаша ссылка:\nhttps://t.me/{config.BOT_NICKNAME}?start={call.message.chat.id}\n\nТекущее количество приглашенных людей: {data['usersData'][str(call.message.chat.id)]['invitedCol']}")
    elif callRazd[0] == "rasp":
        rasp(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "news":
        see_news(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "homeTask":
        see_dz(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "school_infoo":
        school_info(call.message)
    elif callRazd[0] == "add_rasp_list":
        add_rasp_list(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "add_dz":
        if len(callRazd)==4:
            add_dz(call.message, callRazd[1], callRazd[2], callRazd[3])
        elif len(callRazd)==5:
            add_dz(call.message, callRazd[1], callRazd[2], callRazd[3], callRazd[4])
        elif len(callRazd)==6:
            add_dz(call.message, callRazd[1], callRazd[2], callRazd[3], callRazd[4], callRazd[5])
    elif callRazd[0] == "add_homeTask":
        add_homeTask(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "rem_homeTask":
        rem_homeTask(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "GDZ":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Делай сам")
    elif callRazd[0] == "see_dz_step_1":
        see_dz_step_1(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "new_name":
        bot.send_message(int(callRazd[1]), "Впишите новое имя")
        message = data["usersData"]["tempMessage"]
        bot.register_next_step_handler(message, new_name)
    elif callRazd[0] == "new_last_name":
        bot.send_message(int(callRazd[1]), "Впишите новую фамилию")
        message = data["usersData"]["tempMessage"]
        bot.register_next_step_handler(message, new_last_name)
def new_name(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET first_name = ? WHERE chatID = ?', (message.text, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    my_room(message)
def new_last_name(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('UPDATE users SET last_name = ? WHERE chatID = ?', (message.text, message.chat.id))
    conn.commit()
    cur.close()
    conn.close()
    my_room(message)
def send_vibor_obl(call):
    markup = types.InlineKeyboardMarkup()

    conn = sql.connect('db.sql')
    cur = conn.cursor()
    temp = data["usersData"][f"{call.message.chat.id}"]["contry"]
    cur.execute('SELECT obl FROM schools WHERE contry = ?', (temp,))
    obls = cur.fetchall()
    cur.close()
    conn.close()
    my_array=[]
    for el in obls:
        if str(el[0]) != "None":
            for elem in my_array:
                if elem != str(el[0]):
                    my_array.append(str(el[0]))
    for el in my_array:
        btn = types.InlineKeyboardButton(el, callback_data=f"second_register_step:{el}")
        markup.add(btn)
    btn = types.InlineKeyboardButton("Другая", callback_data=f"second_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выбери область',reply_markup=markup)

def else_obl(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO schools (contry, obl) VALUES ("%s", "%s")' % (data["usersData"][f"{message.chat.id}"]["contry"], message.text))
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, data["usersData"][str(message.chat.id)]["MessageID"])
    data["usersData"][f"{message.chat.id}"]["obl"] = message.text
    send_vibor_sity(data["usersData"][f"{message.chat.id}"]["botMessageID"])

def send_vibor_sity(message):
    markup = types.InlineKeyboardMarkup()

    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT sity FROM schools WHERE contry = ? AND obl = ?', (data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"]))
    sitys = cur.fetchall()
    cur.close()
    conn.close()
    my_array = []
    for el in sitys:
        if str(el[0]) != "None":
            for elem in my_array:
                if elem != el[0]:
                    my_array.append(el[0])
    for el in my_array:
        btn = types.InlineKeyboardButton(el, callback_data=f"serd_register_step:{el}")
        markup.add(btn)
    btn = types.InlineKeyboardButton("Друой", callback_data=f"serd_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Выбери город',reply_markup=markup)

def else_sity(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO schools (contry, obl, sity) VALUES ("%s", "%s", "%s")' % (data["usersData"][f"{message.chat.id}"]["contry"],data["usersData"][f"{message.chat.id}"]["obl"],  message.text))
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, data["usersData"][str(message.chat.id)]["MessageID"])
    data["usersData"][f"{message.chat.id}"]["sity"] = message.text
    send_vibor_school(data["usersData"][f"{message.chat.id}"]["botMessageID"])

def send_vibor_school(message):
    markup = types.InlineKeyboardMarkup()

    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT school FROM schools WHERE contry = ? AND obl = ? AND sity = ?',
                (data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"], data["usersData"][f"{message.chat.id}"]["sity"]))
    schools = cur.fetchall()
    cur.close()
    conn.close()
    my_array = []
    for el in schools:
        if str(el[0]) != "None":
            for elem in my_array:
                if elem != el[0]:
                    my_array.append(el[0])
    for el in my_array:
        btn = types.InlineKeyboardButton(el, callback_data=f"fourth_register_step:{el}")
        markup.add(btn)
    btn = types.InlineKeyboardButton("Другая", callback_data=f"fourth_register_step_else")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Выбери школу',reply_markup=markup)

def else_school(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT school FROM schools')
    schols = cur.fetchall()
    cur.execute('INSERT INTO schools (contry, obl, sity, school, schoolID, rating) VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' % (
    data["usersData"][f"{message.chat.id}"]["contry"], data["usersData"][f"{message.chat.id}"]["obl"], data["usersData"][f"{message.chat.id}"]["sity"], message.text, len(schols),0))
    cur.execute(f'UPDATE users SET schoolID = {len(schols)} WHERE chatID = {message.chat.id}')
    cur.execute(f'UPDATE users SET autorizationStep = {1} WHERE chatID = {message.chat.id}')
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, data["usersData"][str(message.chat.id)]["MessageID"])
    bot.send_message(message.chat.id,"Вы успешно зарегистрированы, для начала работы с ботом пропишите /start")
    create_new_scholl_db(len(schols))
    Go_start(message)

bot.polling(none_stop=True)