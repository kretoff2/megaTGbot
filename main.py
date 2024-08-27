import telebot
from telebot import types
import sqlite3 as sql
import datetime
from datetime import *
import random
import os
import json
import config
from pathlib import Path
import requests

bot = telebot.TeleBot(config.bot)

tempData = {
    "usersData": {

    }
}
conn = sql.connect('db.sql')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, first_name varchar(50), last_name varchar(50), chatID int, bagsTimeOut float, schoolID int, autorizationStep int, teacher bit, experience int, level int, coins int, diamonds int, tickets int, class varchar(6))')
cur.execute('CREATE TABLE IF NOT EXISTS schools(id int auto_increment primary key, schoolID int, contry varchar(20), obl varchar(50), sity varchar(50), school varchar(50), rating int)')
cur.execute('CREATE TABLE IF NOT EXISTS bags (id int auto_increment primary key, date varchar(50), user varchar(100), bag varchar(5000), bagId int)')
cur.execute('CREATE TABLE IF NOT EXISTS admins (id int auto_increment primary key, name varchar(50), chatID int)')
cur.execute('CREATE TABLE IF NOT EXISTS news (id int auto_increment primary key, date varchar(50), news varchar(5000), NewsId int)')
cur.execute('CREATE TABLE IF NOT EXISTS timeOuts (chatID int primary key, report int, selectClass int, selectSchool int)')
cur.execute('SELECT * FROM timeOuts')
print(cur.fetchall())
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Беларусь"))
#cur.execute('INSERT INTO schools (contry) VALUES ("%s")' % ("Россия"))

conn.commit()

cur.execute('SELECT chatID FROM users')
usersIds = cur.fetchall()
for el in usersIds:
    tempData['usersData'][str(el[0])]={}

cur.close()
conn.close()
data = {
    "usersData":{

    },
    "education":{

    }
}

def sql_conn():
    conn = sql.connect("db.sql")
    return conn

lessonsData = {}
if not os.path.exists('./data.json'):
    with open('data.json', 'w') as f:
        json.dump(data, f)
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('lessons.json', 'r', encoding='utf-8') as f:
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
    btn = types.KeyboardButton("Школа kretoffer'a 💻")
    markup.add(btn)
    return markup
@bot.message_handler(commands=['delOldDz'])
def main(message):
    if message.chat.id != config.ADMIN_ID:
        bot.send_message(message.chat.id, "Недостаточнго прав")
    delOldDz(message)

def delOldDz(message=None):
    folder_name = "sqls"
    folder = Path(folder_name)
    col = sum(1 for x in folder.iterdir())
    i = 0
    yesterday = datetime.today().date()
    yesterdaySPL = str(yesterday).split('-')
    for i in range(0, col):
        i += 1
        conn = sql.connect(f'./sqls/{i}.sql')
        cur = conn.cursor()
        j = 0
        v = int(yesterdaySPL[2]) - 1
        for j in range(0, 10):
            if v == 0:
                v = 31
            date = f'{v}.{yesterdaySPL[1]}.{yesterdaySPL[0]}'
            try:
                cur.execute('DELETE FROM dz WHERE date = ?', (date,))
            except sql.OperationalError:
                pass
            j += 1
            v -= 1
        conn.commit()
        cur.close()
        conn.close()
    if message != None: bot.send_message(message.chat.id, "Старое дз на 10 дней назад удалено")
    else: print("Старое дз за последние 10 дней удалено")

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
    if str(message.chat.id) not in data["usersData"]:
        data["usersData"][str(message.chat.id)] = {}
        data["usersData"][str(message.chat.id)]["invited"] = {}
        data["usersData"][str(message.chat.id)]["invitedCol"] = 0
        data["usersData"][str(message.chat.id)]["inviter"] = None
        data["education"][str(message.chat.id)] = {}
        save_data()
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE chatID = ?', (message.chat.id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user is None:
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO users (first_name, last_name, chatID, bagsTimeOut, autorizationStep, experience, level, coins, diamonds, tickets) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (
            message.from_user.first_name, message.from_user.last_name, message.chat.id, 0, 0, 0, 0, 0, 0, 0))
        tempData['usersData'][str(message.chat.id)] = {}
        start_command = message.text
        refer_id = str(start_command[7:])
        if refer_id != "" and refer_id != str(message.chat.id):
            data["usersData"][str(message.chat.id)]["inviter"] = int(refer_id)
            data["usersData"][str(refer_id)]["invitedCol"] += 1
            data["usersData"][str(message.chat.id)]["invited"][
                str(data["usersData"][str(refer_id)]["invitedCol"])] = message.chat.id
            save_data()
            cur.execute("UPDATE users SET diamonds = diamonds+10 WHERE chatID = ? OR chatID = ?",
                        (refer_id, message.chat.id))
            bot.send_message(refer_id, f"По вашей ссылке зарегестрировался пользователь @{message.from_user.username}")
        conn.commit()
        cur.close()
        conn.close()
    elif user[6] == 0:
        markup = types.InlineKeyboardMarkup()
        btnBel = types.InlineKeyboardButton("Беларусь", callback_data="first_register_step:Беларусь")
        btnRus = types.InlineKeyboardButton("Россия", callback_data="first_register_step:Россия")
        markup.row(btnBel)
        markup.row(btnRus)
        bot.send_message(message.chat.id,"Выбери страну", reply_markup=markup)
    else:
        Go_start(message)
def gdz(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    conn = sql.connect("db.sql")
    cur = conn.cursor()
    cur.execute("SELECT class FROM users WHERE chatID = ?", (message.chat.id,))
    userClass = cur.fetchone()[0]
    cur.close()
    conn.close()
    for el in lessonsData["GDZ"]["by"]:
        btn = types.InlineKeyboardButton(el, callback_data=f"GDZ_s:{userClass[0]}:{el}")
        markup.add(btn)
    bot.send_message(message.chat.id, "Выбери предмет", reply_markup=markup)

#гдз для 8 класса
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('GDZ_s:8:'))
def gdz_s_8(call):
    subject = call.data.split(":")[2]
    message = call.message
    if subject == "Русский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_rus_8)
    elif subject == "Белорусский язык":
        bot.send_message(message.chat.id, "Введите номер упражнения")
        bot.register_next_step_handler(message, gdz_bel_8)
    elif subject == "Биология":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_bio_8)
    elif subject == "География":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_geo_8)
    elif subject == "Геометрия":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_geom_8)
    elif subject == "Алгебра":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Глава 1", callback_data="gdz_alg_8:0")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 2", callback_data="gdz_alg_8:2")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 3", callback_data="gdz_alg_8:7")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Глава 4", callback_data="gdz_alg_8:9")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери главу", reply_markup=markup)
    elif subject == "Английский":
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Стандартный", callback_data="gdz_0:8-angl-2021")
        markup.add(btn)
        btn = types.InlineKeyboardButton("Повышенный", callback_data="gdz_0:8-angl-profi")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выбери уровень", reply_markup=markup)
    elif subject == "Физика":
        bot.send_message(message.chat.id, "Введите номер упражнения (от 1 до 26)")
        bot.register_next_step_handler(message, gdz_fiz_8_0)
    elif subject == "Химия":
        bot.send_message(message.chat.id, "Введите номер параграфа")
        bot.register_next_step_handler(message, gdz_xim_8_0)
    else: bot.send_message(message.chat.id, "Извините но этот предмет не доступен для вашего класса")

def gdz_fiz_8_0(message):
    try:
        upr = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, введите число")
        bot.register_next_step_handler(message, gdz_fiz_8_0)
        return
    bot.send_message(message.chat.id, "Введите номер задания")
    bot.register_next_step_handler(message, gdz_fiz_8, upr)
def gdz_fiz_8(message, upr):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_fiz_8, upr)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-fizika-2018/{upr-1}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return

def gdz_xim_8_0(message):
    try:
        upr = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не число, введите число")
        bot.register_next_step_handler(message, gdz_xim_8_0)
        return
    bot.send_message(message.chat.id, "Введите номер задания")
    bot.register_next_step_handler(message, gdz_xim_8, upr)
def gdz_xim_8(message, upr):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_xim_8, upr)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-him-2018/{upr-1}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_rus_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_rus_8)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-russk-2018/0/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_bel_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bel_8)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-bel-2020/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_bio_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_bio_8)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-biol-2023/par/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_geo_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_geo_8)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-geograf/1/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('gdz_0:8-angl-'))
def gdz_angl_8_0(call):
    val = call.data.split(":")
    if val[1] == "8-angl-2021":
        bot.send_message(call.message.chat.id, "Введите номер страницы")
        bot.register_next_step_handler(call.message, gdz_angl_8, val[1])
    elif val[1] == "8-angl-profi":
        if len(val) == 2:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton("Часть 1", callback_data="gdz_0:8-angl-profi:chast-1")
            markup.add(btn)
            btn = types.InlineKeyboardButton("Часть 2", callback_data="gdz_0:8-angl-profi:chast-2")
            markup.add(btn)
            bot.send_message(call.message.chat.id, "Выбери часть", reply_markup=markup)
        elif len(val) == 3:
            bot.send_message(call.message.chat.id, "Введите номер страницы")
            bot.register_next_step_handler(call.message, gdz_angl_8, val[1], val[2])
def gdz_angl_8(message, book, part = None):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_angl_8, book, part)
        return
    try:
        URL = f'https://resheba.top/GDZ/{book}'
        if part != None: URL+=f"/{part}"
        else: URL+="/str"
        URL+=f"/{nomer}.png"
        response = requests.get(URL)
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('gdz_alg_8:'))
def gdz_alg_8_0(call):
    val0 = call.data.split(":")[1]
    bot.send_message(call.message.chat.id, "Введите номер")
    bot.register_next_step_handler(call.message, gdz_alg_8, val0)
def gdz_alg_8(message, val0):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_alg_8, val0)
        return
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-alg-2018/{val0}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return
def gdz_geom_8(message):
    try:
        nomer = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Вы ввели не номер, введите номер")
        bot.register_next_step_handler(message, gdz_alg_8)
        return
    if nomer <= 153:
        val0 = 1
    elif nomer <= 260:
        val0 = 3
    elif nomer <= 350:
        val0 = 4
    elif nomer <= 422:
        val0 = 6
    try:
        response = requests.get(f'https://resheba.top/GDZ/8-geom-2018/{val0}/{nomer}.png')
        bot.send_photo(message.chat.id, response.content)
    except:
        bot.send_message(message.chat.id, "Что-то пошло не так, поищите здесь https://resheba.top")
        return

def go_education(message):
    conn = sql.connect("db.sql")
    cur = conn.cursor()
    cur.execute("SELECT class FROM users WHERE chatID = ?", (message.chat.id,))
    userClass = cur.fetchone()[0]
    cur.close()
    conn.close()
    if userClass is None:
        bot.send_message(message.chat.id, "Для начала укажите в каком вы классе в личном кабинете. Класс можно менять только раз в месяц")
        return
    if str(message.chat.id) not in data["education"] or data['education'][str(message.chat.id)] == {}:
        data['education'][str(message.chat.id)]['completed_lesson'] = 0
        data['education'][str(message.chat.id)]['completed_tests'] = 0
        data['education'][str(message.chat.id)]['my_courses'] = {}
        data['education'][str(message.chat.id)]['complet_lessons'] = {}
        data['education'][str(message.chat.id)]['complet_tests'] = {}
        data['education'][str(message.chat.id)]['completed_courses'] = 0
        data['education'][str(message.chat.id)]['GPA'] = 0
        data['education'][str(message.chat.id)]['problems_solved'] = 0
        data['education'][str(message.chat.id)]['decided_correctly'] = 0
        save_data()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Мои курсы", callback_data="my_courses")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Уроки", callback_data="lessons_list")
    btn1 = types.InlineKeyboardButton("Курсы", callback_data="courses_list")
    markup.add(btn, btn1)
    btn = types.InlineKeyboardButton("Тесты", callback_data="tests_list")
    btn1 = types.InlineKeyboardButton("Шпаргалки", callback_data="cheat_sheets_list")
    markup.add(btn, btn1)
    text = f"Давай начнем обучение.\n\nТы прошел(а):\n{data['education'][str(message.chat.id)]['completed_lesson']} уроков" \
           f"\n{data['education'][str(message.chat.id)]['completed_courses']} учебных курсов\n{data['education'][str(message.chat.id)]['completed_tests']} тестов\n" \
           f"\nСредний балл: {data['education'][str(message.chat.id)]['GPA']}\n\nРешено задач: {data['education'][str(message.chat.id)]['problems_solved']}" \
           f"\nРешено правильно: {data['education'][str(message.chat.id)]['decided_correctly']}"
    bot.send_message(message.chat.id, text, reply_markup=markup)
def my_courses(message):
    info = f"Вы прошли {data['education'][str(message.chat.id)]['completed_courses']} учебных курсов"
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Пройденные курсы", callback_data="completed_courses")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in data['education'][str(message.chat.id)]['my_courses']:
        if data['education'][str(message.chat.id)]['my_courses'][el]['completed'] != True:
            btn = types.InlineKeyboardButton(lessonsData['courses'][el]['name'], callback_data=f"course:{el}")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def completed_courses(message):
    markup = types.InlineKeyboardMarkup()
    info = "Пройденныйе курсы:\n"
    for el in data['education'][str(message.chat.id)]['my_courses']:
        if data['education'][str(message.chat.id)]['my_courses'][el]["completed"] == True:
            i = lessonsData["courses"][str(el)]['name']
            btn = types.InlineKeyboardButton(i, callback_data=f"course:{el}")
            markup.add(btn)
    btn = types.InlineKeyboardButton("Назад", callback_data="my_courses")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def courses_list(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData['subjects'][el], callback_data=f"courses_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет", reply_markup=markup)
def courses_subject_list(message, subject, userClass):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="courses_list")
    markup.add(btn)
    for el in lessonsData['courses']:
        if lessonsData["courses"][el]["subject"] == subject and lessonsData["courses"][el]["class"] == userClass:
            if el not in data['education'][str(message.chat.id)]['my_courses'] or data['education'][str(message.chat.id)]['my_courses'][el]['completed'] != True:
                btn = types.InlineKeyboardButton(lessonsData['courses'][el]['name'], callback_data=f"course:{el}")
                markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери курс",reply_markup=markup)
def start_course(message, courseID):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Начать урок", callback_data=f"go_course_lesson:{courseID}")
    markup.add(btn)
    info = f"Курс {lessonsData['courses'][str(courseID)]['name']}:\n{lessonsData['courses'][str(courseID)]['subtitle']}\n\nКласс: {lessonsData['courses'][str(courseID)]['class']}\nУроков: {len(lessonsData['courses'][str(courseID)]['lessons'])}\n\nРекомендации к курсу: {lessonsData['courses'][str(courseID)]['recommendations']}\n"
    if str(courseID) in data['education'][str(message.chat.id)]['my_courses']:
        info += f"Пройдено уроков: {data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons']}"
        if data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed'] == True:
            btn = types.InlineKeyboardButton("Обнулить курс", callback_data=f"course_back:{courseID}")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def go_course_lesson(message, courseID):
    if str(courseID) in data['education'][str(message.chat.id)]['my_courses']:
        pass
    else:
        data['education'][str(message.chat.id)]['my_courses'][str(courseID)]={"completed_lessons":0, "completed":False}
    data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons']+=1
    i = data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons']
    if i >= len(lessonsData['courses'][str(courseID)]['lessons']):
        if data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed'] != True:
            data['education'][str(message.chat.id)]['completed_courses']+=1
            data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed'] = True
        data['education'][str(message.chat.id)]['my_courses'][str(courseID)]['completed_lessons'] = len(lessonsData['courses'][str(courseID)]['lessons'])
        i = len(lessonsData['courses'][str(courseID)]['lessons'])
    save_data()
    start_lesson(message, lessonsData['courses'][str(courseID)]['lessons'][str(i)], 1)
def lessons_list(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пройденные уроки", callback_data="completed_lessons_list")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData["subjects"][el], callback_data=f"lessons_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет", reply_markup=markup)

def проверка_на_то_пройдены_ли_все_уроки_темы(userClass, chatID, theme):
    for elem in lessonsData["lessons"]["themes"][f"{userClass}classThemes"][theme]["list"]:
        if elem not in data['education'][str(chatID)]["complet_lessons"]:
            return True
    return False
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('lessons_subject_list:'))
def lessons_subject_list(callback):
    message, subject, userClass = callback.data.split(":")
    message = callback.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="lessons_list")
    markup.add(btn)
    for el in lessonsData["lessons"]["themes"][f"{userClass}classThemes"]:
        if lessonsData["lessons"]["themes"][f"{userClass}classThemes"][el]["subject"] == subject:
            if проверка_на_то_пройдены_ли_все_уроки_темы(userClass, message.chat.id, el):
                btn = types.InlineKeyboardButton(el, callback_data=f"lessons_theme_list:{subject}:{userClass}:{el}")
                markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери тему",reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('lessons_theme_list:'))
def lessons_theme_list(call):
    message, subject, userClass, theme = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"lessons_subject_list:{subject}:{userClass}")
    markup.add(btn)
    for el in lessonsData["lessons"]["themes"][f"{userClass}classThemes"][theme]["list"]:
        if el not in data["education"][str(message.chat.id)]["complet_lessons"]:
            btn = types.InlineKeyboardButton(lessonsData["lessons"][el]["name"], callback_data=f"lesson:{el}:1")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери урок",reply_markup=markup)
def completed_lessons_list(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="lessons_list")
    markup.add(btn)
    for el in lessonsData['lessons']:
        if el in data['education'][str(message.chat.id)]['complet_lessons']:
            btn = types.InlineKeyboardButton(lessonsData['lessons'][el]['name'], callback_data=f"lesson:{el}:1")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Пройденные уроки:", reply_markup=markup)
def tests_list(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    btn = types.InlineKeyboardButton("Пройденные тесты", callback_data="completed_tests_list")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData["subjects"][el],callback_data=f"tests_subject_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет",reply_markup=markup)

def проверка_на_то_пройдены_ли_все_тесты_темы(userClass, chatID, theme):
    for elem in lessonsData["tests"]["themes"][f"{userClass}classThemes"][theme]["list"]:
        if elem not in data['education'][str(chatID)]["complet_tests"]:
            return True
    return False
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('tests_subject_list:'))
def tests_list_subject(call):
    message, subject, userClass = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="tests_list")
    markup.add(btn)
    for el in lessonsData["tests"]["themes"][f"{userClass}classThemes"]:
        if lessonsData["lessons"]["themes"][f"{userClass}classThemes"][el]["subject"] == subject:
            if проверка_на_то_пройдены_ли_все_тесты_темы(userClass, message.chat.id, el):
                btn = types.InlineKeyboardButton(el, callback_data=f"tests_theme_list:{subject}:{userClass}:{el}")
                markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери тему",reply_markup=markup)
@bot.callback_query_handler(func=lambda callback: callback.data.startswith('tests_theme_list:'))
def tests_theme_list(call):
    message, subject, userClass, theme = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"tests_subject_list:{subject}:{userClass}")
    markup.add(btn)
    for el in lessonsData["tests"]["themes"][f"{userClass}classThemes"][theme]["list"]:
        if el not in data["education"][str(message.chat.id)]["complet_tests"]:
            btn = types.InlineKeyboardButton(lessonsData["tests"][el]["name"], callback_data=f"test:{el}:1:0:False")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери тест",reply_markup=markup)
def completed_tests_list(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="tests_list")
    markup.add(btn)
    for el in lessonsData['tests']:
        if el in data['education'][str(message.chat.id)]['complet_tests']:
            btn = types.InlineKeyboardButton(lessonsData['tests'][el]['name'], callback_data=f"test:{el}:1:0:False")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Пройденные тесты:", reply_markup=markup)
def cheat_sheets_list(message):
    conn = sql_conn()
    cur = conn.cursor()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    userClass = int(cur.fetchone()[0][0])
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="education")
    markup.add(btn)
    for el in lessonsData["subjects"]:
        btn = types.InlineKeyboardButton(lessonsData["subjects"][el], callback_data=f"sen_cheat_sheets_list:{el}:{userClass}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет", reply_markup=markup)
def start_lesson(message, lessonID, index):
    markup = types.InlineKeyboardMarkup()
    if index == len(lessonsData["lessons"][lessonID]["text"]):
        if str(lessonID) in data['education'][str(message.chat.id)]['complet_lessons']:
            data['education'][str(message.chat.id)]['complet_lessons'][str(lessonID)]+=1
        else:
            data['education'][str(message.chat.id)]['completed_lesson']+=1
            data['education'][str(message.chat.id)]['complet_lessons'][str(lessonID)]=1
        save_data()
        btn = types.InlineKeyboardButton("Пройти тест", callback_data=f'test:{lessonsData["lessons"][lessonID]["test"]}:1:0:False')
        markup.add(btn)
    else:
        btn = types.InlineKeyboardButton("Дальше", callback_data=f'lesson:{lessonID}:{index+1}')
        markup.add(btn)
    btn = types.InlineKeyboardButton("Закончить", callback_data='lessons_list')
    markup.add(btn)
    info = lessonsData["lessons"][lessonID]["text"][str(index)]
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def start_test(message, testID, index, score, true=False):
    markup = types.InlineKeyboardMarkup()
    question = ""
    if index != 1 and true == False:
        question += "Не верно\nПравильный ответ: " + lessonsData["tests"][testID]["questions"][f"{index-1}variants"]["1"] + "\n\n"
    if true == True:
        question += "Верно\n\n"
        score+=1
    if index > len(lessonsData["tests"][testID]["questions"])/2:
        info = f"Результат теста\nВопросов: {index-1}\nПравильных ответов: {score}"
        if str(testID) in data['education'][str(message.chat.id)]['complet_tests']:
            data['education'][str(message.chat.id)]['complet_tests'][str(testID)]+=1
        else:
            data['education'][str(message.chat.id)]['completed_tests']+=1
            i = 10/(index-1)*score
            t = data['education'][str(message.chat.id)]['GPA']
            if data['education'][str(message.chat.id)]["completed_tests"] == 1: t = i
            data['education'][str(message.chat.id)]['GPA'] = round((i+t)/2, 2)
            data['education'][str(message.chat.id)]['complet_tests'][str(testID)]=1
        data['education'][str(message.chat.id)]['problems_solved'] += index - 1
        data['education'][str(message.chat.id)]['decided_correctly'] += score
        save_data()
        btn = types.InlineKeyboardButton("Выйти", callback_data="education")
        markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
    else:
        question += lessonsData["tests"][testID]["questions"][str(index)]
        method = [1,2,3,4]
        random.shuffle(method)
        for el in method:
            if el == 1:
                btn = types.InlineKeyboardButton(lessonsData["tests"][testID]["questions"][f"{index}variants"][str(el)], callback_data=f'test:{testID}:{index+1}:{score}:True')
            else:
                btn = types.InlineKeyboardButton(lessonsData["tests"][testID]["questions"][f"{index}variants"][str(el)],callback_data=f'test:{testID}:{index+1}:{score}:False')
            markup.add(btn)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=question, reply_markup=markup)
def sen_cheat_sheets_list(message, subject, userClass):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="cheat_sheets_list")
    markup.add(btn)
    for el in lessonsData["cheat_sheets"][f"{userClass}class"]:
        if lessonsData["cheat_sheets"][f"{userClass}class"][el]["subject"] == subject:
            btn = types.InlineKeyboardButton(el, callback_data=f"s_theme_list:{subject}:{userClass}:{el}")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Выбери тему", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: callback.data.startswith('s_theme_list:'))
def s_theme_list(call):
    message, subject, userClass, theme = call.data.split(":")
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"sen_cheat_sheets_list:{subject}:{userClass}")
    markup.add(btn)
    for el in lessonsData["cheat_sheets"][f"{userClass}class"][theme]:
        if el != "subject":
            btn = types.InlineKeyboardButton(lessonsData["cheat_sheets"][f"{userClass}class"][theme][el]["name"], callback_data=f"sen_cheat_sheets:{userClass}:{theme}:{el}")
            markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Выбери шпаргалку",reply_markup=markup)
def sen_cheat_sheets(message, userClass, theme, cheat_sheetsID):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"s_theme_list:{lessonsData['cheat_sheets'][f'{userClass}class'][theme]['subject']}:{userClass}:{theme}")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=lessonsData['cheat_sheets'][f'{userClass}class'][theme][cheat_sheetsID]["text"], reply_markup=markup)
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
    tempData["usersData"][str(message.chat.id)]["tempMessage"] = message
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
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    if cur.fetchone()[0] is None:
        bot.send_message(message.chat.id, "Сначала укажите класс в личном кабинете")
        cur.close()
        conn.close()
        return
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
                "Русская лит.", "Белорусская лит.", "Человек и мир", "Всемирная истроия",
                "История Беларуси", "История России", "Искусство", "Биология", "География", "Информатика", "Физика",
                "Химия", "Обществоведение", "Допризыв. под.", "Мед. подготовка", "Черчение",
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
    if int(number) >= 10:
        rasp(message, schoolID, school_class, 2)
        return
    for el in subjects:
        btn = types.InlineKeyboardButton(el, callback_data=f"add_dz:{schoolID}:{school_class}:{day}:{int(number)+1}:{el}")
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Выбери {int(number)+1} урок", reply_markup=markup)
def see_news(message, schoolID, school_class):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM news WHERE class = ?', (school_class,))
    news = cur.fetchall()
    cur.close()
    conn.close()
    info = "Новости:\n"
    for el in news:
        info+=el[1]+"\n"+el[2]+"\n\n"
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="school_infoo")
    markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
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
        temp_array.append(el[1])
    temp_set = list(set(temp_array))
    for el in temp_set:
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
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=markup)
def add_homeTask(message, schoolID, school_class):
    today = datetime.today().date()
    todaySPL = str(today).split('-')
    i = 0
    d = int(todaySPL[2])
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID}:{school_class}:0")
    markup.add(btn)
    for i in range(0,10):
        btn = types.InlineKeyboardButton(f'{d}.{todaySPL[1]}.{todaySPL[0]}', callback_data=f"add_homeTask_step_1:{d}.{todaySPL[1]}.{todaySPL[0]}")
        markup.add(btn)
        d+=1
        if d >= 32:
            d=1
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери дату (Обратите внимание на 31 число, его может не быть в месяце)", reply_markup=markup)
def add_homeTask_step_1(message):
    global tempData
    ttempData = tempData["usersData"][str(message.chat.id)]["tempDate"]
    date = datetime.strptime(ttempData, '%d.%m.%Y')
    weekday = date.weekday()
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT schoolID FROM users WHERE chatID = ?', (message.chat.id,))
    schoolID = cur.fetchone()
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    my_class = cur.fetchone()
    cur.close()
    conn.close()
    conn = sql.connect(f'./sqls/{schoolID[0]}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM rasp WHERE day = ? AND class = ?', (weekday, my_class[0]))
    rasp = cur.fetchone()
    cur.execute('SELECT predmet FROM dz WHERE date = ? AND class = ?', (ttempData, my_class[0]))
    dzs = cur.fetchall()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID[0]}:{my_class[0]}:0")
    markup.add(btn)
    i = 0
    for i in range(0,10):
        i += 1
        if rasp[i+2] != None:
            b = True
            for el in dzs:
                if el[0] == rasp[i+2]:
                    b = False
            if b == True:
                btn = types.InlineKeyboardButton(rasp[i+2], callback_data=f"add_homeTask_step_2:{ttempData}:{rasp[i+2]}")
                markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет\n\nЕсли нужного предмета нету, значит дз на него уже задано или его нет в расписании на это число", reply_markup=markup)

def add_homeTask_step_2(message, date, subject):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data="school_infoo")
    markup.add(btn)
    tempData["usersData"][str(message.chat.id)]["tempSubject"] = subject
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Впиши дз по {subject} на {date}", reply_markup=markup)
    bot.register_next_step_handler(message, add_homeTask_step_3)
def add_homeTask_step_3(message):
    conn = sql.connect('db.sql')
    cur = conn.cursor()
    cur.execute('SELECT schoolID FROM users WHERE chatID = ?', (message.chat.id,))
    t = cur.fetchone()
    schoolID = t[0]
    cur.execute('SELECT class FROM users WHERE chatID = ?', (message.chat.id,))
    t = cur.fetchone()
    my_class = t[0]
    cur.close()
    conn.close()
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO dz (date, predmet, dz, class) VALUES (?,?,?,?)', (tempData["usersData"][str(message.chat.id)]["tempDate"], tempData["usersData"][str(message.chat.id)]["tempSubject"], message.text, my_class))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Дз добавлено")
    school_info(message)
def rem_homeTask(message, schoolID, school_class):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM dz WHERE class = ?', (school_class,))
    dzs = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID}:{school_class}:0")
    markup.add(btn)
    temp_array = []
    for el in dzs:
        temp_array.append(el[1])
    temp_set = list(set(temp_array))
    for el in temp_set:
        btn = types.InlineKeyboardButton(el, callback_data=f'rem_dz_step_1:{schoolID}:{school_class}:{el}')
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери день",reply_markup=markup)

def rem_dz_step_1(message, schoolID, school_class, date):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM dz WHERE class = ? AND date = ?', (school_class, date))
    dzs = cur.fetchall()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("Назад", callback_data=f"homeTask:{schoolID}:{school_class}:0")
    markup.add(btn)
    temp_array = []
    for el in dzs:
        temp_array.append(el[2])
    temp_set = list(set(temp_array))
    for el in temp_set:
        btn = types.InlineKeyboardButton(el, callback_data=f'rem_dz_step_2:{schoolID}:{school_class}:{date}:{el}')
        markup.add(btn)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбери предмет и дз по нему сразу удалится",reply_markup=markup)
def rem_dz_step_2(message, schoolID, school_class, date, subject):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('DELETE FROM dz WHERE class = ? AND predmet = ? AND date = ?', (school_class, subject, date))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, "Дз успешно удалено")
    see_dz(message, schoolID, school_class, 0)
def create_new_scholl_db(schoolID):
    conn = sql.connect(f'./sqls/{schoolID}.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS rasp (id int auto_increment primary key, class varchar(6), day int, lesson1 varchar(25), lesson2 varchar(25), lesson3 varchar(25), lesson4 varchar(25), lesson5 varchar(25), lesson6 varchar(25), lesson7 varchar(25), lesson8 varchar(25), lesson9 varchar(25), lesson10 varchar(25))')
    cur.execute('CREATE TABLE IF NOT EXISTS news (id int auto_increment primary key, date varchar(50), news varchar(5000), NewsId int, class varchar(6))')
    cur.execute('CREATE TABLE IF NOT EXISTS dz (id int auto_increment primary key, date varchar(50), predmet varchar(25), dz varchar(1000), dzId int, class varchar(25))')
    conn.commit()
    cur.close()
    conn.close()

def kretoffSchool(message):
    markup = types.InlineKeyboardMarkup()
    bot.send_message(message.chat.id, "В разработке", reply_markup=markup)
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
    elif message.text == "Школа kretoffer'a 💻":
        kretoffSchool(message)
    else:
        if message.text.lower() in ["ты лох", "ты дурак", "ты ужасен", "ты худший"]:
            bot.send_message(message.chat.id, f"Сам {message.text.lower()}! 😤")
            return
        bot.send_message(message.chat.id, "Я вас не понимаю")

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
        tempData["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        tempData["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_obl)
    elif callRazd[0] == "serd_register_step":
        data["usersData"][str(call.message.chat.id)]["sity"] = callRazd[1]
        send_vibor_school(call.message)
    elif callRazd[0] == "serd_register_step_else":
        tempData["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        tempData["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
        bot.register_next_step_handler(call.message, else_sity)
    elif callRazd[0] == "fourth_register_step":
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute(f"SELECT schoolID FROM schools WHERE school = ?",(callRazd[1],))
        school = cur.fetchone()
        cur.execute('UPDATE users SET schoolID = ? WHERE chatID = ?', (school[0], call.message.chat.id))
        cur.execute('UPDATE users SET autorizationStep = ? WHERE chatID = ?', (1, call.message.chat.id))
        cur.execute('INSERT INTO timeOuts (chatID, report, selectClass, selectSchool) VALUES ("%s", "%s", "%s", "%s")' % (call.message.chat.id, 0, 0, 0))
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(call.message.chat.id, "Вы успешно зарегистрированы")
        Go_start(call.message)
    elif callRazd[0] == "fourth_register_step_else":
        tempData["usersData"][str(call.message.chat.id)]["botMessageID"] = call.message
        tempData["usersData"][str(call.message.chat.id)]["MessageID"] = bot.send_message(call.message.chat.id, "Введите название").message_id
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
        infoText = f'ID: {info[1]}\n\nСтрана: {info[2]}\nОбласть: {info[3]}\nГород/деревня: {info[4]}\nШкола: {info[5]}\nРейтинг: {info[6]}'
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
        conn = sql.connect('db.sql')
        cur = conn.cursor()
        cur.execute('SELECT selectClass FROM timeOuts WHERE chatID = ?', (call.message.chat.id,))
        timeOut = int(cur.fetchone()[0])
        cur.close()
        conn.close()
        if timeOut+2592000 > datetime.now().timestamp():
            bot.send_message(call.message.chat.id, f"Вы сможете изменить класс только через {int((timeOut+2592000-datetime.now().timestamp())/86400)} дней") ######
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
        cur.execute('UPDATE timeOuts SET selectClass = ? WHERE chatID = ?', (datetime.now().timestamp(), call.message.chat.id))
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
        bot.send_message(call.message.chat.id, f"Если ваш друг перейдет по вашей реферальной ссылке, то вы и ваш друг получите по 10 алмазов\n\nВаша ссылка:\nhttps://t.me/{config.BOT_NICKNAME}?start={call.message.chat.id}\n\nТекущее количество приглашенных людей: {data['usersData'][str(call.message.chat.id)]['invitedCol']}")
    elif callRazd[0] == "rasp":
        rasp(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "news":
        see_news(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "homeTask":
        see_dz(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "school_infoo":
        bot.delete_message(call.message.chat.id, call.message.message_id)
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
        gdz(call.message)
    elif callRazd[0] == "see_dz_step_1":
        see_dz_step_1(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "new_name":
        bot.send_message(int(callRazd[1]), "Впишите новое имя")
        message = tempData["usersData"][str(callRazd[1])]["tempMessage"]
        bot.register_next_step_handler(message, new_name)
    elif callRazd[0] == "new_last_name":
        bot.send_message(int(callRazd[1]), "Впишите новую фамилию")
        message = tempData["usersData"][str(callRazd[1])]["tempMessage"]
        bot.register_next_step_handler(message, new_last_name)
    elif callRazd[0] == "add_homeTask_step_1":
        print(call.message)
        tempData["usersData"][str(call.message.chat.id)]["tempDate"] = callRazd[1]
        add_homeTask_step_1(call.message)
    elif callRazd[0] == "add_homeTask_step_2":
        add_homeTask_step_2(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "rem_dz_step_1":
        rem_dz_step_1(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "rem_dz_step_2":
        rem_dz_step_2(call.message, callRazd[1], callRazd[2], callRazd[3], callRazd[4])
    elif callRazd[0] == "my_courses":
        my_courses(call.message)
    elif callRazd[0] == "lessons_list":
        lessons_list(call.message)
    elif callRazd[0] == "courses_list":
        courses_list(call.message)
    elif callRazd[0] == "tests_list":
        tests_list(call.message)
    elif callRazd[0] == "cheat_sheets_list":
        cheat_sheets_list(call.message)
    elif callRazd[0] == "completed_courses":
        completed_courses(call.message)
    elif callRazd[0] == "education":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        go_education(call.message)
    elif callRazd[0] == "course":
        start_course(call.message, callRazd[1])
    elif callRazd[0] == "lesson":
        start_lesson(call.message, callRazd[1], int(callRazd[2]))
    elif callRazd[0] == "test":
        if callRazd[4] == "False": t = False
        elif callRazd[4] == "True": t = True
        start_test(call.message, callRazd[1], int(callRazd[2]), int(callRazd[3]), t)
    elif callRazd[0] == "sen_cheat_sheets_list":
        sen_cheat_sheets_list(call.message, callRazd[1], callRazd[2])
    elif callRazd[0] == "sen_cheat_sheets":
        sen_cheat_sheets(call.message, callRazd[1], callRazd[2], callRazd[3])
    elif callRazd[0] == "go_course_lesson":
        go_course_lesson(call.message, callRazd[1])
    elif callRazd[0] == "completed_lessons_list":
        completed_lessons_list(call.message)
    elif callRazd[0] == "completed_tests_list":
        completed_tests_list(call.message)
    elif callRazd[0] == "course_back":
        data['education'][str(call.message.chat.id)]['my_courses'][callRazd[1]]['completed'] = False
        data['education'][str(call.message.chat.id)]['my_courses'][callRazd[1]]['completed_lessons'] = 0
        save_data()
    elif callRazd[0] == "courses_subject_list":
        courses_subject_list(call.message, callRazd[1], int(callRazd[2]))
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
            if el[0] not in my_array:
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
    bot.delete_message(message.chat.id, tempData["usersData"][str(message.chat.id)]["MessageID"])
    data["usersData"][f"{message.chat.id}"]["obl"] = message.text
    save_data()
    send_vibor_sity(tempData["usersData"][f"{message.chat.id}"]["botMessageID"])

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
            if el[0] not in my_array:
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
    bot.delete_message(message.chat.id, tempData["usersData"][str(message.chat.id)]["MessageID"])
    data["usersData"][f"{message.chat.id}"]["sity"] = message.text
    save_data()
    send_vibor_school(tempData["usersData"][f"{message.chat.id}"]["botMessageID"])

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
            if el[0] not in my_array:
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
    cur.execute('INSERT INTO timeOuts (chatID, report, selectClass, selectSchool) VALUES ("%s", "%s", "%s", "%s")' % (message.chat.id, 0, 0, 0))
    conn.commit()
    cur.close()
    conn.close()
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, tempData["usersData"][str(message.chat.id)]["MessageID"])
    bot.send_message(message.chat.id,"Вы успешно зарегистрированы, для начала работы с ботом пропишите /start")
    create_new_scholl_db(len(schols))
    Go_start(message)

print("бот запущен...")
delOldDz()
bot.send_message(config.ADMIN_ID, "Бот запущен")
bot.polling(none_stop=True)
bot.send_message(config.ADMIN_ID, "Бот выключается")